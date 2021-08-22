from __future__ import annotations

from functools import singledispatchmethod
from typing import Any, Dict, KeysView, List, Optional, ValuesView, Sequence
from pathlib import Path

from .connection import SheetsConnection
from ._view import GSheetView
from .interfaces import AuthConfig, FullRange
from .tab import Tab
from .range import Range
from .dtypes import EffectiveVal, GoogleValueType


class GSheet(GSheetView):
    """
    Provides a connection to a single Google Sheet and access to its properties
    and Tabs.
    """

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
        Args:
            gsheet_id (str): The id string of the target Google Sheet; can be found
                in the link to the Google Sheet.
            title (str, optional): The name of the Google Sheet, defaults to None.
            tabs (List[Tab], optional): A list of Tabs attached to the Google Sheet.
                You should probably manage Tabs with GSheet.fetch () or by getting
                the GSheet directly from a Drive, rather than using this parameter,
                defaults to None.
            auth_config (AuthConfig, optional): Optional custom AuthConfig object,
                defaults to None.
            sheets_conn (SheetsConnection, optional): Optional manually created
                SheetsConnection, defaults to None.
            autoconnect (bool, optional): If you want to instantiate a GSheet
                without immediately checking your authentication credentials and
                connecting to the Google Sheets api, set this to False, defaults to
                True.

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

        Returns:
            List[Dict[str, Any]]: List of update request dictionaries that have
            been created for this GSheet.

        """
        return self._requests

    @property
    def tabs(self) -> Dict[str, Tab]:
        """
        Dictionary of fetched Tabs on this GSheet by title.

        Returns:
            Dict[str, Tab]: Tab titles as keys and corresponding Tabs as values.

        """
        return {tab.title: tab for tab in self._tabs}

    @property
    def title(self) -> Optional[str]:
        """
        The name of the GSheet.

        Returns:
            Optional[str]: The name of the GSheet, or None if its name hasn't been
            fetched.

        """
        return self._title

    def fetch(self) -> GSheet:
        """
        Gets the latest metadata from the API for this GSheet. Populates title and
        tab properties.

        .. note::

            This method will cause a request to be posted to the relevant Google
            API immediately.

        Returns:
          GSheet: This GSheet

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

    @singledispatchmethod
    def add_tab(self, tab: Tab) -> GSheet:
        """
        Adds a Tab to the GSheet.

        Args:
            tab (Tab): The Tab instance you want to add.

        Returns:
            GSheet: This Gsheet.

        Raises:
            ValueError: If the GSheet already has a Tab with that title.

        """
        if tab.title in self.tabs.keys():
            raise ValueError(f"GSheet already has tab with title {tab.title}")
        self._tabs.insert(tab.index, tab)
        self._requests.append(tab.gen_add_tab_request())
        return self

    def gen_range(self, rng: FullRange, tab: str | int | None = None) -> Range:
        """
        Convenience method for generating a new Range object from a Tab in this
        GSheet.

        Args:
            rng (FullRange): The desired FullRange of the new Range object.
            tab (str | int, optional): The name of the Tab to generate from, or
                its index. Defaults to None, which will generate a range from the
                first Tab.

        Returns:
            Range: The newly generated Range object.
        """
        if isinstance(tab, str):
            from_tab = self.tabs[tab]
        elif isinstance(tab, int):
            from_tab = self._tabs[tab]
        else:
            from_tab = self._tabs[0]
        return from_tab.gen_range(rng)

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
        data: Sequence[Sequence[Any] | Dict[str, Any]],
        to_tab: str | None = None,
        rng: FullRange | str | None = None,
    ) -> GSheet:
        """
        Adds a request to write data. GSheet.commit () to commit the requests.

        Args:
            data (Sequence[Sequence[Any] | Dict[str, Any]]): The data to write.
                Each sequence or dictionary in the passed data is a row, with
                each value in that sub-iterable being a column. Dictionary keys
                will be used as a header row in the written data.
            to_tab (str, optional): The name of the tab to write to, defaults to
                None, which will write to whatever tab is first in the Sheet.
            rng (FullRange | str, optional): The range to which the data will be
                written, starting with the top-left-most cell in the range,
                defaults to None, which will write to the top-left-most cell in
                the passed tab, or the first tab.

        Returns:
            GSheet: This GSheet.

        Raises:
            KeyError: If the passed tab name (to_tab) isn't present in the GSheet's
                current tabs property.

        """
        tab = self.tabs.get(to_tab) if to_tab else self._tabs[0]
        if not tab:
            raise KeyError(f"{to_tab} not found in {self._title} tabs.")
        rng = self.ensure_full_range(tab.full_range(), rng)
        self._write_values(data, tab._tab_id, rng.to_dict())
        return self

    def get_data(
        self,
        tab: str | int | None = None,
        rng: FullRange | str | None = None,
        value_type: GoogleValueType = EffectiveVal,
    ) -> GSheet:
        """
        Gets the data from the cells of the GSheet.

        .. note::

            This method will cause a request to be posted to the relevant Google
            API immediately.

        Args:
            tab (str | int, optional): The name of the tab, or its (0-based) index
                (from left to right), defaults to None, which will collect data from
                the first tab in the Sheet.
            rng (FullRange | str, optional): The specific range to fetch data
                from, defaults to None, for all data in the target tab.
            value_type (GoogleValueType, optional): Allows you to toggle the
                type of the values returned by the Google Sheets API. See the
                :mod:`dtypes <autodrive.dtypes>` documentation for more info on
                the different GoogleValueTypes.

        Returns:
            GSheet: This GSheet.

        Raises:
            KeyError: If the passed tab name is not found in this GSheet's tabs.
            TypeError: If anything other than the displayed types is passed for
                the tab parameter.

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
        rng = self.ensure_full_range(tab_.full_range(), rng)
        if not rng.tab_title:
            rng.tab_title = tab_.title
        values, formats = self._get_data(self._gsheet_id, str(rng), value_type)
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

        Returns:
            KeysView[str]: The tab titles on this GSheet.

        """
        return self.tabs.keys()

    def values(self) -> ValuesView[Tab]:
        """
        Gets the values (Tabs) for the fetched tabs on this GSheet.

        Returns:
            ValuesView[Tab]: The Tabs on this GSheet.

        """
        return self.tabs.values()

    def get_tab_index_by_title(self, tab_title: str) -> Optional[int]:
        for t in self._tabs:
            if t.title == tab_title:
                return t.index
        else:
            return None

    def to_csv(
        self,
        root_path: str | Path,
        filename_overrides: Dict[str, str] | None = None,
        **tabs_and_headers: Sequence[Any] | None,
    ) -> None:
        """
        Convenience method for calling :meth:`.to_csv() <autodrive.tab.Tab.to_csv>`
        on some or all of the GSheet's tabs.

        Args:
            root_path (str): The root directory path to save tab files to.
            filename_overrides (Dict[str, str], optional): By default, this method
                will name each file after the corresponding tab's title. To
                override some or all of the resulting filenames, pass a dictionary
                with keys equal to the names of the tab you want to override and
                the values equal to the name of the filename you want. Defaults to
                None, for all tabs being treated with default behavior.
            tabs_and_headers: (Sequence[Any], optional): If you want to only
                output the data for some of the tabs, you can pass the names of
                the desired tabs as kwargs. If you wish, you can also pass a
                header row for those tabs, which will be inserted as the first
                row of the file. If you don't want to pass a header row, simply
                pass ``tabname=None`` for that tab.

        Raises:
            ValueError: If root_path does not lead to a directory.
        """
        root_path = Path(root_path)
        if not root_path.is_dir():
            raise ValueError(f"{root_path} is not a directory.")
        overrides = filename_overrides or {}
        tab_info = (
            tabs_and_headers
            if len(tabs_and_headers) > 0
            else {t.title: None for t in self._tabs}
        )
        for tab_name, header in tab_info.items():
            tab = self.tabs[tab_name]
            filename = overrides.get(tab_name, tab.title)
            p = root_path.joinpath(filename).with_suffix(".csv")
            tab.to_csv(p, header)

    def to_json(
        self,
        root_path: str | Path,
        filename_overrides: Dict[str, str] | None = None,
        **tabs_and_headers: Sequence[str] | int,
    ) -> None:
        """
        Convenience method for calling :meth:`.to_json() <autodrive.tab.Tab.to_json>`
        on some or all of the GSheet's tabs.

        Args:
            root_path (str): The root directory path to save tab files to.
            filename_overrides (Dict[str, str], optional): By default, this method
                will name each file after the corresponding tab's title. To
                override some or all of the resulting filenames, pass a dictionary
                with keys equal to the names of the tab you want to override and
                the values equal to the name of the filename you want. Defaults to
                None, for all tabs being treated with default behavior.
            tabs_and_headers: (Sequence[str] | int, optional): If you want to only
                output the data for some of the tabs, you can pass the names of
                the desired tabs as kwargs. You must also indicate what keys
                should be used when creating the jsons for those tabs. For each
                header value, you may either pass a row index to pull for the keys,
                or a list of keys.

        Raises:
            ValueError: If root_path does not lead to a directory.
        """
        root_path = Path(root_path)
        if not root_path.is_dir():
            raise ValueError(f"{root_path} is not a directory.")
        overrides = filename_overrides or {}
        tab_info = (
            tabs_and_headers
            if len(tabs_and_headers) > 0
            else {t.title: 0 for t in self._tabs}
        )
        for tab_name, header in tab_info.items():
            tab = self.tabs[tab_name]
            filename = overrides.get(tab_name, tab.title)
            p = root_path.joinpath(filename).with_suffix(".jsonl")
            tab.to_json(p, header)
