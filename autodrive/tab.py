from __future__ import annotations

from typing import Any, Dict, Tuple, Sequence

from . import _google_terms as terms
from .connection import SheetsConnection
from ._view import Component
from .formatting.format_tab import (
    TabCellFormatting,
    TabGridFormatting,
    TabTextFormatting,
)
from .interfaces import AuthConfig, FullRange
from .range import Range
from .dtypes import EffectiveVal, GoogleValueType


class Tab(Component[TabCellFormatting, TabGridFormatting, TabTextFormatting]):
    """
    Provides a connection to a single Google Sheet Tab, its properties, and its
    data.
    """

    def __init__(
        self,
        gsheet_id: str,
        tab_title: str,
        tab_idx: int,
        tab_id: int,
        column_count: int = 26,
        row_count: int = 1000,
        *,
        auth_config: AuthConfig | None = None,
        sheets_conn: SheetsConnection | None = None,
        autoconnect: bool = True,
    ) -> None:
        """

        Args:
            gsheet_id (str): The id string of the target Google Sheet that the Tab
                resides in; can be found in the Google Sheet url.
            tab_title (str): The name of the Tab.
            tab_idx (int): The index (0-based) of the Tab in the Google Sheet.
            tab_id (int): The id of the Tab, can be found in the Google Sheet url
                (after gid=).
            column_count (int, optional): The starting number of columns in the
                Tab, defaults to 26.
            row_count (int, optional): The starting number of rows in the Tab,
                defaults to 1000.
            auth_config (AuthConfig, optional): Optional custom AuthConfig, defaults
                to None.
            sheets_conn (SheetsConnection, optional): Optional manually created
                SheetsConnection, defaults to None.
            autoconnect (bool, optional): If you want to instantiate a Tab without
                immediately checking your authentication credentials and connection
                to the Google Sheets api, set this to False, defaults to True.

        """
        self._tab_id = tab_id
        self._title = tab_title
        self._index = tab_idx
        self._column_count = column_count
        self._row_count = row_count
        super().__init__(
            gsheet_id=gsheet_id,
            gsheet_range=FullRange(
                start_row=0,
                end_row=row_count,
                start_col=0,
                end_col=column_count,
                tab_title=tab_title,
                base0_idxs=True,
            ),
            tab_id=self._tab_id,
            grid_formatting=TabGridFormatting,
            text_formatting=TabTextFormatting,
            cell_formatting=TabCellFormatting,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )

    @property
    def tab_id(self) -> int:
        """
        Returns:
            int: This Tab's id. Matches the gid of the parent GSheet's url.

        """
        return self._tab_id

    @property
    def format_grid(self) -> TabGridFormatting:
        """
        Returns:
            TabGridFormatting: An object with grid formatting methods.

        """
        return self._format_grid

    @property
    def format_text(self) -> TabTextFormatting:
        """
        Returns:
            TabTextFormatting: An object with text formatting methods.

        """
        return self._format_text

    @property
    def format_cell(self) -> TabCellFormatting:
        """
        Returns:
            TabCellFormatting: An object with cell formatting methods.

        """
        return self._format_cell

    @property
    def title(self) -> str:
        """
        Returns:
            str: The name of this Tab.

        """
        return self._title

    @property
    def index(self) -> int:
        """
        Returns:
            int: The (0-based) index location of this Tab among the other Tabs on
            the parent GSheet.

        """
        return self._index

    @property
    def column_count(self) -> int:
        """
        Returns:
            int: The number of columns in this Tab.

        """
        return self._column_count

    @property
    def row_count(self) -> int:
        """
        Returns:
            int: The number of rows in this Tab.

        """
        return self._row_count

    def fetch(self) -> Tab:
        """
        Gets the latest metadata from the API for this Tab. Re-populates tab
        properties like row and column count.

        .. note::

            This method will cause a request to be posted to the relevant Google
            API immediately.

        Returns:
            Tab: This GSheet
        """
        properties = self.conn.get_properties(self._gsheet_id)
        _, sheets = self._parse_properties(properties)
        title, index, tab_id, column_count, row_count = self._unpack_tab_properties(
            sheets[self._index]
        )
        self._title = title
        self._index = index
        self._tab_id = tab_id
        self._column_count = column_count
        self._row_count = row_count
        return self

    @staticmethod
    def _unpack_tab_properties(
        properties: Dict[str, Any]
    ) -> Tuple[str, int, int, int, int]:
        title = str(properties[terms.TAB_NAME])
        index = int(properties[terms.TAB_IDX])
        tab_id = int(properties[terms.TAB_ID])
        column_count = int(properties[terms.GRID_PROPS][terms.COL_CT])
        row_count = int(properties[terms.GRID_PROPS][terms.ROW_CT])
        return title, index, tab_id, column_count, row_count

    @classmethod
    def from_properties(
        cls,
        gsheet_id: str,
        properties: Dict[str, Any],
        auth_config: AuthConfig | None = None,
        sheets_conn: SheetsConnection | None = None,
        autoconnect: bool = True,
    ) -> Tab:
        """
        Generates a Tab assigned to the passed gsheet_id with the passed tab
        properties dictionary from a SheetsConnection.get_properties call.

        Unless you have a special use-case, it is probably more trouble than it's
        worth to try to instantiate a Tab with this method, as it is designed for
        use by other Autodrive objects.

        Args:
            gsheet_id (str): The id of the parent GSheet.
            properties (Dict[str, Any]): A properties dictionary, which must
                contain index, SheetId, title, and gridProperties keys. The
                gridProperties must be a dictionary containing columnCount and
                rowCount keys.
            auth_config (AuthConfig, optional): Optional custom AuthConfig,
                defaults to None.
            sheets_conn (SheetsConnection, optional): Optional manually created
                SheetsConnection, defaults to None.
            autoconnect (bool, optional): If you want to instantiate a Tab without
                immediately checking your authentication credentials and connection
                to the Google Sheets api, set this to False, defaults to True.

        Returns:
            Tab: A Tab with the values from the passed properties dictionary.

        """
        title, index, tab_id, column_count, row_count = cls._unpack_tab_properties(
            properties
        )
        return Tab(
            gsheet_id,
            tab_title=title,
            tab_idx=index,
            tab_id=tab_id,
            column_count=column_count,
            row_count=row_count,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )

    def full_range(self) -> FullRange:
        """
        Generates a FullRange object corresponding to the full range of the Tab.

        Returns:
            FullRange: A FullRange from A1:the end of the Tab.

        """
        return FullRange(
            start_row=0,
            end_row=self._row_count,
            start_col=0,
            end_col=self._column_count,
            base0_idxs=True,
        )

    def get_data(
        self,
        rng: FullRange | str | None = None,
        value_type: GoogleValueType = EffectiveVal,
    ) -> Tab:
        """
        Gets the data from the cells of this Tab.

        .. note::

            This method will cause a request to be posted to the relevant Google
            API immediately.

        Args:
            rng (FullRange | HalfRange, optional): An optional range value, to
                specify a subset of the Tab's values to get, defaults to None,
                which fetches all values in the Tab.
            value_type (GoogleValueType, optional): Allows you to toggle the
                type of the values returned by the Google Sheets API. See the
                :mod:`dtypes <autodrive.dtypes>` documentation for more info on
                the different GoogleValueTypes.

        Returns:
            Tab: This Tab.

        """
        rng = self.ensure_full_range(self.full_range(), rng)
        if not rng.tab_title:
            rng.tab_title = self._title
        self._values, self._formats = self._get_data(
            self._gsheet_id, str(rng), value_type
        )
        return self

    def write_values(
        self,
        data: Sequence[Sequence[Any] | Dict[str, Any]],
        rng: FullRange | str | None = None,
    ) -> Tab:
        """
        Adds a request to write data. Tab.commit () to commit the requests.

        Args:
            data (Sequence[Sequence[Any] | Dict[str, Any]]): The data to write.
                Each sequence or dictionary in the passed data is a row, with
                each value in that sub-iterable being a column. Dictionary keys
                will be used as a header row in the written data.
            rng (FullRange, optional): A specific range to write to,
                starting with the top-left-most cell in the range, defaults to None,
                which will write to the top-left-most cell of the Tab.

        Returns:
            Tab: This Tab.

        """
        rng = self.ensure_full_range(self.full_range(), rng)
        self._write_values(data, self._tab_id, rng.to_dict())
        return self

    @classmethod
    def new_tab_request(
        cls,
        tab_title: str,
        tab_id: int | None = None,
        tab_idx: int | None = None,
        num_rows: int = 1000,
        num_cols: int = 26,
    ) -> Dict[str, Any]:
        """
        Creates a dictionary request to create a new tab in a Google Sheet.

        Args:
            tab_title (str): The name of the tab.
            tab_id (int, optional): The desired id of the tab, which cannot already
                exist in the Google Sheet, defaults to None, which will allow the
                Google Sheet to generate the tab_id.
            tab_idx (int, optional): The (0-based) index to create the tab at,
                defaults to None, meaning the tab will be created as the last tab
                in the Google Sheet.
            num_rows (int, optional): The starting number of rows in the new tab,
                defaults to 1000.
            num_cols (int, optional): The starting number of columns in the new
                tab, defaults to 26.

        Returns:
            Dict[str, Any]: A dictionary ready to be passed as a request via a
            request commit.

        """
        props: Dict[str, Any] = {
            terms.TAB_NAME: tab_title,
            terms.GRID_PROPS: {terms.COL_CT: num_cols, terms.ROW_CT: num_rows},
        }
        if tab_id is not None:
            props[terms.TAB_ID] = tab_id
        if tab_idx is not None:
            props[terms.TAB_IDX] = tab_idx
        result = {terms.ADDTAB: {terms.TAB_PROPS: props}}
        return result

    def gen_add_tab_request(self) -> Dict[str, Any]:
        """
        Generates a new tab request dictionary for this Tab. Useful when you have
        manually instantiated a Tab object instead of fetching it and want to add
        it to the parent GSheet.

        Returns:
            Dict[str, Any]: A dictionary ready to be passed as a request via a
            request commit.

        """
        return self.new_tab_request(
            self._title, self._tab_id, self._index, self._row_count, self._column_count
        )

    def create(self) -> Tab:
        """
        Convenience method for generating a new tab request based on this Tab and
        immediately committing it, thus adding it to the parent Google Sheet.

        .. note::

            This method will cause a request to be posted to the relevant Google
            API immediately.

        Returns:
            Tab: This Tab.

        """
        req = self.new_tab_request(
            self.title, self.tab_id, self.index, self.row_count, self.column_count
        )
        self._requests.append(req)
        self.commit()
        return self

    def gen_range(self, rng: FullRange) -> Range:
        """
        Convenience method for generating a new Range object in this Tab.

        Args:
            rng (FullRange): The desired FullRange of the new Range object.

        Returns:
            Range: The newly generated Range.
        """
        return Range(
            rng, self._gsheet_id, self._title, self._tab_id, sheets_conn=self._conn
        )
