from __future__ import annotations

from typing import Any, Dict, List, Literal

from . import _google_terms as terms
from ._conn import Connection
from .dtypes import EffectiveFmt, EffectiveVal, FormattedVal, UserEnteredVal
from .interfaces import AuthConfig


class DriveConnection(Connection):
    """
    Provides a connection to the Google Drive api, and methods to send requests
    to it.

    This class is documented primarily for reference, if you want to connect to
    Google Drive, it's easier to just use a :class:`Drive <autodrive.drive.Drive>`
    instance.
    """

    def __init__(
        self,
        *,
        auth_config: AuthConfig | None = None,
        api_version: str = "v3",
    ) -> None:
        """

        Args:
            auth_config (AuthConfig, optional): Optional custom AuthConfig object,
                defaults to None.
            api_version (str, optional): The version of the Drive api to connect to,
                defaults to "v3".

        """
        super().__init__(
            api_name="drive",
            api_version=api_version,
            auth_config=auth_config,
        )
        self._files = self._core.files()  # type: ignore

    def find_object(
        self,
        obj_name: str,
        obj_type: Literal["sheet", "folder"],
        shared_drive_id: str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Searches for a Google Drive Object via the connected api.

        Args:
            obj_name (str): The name of the object, or part of its name.
            obj_type (Literal["sheet", "folder"]): The type of object to restrict
                the search to.
            shared_drive_id (str, optional): The id of a Shared Drive to search
                within, if desired, defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of object properties, if any matches are
            found.

        """
        query = f"name = '{obj_name}'"
        if obj_type:
            query += f" and mimeType='{self.google_obj_types[obj_type]}'"
        kwargs = self._setup_drive_id_kwargs(shared_drive_id)
        page_token = None
        results: List[Dict[str, Any]] = []
        while True:
            response = self._files.list(  # type: ignore
                q=query,
                spaces="drive",
                fields=f"nextPageToken, files ({terms.ID},{terms.NAME},{terms.PARENTS})",
                pageToken=page_token,
                **kwargs,
            ).execute()
            for file in response.get("files", []):  # type: ignore
                results.append(
                    dict(
                        name=file.get(terms.NAME),  # type: ignore
                        id=file.get(terms.ID),  # type: ignore
                        parents=file.get(terms.PARENTS),  # type: ignore
                    )
                )
            page_token = response.get("nextPageToken", None)  # type: ignore
            if page_token is None:
                break
        return results

    def create_object(
        self,
        obj_name: str,
        obj_type: Literal["sheet", "folder"],
        parent_id: str | None = None,
    ) -> str:
        """
        Creates a file or folder via the Google Drive connection.

        Args:
            obj_name (str): The desired name of the object to create.
            obj_type (Literal["sheet", "folder"]): The type of object to create.
            parent_id (str, optional): The id of the folder or shared drive to
                create the object within, defaults to None.

        Returns:
            str: The new id of the created object.

        """
        kwargs: Dict[str, List[str]] = (
            dict(parents=[parent_id]) if parent_id else dict()
        )
        file_metadata: Dict[str, Any] = dict(
            name=obj_name, mimeType=self.google_obj_types[obj_type], **kwargs
        )
        file = self._files.create(  # type: ignore
            body=file_metadata, fields=terms.ID, supportsAllDrives=True
        ).execute()
        return file.get(terms.ID)  # type: ignore

    def delete_object(self, object_id: str) -> None:
        """
        Deletes the passed Google object id from the connected Google Drive.

        Args:
            object_id (str): A Google object id.

        """
        self._files.delete(  # type: ignore
            fileId=object_id, supportsAllDrives=True
        ).execute()

    @staticmethod
    def _setup_drive_id_kwargs(drive_id: str | None = None) -> Dict[str, str | bool]:
        """
        Whenever a drive_id is needed to access a shared drive, two other kwargs
        need to be passed to the relevant function. This method preps all three
        kwargs.

        Args:
            drive_id (str, optional): The id of the shared drive, defaults to None.

        Returns:
            Dict[str, str | bool]: A dictionary containing the kwargs needed to
            access the shared drive.

        """
        kwargs: Dict[str, str | bool] = dict()
        if drive_id:
            kwargs["corpora"] = "drive"
            kwargs["driveId"] = drive_id
            kwargs["includeItemsFromAllDrives"] = True
            kwargs["supportsAllDrives"] = True
        return kwargs


class SheetsConnection(Connection):
    """
    Provides a connection to the Google Sheets api, and methods to send requests
    to it.

    This class is documented primarily for reference, if you want to connect to
    Google Sheets, it's easier to just use a View.
    """

    def __init__(
        self,
        *,
        auth_config: AuthConfig | None = None,
        api_version: str = "v4",
    ) -> None:
        """
        Args:
            auth_config (AuthConfig, optional): Optional custom AuthConfig object,
                defaults to None.
            api_version (str, optional): The version of the Sheets api to connect
                to, defaults to "v4".

        """
        super().__init__(
            api_name="sheets",
            api_version=api_version,
            auth_config=auth_config,
        )
        self._sheets = self._core.spreadsheets()  # type: ignore

    def execute_requests(
        self, spreadsheet_id: str, requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Sends the passed list of request dictionaries to the Sheets api to be
        applied to the spreadsheet_id via batch update.

        Args:
            spreadsheet_id (str): The id of the Google Sheet to update.
            requests (List[Dict[str, Any]]): A list of dictionaries formatted as
                requests.

        Returns:
            Dict[str, Any]: The resulting response from the Sheets api as a
            dictionary.

        """
        result: Dict[str, Any] = self._sheets.batchUpdate(  # type: ignore
            spreadsheetId=spreadsheet_id, body=self._preprocess_requests(requests)
        ).execute()
        return result

    def get_properties(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Gets the metadata properties of the indicated Google Sheet.

        Args:
            spreadsheet_id (str): The id of the Google Sheet to collect properties
                from.

        Returns:
            Dict[str, Any]: A dictionary of the Google Sheet's properties.

        """
        gsheet_props = f"{terms.FILE_PROPS}({terms.FILE_NAME})"
        grid_props = f"{terms.GRID_PROPS}({terms.COL_CT},{terms.ROW_CT})"
        tab_props = f"{terms.TAB_IDX},{terms.TAB_ID},{terms.TAB_NAME},{grid_props}"
        tabs_prop = f"{terms.TABS_PROP}({terms.TAB_PROPS}({tab_props}))"
        return self._sheets.get(  # type: ignore
            spreadsheetId=spreadsheet_id, fields=f"{gsheet_props},{tabs_prop}"
        ).execute()

    def get_data(
        self, spreadsheet_id: str, ranges: List[str] | None = None
    ) -> Dict[str, Any]:
        """
        Collects data from cells in the passed spreadsheet.

        Args:
            spreadsheet_id (str): The id of the Google Sheet to collect data from.
            ranges (List[str], optional): A list of range strings
                (e.g. Sheet1!A1:C3), defaults to None, which prompts get_data to
                fetch all data from all cells.

        Returns:
            Dict[str, Any]: The collected data from the spreadsheet, raw and
            unparsed.

        """
        data_values = f"{UserEnteredVal},{FormattedVal},{EffectiveVal}"
        formatting_values = f"{EffectiveFmt}"
        values = f"{terms.VALUES}({data_values},{formatting_values})"
        return self._sheets.get(  # type: ignore
            spreadsheetId=spreadsheet_id,
            fields=f"{terms.TABS_PROP}({terms.DATA}({terms.ROWDATA}({values})))",
            ranges=ranges or [],
        ).execute()
