from __future__ import annotations

from typing import Any, List

from .connection import SheetsConnection
from .core import Component
from .formatting import RangeCellFormatting, RangeGridFormatting, RangeTextFormatting
from .interfaces import AuthConfig, TwoDRange


class Range(Component[RangeCellFormatting, RangeGridFormatting, RangeTextFormatting]):
    def __init__(
        self,
        gsheet_range: TwoDRange,
        gsheet_id: str,
        tab_title: str,
        *,
        auth_config: AuthConfig | None = None,
        sheets_conn: SheetsConnection | None = None,
        autoconnect: bool = True,
    ) -> None:
        """
        Provides a connection to the data in a specific range in a Google Sheet Tab.

        :param gsheet_range: The range (i.e. A5:C10) to associate with this Range.
        :type gsheet_range: TwoDRange
        :param gsheet_id: The id string of the target Google Sheet that the Range
            resides in; can be found in the Google Sheet url.
        :type gsheet_id: str
        :param tab_title: The name of the Tab this Range is within.
        :type tab_title: str
        :param auth_config: Optional custom AuthConfig, defaults to None.
        :type auth_config: AuthConfig, optional
        :param sheets_conn: Optional manually created SheetsConnection, defaults to
            None.
        :type sheets_conn: SheetsConnection, optional
        :param autoconnect: If you want to instantiate a Range without immediately
            checking your authentication credentials and connection to the Google Sheets
            api, set this to False, defaults to True.
        :type autoconnect: bool, optional
        """
        self._tab_title = tab_title
        gsheet_range.tab_title = tab_title
        self._rng = gsheet_range
        super().__init__(
            gsheet_id=gsheet_id,
            gsheet_range=gsheet_range,
            grid_formatting=RangeGridFormatting,
            text_formatting=RangeTextFormatting,
            cell_formatting=RangeCellFormatting,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )

    @property
    def format_grid(self) -> RangeGridFormatting:
        """
        Contains request generation methods related to formatting this Range's grid
        (width and height, etc).

        :return: An object with grid formatting methods.
        :rtype: RangeGridFormatting
        """
        return self._format_grid

    @property
    def format_text(self) -> RangeTextFormatting:
        """
        Contains request generation methods methods relating to formatting this
        Range's text (the text format of any cells, even those containing non-text
        values like integers or null values).

        :return: An object with text formatting methods.
        :rtype: RangeTextFormatting
        """
        return self._format_text

    @property
    def format_cell(self) -> RangeCellFormatting:
        """
        Contains request generation methods relating to formatting this Range's
        cells (like adding borders and backgrounds and such).

        :return: An object with cell formatting methods.
        :rtype: RangeCellFormatting
        """
        return self._format_cell

    def get_data(self) -> Range:
        """
        Gets the data from the cells of this Range.

        :return: This Range.
        :rtype: Range
        """
        self._values, self._formats = self._get_data(self._gsheet_id, str(self._rng))
        return self

    def write_values(self, data: List[List[Any]]) -> Range:
        """
        Adds a request to write data. Range.commit() to commit the requests.

        :param data: The data to write. Each list in the passed data list is a row,
            with each value in that sublist being a column.
        :type data: List[List[Any]]
        :return: This Tab.
        :rtype: Range
        """
        self._write_values(data, self._rng.to_dict())
        return self
