from __future__ import annotations

from typing import Any, Dict


def auto_column_width(tab_id: int, start_col: int, end_col: int) -> Dict[str, Any]:
    """
    Adds an autoResizeDimensions request to the GSheetFormatting
        object's requests queue.

    Args:
        start_col: The 0-initial index of the first column to auto-
            resize.
        end_col: The 0-initial index of the last column to auto-
            resize.

    Returns: self

    """
    return {
        "autoResizeDimensions": {
            "dimensions": {
                "sheetId": tab_id,
                "dimension": "COLUMNS",
                "startIndex": start_col,
                "endIndex": end_col,
            }
        }
    }

    # def append_rows(self, num_rows: int):
    #     """
    #     Adds the specified number of rows to the end of a Google Sheet.

    #     Args:
    #         num_rows: The number of rows to add.

    #     Returns: self

    #     """
    #     request = dict(
    #         appendDimension=dict(
    #             sheetId=self.sheet_id, dimension="ROWS", length=num_rows
    #         )
    #     )
    #     self.requests.append(request)
    #     return self

    # def insert_rows(self, num_rows: int, at_row: int = 0):
    #     """
    #     Adds an insertDimension request to add more rows to the
    #     GSheetFormatting object's requests queue.

    #     WARNING: Do NOT use this method to add rows to the end of a
    #     Google Sheet. It will not work. Use append_rows instead.

    #     Args:
    #         num_rows: The # of rows to insert.
    #         at_row: The 0-initial index of the row to start inserting
    #            at.

    #     Returns: self.

    #     """
    #     request = self._insert_dims(self.sheet_id, "ROWS", at_row, at_row + num_rows)
    #     self.requests.append(request)
    #     return self

    # def delete_rows(self, start_row: int, end_row: int):
    #     """
    #     Adds a deleteDimension request to the GSheetFormatting object's
    #     requests queue.

    #     Args:
    #         start_row: The 0-initial index of the first row to delete.
    #         end_row: The 0-initial index of the last row to delete.

    #     Returns: self.

    #     """
    #     request = self._delete_dims(self.sheet_id, "ROWS", start_row, end_row)
    #     self.requests.append(request)
    #     return self

    # def _delete_dims(self, *vals) -> dict:
    #     return dict(deleteDimension=dict(range=self._build_dims_dict(*vals)))

    # def _insert_dims(self, *vals, inherit: bool = False) -> dict:
    #     """
    #     Creates an insertDimensions request.

    #     Args:
    #         *vals:  Values to be passed to _build_dims_dict.
    #         inherit: Indicates whether the inserted rows should inherit
    #             formatting from the rows before them.

    #     Returns: A dictionary request to insert new dimensions into a
    #         Google Sheet.

    #     """
    #     return dict(
    #         insertDimension=dict(
    #             range=self._build_dims_dict(*vals), inheritFromBefore=inherit
    #         )
    #     )

    # @staticmethod
    # def _build_dims_dict(*vals) -> dict:
    #     """
    #     Quick method for building a range/dimensions dictionary for use
    #     in a request dictionary wrapper intended to change Sheet
    #     dimensions (like inserting/deleting rows/columns or changing
    #     row/column widths).

    #     Args:
    #         *vals: One to 4 values, which will be slotted into the dict
    #             below in the order passed.

    #     Returns: A dictionary usable in a Google Sheets API request
    #         dictionary as either the range or dimensions value.

    #     """
    #     d = dict(sheetId=None, dimension=None, startIndex=None, endIndex=None)
    #     return dict(zip(d.keys(), vals))
