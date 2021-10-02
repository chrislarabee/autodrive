from .interfaces import AuthConfig as AuthConfig
from abc import ABC
from google.oauth2.credentials import Credentials  # type: ignore
from googleapiclient.discovery import Resource
from typing import Any, Dict, List, Literal, Tuple, Union

SCOPES: Any

class Connection(ABC):
    google_obj_types: Any = ...
    _auth_config: Any = ...
    _core: Any = ...
    def __init__(
        self,
        api_name: Literal["sheets", "drive"],
        api_version: str,
        *,
        auth_config: Union[AuthConfig, None] = ...
    ) -> None: ...
    @property
    def auth(self) -> AuthConfig: ...
    @classmethod
    def _authenticate(
        cls: Any, scopes: List[str], auth_config: AuthConfig
    ) -> Credentials: ...
    def _connect(
        self, scopes: List[str], api: Literal["drive", "sheets"], version: str
    ) -> Resource: ...
    @staticmethod
    def get_creds_from_env() -> Union[Credentials, None]: ...
    @classmethod
    def _merge_dicts(
        cls: Any, dict1: Dict[str, Any], dict2: Dict[str, Any]
    ) -> Dict[str, Any]: ...
    @staticmethod
    def _create_range_tuple_key(
        input: Dict[str, Any]
    ) -> Tuple[Tuple[str, Any], ...]: ...
    @classmethod
    def _preprocess_requests(
        cls: Any, requests: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]: ...
