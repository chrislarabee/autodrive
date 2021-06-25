from __future__ import annotations

from typing import Dict, KeysView, List, Optional, Any, Tuple, ValuesView
from functools import singledispatchmethod

from .connection import SheetsConnection
from .core import GSheetView
from .interfaces import AuthConfig
from . import google_terms as terms
from .tab import Tab
from .range import Range


class GSheet(GSheetView):
    def __init__(
        self,
        gsheet_id: str,
        title: str = None,
        *,
        tabs: List[Tab] = None,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> None:
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
        return self._requests

    @property
    def tabs(self) -> Dict[str, Tab]:
        return {tab.title: tab for tab in self._tabs}

    @property
    def title(self) -> Optional[str]:
        return self._title

    def fetch(self) -> GSheet:
        properties = self.conn.get_properties(self._gsheet_id)
        name, sheets = self._parse_properties(properties)
        self._name = name
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
        self, data: List[List[Any]], to_tab: str = None, rng: Range = None
    ) -> GSheet:
        tab = self.tabs.get(to_tab) if to_tab else self._tabs[0]
        if not tab:
            raise KeyError(f"{to_tab} not found in {self._title} tabs.")
        if not rng:
            rng = Range.from_raw_args(
                self._gsheet_id,
                (0, len(data)),
                (0, len(data[0])),
                tab_id=tab.tab_id,
                tab_title=tab.title,
                sheets_conn=self.conn,
            )
        self._write_values(data, rng.to_dict())
        return self

    def get_data(self, tab: str | int = None, rng: Range = None) -> GSheet:
        if isinstance(tab, str):
            tab_ = self.tabs.get(tab)
            if not tab_:
                raise ValueError(f"{tab} not found in GSheet tabs.")
        elif isinstance(tab, int) or tab is None:
            tab_ = self._tabs[tab or 0]
        else:
            raise TypeError(
                f"tab must be a string, integer, or None. type = {type(tab)}"
            )
        if not rng:
            rng = Range.from_raw_args(
                self._gsheet_id,
                row_range=(0, tab_.row_count),
                col_range=(0, tab_.column_count),
                tab_id=tab_.tab_id,
                tab_title=tab_.title,
                sheets_conn=self._conn,
            )
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

    def keys(self) -> KeysView:
        return self.tabs.keys()

    def values(self) -> ValuesView:
        return self.tabs.values()

    def get_tab_index_by_title(self, tab_title: str) -> Optional[int]:
        for t in self._tabs:
            if t.title == tab_title:
                return t.index
        else:
            return None
