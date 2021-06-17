from typing import Dict, Any, Union
from pathlib import Path

from .connection import DriveConnection, AuthConfig


class Drive:
    def __init__(
        self,
        *,
        auth_config: AuthConfig = None,
    ) -> None:
        self._conn = DriveConnection(
            auth_config=auth_config
        )

    def create_folder(self, folder_name: str):
        result = self._conn.create_object(folder_name, "folder")

    def create_gsheet(self, gsheet_name: str):
        result = self._conn.create_object(gsheet_name, "sheet")
