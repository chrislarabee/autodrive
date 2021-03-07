from typing import List, Dict, Tuple, Optional, Union

from googleapiclient.discovery import Resource


class Sheets:
    def __init__(self, resource: Resource) -> None:
        self._core = resource

    def add_sheet(self, sheet_id: str, **sheet_properties):
        """
        Adds a new sheet to the Google Sheet at the passed id.

        Args:
            sheet_id: The id of a Google Sheet.
            **sheet_properties: The desired properties of the new
                sheet, such as:
                    title: The title of the sheet.

        Returns: The title and index position of the new sheet.

        """
        result = (
            self._core.spreadsheets()
            .batchUpdate(
                spreadsheetId=sheet_id,
                body={"requests": [{"addSheet": {"properties": sheet_properties}}]},
            )
            .execute()
        )
        r = result.get("replies")
        if r:
            r = r[0]["addSheet"]["properties"]
            return r.get("title"), r.get("index")
        else:
            return None

    def get_sheets(self, sheet_id: str) -> List[Dict[str, dict]]:
        """
        Gets a list of sheets within the Google Sheet located at the
        passed sheet_id.
        Args:
            sheet_id: A Google Sheet ID.

        Returns: A list of dictionaries, each being the properties of a
            sheet in the Google Sheet.

        """
        return (
            self._core.spreadsheets()
            .get(
                spreadsheetId=sheet_id,
                fields=(
                    "sheets(data/rowData/values/userEnteredValue,"
                    "properties(index,sheetId,title))"
                ),
            )
            .execute()
            .get("sheets", [])
        )

    def check_sheet_titles(
        self, sheet_title: str, sheet_id: str = None, sheets: list = None
    ) -> Optional[int]:
        """
        Checks the sheets of the Google Sheet at the passed sheet_id,
        or just the passed sheets, for a sheet with a title matching
        that of sheet_title.

        Args:
            sheet_title: A string, the title of a sheet to search for.
            sheet_id: A string, the id of a Google Sheet.
            sheets: A list of sheet property dictionaries. Can be used
                in place of sheet_id if another process has already
                generated this list.

        Returns: An integer, the index of the sheet if it is found in
            the sheets of the Google Sheet, or None, if it is not.

        """
        if sheets is None and sheet_id:
            sheets = self.get_sheets(sheet_id)
        else:
            raise ValueError("Must pass sheet_id or sheets to check_sheet_titles.")
        idx = None
        for s in sheets:
            if s["properties"]["title"] == sheet_title:
                idx = s["properties"]["index"]
        return idx

    def get_sheet_metadata(
        self, sheet_id: str, sheet_title: str = None
    ) -> Optional[Dict[str, Union[str, int]]]:
        """
        Retrieves metadata about the first sheet in the Google Sheet
        corresponding to the passed sheet_id.

        Args:
            sheet_id: A string, the id of a Google Sheet.
            sheet_title: A string, the name of the sheet within the
                Google Sheet to get metadata for. If none, metadata for
                the first sheet will be used.

        Returns: A dictionary containing information about the data in
            the passed sheet, or None if the passed sheet does not
            exist.

        """
        raw = self.get_sheets(sheet_id)
        s_idx = 0
        if sheet_title:
            s_idx = self.check_sheet_titles(sheet_title, sheets=raw)
        # This MUST specify "is not None" because of truth-value of 0 index:
        if s_idx is not None:
            sheet = raw[s_idx]
            # Newly created Google Sheets have no rowData.
            row_data = sheet["data"][0].get("rowData")
            if row_data:
                last_row_idx = len(row_data)
                last_col_idx = max([len(e["values"]) for e in row_data if e])
            else:
                last_row_idx = 0
                last_col_idx = 0
            return dict(
                id=sheet["properties"]["sheetId"],
                index=s_idx,
                title=sheet["properties"]["title"],
                row_limit=last_row_idx,
                col_limit=last_col_idx,
            )

    def write_values(
        self, file_id: str, data: list, sheet_title: str = "", start_cell: str = "A1"
    ) -> Tuple[int, int]:
        """
        Writes the passed data to the passed Google Sheet.

        Args:
            file_id: The file id of the Google Sheet.
            data: A list of lists, the data to write.
            sheet_title: The title of the sheet within the Google Sheet
                to write to. Default is the first sheet.
            start_cell: The starting cell to write to. Values will be
                written from left to write and top to bottom from
                this cell, overwriting any existing values.

        Returns: A tuple containing the # of rows and columns updated.

        """
        if sheet_title:
            r = sheet_title + "!"
            s = self.check_sheet_titles(sheet_title, sheet_id=file_id)
            if s is None:
                self.add_sheet(file_id, title=sheet_title)
        else:
            r = ""
        result = (
            self._core.spreadsheets()
            .values()
            .update(
                spreadsheetId=file_id,
                range=r + start_cell,
                valueInputOption="USER_ENTERED",
                body=dict(values=data),
            )
            .execute()
        )
        return result.get("updatedRows"), result.get("updatedColumns")

    def get_values(self, file_id: str, sheet_title: str = None):
        """
        Gets all values from the passed Google Sheet id.

        Args:
            file_id: The id of the Google Sheet.
            sheet_title: The title of the desired sheet within the
                Google Sheet to pull values from. Default is the first
                sheet.

        Returns: A list of lists, the values from the sheet.

        """
        sheet_md = self.get_sheet_metadata(file_id, sheet_title)
        r = sheet_title + "!" if sheet_title else ""
        last_col_alpha = u.gen_alpha_keys(sheet_md["col_limit"])
        col_letter = last_col_alpha[sheet_md["col_limit"] - 1]
        result = (
            self._core.spreadsheets()
            .values()
            .get(
                spreadsheetId=file_id,
                range=f"{r}A1:{col_letter}{sheet_md['row_limit']}",
            )
            .execute()
        )
        return result.get("values", [])

    def batch_update(self, file_id: str, requests: list):
        """
        Executes a list of requests on the passed spreadsheet file.
        Args:
            file_id: The id of the Google Sheet.
            requests: A list of request dictionaries.

        Returns: The results of the batchUpdate.

        """
        return (
            self._core.spreadsheets()
            .batchUpdate(spreadsheetId=file_id, body=dict(requests=requests))
            .execute()
        )

    def format_sheet(self, file_id: str, sheet_title: str = None):
        """
        Instantiates a GSheetFormatting object for the passed Google
        Sheet and sheet title, which provides a variety of methods
        for specifying all the formatting changes you want.

        Args:
            file_id: The id of the Google Sheet.
            sheet_title: The name of a sheet in the Google Sheet,
                defaults to the first sheet.

        Returns: A GSheetFormatting object, which can be chained into
            its formatting methods and ended with a call to .execute()
            to apply the formatting, or used for other purposes.

        """
        sheet_id = self.get_sheet_metadata(file_id, sheet_title)["id"]
        # return GSheetFormatting(file_id, sheet_id, self)