from typing import Tuple, Union, Dict

from googleapiclient.discovery import Resource


class GSheetFormatting:
    number_fmt = ""
    accounting_fmt = ("NUMBER", '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)')

    def __init__(self, file_id: str, sheet_id: int = 0, parent: Resource = None):
        """
        This object contains methods for creating a list of formatting
        requests and row/column operation requests that can then be
        processed with the execute() method.

        Args:
            file_id: The id of the Google Sheet to apply formatting to.
            sheet_id: The id of the sheet within the Google Sheet to
                apply formatting to.
            parent: The SheetsAPI object that generated this formatting.
        """
        self.parent = parent
        self.file_id: str = file_id
        self.sheet_id: int = sheet_id
        self.requests: list = []

    def execute(self) -> None:
        """
        Executes the amassed requests on this GSheetFormatting object.

        Returns: None

        """
        if self.parent:
            self.parent.batch_update(self.file_id, self.requests)

    def auto_column_width(self, start_col: int, end_col: int):
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
        request = dict(
            autoResizeDimensions=dict(
                dimensions=self._build_dims_dict(
                    self.sheet_id, "COLUMNS", start_col, end_col
                )
            )
        )
        self.requests.append(request)
        return self

    def append_rows(self, num_rows: int):
        """
        Adds the specified number of rows to the end of a Google Sheet.

        Args:
            num_rows: The number of rows to add.

        Returns: self

        """
        request = dict(
            appendDimension=dict(
                sheetId=self.sheet_id, dimension="ROWS", length=num_rows
            )
        )
        self.requests.append(request)
        return self

    def insert_rows(self, num_rows: int, at_row: int = 0):
        """
        Adds an insertDimension request to add more rows to the
        GSheetFormatting object's requests queue.

        WARNING: Do NOT use this method to add rows to the end of a
        Google Sheet. It will not work. Use append_rows instead.

        Args:
            num_rows: The # of rows to insert.
            at_row: The 0-initial index of the row to start inserting
               at.

        Returns: self.

        """
        request = self._insert_dims(self.sheet_id, "ROWS", at_row, at_row + num_rows)
        self.requests.append(request)
        return self

    def delete_rows(self, start_row: int, end_row: int):
        """
        Adds a deleteDimension request to the GSheetFormatting object's
        requests queue.

        Args:
            start_row: The 0-initial index of the first row to delete.
            end_row: The 0-initial index of the last row to delete.

        Returns: self.

        """
        request = self._delete_dims(self.sheet_id, "ROWS", start_row, end_row)
        self.requests.append(request)
        return self

    def _delete_dims(self, *vals) -> dict:
        return dict(deleteDimension=dict(range=self._build_dims_dict(*vals)))

    def _insert_dims(self, *vals, inherit: bool = False) -> dict:
        """
        Creates an insertDimensions request.

        Args:
            *vals:  Values to be passed to _build_dims_dict.
            inherit: Indicates whether the inserted rows should inherit
                formatting from the rows before them.

        Returns: A dictionary request to insert new dimensions into a
            Google Sheet.

        """
        return dict(
            insertDimension=dict(
                range=self._build_dims_dict(*vals), inheritFromBefore=inherit
            )
        )

    @staticmethod
    def _build_dims_dict(*vals) -> dict:
        """
        Quick method for building a range/dimensions dictionary for use
        in a request dictionary wrapper intended to change Sheet
        dimensions (like inserting/deleting rows/columns or changing
        row/column widths).

        Args:
            *vals: One to 4 values, which will be slotted into the dict
                below in the order passed.

        Returns: A dictionary usable in a Google Sheets API request
            dictionary as either the range or dimensions value.

        """
        d = dict(sheetId=None, dimension=None, startIndex=None, endIndex=None)
        return dict(zip(d.keys(), vals))

    def apply_font(
        self,
        row_idxs: tuple = (None, None),
        col_idxs: tuple = (None, None),
        size: int = None,
        style: Union[str, Tuple[str, ...]] = None,
    ):
        """
        Adds a textFormat request to the GSheetFormatting object's
        request queue.

        Args:
            row_idxs: A tuple of the start and end rows to apply font
                formatting to.
            col_idxs: A tuple of the start and end columns to apply font
                formatting to.
            size: Font size formatting.
            style: Font style formatting (bold, italic?, underline?).
                Bold is the only current style tested.

        Returns: self.

        """
        text_format = dict()
        if size:
            text_format["fontSize"] = size
        if style:
            style = (style,) if isinstance(style, str) else style
            for s in style:
                text_format[s] = True
        repeat_cell = self._build_repeat_cell_dict(
            dict(textFormat=text_format), row_idxs, col_idxs, self.sheet_id
        )
        repeat_cell["fields"] = "userEnteredFormat(textFormat)"
        request = dict(repeatCell=repeat_cell)
        self.requests.append(request)
        return self

    def apply_nbr_format(
        self, fmt: str, row_idxs: tuple = (None, None), col_idxs: tuple = (None, None)
    ):
        """
        Adds a numberFormat request to the GSheetFormatting object's
        request queue.

        Args:
            fmt: A _fmt property from this object (like
                accounting_fmt) with or without the _fmt suffix.
            row_idxs: A tuple of the start and end rows to apply number
                formatting to.
            col_idxs: A tuple of the start and end columns to apply
                number formatting to.

        Returns: self.

        """
        fmt += "_fmt" if fmt[-4:] != "_fmt" else ""
        t, p = getattr(self, fmt)
        nbr_format = dict(type=t, pattern=p)

        repeat_cell = self._build_repeat_cell_dict(
            dict(numberFormat=nbr_format), row_idxs, col_idxs, self.sheet_id
        )
        repeat_cell["fields"] = "userEnteredFormat.numberFormat"
        request = dict(repeatCell=repeat_cell)
        self.requests.append(request)
        return self

    def freeze(self, rows: int = None, columns: int = None):
        """
        Adds a freeze rows and/or columns request to the
        GSheetFormatting object's request queue.

        Args:
            rows: Number of rows to freeze.
            columns: Number of columns to freeze.

        Returns: self.

        """
        grid_prop = dict()
        if not rows and not columns:
            raise ValueError("One of rows or columns must not be None.")
        if rows:
            grid_prop["frozenRowCount"] = rows
        if columns:
            grid_prop["frozenColumnCount"] = columns
        request = dict(
            updateSheetProperties=dict(
                properties=dict(sheetId=self.sheet_id, gridProperties=grid_prop),
                fields="gridProperties(frozenRowCount, frozenColumnCount)",
            )
        )
        self.requests.append(request)
        return self

    def alternate_row_background(
        self, *rgb_vals, row_idxs: tuple = (None, None), col_idxs: tuple = (None, None)
    ):
        """
        Adds a background of the specified color to every other row in
        the passed range.

        Args:
            row_idxs: A tuple of the start and stop row indexes.
            col_idxs: A tuple of the start and stop column indexes.
            *rgb_vals: Red, green, and blue values, in order. More than
                3 values will be ignored, default value is 0, so you
                only need to specify up to the last non-zero value.

        Returns: self.

        """
        request = dict(
            addConditionalFormatRule=dict(
                rule=dict(
                    ranges=[self._build_range_dict(self.sheet_id, row_idxs, col_idxs)],
                    booleanRule=dict(
                        condition=dict(
                            type="CUSTOM_FORMULA",
                            values=[dict(userEnteredValue="=MOD(ROW(), 2)")],
                        ),
                        format=dict(backgroundColor=self._build_color_dict(*rgb_vals)),
                    ),
                ),
                index=0,
            )
        )
        self.requests.append(request)
        return self

    @classmethod
    def _build_repeat_cell_dict(
        cls,
        fmt_dict: dict,
        row_idxs: tuple = (None, None),
        col_idxs: tuple = (None, None),
        sheet_id: int = 0,
    ) -> dict:
        """
        Quick method for building a repeatCell dictionary for use in a
        request dictionary wrapper intended to change cell formatting or
        contents (like changing font, borders, background, contents,
        etc).

        Args:
            fmt_dict: A formatting dictionary.
            row_idxs: A tuple of the start and stop row indexes.
            col_idxs: A tuple of the start and stop column indexes.
            sheet_id: The id of the sheet to apply the formatting to.
                Default is 0.

        Returns: A dictionary ready to be slotted in at the repeatCell
            key in a request.

        """
        return dict(
            range=cls._build_range_dict(sheet_id, row_idxs, col_idxs),
            cell=dict(userEnteredFormat=fmt_dict),
        )

    @staticmethod
    def _build_range_dict(
        sheet_id: int = 0,
        row_idxs: tuple = (None, None),
        col_idxs: tuple = (None, None),
    ) -> dict:
        """
        Quick method for building a range dictionary for use in a
        request dictionary wrapper intended to change cell formatting or
        contents (like changing font, borders, background, contents,
        etc).

        Args:
            sheet_id: The id of the sheet to build a range for,
                default is 0, the first sheet.
            row_idxs: A tuple of the start and stop row indexes.
            col_idxs: A tuple of the start and stop column indexes.

        Returns: A dictionary ready to be slotted into a format request
            generating function.

        """
        range_dict = dict(sheetId=sheet_id)

        range_ = (*row_idxs, *col_idxs)
        non_nulls = 0
        for r in range_:
            non_nulls += 1 if r is not None else 0
        if non_nulls < 2:
            raise ValueError("Must pass one or both of row_idxs, col_idxs.")

        start_row_idx, end_row_idx = row_idxs
        start_col_idx, end_col_idx = col_idxs
        # Must specify is not None because python interprets 0 as false.
        if start_row_idx is not None:
            range_dict["startRowIndex"] = start_row_idx
        if end_row_idx is not None:
            range_dict["endRowIndex"] = end_row_idx
        if start_col_idx is not None:
            range_dict["startColumnIndex"] = start_col_idx
        if end_col_idx is not None:
            range_dict["endColumnIndex"] = end_col_idx
        return range_dict

    @staticmethod
    def _build_color_dict(*rgb_vals) -> Dict[str, float]:
        """
        Quick method for building a color dictionary for use in a
        foreground, background, or font color dictionary.

        Args:
            *rgb_vals: Red, green, and blue values, in order. More than
                3 values will be ignored, default value is 0, so you
                only need to specify up to the last non-zero value.

        Returns: A dictionary containing RGB color names and values.

        """
        rgb_vals = list(rgb_vals)
        rgb = ["red", "green", "blue"]
        rgb_vals += [0] * (3 - len(rgb_vals))
        return {k: v for k, v in dict(zip(rgb, rgb_vals)).items()}
