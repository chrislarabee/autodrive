from typing import List, Dict, Union, Any, Literal
import pickle
from abc import ABC
from pathlib import Path

from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


DEFAULT_TOKEN = "gdrive_token.pickle"
DEFAULT_CREDS = "credentials.json"


class Connection(ABC):
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
        token_path: Path,
        creds_path: Path,
        secrets_config: Dict[str, Any] = None,
    ) -> None:
        self._token = token_path
        self._creds = creds_path
        self._client_config = secrets_config
        self._core = self._connect(api_scopes, api_name, api_version)

    @staticmethod
    def _authenticate(
        scopes: List[str],
        token_path: Path,
        creds_path: Path,
        config: Dict[str, Any] = None,
    ) -> Credentials:
        """
        Uses locally stored credentials to attempt to login to Google
        Drive. The first time it is run it will cause a web page to
        open up and solicit permission to access the Google Drive as
        specified in the credentials. Then it will create a token that
        it will use going forward.

        Args:
            scopes: A list of scopes dictating the limits of the
                authenticated connection.

        Returns: The prepped credentials object.

        """
        creds = None
        # The token file stores the user's access and refresh tokens, and
        # is created automatically when the authorization flow completes for the
        # first time.
        if token_path.exists():
            with open(token_path, "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, prompt user to log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if config:
                    flow = InstalledAppFlow.from_client_config(config, scopes)
                elif creds_path.exists():
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(creds_path), scopes
                    )
                else:
                    raise FileNotFoundError(
                        f"Credentials file {creds_path} could not be found."
                    )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
        return creds

    def _connect(
        self, scopes: List[str], api: Literal["drive", "sheets"], version: str
    ) -> Resource:
        """
        Connects to the Google API specified using locally stored credentials.

        Returns: A connection to the Google API of choice.

        """
        creds = self._authenticate(
            scopes, self._token, self._creds, self._client_config
        )
        return build(api, version, credentials=creds)


class DriveConnection(Connection):
    def __init__(
        self,
        *,
        token_path: Path,
        creds_path: Path,
        secrets_config: Dict[str, Any] = None,
        api_version: str = "v3",
    ) -> None:
        super().__init__(
            api_name="drive",
            api_version=api_version,
            api_scopes=["https://www.googleapis.com/auth/drive"],
            secrets_config=secrets_config,
            token_path=token_path,
            creds_path=creds_path,
        )
        self._files = self._core.files()  # type: ignore

    def find_object(
        self,
        obj_name: str,
        obj_type: Literal["sheet", "folder"],
        shared_drive_id: str = None,
    ) -> List[Dict]:
        """
        Searches for a Google Drive Object in the attached Google Drive
        by name.

        Args:
            obj_name: A string, the name of the object, or part of it.
            obj_type: The type of object to restrict the search to.
                Must be one of the keys in Connection.google_obj_types.
            drive_id: The id of the Shared Drive to search within.

        Returns: A list of the matching Drive Object names and ids.

        """
        query = f"name = '{obj_name}'"
        if obj_type:
            query += f" and mimeType='{self.google_obj_types[obj_type]}'"
        kwargs = self._setup_drive_id_kwargs(shared_drive_id)
        page_token = None
        results = []
        while True:
            response = self._files.list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, parents)",
                pageToken=page_token,
                **kwargs,
            ).execute()
            for file in response.get("files", []):
                results.append(
                    dict(
                        name=file.get("name"),
                        id=file.get("id"),
                        parents=file.get("parents"),
                    )
                )
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
        return results

    def create_object(
        self, obj_name: str, obj_type: Literal["sheet", "folder"], parent_id: str = None
    ) -> str:
        """
        Creates a file or folder via the Google Drive connection.

        Args:
            obj_name: A string, the desired name of the object to
                create.
            obj_type: A string, the type of object to create. Must be
                one of the keys in SheetsAPI.google_obj_types.
            parent_id: A string, the id of the folder or Shared Drive
                to create the object in.

        Returns:

        """
        kwargs = dict(parents=[parent_id]) if parent_id else dict()
        file_metadata = dict(
            name=obj_name, mimeType=self.google_obj_types[obj_type], **kwargs
        )
        file = self._files.create(
            body=file_metadata, fields="id", supportsAllDrives=True
        ).execute()
        return file.get("id")

    def delete_object(self, object_id: str) -> None:
        """
        Deletes the passed Google Object ID from the connected Google
        Drive.

        Args:
            object_id: A Google Object ID.

        Returns: None

        """
        self._files.delete(fileId=object_id, supportsAllDrives=True).execute()

    @staticmethod
    def _setup_drive_id_kwargs(drive_id: str = None) -> Dict[str, Union[str, bool]]:
        """
        Whenever a drive_id is needed to access a shared drive, two
        other kwargs need to be passed to the relevant function. This
        method preps all three kwargs.

        Args:
            drive_id: The id of the shared drive to set up access to.

        Returns: A dictionary, either empty or containing the
            appropriate kwargs if drive_id is passed.

        """
        kwargs = dict()
        if drive_id:
            kwargs["corpora"] = "drive"
            kwargs["driveId"] = drive_id
            kwargs["includeItemsFromAllDrives"] = True
            kwargs["supportsAllDrives"] = True
        return kwargs


class SheetsConnection(Connection):
    def __init__(
        self,
        *,
        token_path: Path,
        creds_path: Path,
        secrets_config: Dict[str, Any] = None,
        api_version: str = "v4",
    ) -> None:
        super().__init__(
            api_name="sheets",
            api_version=api_version,
            api_scopes=["https://www.googleapis.com/auth/spreadsheets"],
            secrets_config=secrets_config,
            token_path=token_path,
            creds_path=creds_path,
        )
        self._sheets = self._core.spreadsheets()  # type: ignore

    def execute_requests(
        self, spreadsheet_id: str, requests: List[Dict[str, Any]]
    ) -> None:
        self._sheets.batchUpdate(
            spreadsheetId=spreadsheet_id, body={"requests": requests}
        )
