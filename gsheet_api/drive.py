from typing import Union, Dict, List, Tuple
import warnings

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

    def delete_object(self, object_id: str) -> None:
        """
        Deletes the passed Google Object ID from the connected Google
        Drive.

        Args:
            object_id: A Google Object ID.

        Returns: None

        """
        self._core.files().delete(fileId=object_id, supportsAllDrives=True).execute()

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
