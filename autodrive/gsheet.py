from __future__ import annotations

from typing import Dict, KeysView, List, Optional, Any, Tuple, TypeVar, ValuesView
import re
import string
from functools import singledispatchmethod

from .connection import SheetsConnection
from .core import GSheetView, Component
from .interfaces import TwoDRange, AuthConfig
from .formatting.formatting import (
    RangeGridFormatting,
    RangeTextFormatting,
    RangeCellFormatting,
    TabGridFormatting,
    TabCellFormatting,
    TabTextFormatting,
)
from . import google_terms as terms

"""
THIS CAN BE DONE:
result = sheet.spreadsheets().batchUpdate(
    spreadsheetId=sheet_id, 
    body={
        'requests': [
            {
                'updateCells': {
                    'fields': '*', 
                    "rows": [
                        {
                            'values': [
                                {'userEnteredValue': {'numberValue': 1}}, 
                                {'userEnteredValue': {'numberValue': 2}}, 
                                {'userEnteredValue': {'numberValue': 3}}, 
                                {'userEnteredValue': {'numberValue': 4}}, 
                                {'userEnteredValue': {'numberValue': 5}}
                            ]
                        }
                    ], 
                    "range": {
                        "sheetId": 0, 
                        "startRowIndex": 25, 
                        "startColumnIndex": 0, 
                        "endColumnIndex": 5
                    }
                }
            }, 
            {
                'repeatCell': {
                    "fields": "userEnteredFormat(textFormat)", 
                    "range": {
                        "sheetId": 0, 
                        "startRowIndex": 25, 
                        "startColumnIndex": 0
                    }, 
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "fontSize": 14, 
                                "bold": True
                            }
                        }
                    }
                }
            }
        ]
    }
)
"""


"""
Structural Idea:

Drive:
    -m get (returns):
        GFolder?:
        GSheet:
            -a Tab Instances:
                -a Request List
                -a Formatting Instance (to add formatting requests):
                -a Values Instance (to add values requests):
                -m Execute (sends Request List)
            -a Default Tab attr (maps to GSheet._tabs[0])
            -m Execute (collects Tab Request Lists, combines them, and sends)
        GDoc?:
            
"""


T = TypeVar("T", bound="GSheetView")


class GSheetError(Exception):
    pass


class ParseRangeError(GSheetError):
    def __init__(self, rng: str, msg_addon: str = None, *args: object) -> None:
        msg = f"{rng} is not a valid range.{' ' + msg_addon if msg_addon else ''}"
        super().__init__(msg, *args)


class Range(Component):
    def __init__(
        self,
        gsheet_range: str,
        gsheet_id: str,
        tab_id: int,
        tab_title: str,
        *,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> None:
        self._range_str = ""
        title, start, end = self._parse_range_str(gsheet_range)
        title = title or tab_title
        # Assemble start/end row/col indices:
        start_col, start_row = self._convert_cell_str_to_coord(start)
        if end:
            end_col, end_row = self._convert_cell_str_to_coord(end)
            end_col = end_col + 1
            end_row = end_row + 1 if end_row else end_row
        else:
            end_row = start_row
            end_col = start_col
            start_row = 0
            start_col = 0
        # Construct fully formatted range str:
        end_range = f":{end}" if end else ""
        self._range_str = f"{title}!{start}{end_range}"
        super().__init__(
            gsheet_id=gsheet_id,
            tab_id=tab_id,
            start_row_idx=start_row or 0,
            end_row_idx=end_row,
            start_col_idx=start_col or 0,
            end_col_idx=end_col,
            grid_formatting=RangeGridFormatting,
            text_formatting=RangeTextFormatting,
            cell_formatting=RangeCellFormatting,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )

    @property
    def format_grid(self) -> RangeGridFormatting:
        return self._format_grid

    @property
    def format_text(self) -> RangeTextFormatting:
        return self._format_text

    @property
    def format_cell(self) -> RangeCellFormatting:
        return self._format_cell

    @property
    def range_str(self) -> str:
        return self._range_str

    def __str__(self) -> str:
        return self._range_str

    def to_dict(self) -> Dict[str, int]:
        return dict(
            TwoDRange(
                tab_id=self._tab_id,
                start_row=self._start_row,
                end_row=self._end_row,
                start_col=self._start_col,
                end_col=self._end_col,
            )
        )

    def get_data(self) -> Range:
        self._values, self._formats = self._get_data(self._gsheet_id, str(self))
        return self

    def write_values(self, data: List[List[Any]]) -> Range:
        self._write_values(data, self.to_dict())
        return self

    @classmethod
    def from_raw_args(
        cls,
        gsheet_id: str,
        row_range: Tuple[int, int],
        col_range: Tuple[int, int],
        tab_title: str = None,
        tab_id: int = None,
        parent_tab: Tab = None,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> Range:
        if not tab_id and parent_tab:
            tab_id = parent_tab.tab_id
        else:
            raise ValueError("Must pass either tab_id or parent_tab.")
        if not tab_title and parent_tab:
            tab_title = parent_tab.title
        else:
            raise ValueError("Must pass either tab_title or parent_tab")
        range_str = cls._construct_range_str(tab_title, row_range, col_range)
        rng = Range(
            range_str,
            tab_title=tab_title,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            gsheet_id=gsheet_id,
            tab_id=tab_id,
            autoconnect=autoconnect,
        )
        return rng

    @classmethod
    def _gen_args_from_range_str(cls, range_str: str):
        tab_title, start, end = cls._parse_range_str(range_str)
        error_msg = "Cannot generate Range args without {0}"
        if not tab_title:
            raise ParseRangeError(
                range_str, error_msg.format("tab title (e.g. Sheet1!)")
            )
        if not end:
            raise ParseRangeError(range_str, error_msg.format("end range."))
        # Assemble start/end row/col indices:
        col, row = cls._convert_cell_str_to_coord(start)
        start_row = row or 0
        start_col = col or 0
        col, row = cls._convert_cell_str_to_coord(end)
        end_row = row or 999
        end_col = col or 25
        return (start_col, end_col), (start_row, end_row), tab_title

    @classmethod
    def _construct_range_str(
        cls,
        tab_title: str,
        row_range: Tuple[int, int] = None,
        col_range: Tuple[int, int] = None,
    ) -> str:
        rng = ""
        if col_range and row_range:
            start_letter = cls._convert_col_idx_to_alpha(col_range[0])
            end_letter = cls._convert_col_idx_to_alpha(col_range[1])
            start_int = row_range[0] + 1
            end_int = row_range[1] + 1
            rng = f"!{start_letter}{start_int}:{end_letter}{end_int}"
        return tab_title + rng

    @staticmethod
    def _parse_range_str(rng: str) -> Tuple[Optional[str], str, Optional[str]]:
        result = re.match(r"(?:(.*)!)?([A-Z]+\d+?)(?::([A-Z]*\d*))?", rng)
        if result:
            grps = result.groups()
            return grps  # type: ignore
        else:
            raise ParseRangeError(rng)

    @staticmethod
    def _parse_cell_str(cell_str: str) -> Tuple[str, Optional[str]]:
        result = re.match(r"([A-Z]+)(\d+)?", cell_str)
        if result:
            grps = result.groups()
            return grps  # type: ignore
        else:
            raise ParseRangeError(cell_str)

    @classmethod
    def _convert_cell_str_to_coord(cls, cell_str: str) -> Tuple[int, Optional[int]]:
        col, row = cls._parse_cell_str(cell_str)
        col_idx = cls._convert_alpha_col_to_idx(col)
        row_idx = int(row) - 1 if row else None
        return col_idx, row_idx

    @staticmethod
    def _convert_alpha_col_to_idx(alpha_col: str) -> int:
        values = []
        for i, a in enumerate(alpha_col, start=1):
            base_idx = string.ascii_uppercase.index(a) + 1
            remainder = len(alpha_col[i:])
            values.append(26 ** remainder * base_idx)
        return sum(values) - 1

    @staticmethod
    def _convert_col_idx_to_alpha(idx: int) -> str:
        chars = []
        col_num = idx + 1
        while col_num > 0:
            remainder = col_num % 26
            if remainder == 0:
                remainder = 26
            col_letter = chr(ord("A") + remainder - 1)
            chars.append(col_letter)
            col_num = int((col_num - 1) / 26)
        chars.reverse()
        return "".join(chars)


class Tab(Component):
    def __init__(
        self,
        gsheet_id: str,
        tab_title: str,
        tab_idx: int,
        tab_id: int,
        column_count: int = 26,
        row_count: int = 1000,
        *,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> None:
        self._title = tab_title
        self._index = tab_idx
        self._column_count = column_count
        self._row_count = row_count
        super().__init__(
            gsheet_id=gsheet_id,
            tab_id=tab_id,
            start_row_idx=0,
            end_row_idx=row_count,
            start_col_idx=0,
            end_col_idx=column_count,
            grid_formatting=TabGridFormatting,
            text_formatting=TabTextFormatting,
            cell_formatting=TabCellFormatting,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )

    @property
    def format_grid(self) -> TabGridFormatting:
        return self._format_grid

    @property
    def title(self) -> str:
        return self._title

    @property
    def index(self) -> int:
        return self._index

    @property
    def column_count(self) -> int:
        return self._column_count

    @property
    def row_count(self) -> int:
        return self._row_count

    @classmethod
    def from_properties(
        cls,
        gsheet_id: str,
        properties: Dict[str, Any],
        parent_gsheet: GSheet = None,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> Tab:
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

    def get_data(self, rng: Range = None) -> Tab:
        if not rng:
            rng = Range.from_raw_args(
                self._gsheet_id,
                row_range=(0, self._row_count),
                col_range=(0, self._column_count),
                parent_tab=self,
                sheets_conn=self._conn,
            )
        self._values, self._formats = self._get_data(self._gsheet_id, str(rng))
        return self

    def write_values(self, data: List[List[Any]], rng: Range = None) -> Tab:
        if not rng:
            rng = Range.from_raw_args(
                self._gsheet_id,
                row_range=(0, len(data)),
                col_range=(0, len(data[0])),
                parent_tab=self,
                sheets_conn=self._conn,
            )
        self._write_values(data, rng.to_dict())
        return self

    @classmethod
    def new_tab_request(
        cls,
        tab_title: str,
        tab_id: int = None,
        tab_idx: int = None,
        num_rows: int = 1000,
        num_cols: int = 26,
    ) -> Dict[str, Any]:
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
        return self.new_tab_request(
            self._title, self._tab_id, self._index, self._row_count, self._column_count
        )

    def create(self) -> Tab:
        req = self.new_tab_request(
            self.title, self.tab_id, self.index, self.row_count, self.column_count
        )
        self._requests.append(req)
        self.commit()
        return self


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
        properties = self._conn.get_properties(self._gsheet_id)
        name, sheets = self._parse_properties(properties)
        self._name = name
        tabs = [
            Tab.from_properties(self._gsheet_id, props, self, sheets_conn=self._conn)
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
                parent_tab=tab,
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
                parent_tab=tab_,
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
