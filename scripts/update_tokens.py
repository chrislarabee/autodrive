from typing import Any, Dict
import json
import requests
from base64 import b64encode

from nacl.public import SealedBox, PublicKey  # type: ignore
from nacl.encoding import Base64Encoder  # type: ignore

"""
This is a convenience script for updating the GitHub repo with the necessary 
secret keys to access a Google Drive for CI testing.

This script requires an up-to-date GitHub Personal Access Token with the following
permissions granted:
Full control of private repositories.
"""

token_key = "token"
refresh_key = "refresh_token"
token_secret = "AUTODRIVE_TOKEN"
refresh_secret = "AUTODRIVE_REFR_TOKEN"
secrets_url = "https://api.github.com/repos/chrislarabee/autodrive/actions/secrets"


def load_github_pat() -> str:
    pat = ""
    with open("github_pat.txt", "r") as r:
        for line in r:
            pat = line
    return pat


def load_tokens() -> Dict[str, Any]:
    token: Dict[str, Any] = {}
    result: Dict[str, str] = {}

    with open("gdrive_token.json", "r") as r:
        for line in r:
            token = json.loads(line)
    if token_key in token.keys():
        result[token_secret] = token[token_key]
    if refresh_key in token.keys():
        result[refresh_secret] = token[refresh_key]
    return result


def gen_header(pat: str) -> Dict[str, str]:
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {pat}",
    }


def get_repo_public_key(pat: str) -> Dict[str, str]:
    url = secrets_url + "/public-key"
    response = requests.get(url, headers=gen_header(pat))
    resp_json = response.json()
    if "key" in resp_json.keys():
        return resp_json
    else:
        raise ValueError(f"Unexpected json response: {resp_json}")


def encrypt_secret(secret_value: str, public_key: str) -> str:
    pkey = PublicKey(public_key.encode(), Base64Encoder())  # type: ignore
    sealed_box = SealedBox(pkey)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))  # type: ignore
    return b64encode(encrypted).decode("utf-8")  # type: ignore


def send_updated_tokens(
    pat: str, token_dict: Dict[str, str], public_key: Dict[str, str]
) -> Dict[str, Dict[str, Any]]:
    key: str = public_key["key"]
    key_id: str = public_key["key_id"]
    results: Dict[str, Dict[str, Any]] = {k: {} for k in token_dict.keys()}
    for secret, token in token_dict.items():
        url = f"{secrets_url}/{secret}"
        encrypted_secret = encrypt_secret(token, key)
        data = {"encrypted_value": encrypted_secret, "key_id": key_id}
        print(f"PUT {secret} to {url}...")
        response = requests.put(
            url,
            json=data,
            headers=gen_header(pat),
        )
        result: Dict[str, Any] = {}
        # Put response has no text, only status_code.
        result["status_code"] = response.status_code
        if response.status_code == 204:
            result["response"] = "Successful upload."
        else:
            result["response"] = "Unknown response."
        print(f"  > Result = {result}")
        results[secret] = result
    return results


if __name__ == "__main__":
    pat = load_github_pat()
    tokens = load_tokens()
    ad_pub_key = get_repo_public_key(pat)
    results = send_updated_tokens(pat, tokens, ad_pub_key)
