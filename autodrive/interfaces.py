from __future__ import annotations

import re
import string
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Optional, Tuple, TypeVar

from . import google_terms as terms

DEFAULT_TOKEN = "gdrive_token.pickle"
DEFAULT_CREDS = "credentials.json"


T = TypeVar("T")


class ParseRangeError(Exception):
    def __init__(self, rng: str, msg_addon: str | None = None, *args: object) -> None:
        msg = f"{rng} is not a valid range.{' ' + msg_addon if msg_addon else ''}"
        super().__init__(msg, *args)


class AuthConfig:
    def __init__(
        self,
        secrets_config: Dict[str, Any] | None = None,
        token_filepath: str | Path = DEFAULT_TOKEN,
        creds_filepath: str | Path = DEFAULT_CREDS,
    ) -> None:
        self.secrets_config = secrets_config
        self._token_filepath = Path(token_filepath)
        self._creds_filepath = Path(creds_filepath)

    @property
    def token_filepath(self) -> Path:
        return self._token_filepath

    @property
    def creds_filepath(self) -> Path:
        return self._creds_filepath


class Interface(Mapping[str, T]):
    def to_dict(self) -> Dict[str, T]:
        return {}

    def __iter__(self) -> Iterator[str]:
        return iter(self.to_dict())

    def __getitem__(self, k: str) -> T:
        return self.to_dict()[k]

    def __len__(self) -> int:
        return len(self.to_dict())


class RangeInterface(Interface[int]):
    def __init__(self, tab_id: int, tab_title: str | None = None) -> None:
        self.tab_id = tab_id
        self.tab_title = tab_title

    def to_dict(self) -> Dict[str, int]:
        return {terms.TAB_ID: self.tab_id}

    @classmethod
    def _construct_range_str(
        cls,
        start_row: Optional[int] = 0,
        end_row: Optional[int] = None,
        start_col: Optional[int] = 0,
        end_col: Optional[int] = 0,
    ) -> str:
        start_letter = ""
        end_letter = ""
        start_letter = cls._convert_col_idx_to_alpha(start_col or 0)
        end_letter = cls._convert_col_idx_to_alpha(end_col - 1 if end_col else 0)
        start_int = (start_row or 0) + 1
        end_int = end_row if end_row is not None else None
        return f"{start_letter}{start_int}:{end_letter}{end_int or ''}"

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
        values: List[int] = []
        for i, a in enumerate(alpha_col, start=1):  # type: ignore
            base_idx = string.ascii_uppercase.index(a) + 1  # type: ignore
            remainder = len(alpha_col[i:])
            values.append(26 ** remainder * base_idx)
        return sum(values) - 1

    @staticmethod
    def _convert_col_idx_to_alpha(idx: int) -> str:
        chars: List[str] = []
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

    @classmethod
    def _parse_idx(
        cls, idx: str | int | None = None, base0_idxs: bool = False, mod: int = 1
    ) -> Optional[int]:
        adj = 0 if base0_idxs else mod
        result = None
        if isinstance(idx, str):
            result = cls._convert_alpha_col_to_idx(idx)
        elif idx is not None:
            result = idx + adj
        return result


class OneDRange(RangeInterface):
    def __init__(
        self,
        tab_id: int,
        start_idx: str | int | None = None,
        end_idx: str | int | None = None,
        *,
        tab_title: str | None = None,
        base0_idxs: bool = False,
        column: bool = False,
    ) -> None:
        super().__init__(tab_id, tab_title)
        self.start_idx = self._parse_idx(start_idx, base0_idxs, -1)
        self.end_idx = self._parse_idx(end_idx, base0_idxs)
        self.column = column
        if isinstance(start_idx, str):
            self.column = True
        if self.column and self.end_idx and not base0_idxs:
            self.end_idx += 1

    def to_dict(self) -> Dict[str, int]:
        result = {terms.TAB_ID: self.tab_id}
        # All of these must be is not None because any of them can be 0:
        if self.start_idx is not None:
            result["startIndex"] = self.start_idx
        if self.end_idx is not None:
            result["endIndex"] = self.end_idx
        return result

    def __str__(self) -> str:
        if self.column:
            rng = self._construct_range_str(
                start_col=self.start_idx, end_col=self.end_idx
            )
        else:
            raise AttributeError(
                f"{self}.column indicator is False. Cannot convert row OneDRanges to "
                "strings."
            )
        return f"{self.tab_title or ''}{'!' if self.tab_title else ''}{rng}"

    @property
    def start_row(self) -> int:
        return self.start_idx or 0

    @property
    def end_row(self) -> int:
        return self.start_idx + 1 if self.start_idx else 0

    @property
    def start_col(self) -> int:
        return self.start_idx or 0

    @property
    def end_col(self) -> int:
        return self.start_idx + 1 if self.start_idx else 0


class TwoDRange(RangeInterface):
    def __init__(
        self,
        tab_id: int,
        start_row: int | None = None,
        end_row: int | None = None,
        start_col: int | str | None = None,
        end_col: int | str | None = None,
        *,
        range_str: str | None = None,
        base0_idxs: bool = False,
        tab_title: str | None = None,
    ) -> None:
        super().__init__(tab_id, tab_title)
        if range_str:
            title, start, end = self._parse_range_str(range_str)
            if title and not self.tab_title:
                self.tab_title = title
            if end:
                cend, rend = self._convert_cell_str_to_coord(end)
                cstart, rstart = self._convert_cell_str_to_coord(start)
            else:
                cend, rend = self._convert_cell_str_to_coord(start)
                cstart = 0
                rstart = 0
            self.start_row = rstart
            self.end_row = rend + 1 if rend else None
            self.start_col = cstart
            self.end_col = cend + 1 if cend else None
        else:
            self.start_row = self._parse_idx(start_row, base0_idxs, -1)
            self.end_row = self._parse_idx(end_row, base0_idxs)
            self.start_col = self._parse_idx(start_col, base0_idxs, -1) or 0
            self.end_col = self._parse_idx(end_col, base0_idxs)

    @property
    def row_range(self) -> OneDRange:
        return OneDRange(
            self.tab_id,
            self.start_row,
            self.end_row,
            tab_title=self.tab_title,
            base0_idxs=True,
        )

    @property
    def col_range(self) -> OneDRange:
        return OneDRange(
            self.tab_id,
            self.start_col,
            self.end_col,
            tab_title=self.tab_title,
            base0_idxs=True,
            column=True,
        )

    def __str__(self) -> str:
        rng = self._construct_range_str(
            self.start_row, self.end_row, self.start_col, self.end_col
        )
        return f"{self.tab_title or ''}{'!' if self.tab_title else ''}{rng}"

    def to_dict(self) -> Dict[str, int]:
        result = {terms.TAB_ID: self.tab_id}
        # All of these must be is not None because any of them can be 0:
        if self.start_row is not None:
            result["startRowIndex"] = self.start_row
        if self.end_row is not None:
            result["endRowIndex"] = self.end_row
        if self.start_col is not None:
            result["startColumnIndex"] = self.start_col
        if self.end_col is not None:
            result["endColumnIndex"] = self.end_col
        return result


class Color(Interface[float]):
    def __init__(
        self,
        red: int | float = 0,
        green: int | float = 0,
        blue: int | float = 0,
        alpha: int | float = 100,
    ) -> None:
        self.red = red if isinstance(red, float) else red / 255
        self.green = green if isinstance(green, float) else green / 255
        self.blue = blue if isinstance(blue, float) else blue / 255
        self.alpha = alpha if isinstance(alpha, float) else alpha / 100

    def to_dict(self) -> Dict[str, float]:
        return {
            "red": self.red,
            "green": self.green,
            "blue": self.blue,
            "alpha": self.alpha,
        }


class Format(Interface[Any]):
    def __init__(self, format_key: str) -> None:
        self._format_key = format_key

    @property
    def format_key(self) -> str:
        return self._format_key

    def __str__(self) -> str:
        return f"userEnteredFormat({self._format_key})"

    def _fmt_contents(self) -> Dict[str, Any]:
        return {}

    def to_dict(self) -> Dict[str, Any]:
        result = self._fmt_contents()
        return {"userEnteredFormat": {self._format_key: result}}


class TextFormat(Format):
    def __init__(
        self,
        *,
        font: str | None = None,
        color: Color | None = None,
        font_size: int | None = None,
        bold: bool | None = None,
        italic: bool | None = None,
        underline: bool | None = None,
        strikethrough: bool | None = None,
    ) -> None:
        super().__init__("textFormat")
        self.font = font
        self.color = color
        self.font_size = font_size
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough

    def _fmt_contents(self) -> Dict[str, bool | str | int | Dict[str, float]]:
        result: Dict[str, bool | str | int | Dict[str, float]] = {}
        if self.bold is not None:
            result["bold"] = self.bold
        if self.italic is not None:
            result["italic"] = self.italic
        if self.underline is not None:
            result["underline"] = self.underline
        if self.strikethrough is not None:
            result["strikethrough"] = self.strikethrough
        if self.font:
            result["fontFamily"] = self.font
        if self.color:
            result["foregroundColor"] = self.color.to_dict()
        if self.font_size is not None:
            result["fontSize"] = self.font_size
        return result


# TODO: Add BorderFormat
# TODO: Add AlignmentFormat?


class NumericFormat(Format):
    def __init__(self, pattern: str = "") -> None:
        super().__init__("numberFormat")
        self.type = "NUMBER"
        self.pattern = pattern

    def _fmt_contents(self) -> Dict[str, str]:
        return {"type": self.type, "pattern": self.pattern}


StdNumericFormat = NumericFormat()
AccountingFormat = NumericFormat('_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)')
