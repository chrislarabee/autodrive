from typing import Tuple, List, Optional, Dict, Union
import os
import pickle
import warnings

from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from gsheet_api.sheets import Sheets


class GSheetsAPI:
    google_obj_types = {
        "folder": "application/vnd.google-apps.folder",
        "sheet": "application/vnd.google-apps.spreadsheet",
    }
    connection_msg = "GSheetsAPI is not connected. Execute GSheetsAPI.connect()."

    def __init__(self, auto_connect: bool = True) -> None:
        if auto_connect:
            self._drive = self._connect_drive()
            self._sheets = Sheets(self._connect_sheets())
        else:
            self._drive = None
            self._sheets = None

    @property
    def drive(self) -> Resource:
        if not self._drive:
            raise ConnectionError(self.connection_msg)
        return self._drive

    @property
    def sheets(self) -> Sheets:
        if not self._sheets:
            raise ConnectionError(self.connection_msg)
        return self._sheets

    def connect(self) -> Tuple[Resource, Resource]:
        drive = self._connect_drive()
        sheets = self._connect_sheets()
        self._drive = drive
        self._sheets = Sheets(sheets)
        return drive, sheets

    def create_object(self, obj_name: str, obj_type: str, parent_id: str = None) -> str:
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
        file = (
            self._drive.files()
            .create(body=file_metadata, fields="id", supportsAllDrives=True)
            .execute()
        )
        return file.get("id")

    def find_object(
        self, obj_name: str, obj_type: str = None, shared_drive_id: str = None
    ) -> List[Dict]:
        """
        Searches for a Google Drive Object in the attached Google Drive
        by name.

        Args:
            obj_name: A string, the name of the object, or part of it.
            obj_type: The type of object to restrict the search to.
                Must be one of the keys in SheetsAPI.google_obj_types.
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
            response = (
                self._drive.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, parents)",
                    pageToken=page_token,
                    **kwargs,
                )
                .execute()
            )
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

    def delete_object(self, object_id: str) -> None:
        """
        Deletes the passed Google Object ID from the connected Google
        Drive.

        Args:
            object_id: A Google Object ID.

        Returns: None

        """
        self._drive.files().delete(fileId=object_id, supportsAllDrives=True).execute()

    def find_or_create_object(
        self,
        obj_name: str,
        obj_type: str,
        parent_folder: str = None,
        shared_drive_id: str = None,
    ) -> Tuple[str, bool]:
        """
        Convenience method for checking if an object exists and creating
        it if it does not.

        Args:
            obj_name: The name of the object.
            obj_type: The type of the object. Must be one of the keys in
                SheetsAPI.google_obj_types.
            parent_folder: The name of the folder to save the new object
                to. Separate nested folders with /, as if it were a
                local file path.
            drive_id: The id of the Shared Drive to search for the folder
                path and to save to.

        Returns: A tuple containing the id of the object, and a boolean
            indicating whether the object is new or not.

        """
        p_folder_id = None
        if parent_folder:
            search_res = self.find_object(parent_folder, "folder", shared_drive_id)
            if len(search_res) == 1:
                p_folder_id = search_res[0].get("id")
            else:
                warnings.warn(
                    f"Cannot find single exact match for {parent_folder}. "
                    f"Saving {obj_name} to root Drive."
                )
        search_res = self.find_object(obj_name, obj_type, shared_drive_id)
        new_obj = False
        if len(search_res) > 1:
            for result in search_res:
                if result.get("parents")[0] == p_folder_id:
                    file_id = str(result.get("id"))
                    break
            else:
                raise ValueError(f"Cannot find {obj_name} in {parent_folder}")
        elif len(search_res) == 1:
            file_id = str(search_res[0].get("id"))
        else:
            new_obj = True
            file_id = self.create_object(obj_name, obj_type, p_folder_id)
        return file_id, new_obj

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

    @staticmethod
    def _authenticate(scopes: List[str]) -> Credentials:
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
        # The file token.pickle stores the user's access and refresh tokens, and
        # is created automatically when the authorization flow completes for the
        # first time.
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, prompt user to log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        return creds

    @classmethod
    def _connect_drive(cls) -> Resource:
        """
        Connects to the Google Drive specified in locally stored
        credentials.

        Returns: A connection to Google Drive.

        """
        scopes = ["https://www.googleapis.com/auth/drive"]
        creds = cls._authenticate(scopes)
        return build("drive", "v3", credentials=creds)

    @classmethod
    def _connect_sheets(cls) -> Resource:
        """
        Connects to the Google Sheets specified in locally stored
        credentials.

        Returns: A connection to Google Sheets.

        """
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = cls._authenticate(scopes)
        return build("sheets", "v4", credentials=creds)
