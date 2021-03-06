from typing import Union, Dict, List

from googleapiclient.discovery import Resource


class Drive:
    google_obj_types = { 
        "folder": "application/vnd.google-apps.folder",
        "sheet": "application/vnd.google-apps.spreadsheet",
    }

    def __init__(self, resource: Resource) -> None:
        self._core = resource

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
            self._core.files()
            .create(body=file_metadata, fields="id", supportsAllDrives=True)
            .execute()
        )
        return file.get("id")

    def find_object(
        self, obj_name: str, obj_type: str = None, drive_id: str = None
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
        kwargs = self._setup_drive_id_kwargs(drive_id)
        page_token = None
        results = []
        while True:
            response = (
                self._core.files()
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
