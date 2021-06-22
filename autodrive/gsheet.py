from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple, TypeVar, Type, Union
from abc import ABC
import re
import string

from .connection import SheetsConnection, AuthConfig
from . import google_terms as terms
from .dtypes import (
    Boolean,
    GOOGLE_DTYPES,
    GoogleDtype,
    GoogleValueType,
    TYPE_MAP,
    UserEnteredVal,
    EffectiveVal,
    FormattedVal,
    String,
    Formula,
)

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


T = TypeVar("T", bound="Component")


class GSheetError(Exception):
    pass


class NoConnectionError(GSheetError):
    def __init__(self, ctype: Type[Component], *args: object) -> None:
        msg = f"No SheetsConnection has been established for this {ctype}."
        super().__init__(msg, *args)


class ParseRangeError(GSheetError):
    def __init__(self, rng: str, msg_addon: str = None, *args: object) -> None:
        msg = f"{rng} is not a valid range.{' ' + msg_addon if msg_addon else ''}"
        super().__init__(msg, *args)


class Component(ABC):
    def __init__(
        self,
        gsheet_id: str,
        *,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        parent: Component = None,
        autoconnect: bool = True,
    ) -> None:
        if not sheets_conn and autoconnect:
            sheets_conn = SheetsConnection(auth_config=auth_config)
        self._conn = sheets_conn
        self._auth = auth_config
        self._requests: List[Dict[str, Any]] = []
        self._gsheet_id = gsheet_id
        self._parent = parent

    @property
    def requests(self) -> List[Dict[str, Any]]:
        return self._requests

    @property
    def conn(self) -> SheetsConnection:
        if not self._conn:
            raise NoConnectionError(type(self))
        return self._conn

    @property
    def auth(self) -> AuthConfig:
        if not self._auth:
            raise NoConnectionError(type(self))
        return self._auth

    @property
    def gsheet_id(self) -> str:
        return self._gsheet_id

    def commit(self) -> Dict[str, Any]:
        if not self._conn:
            raise NoConnectionError(type(self))
        results = self._conn.execute_requests(self._gsheet_id, self._requests)
        self._requests = []
        return results

    @classmethod
    def _parse_row_data(
        cls,
        row_data: List[Dict[str, List[Dict[str, Any]]]],
        value_type: GoogleValueType = EffectiveVal,
    ) -> List[List[Any]]:
        results = []
        for row in row_data:
            row_list = []
            for cell in row.get(terms.VALUES, []):
                raw_value = cell.get(str(value_type))
                value = raw_value
                if value_type in (UserEnteredVal, EffectiveVal):
                    if raw_value:
                        for dtype in GOOGLE_DTYPES:
                            value = raw_value.get(str(dtype))
                            if value:
                                if value_type == UserEnteredVal:
                                    value = dtype.parse(value)
                                break
                row_list.append(value)
            results.append(row_list)
        return results

    def _get_values(
        self,
        gsheet_id: str,
        rng: Range,
        value_type: GoogleValueType = EffectiveVal,
    ) -> List[List[Any]]:
        raw = self._conn.get_values(gsheet_id, [str(rng)])
        row_data = raw[terms.TABS_PROP][0][terms.DATA][0][terms.ROWDATA]
        return self._parse_row_data(row_data, value_type=value_type)

    def _write_values(self: T, data: List[List[Any]], rng: Range) -> T:
        write_values = [
            [self._gen_cell_write_value(val) for val in row] for row in data
        ]
        request = {
            "updateCells": {
                terms.FIELDS: "*",
                terms.ROWS: [{terms.VALUES: values} for values in write_values],
                terms.RNG: rng.to_dict(),
            }
        }
        self._requests.append(request)
        return self

    @staticmethod
    def _gen_cell_write_value(python_val: Any) -> Dict[str, Any]:
        type_ = type(python_val)
        if (
            isinstance(python_val, str)
            and len(python_val) >= 2
            and python_val[0] == "="
        ):
            dtype = Formula
        else:
            dtype = TYPE_MAP.get(type_, String)
        return {UserEnteredVal.value_key: {dtype.type_key: python_val}}

    # TODO: Delete this?
    @staticmethod
    def gen_alpha_keys(num: int) -> List[str]:
        """
        Generates a list of characters from the Latin alphabet a la gsheet/excel
        headers.

        Args:
            num (int): The desired length of the list.

        Returns:
            List[str]: A list containing as many letters and letter combos as
                desired. Can be used to generate sets up to 676 in length.
        """
        a = string.ascii_uppercase
        result = list()
        x = num // 26
        for i in range(x + 1):
            root = a[i - 1] if i > 0 else ""
            keys = [root + a[j] for j in range(26)]
            for k in keys:
                result.append(k) if len(result) < num else None
        return result


class Range(Component):
    def __init__(
        self,
        gsheet_range: str,
        gsheet_id: str,
        tab_id: int,
        *,
        parent_tab: Tab = None,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> None:
        super().__init__(
            gsheet_id=gsheet_id,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
            parent=parent_tab,
        )
        self._tab_id = tab_id
        self._values: List[List[Any]] = []
        self._end_row = 1000  # remember: end values are exclusive.
        self._end_col = 26  # remember: end values are exclusive.
        self._range_str = ""
        tab_title, start, end = self._parse_range_str(gsheet_range)
        tab_title = tab_title if tab_title else parent_tab.title
        # Assemble start/end row/col indices:
        col, row = self._convert_cell_str_to_coord(start)
        self._start_row = row or 0
        self._start_col = col or 0
        if end:
            col, row = self._convert_cell_str_to_coord(end)
            col = col + 1 or parent_tab.column_count
            row = row + 1 or parent_tab.row_count
        else:
            col = parent_tab.column_count
            row = parent_tab.row_count
        self._end_row = row
        self._end_col = col
        # Construct fully formatted range str:
        end_range = f":{end}" if end else ""
        self._range_str = f"{tab_title}!{start}{end_range}"

    @property
    def tab_id(self) -> int:
        return self._tab_id

    @property
    def start_row_idx(self) -> int:
        return self._start_row

    @property
    def end_row_idx(self) -> int:
        return self._end_row

    @property
    def start_col_idx(self) -> int:
        return self._start_col

    @property
    def end_col_idx(self) -> int:
        return self._end_col

    @property
    def range_str(self) -> str:
        return self._range_str

    @property
    def values(self) -> List[List[Any]]:
        return self._values

    @property
    def parent_tab(self) -> Tab:
        if not self._parent:
            raise AttributeError("This Range has no parent_tab.")
        return self._parent

    @parent_tab.setter
    def parent_tab(self, tab: Tab) -> None:
        self._parent = tab

    def __str__(self) -> str:
        return self._range_str

    def to_dict(self) -> Dict[str, int]:
        if self._tab_id is None:  # tab_id can be 0
            raise ValueError(
                "This range has no tab_id specified, you must specify tab_id."
            )
        return {
            terms.TAB_ID: self._tab_id,
            "startRowIndex": self._start_row,
            "endRowIndex": self._end_row,
            "startColumnIndex": self._start_col,
            "endColumnIndex": self._end_col,
        }

    def get_values(self) -> Range:
        self._values = self._get_values(self._gsheet_id, self)
        return self

    def write_values(self, data: List[List[Any]]) -> Range:
        self._write_values(data, self)
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
            tab_id = parent_tab.id
        else:
            raise ValueError("Must pass either tab_id or parent_tab.")
        if not tab_title and parent_tab:
            tab_title = parent_tab.title
        else:
            raise ValueError("Must pass either tab_title or parent_tab")
        range_str = cls._construct_range_str(tab_title, row_range, col_range)
        rng = Range(
            range_str,
            parent_tab=parent_tab,
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
        parent_gsheet: GSheet = None,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> None:
        super().__init__(
            gsheet_id=gsheet_id,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
            parent=parent_gsheet,
        )
        self._title = tab_title
        self._index = tab_idx
        self._tab_id = tab_id
        self._column_count = column_count
        self._row_count = row_count
        self._values = []

    @property
    def title(self) -> str:
        return self._title

    @property
    def index(self) -> int:
        return self._index

    @property
    def id(self) -> int:
        return self._tab_id

    @property
    def column_count(self) -> int:
        return self._column_count

    @property
    def row_count(self) -> int:
        return self._row_count

    @property
    def data_shape(self) -> Tuple[int, int]:
        width = len(self._values[0]) if self._values else 0
        return len(self._values), width

    @property
    def values(self) -> List[List[Any]]:
        return self._values

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
            parent_gsheet=parent_gsheet,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )

    def get_values(self, rng: Range = None) -> Tab:
        if not rng:
            rng = Range.from_raw_args(
                self._gsheet_id,
                row_range=(0, self._row_count),
                col_range=(0, self._column_count),
                parent_tab=self,
                sheets_conn=self._conn,
            )
        self._values = self._get_values(self._gsheet_id, rng)
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
        self._write_values(data, rng)
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

    def create(self) -> Tab:
        req = self.new_tab_request(
            self.title, self.id, self.index, self.row_count, self.column_count
        )
        self._requests.append(req)
        self.commit()
        return self


class GSheet(Component):
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
    def id(self) -> str:
        return self._gsheet_id

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
        self._partial = False
        return self

    @staticmethod
    def _parse_properties(
        properties: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        sheet_title = properties[terms.FILE_PROPS][terms.FILE_NAME]
        sheet_props = [sheet[terms.TAB_PROPS] for sheet in properties[terms.TABS_PROP]]
        return sheet_title, sheet_props

    def add_tab(self, title: str, index: int = None) -> GSheet:
        if title in self.tabs.keys():
            raise ValueError(f"Sheet already has tab with title {title}")
        self._requests.append(
            {
                terms.ADDTAB: {
                    terms.TAB_PROPS: {terms.TAB_NAME: title, terms.TAB_IDX: index or 0}
                }
            }
        )
        return self

    def write_values(
        self, data: List[List[Any]], to_tab: str, rng: Range = None
    ) -> GSheet:
        tab = self.tabs.get(to_tab)
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
        self._write_values(data, rng)
        return self

    def get_tab_index_by_title(self, tab_title: str) -> Optional[int]:
        for t in self._tabs:
            if t.title == tab_title:
                return t.index
        else:
            return None
