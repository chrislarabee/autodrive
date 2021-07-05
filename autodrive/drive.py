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
        """
        Stores all the necessary properties of a Google Drive Folder and provides
        methods for interacting with its subfolders and files.

        :param folder_id: The id string of the folder.
        :type folder_id: str
        :param name: The name of the folder.
        :type name: str
        :param parents: A list of the Folder's parents, usually just its parent folder
            or parent shared drive, if any, defaults to None, signifying that the
            folder is at the root of an unshared drive.
        :type parents: List[str], optional
        :param auth_config: Optional custom AuthConfig object, defaults to None
        :type auth_config: AuthConfig, optional
        :param drive_conn: Optional manually created DriveConnection, defaults to None
        :type drive_conn: DriveConnection, optional
        """
        self._id = folder_id
        self._name = name
        self._parents = parents or []
        self._conn = drive_conn or DriveConnection(auth_config=auth_config)

    @property
    def id(self) -> str:
        """
        :return: The id string of the Folder.
        :rtype: str
        """
        return self._id

    @property
    def name(self) -> str:
        """
        :return: The name of the Folder.
        :rtype: str
        """
        return self._name

    @property
    def parent_ids(self) -> List[str]:
        """
        :return: The list of the Folder's parents, usually just its parent folder
            or parent shared drive, if any.
        :rtype: List[str]
        """
        return self._parents

    def create_folder(self, folder_name: str) -> Folder:
        """
        Generates a new Folder with this Folder as its parent.

        :param folder_name: The name of the Folder to create.
        :type folder_name: str
        :return: The newly created Folder.
        :rtype: Folder
        """
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
        """
        A one-stop shop for finding and managing Google Drive objects, including
        folders and Google Sheets.

        :param auth_config: Optional custom AuthConfig object, defaults to None
        :type auth_config: AuthConfig, optional
        :param drive_conn: Optional manually created DriveConnection, defaults to None
        :type drive_conn: DriveConnection, optional
        :param sheets_conn: Optional manually created SheetsConnection, defaults to None
        :type sheets_conn: SheetsConnection, optional
        """
        self._conn = drive_conn or DriveConnection(auth_config=auth_config)
        self._sheets_conn = sheets_conn or SheetsConnection(auth_config=self._conn.auth)

    def create_folder(
        self, folder_name: str, parent: str | Folder | None = None
    ) -> Folder:
        """
        Creates a folder in the connected Google Drive.

        :param folder_name: The desired name of the new folder
        :type folder_name: str
        :param parent: The parent folder/id to create this folder within, or the id
            of the shared drive to create within, defaults to None
        :type parent: str | Folder, optional
        :return: A Folder with the details of the newly created object.
        :rtype: Folder
        """
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
        """
        Creates a Google Sheet in the connected Google Drive.

        :param gsheet_name: The desired name of the new Google Sheet.
        :type gsheet_name: str
        :param parent: The parent folder/id to create this gsheet within, or the id
            of the shared drive to create within, defaults to None
        :type parent: str | Folder, optional
        :return: A GSheet with the details of the newly created object.
        :rtype: GSheet
        """
        parent_id = self._ensure_parent_id(parent)
        new_id = self._conn.create_object(gsheet_name, "sheet", parent_id)
        return GSheet(new_id, gsheet_name, sheets_conn=self._sheets_conn)

    def find_gsheet(self, gsheet_name: str) -> List[GSheet]:
        """
        Search for Google Sheets that match the passed name. GSheets found in this
        way will need to have their properties gathered with a GSheet.fetch() call.
        To save round trips this method only collects the basic details of the Google
        Sheets it matches. These properties cannot be gathered via the Google Drive api,
        unfortunately.

        :param gsheet_name: The name (or part of the name) to search for.
        :type gsheet_name: str
        :return: A list of GSheet objects with basic details (id, name) that matched
            the name parameter.
        :rtype: List[GSheet]
        """
        result = self._conn.find_object(gsheet_name, "sheet")
        return [
            GSheet(r["id"], r["name"], sheets_conn=self._sheets_conn) for r in result
        ]

    def find_folder(
        self, folder_name: str, shared_drive_id: str | None = None
    ) -> List[Folder]:
        """
        Search for folders that match the passed name.

        :param folder_name: The name (or part of the name) to search for.
        :type folder_name: str
        :param shared_drive_id: The shared drive id to search within, defaults to None
        :type shared_drive_id: str, optional
        :return: A list of Folder object that matched the name parameter.
        :rtype: List[Folder]
        """
        result = self._conn.find_object(folder_name, "folder", shared_drive_id)
        return [
            Folder(r["id"], r["name"], parents=r["parents"], drive_conn=self._conn)
            for r in result
        ]

    @staticmethod
    def _ensure_parent_id(parent: str | Folder | None = None) -> Optional[str]:
        """
        Simple convenience method for standardizing parent inputs to be ids and not
        Folders.

        :param parent: Parent id or Folder to extract parent_id from, defaults to None
        :type parent: str | Folder, optional
        :return: The extracted parent_id or None.
        :rtype: Optional[str]
        """
        return parent.id if isinstance(parent, Folder) else parent
