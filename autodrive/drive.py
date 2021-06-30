from __future__ import annotations

from typing import List, Optional

from .connection import AuthConfig, DriveConnection, SheetsConnection
from .gsheet import GSheet


class Folder:
    def __init__(
        self,
        folder_id: str,
        name: str,
        *,
        parents: List[str] | None = None,
        auth_config: AuthConfig | None = None,
        drive_conn: DriveConnection | None = None,
    ) -> None:
        self._id = folder_id
        self._name = name
        self._parents = parents or []
        self._conn = drive_conn or DriveConnection(auth_config=auth_config)

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent_ids(self) -> List[str]:
        return self._parents

    def create_folder(self, folder_name: str) -> Folder:
        id = self._conn.create_object(folder_name, "folder", self._id)
        return Folder(
            id,
            folder_name,
            parents=[self._id],
            drive_conn=self._conn,
        )


class Drive:
    def __init__(
        self,
        *,
        auth_config: AuthConfig | None = None,
        drive_conn: DriveConnection | None = None,
        sheets_conn: SheetsConnection | None = None,
    ) -> None:
        self._conn = drive_conn or DriveConnection(auth_config=auth_config)
        self._sheets_conn = sheets_conn or SheetsConnection(auth_config=self._conn.auth)

    def create_folder(
        self, folder_name: str, parent: str | Folder | None = None
    ) -> Folder:
        parent_id = self._ensure_parent_id(parent)
        new_id = self._conn.create_object(folder_name, "folder", parent_id)
        return Folder(
            folder_id=new_id,
            name=folder_name,
            parents=[parent_id] if parent_id else None,
            drive_conn=self._conn,
        )

    def create_gsheet(
        self, gsheet_name: str, parent: str | Folder | None = None
    ) -> GSheet:
        parent_id = self._ensure_parent_id(parent)
        new_id = self._conn.create_object(gsheet_name, "sheet", parent_id)
        return GSheet(new_id, gsheet_name, sheets_conn=self._sheets_conn)

    def find_gsheet(self, gsheet_name: str) -> List[GSheet]:
        result = self._conn.find_object(gsheet_name, "sheet")
        return [
            GSheet(r["id"], r["name"], sheets_conn=self._sheets_conn) for r in result
        ]

    def find_folder(
        self, folder_name: str, shared_drive_id: str | None = None
    ) -> List[Folder]:
        result = self._conn.find_object(folder_name, "folder", shared_drive_id)
        return [
            Folder(r["id"], r["name"], parents=r["parents"], drive_conn=self._conn)
            for r in result
        ]

    @staticmethod
    def _ensure_parent_id(parent: str | Folder | None = None) -> Optional[str]:
        return parent.id if isinstance(parent, Folder) else parent
