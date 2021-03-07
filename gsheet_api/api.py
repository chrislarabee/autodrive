from typing import Tuple, List, Optional
import os
import pickle

from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from gsheet_api.drive import Drive
from gsheet_api.sheets import Sheets

class GSheetsAPI:
    def __init__(self) -> None:
        self._drive = None
        self._sheets = None

    @property
    def drive(self) -> Optional[Drive]:
        return self._drive

    @property
    def sheets(self) -> Optional[Sheets]:
        return self._sheets

    def connect(self) -> Tuple[Resource, Resource]:
        drive = self._connect_drive()
        sheets = self._connect_sheets()
        self._drive = Drive(drive)
        self._sheets = Sheets(sheets)
        return drive, sheets

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
