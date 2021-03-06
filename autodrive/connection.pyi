from ._conn import Connection as Connection
from .dtypes import (
    EffectiveFmt as EffectiveFmt,
    EffectiveVal as EffectiveVal,
    FormattedVal as FormattedVal,
    UserEnteredVal as UserEnteredVal,
)
from .interfaces import AuthConfig as AuthConfig
from pathlib import Path
from typing import Any, Dict, List, Literal, Union

class FileUpload:
    path: Path = ...
    folder: Union[str, None] = ...
    name_override: Union[str, None] = ...
    _do_conv: bool = ...
    def __init__(
        self,
        path: Union[Path, str],
        to_folder_id: Union[str, None] = ...,
        convert: Union[bool, None] = ...,
        name_override: str | None = ...,
    ) -> None: ...
    @property
    def do_conv(self) -> bool: ...

class DriveConnection(Connection):
    _files: Any = ...
    _fmt_map: Any = ...
    def __init__(
        self, *, auth_config: Union[AuthConfig, None] = ..., api_version: str = ...
    ) -> None: ...
    def get_import_formats(self) -> Dict[str, str]: ...
    def find_object(
        self,
        obj_name: str,
        obj_type: Union[Literal["sheet", "folder", "file"], None] = ...,
        shared_drive_id: Union[str, None] = ...,
    ) -> List[Dict[str, Any]]: ...
    def create_object(
        self,
        obj_name: str,
        obj_type: Literal["sheet", "folder"],
        parent_id: Union[str, None] = ...,
    ) -> str: ...
    def delete_object(self, object_id: str) -> None: ...
    def upload_files(
        self, *filepaths: Union[Path, str, FileUpload]
    ) -> Dict[str, str]: ...
    def detect_conv_format(self, p: Path) -> str: ...
    @staticmethod
    def _setup_drive_id_kwargs(
        drive_id: Union[str, None] = ...
    ) -> Dict[str, Union[str, bool]]: ...

class SheetsConnection(Connection):
    _sheets: Any = ...
    def __init__(
        self, *, auth_config: Union[AuthConfig, None] = ..., api_version: str = ...
    ) -> None: ...
    def execute_requests(
        self, spreadsheet_id: str, requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]: ...
    def get_properties(self, spreadsheet_id: str) -> Dict[str, Any]: ...
    def get_data(
        self, spreadsheet_id: str, ranges: Union[List[str], None] = ...
    ) -> Dict[str, Any]: ...
