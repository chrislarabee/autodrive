from __future__ import annotations

from functools import singledispatchmethod
from typing import Any, Dict, KeysView, List, Optional, Tuple, ValuesView

from . import _google_terms as terms
from .connection import SheetsConnection
from ._view import GSheetView
from .interfaces import AuthConfig, OneDRange, TwoDRange
from .tab import Tab


class GSheet(GSheetView):
    def __init__(
        self,
        gsheet_id: str,
        title: str | None = None,
        *,
        tabs: List[Tab] | None = None,
        auth_config: AuthConfig | None = None,
        sheets_conn: SheetsConnection | None = None,
        autoconnect: bool = True,
    ) -> None:
        """
        Provides a connection to a single GoogleSheet and access to its properties
        and Tabs.

        :param gsheet_id: The id string of the target Google Sheet; can be found in
            the link to the Google Sheet.
        :type gsheet_id: str
        :param title: The name of the Google Sheet, defaults to None
        :type title: str, optional
        :param tabs: A list of Tabs attached to the Google Sheet. You should probably
            manage Tabs with GSheet.fetch() or by getting the GSheet directly from a
            Drive, defaults to None
        :type tabs: List[Tab], optional
        :param auth_config: Optional custom AuthConfig object, defaults to None
        :type auth_config: AuthConfig, optional
        :param sheets_conn: Optional manually created SheetsConnection, defaults to None
        :type sheets_conn: SheetsConnection, optional
        :param autoconnect: If you want to instantiate a GSheet without immediately
            checking your authentication credentials and connecting to the Google Sheets
            api, set this to False, defaults to True
        :type autoconnect: bool, optional
        """
        super().__init__(
            gsheet_id=gsheet_id,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )
        self._title = title
        self._tabs = tabs or []

    @property
    def requests(self) -> List[Dict[str, Any]]:
        """
        List of accumulated (uncommitted) requests on this GSheet.

        :return: List of update request dictionaries that have been created for this
            GSheet.
        :rtype: List[Dict[str, Any]]
        """
        return self._requests

    @property
    def tabs(self) -> Dict[str, Tab]:
        """
        Dictionary of fetched Tabs on this GSheet by title.

        :return: Tab titles as keys and corresponding Tabs as values.
        :rtype: Dict[str, Tab]
        """
        return {tab.title: tab for tab in self._tabs}

    @property
    def title(self) -> Optional[str]:
        """
        The name of the GSheet.

        :return: The name of the GSheet, or None if its name hasn't been fetched.
        :rtype: Optional[str]
        """
        return self._title

    def fetch(self) -> GSheet:
        """
        Gets the latest metadata from the API for this GSheet. Populates title and
        tab properties.

        :return: This GSheet
        :rtype: GSheet
        """
        properties = self.conn.get_properties(self._gsheet_id)
        name, sheets = self._parse_properties(properties)
        self._title = name
        tabs = [
            Tab.from_properties(self._gsheet_id, props, sheets_conn=self._conn)
            for props in sheets
        ]
        self._tabs = tabs
        return self

    @staticmethod
    def _parse_properties(
        properties: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        sheet_title = properties[terms.FILE_PROPS][terms.FILE_NAME]
        sheet_props = [sheet[terms.TAB_PROPS] for sheet in properties[terms.TABS_PROP]]
        return sheet_title, sheet_props

    @singledispatchmethod
    def add_tab(self, tab: Tab) -> GSheet:
        """
        Adds a Tab to the GSheet.

        :param tab: The Tab instance you want to add.
        :type tab: Tab
        :raises ValueError: If the GSheet already has a Tab with that title.
        :return: This Gsheet.
        :rtype: GSheet
        """
        if tab.title in self.tabs.keys():
            raise ValueError(f"GSheet already has tab with title {tab.title}")
        self._tabs.insert(tab.index, tab)
        self._requests.append(tab.gen_add_tab_request())
        return self

    # @add_tab.register
    # def add_tab_by_name(
    #     self,
    #     tab: str,
    #     tab_id: int = None,
    #     tab_idx: int = None,
    #     num_rows: int = 1000,
    #     num_cols: int = 26,
    # ) -> GSheet:
    #     if tab in self.tabs.keys():
    #         raise ValueError(f"GSheet already has tab with title {tab}")
    #     req = Tab.new_tab_request(
    #         tab, tab_id=tab_id, tab_idx=tab_idx, num_rows=num_rows, num_cols=num_cols
    #     )
    #     self._requests.append(req)
    #     return self

    def write_values(
        self,
        data: List[List[Any]],
        to_tab: str | None = None,
        rng: TwoDRange | OneDRange | None = None,
    ) -> GSheet:
        """
        Adds a request to write data. GSheet.commit() to commit the requests.

        :param data: The data to write. Each list in the passed data list is a row,
            with each value in that sublist being a column.
        :type data: List[List[Any]]
        :param to_tab: The name of the tab to write to, defaults to None, which will
            write to whatever tab is first in the Sheet.
        :type to_tab: str, optional
        :param rng: A TwoDRange, to which the data will be written, starting with the
            top-left-most cell in the range, defaults to None, which will write to the
            top-left-most cell in the passed tab, or the first tab.
        :type rng: TwoDRange, optional
        :raises KeyError: If the passed tab name (to_tab) isn't present in the GSheet's
            current tabs property.
        :return: This GSheet.
        :rtype: GSheet
        """
        tab = self.tabs.get(to_tab) if to_tab else self._tabs[0]
        if not tab:
            raise KeyError(f"{to_tab} not found in {self._title} tabs.")
        if not rng:
            rng = tab.two_d_range()
        self._write_values(data, rng.to_dict())
        return self

    def get_data(
        self, tab: str | int | None = None, rng: TwoDRange | OneDRange | None = None
    ) -> GSheet:
        """
        Gets the data from the cells of the GSheet.

        :param tab: The name of the tab, or its (0-based) index (from left to write),
            defaults to None, which will collect data from the first tab in the Sheet.
        :type tab: str | int, optional
        :param rng: The specific range to fetch data from, defaults to None, for all
            data in the target tab.
        :type rng: TwoDRange | OneDRange, optional
        :raises KeyError: If the passed tab name is not found in this GSheet's tabs.
        :raises TypeError: If anything other than the displayed types is passed for
            the tab parameter.
        :return: This GSheet.
        :rtype: GSheet
        """
        if isinstance(tab, str):
            tab_ = self.tabs.get(tab)
            if not tab_:
                raise KeyError(f"{tab} not found in GSheet tabs.")
        elif isinstance(tab, int) or tab is None:
            tab_ = self._tabs[tab or 0]
        else:
            raise TypeError(
                f"tab must be a string, integer, or None. type = {type(tab)}"
            )
        if not rng:
            rng = tab_.two_d_range()
        values, formats = self._get_data(self._gsheet_id, str(rng))
        tab_.values = values
        tab_.formats = formats
        return self

    def __iter__(self):
        return self._tabs

    def __len__(self):
        return len(self._tabs)

    def __getitem__(self, key: int | str) -> Tab:
        if isinstance(key, int):
            return self._tabs[key]
        else:
            return self.tabs[key]

    def keys(self) -> KeysView[str]:
        """
        Gets the keys (tab titles) for the fetched tabs on this GSheet.

        :return: The tab titles on this GSheet.
        :rtype: KeysView[str]
        """
        return self.tabs.keys()

    def values(self) -> ValuesView[Tab]:
        """
        Gets the values (Tabs) for the fetched tabs on this GSheet.

        :return: The Tabs on this GSheet.
        :rtype: ValuesView[Tab]
        """
        return self.tabs.values()

    def get_tab_index_by_title(self, tab_title: str) -> Optional[int]:
        for t in self._tabs:
            if t.title == tab_title:
                return t.index
        else:
            return None
