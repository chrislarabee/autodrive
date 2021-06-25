from __future__ import annotations

from typing import Dict, List, Any, Tuple, Optional
import re
import string

from .core import Component
from .interfaces import AuthConfig, TwoDRange
from .connection import SheetsConnection
from .formatting.formatting import (
    RangeCellFormatting,
    RangeGridFormatting,
    RangeTextFormatting,
)


class ParseRangeError(Exception):
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
        tab_title: str,
        tab_id: int,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> Range:
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
