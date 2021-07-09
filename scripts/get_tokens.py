import pickle
from autodrive.interfaces import AuthConfig

"""
Convenience script for pulling the token and refresh token out of the pickled token
file.
"""

if __name__ == "__main__":
    config = AuthConfig()
    with open(config.token_filepath, "rb") as token:
        creds = pickle.load(token)
    with open(config.token_filepath.with_suffix(".txt"), "w") as w:
        w.write(f"{creds.token}\n{creds.refresh_token}")
