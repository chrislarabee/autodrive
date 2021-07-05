from __future__ import annotations

import os
import pickle
from abc import ABC
from typing import Any, Dict, List, Literal

from google.auth.transport.requests import Request  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import Resource, build

from . import google_terms as terms
from .dtypes import EffectiveFmt, EffectiveVal, FormattedVal, UserEnteredVal
from .interfaces import AuthConfig


class _Connection(ABC):
    google_obj_types = {
        "folder": "application/vnd.google-apps.folder",
        "sheet": "application/vnd.google-apps.spreadsheet",
    }

    def __init__(
        self,
        *,
        api_name: Literal["sheets", "drive"],
        api_version: str,
        api_scopes: List[str],
        auth_config: AuthConfig | None = None,
    ) -> None:
        """
        Base class of more specific Connection objects.

        :param api_name: The name of the api to connect to.
        :type api_name: Literal["sheets", "drive"]
        :param api_version: The version of the api to connect to.
        :type api_version: str
        :param api_scopes: A list of the scope strings to connect with (will fail
            if credentials don't grant those scopes).
        :type api_scopes: List[str]
        :param auth_config: Optional custom AuthConfig object, defaults to None
        :type auth_config: AuthConfig, optional
        """
        self._auth_config = auth_config or AuthConfig()
        self._core = self._connect(api_scopes, api_name, api_version)

    @property
    def auth(self) -> AuthConfig:
        """
        :return: The AuthConfig passed to this Connection object, or the AuthConfig
            that was generated automatically upon this Connection's instantiation.
        :rtype: AuthConfig
        """
        return self._auth_config

    @classmethod
    def _authenticate(
        cls,
        scopes: List[str],
        auth_config: AuthConfig,
    ) -> Credentials:
        """
        Uses configuration in passed AuthConfig to attempt to login to Google Drive.
        The first time it is run it will cause a web page to open up and solicit
        permission to access the Google Drive as specified in the credentials.
        Then it will create a token that it will use going forward.

        Note, you can also set environment variables as described in
        _Connection.get_creds_from_env() and _authenticate will automatically pull
        those in and will not create a token file.

        :param scopes: A list of scopes dictating the limits of the authenticated
            connection
        :type scopes: List[str]
        :param auth_config: An AuthConfig object, either customized or automatically
            generated.
        :type auth_config: AuthConfig
        :raises FileNotFoundError: If no credentials file is found and no creds were
            passed as environment variables or as a dictionary within AuthConfig.
        :return: A prepped Credentials object, ready to be slotted into more
            specific connections.
        :rtype: Credentials
        """
        creds = cls.get_creds_from_env()
        # The token file stores the user's access and refresh tokens, and
        # is created automatically when the authorization flow completes for the
        # first time.
        if not creds and auth_config.token_filepath.exists():
            with open(auth_config.token_filepath, "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, prompt user to log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:  # type: ignore
                creds.refresh(Request())  # type: ignore
            else:
                if auth_config.secrets_config:
                    flow = InstalledAppFlow.from_client_config(  # type: ignore
                        auth_config.secrets_config, scopes
                    )
                elif auth_config.creds_filepath.exists():
                    flow = InstalledAppFlow.from_client_secrets_file(  # type: ignore
                        str(auth_config.creds_filepath), scopes
                    )
                else:
                    raise FileNotFoundError(
                        f"Credentials file {auth_config.creds_filepath} could not be "
                        "found."
                    )
                creds = flow.run_local_server(port=0)  # type: ignore
            # Save the credentials for the next run
            with open(auth_config.token_filepath, "wb") as token:
                pickle.dump(creds, token)
        return creds

    def _connect(
        self, scopes: List[str], api: Literal["drive", "sheets"], version: str
    ) -> Resource:
        """
        Generates a connection to the specified Google api.

        :param scopes: A list of scopes dictating the limits of the authenticated
            connection
        :type scopes: List[str]
        :param api: The name of the api to connect to.
        :type api: Literal["sheets", "drive"]
        :param version: The version of the api to connect to.
        :type version: str
        :return: A Google api client Resource, which is a very general object that
            facilitates connections to the appropriate Google api.
        :rtype: Resource
        """
        creds = self._authenticate(
            scopes,
            self._auth_config,
        )
        return build(api, version, credentials=creds)

    @staticmethod
    def get_creds_from_env() -> Credentials | None:
        """
        Checks if necessary credential and token information has been specified
        in environment variables and uses that information to generate a Credentials
        object. Can be used to bypass needing credentials files saved locally.

        :return: A prepped Credentials object, ready to be slotted into more
            specific connections, if appropriate environment variables were found,
            otherwise None.
        :rtype: Credentials, optional
        """
        token = os.getenv("AUTODRIVE_TOKEN")
        refresh_token = os.getenv("AUTODRIVE_REFR_TOKEN")
        client_id = os.getenv("AUTODRIVE_CLIENT_ID")
        client_secret = os.getenv("AUTODRIVE_CLIENT_SECRET")
        if token and refresh_token and client_id and client_secret:
            return Credentials(
                token=token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=["https://www.googleapis.com/auth/drive"],
            )
        else:
            return None


class DriveConnection(_Connection):
    def __init__(
        self,
        *,
        auth_config: AuthConfig | None = None,
        api_version: str = "v3",
    ) -> None:
        """
        Provides a connection to the Google Drive api, and methods to send requests
        to it.

        :param auth_config: Optional custom AuthConfig object, defaults to None.
        :type auth_config: AuthConfig, optional
        :param api_version: The version of the Drive api to connect to, defaults to
            "v3".
        :type api_version: str, optional
        """
        super().__init__(
            api_name="drive",
            api_version=api_version,
            api_scopes=["https://www.googleapis.com/auth/drive"],
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

        :param obj_name: The name of the object, or part of its name.
        :type obj_name: str
        :param obj_type: The type of object to restrict the search to.
        :type obj_type: Literal["sheet", "folder"]
        :param shared_drive_id: The id of a Shared Drive to search within, if desired,
            defaults to None.
        :type shared_drive_id: str, optional
        :return: A list of object properties, if any matches are found.
        :rtype: List[Dict[str, Any]]
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
                fields=f"nextPageToken, files({terms.ID},{terms.NAME},{terms.PARENTS})",
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

        :param obj_name: The desired name of the object to create.
        :type obj_name: str
        :param obj_type: The type of object to create.
        :type obj_type: Literal["sheet", "folder"]
        :param parent_id: The id of the folder or shared drive to create the object
            within, defaults to None.
        :type parent_id: str, optional
        :return: The new id of the created object.
        :rtype: str
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

        :param object_id: A Google object id.
        :type object_id: str
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
            drive_id: The id of the shared drive to set up access to.

        Returns: A dictionary, either empty or containing the
            appropriate kwargs if drive_id is passed.

        :param drive_id: The id of the shared drive, defaults to None.
        :type drive_id: str, optional
        :return: A dictionary containing the kwargs needed to access the shared
            drive.
        :rtype: Dict[str, str | bool]
        """
        kwargs: Dict[str, str | bool] = dict()
        if drive_id:
            kwargs["corpora"] = "drive"
            kwargs["driveId"] = drive_id
            kwargs["includeItemsFromAllDrives"] = True
            kwargs["supportsAllDrives"] = True
        return kwargs


class SheetsConnection(_Connection):
    def __init__(
        self,
        *,
        auth_config: AuthConfig | None = None,
        api_version: str = "v4",
    ) -> None:
        """
        Provides a connection to the Google Sheets api, and methods to send requests
        to it.

        :param auth_config: Optional custom AuthConfig object, defaults to None.
        :type auth_config: AuthConfig, optional
        :param api_version: The version of the Sheets api to connect to, defaults to
            "v4".
        :type api_version: str, optional
        """
        super().__init__(
            api_name="sheets",
            api_version=api_version,
            api_scopes=["https://www.googleapis.com/auth/spreadsheets"],
            auth_config=auth_config,
        )
        self._sheets = self._core.spreadsheets()  # type: ignore

    def execute_requests(
        self, spreadsheet_id: str, requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Sends the passed list of request dictionaries to the Sheets api to be
        applied to the spreadsheet_id via batch update.

        :param spreadsheet_id: The id of the Google Sheet to update.
        :type spreadsheet_id: str
        :param requests: A list of dictionaries formatted as requests.
        :type requests: List[Dict[str, Any]]
        :return: The resulting response from the Sheets api as a dictionary.
        :rtype: Dict[str, Any]
        """
        result: Dict[str, Any] = self._sheets.batchUpdate(  # type: ignore
            spreadsheetId=spreadsheet_id, body={"requests": requests}
        ).execute()
        return result

    def get_properties(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Gets the metadata properties of the indicated Google Sheet.

        :param spreadsheet_id: The id of the Google Sheet to collect properties
            from.
        :type spreadsheet_id: str
        :return: A dictionary of the Google Sheet's properties.
        :rtype: Dict[str, Any]
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

        :param spreadsheet_id: The id of the Google Sheet to collect data from.
        :type spreadsheet_id: str
        :param ranges: A list of range strings (e.g. Sheet1!A1:C3), defaults to None,
            which prompts get_data to fetch all data from all cells.
        :type ranges: List[str], optional
        :return: The collected data from the spreadsheet, raw and unparsed.
        :rtype: Dict[str, Any]
        """
        data_values = f"{UserEnteredVal},{FormattedVal},{EffectiveVal}"
        formatting_values = f"{EffectiveFmt}"
        values = f"{terms.VALUES}({data_values},{formatting_values})"
        return self._sheets.get(  # type: ignore
            spreadsheetId=spreadsheet_id,
            fields=f"{terms.TABS_PROP}({terms.DATA}({terms.ROWDATA}({values})))",
            ranges=ranges or [],
        ).execute()
