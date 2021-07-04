from __future__ import annotations

from typing import Any, Dict, List

from . import google_terms as terms
from .connection import SheetsConnection
from .core import Component
from .formatting import TabCellFormatting, TabGridFormatting, TabTextFormatting
from .interfaces import AuthConfig, OneDRange, TwoDRange


class Tab(Component[TabCellFormatting, TabGridFormatting, TabTextFormatting]):
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
        Provides a connection to a single Google Sheet Tab, its properties, and its
        data.

        :param gsheet_id: The id string of the target Google Sheet that the Tab resides
            in; can be found in the Google Sheet url.
        :type gsheet_id: str
        :param tab_title: The name of the Tab.
        :type tab_title: str
        :param tab_idx: The index (0-based) of the Tab in the Google Sheet.
        :type tab_idx: int
        :param tab_id: The id of the Tab, can be found in the Google Sheet url (after
            gid=).
        :type tab_id: int
        :param column_count: The starting number of columns in the Tab, defaults to 26.
        :type column_count: int, optional
        :param row_count: The starting number of rows in the Tab, defaults to 1000.
        :type row_count: int, optional
        :param auth_config: Optional custom AuthConfig, defaults to None.
        :type auth_config: AuthConfig, optional
        :param sheets_conn: Optional manually created SheetsConnection, defaults to
            None.
        :type sheets_conn: SheetsConnection, optional
        :param autoconnect: If you want to instantiate a Tab without immediately
            checking your authentication credentials and connection to the Google Sheets
            api, set this to False, defaults to True.
        :type autoconnect: bool, optional
        """
        self._tab_id = tab_id
        self._title = tab_title
        self._index = tab_idx
        self._column_count = column_count
        self._row_count = row_count
        super().__init__(
            gsheet_id=gsheet_id,
            gsheet_range=TwoDRange(
                self._tab_id,
                start_row=0,
                end_row=row_count,
                start_col=0,
                end_col=column_count,
                tab_title=tab_title,
                base0_idxs=True,
            ),
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
        :return: This Tab's id. Matches the gid of the parent GSheet's url.
        :rtype: int
        """
        return self._tab_id

    @property
    def format_grid(self) -> TabGridFormatting:
        """
        Contains request generation methods related to formatting this Tab's grid
        (number of columns, rows, width and height, etc).

        :return: An object with grid formatting methods.
        :rtype: TabGridFormatting
        """
        return self._format_grid

    @property
    def format_text(self) -> TabTextFormatting:
        """
        Contains request generation methods relating to formatting this Tab's text
        (the text format of any cells, even those containing non-text values like
        integers or null values).

        :return: An object with text formatting methods.
        :rtype: TabTextFormatting
        """
        return self._format_text

    @property
    def format_cell(self) -> TabCellFormatting:
        """
        Contains request generation methods relating to formatting this Tab's cells
        (like adding borders and backgrounds and such).

        :return: An object with cell formatting methods.
        :rtype: TabCellFormatting
        """
        return self._format_cell

    @property
    def title(self) -> str:
        """
        :return: The name of this Tab.
        :rtype: str
        """
        return self._title

    @property
    def index(self) -> int:
        """
        :return: The (0-based) index location of this Tab among the other Tabs on the
            parent GSheet.
        :rtype: int
        """
        return self._index

    @property
    def column_count(self) -> int:
        """
        :return: The number of columns in this Tab.
        :rtype: int
        """
        return self._column_count

    @property
    def row_count(self) -> int:
        """
        :return: The number of rows in this Tab.
        :rtype: int
        """
        return self._row_count

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
        Generates a Tab assigned to the passed gsheet_id with the passed tab properties
        dictionary from a SheetsConnection.get_properties call.

        Unless you have a special use-case, it is probably more trouble than it's worth
        to try to instantiate a Tab with this method, as it is designed for use by
        other Autodrive objects.

        :param gsheet_id: The id of the parent GSheet.
        :type gsheet_id: str
        :param properties: A properties dictionary, which must contain index, SheetId,
            title, and gridProperties keys. The gridProperties must be a dictionary
            containing columnCount and rowCount keys.
        :type properties: Dict[str, Any]
        :param auth_config: Optional custom AuthConfig, defaults to None.
        :type auth_config: AuthConfig, optional
        :param sheets_conn: Optional manually created SheetsConnection, defaults to
            None.
        :type sheets_conn: SheetsConnection, optional
        :param autoconnect: If you want to instantiate a Tab without immediately
            checking your authentication credentials and connection to the Google
            Sheets api, set this to False, defaults to True.
        :type autoconnect: bool, optional
        :return: A Tab with the values from the passed properties dictionary.
        :rtype: Tab
        """
        title = str(properties[terms.TAB_NAME])
        index = int(properties[terms.TAB_IDX])
        tab_id = int(properties[terms.TAB_ID])
        column_count = int(properties[terms.GRID_PROPS][terms.COL_CT])
        row_count = int(properties[terms.GRID_PROPS][terms.ROW_CT])
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

    def two_d_range(self) -> TwoDRange:
        """
        Generates a TwoDRange object corresponding to the full range of the Tab.

        :return: A TwoDRange from A1:the end of the Tab.
        :rtype: TwoDRange
        """
        return TwoDRange(
            self._tab_id, 0, self._row_count, 0, self._column_count, base0_idxs=True
        )

    def get_data(self, rng: TwoDRange | OneDRange | None = None) -> Tab:
        """
        Gets the data from the cells of this Tab.

        :param rng: An optional range value, to specify a subset of the Tab's values
            to get, defaults to None, which fetches all values in the Tab.
        :type rng: TwoDRange | OneDRange, optional
        :return: This Tab.
        :rtype: Tab
        """
        rng = self.two_d_range() if not rng else rng
        self._values, self._formats = self._get_data(
            self._gsheet_id, f"{self._title}!{rng}"
        )
        return self

    def write_values(
        self, data: List[List[Any]], rng: TwoDRange | OneDRange | None = None
    ) -> Tab:
        """
        Adds a request to write data. Tab.commit() to commit the requests.

        :param data: The data to write. Each list in the passed data list is a row,
            with each value in that sublist being a column.
        :type data: List[List[Any]]
        :param rng: A specific range to write to, starting with the top-left-most cell
            in the range, defaults to None, which will write to the top-left-most cell
            of the Tab.
        :type rng: TwoDRange | OneDRange, optional
        :return: This Tab.
        :rtype: Tab
        """
        rng = self.two_d_range() if not rng else rng
        self._write_values(data, rng.to_dict())
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

        :param tab_title: The name of the tab.
        :type tab_title: str
        :param tab_id: The desired id of the tab, which cannot already exist in the
            Google Sheet, defaults to None, which will allow the Google Sheet to
            generate the tab_id.
        :type tab_id: int, optional
        :param tab_idx: The (0-based) index to create the tab at, defaults to None,
            meaning the tab will be created as the last tab in the Google Sheet..
        :type tab_idx: int, optional
        :param num_rows: The starting number of rows in the new tab, defaults to 1000.
        :type num_rows: int, optional
        :param num_cols: The starting number of columns in the new tab, defaults to 26.
        :type num_cols: int, optional
        :return: A dictionary ready to be passed as a request via a request commit.
        :rtype: Dict[str, Any]
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

        :return: A dictionary ready to be passed as a request via a request commit.
        :rtype: Dict[str, Any]
        """
        return self.new_tab_request(
            self._title, self._tab_id, self._index, self._row_count, self._column_count
        )

    def create(self) -> Tab:
        """
        Convenience method for generating a new tab request based on this Tab and
        immediately committing it, thus adding it to the parent Google Sheet.

        :return: This Tab.
        :rtype: Tab
        """
        req = self.new_tab_request(
            self.title, self.tab_id, self.index, self.row_count, self.column_count
        )
        self._requests.append(req)
        self.commit()
        return self
