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
        """
        Optional custom configuration for Autodrive's authentication processes using
        your Google api credentials.

        :param secrets_config: The dictionary of configuration used by a
            google.oath2.credentials Credentials object. Generally only useful if
            for some reason you are reading in your own token file, defaults to None.
        :type secrets_config: Dict[str, Any], optional
        :param token_filepath: The filepath to your gdrive_token pickle file. This
            doesn't have to exist at time of authentication, and will be saved to
            this path when the authorization flow completes, defaults to DEFAULT_TOKEN,
            which is "gdrive_token.pickle" in your cwd.
        :type token_filepath: str, optional
        :param creds_filepath: The filepath to your api credentials json file. This
            file *does* need to exist at time of authentication, unless you pass a
            secrets_config dictionary, defaults to DEFAULT_CREDS, which is
            "credentials.json" from your cwd.
        :type creds_filepath: str, optional
        """
        self.secrets_config = secrets_config
        self._token_filepath = Path(token_filepath)
        self._creds_filepath = Path(creds_filepath)

    @property
    def token_filepath(self) -> Path:
        """
        :return: The Path to your token pickle file.
        :rtype: Path
        """
        return self._token_filepath

    @property
    def creds_filepath(self) -> Path:
        """
        :return: The Path to your credentials json file.
        :rtype: Path
        """
        return self._creds_filepath


class _Interface(Mapping[str, T]):
    """
    Base class for all Interfaces.
    """

    def to_dict(self) -> Dict[str, T]:
        return {}

    def __iter__(self) -> Iterator[str]:
        return iter(self.to_dict())

    def __getitem__(self, k: str) -> T:
        return self.to_dict()[k]

    def __len__(self) -> int:
        return len(self.to_dict())


class _RangeInterface(_Interface[int]):
    """
    Underlying class for OneD and TwoD Range Interfaces.
    """

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
        """
        Reconstructs a standardized range string (Sheet1!A1:B3) from the passed
        properties.

        :param start_row: 0-based row index for the first row in the range, defaults
            to 0.
        :type start_row: Optional[int], optional
        :param end_row: 0-based row index for the row after the range, defaults to
            None.
        :type end_row: Optional[int], optional
        :param start_col: 0-based column index for the first column in the range,
            defaults to 0.
        :type start_col: Optional[int], optional
        :param end_col: 0-based column index for the column after the range, defaults
            to 0.
        :type end_col: Optional[int], optional
        :return: A string in the format (tab_name!start_cell:end_cell)
        :rtype: str
        """
        start_letter = ""
        end_letter = ""
        start_letter = cls._convert_col_idx_to_alpha(start_col or 0)
        end_letter = cls._convert_col_idx_to_alpha(end_col - 1 if end_col else 0)
        start_int = (start_row or 0) + 1
        end_int = end_row if end_row is not None else None
        return f"{start_letter}{start_int}:{end_letter}{end_int or ''}"

    @staticmethod
    def _parse_range_str(rng: str) -> Tuple[Optional[str], str, Optional[str]]:
        """
        Parses a range string (Sheet1:A1:B3) into its component groups ("Sheet1",
        "A1", "B3").

        :param rng: The range string, which must at least be one cell coordinate (A1),
            which will be returned as the start cell.
        :type rng: str
        :raises ParseRangeError: If the range is invalid.
        :return: The sheet title (if present), a start cell, and an end cell (if
            present).
        :rtype: Tuple[Optional[str], str, Optional[str]]
        """
        result = re.match(r"(?:(.*)!)?([A-Z]+\d+?)(?::([A-Z]*\d*))?", rng)
        if result:
            grps = result.groups()
            return grps  # type: ignore
        else:
            raise ParseRangeError(rng)

    @staticmethod
    def _parse_cell_str(cell_str: str) -> Tuple[str, Optional[str]]:
        """
        Parses an individual cell string (A1) into its component strings ("A", "1")

        :param cell_str: The cell string, which must at least have a column letter.
        :type cell_str: str
        :raises ParseRangeError: If the range is invalid.
        :return: The column letter and the row number.
        :rtype: Tuple[str, Optional[str]]
        """
        result = re.match(r"([A-Z]+)(\d+)?", cell_str)
        if result:
            grps = result.groups()
            return grps  # type: ignore
        else:
            raise ParseRangeError(cell_str)

    @classmethod
    def _convert_cell_str_to_coord(cls, cell_str: str) -> Tuple[int, Optional[int]]:
        """
        Parses the passed cell string (A1) and returns its numeric (0-based) indices
        (0, 0)

        :param cell_str: The cell string.
        :type cell_str: str
        :return: The column index and the row index (if present).
        :rtype: Tuple[int, Optional[int]]
        """
        col, row = cls._parse_cell_str(cell_str)
        col_idx = cls._convert_alpha_col_to_idx(col)
        row_idx = int(row) - 1 if row else None
        return col_idx, row_idx

    @staticmethod
    def _convert_alpha_col_to_idx(alpha_col: str) -> int:
        """
        Converts a string column identifier (A, B, C, ...Z, AA, AAA, etc) into a
        (0 based) numeric index.

        :param alpha_col: A letter or set of letters.
        :type alpha_col: str
        :return: The numeric representation of the alpha_col's index.
        :rtype: int
        """
        values: List[int] = []
        for i, a in enumerate(alpha_col, start=1):  # type: ignore
            base_idx = string.ascii_uppercase.index(a) + 1  # type: ignore
            remainder = len(alpha_col[i:])
            values.append(26 ** remainder * base_idx)
        return sum(values) - 1

    @staticmethod
    def _convert_col_idx_to_alpha(idx: int) -> str:
        """
        Converts a (0-based) index into a string column identifier.

        :param idx: A (0-based) index value.
        :type idx: int
        :return: The string representation of the idx's position.
        :rtype: str
        """
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
        """
        Extracted logic for standardizing OneD and TwoD start/end indices. Allows
        the end user to supply strings or integers as desired to the Ranges, and
        also allows them to use 0-based indices or not.


        :param idx: An index (optionally 0-based) or a string column representation,
            defaults to None.
        :type idx: str | int, optional
        :param base0_idxs: Set to True if passing 0-based indices, otherwise will
            assume it needs to adjust them. defaults to False
        :type base0_idxs: bool, optional
        :param mod: The value by which to adjust non-0-based indices, defaults to 1.
        :type mod: int, optional
        :return: A 0-based numeric representation of the passed index.
        :rtype: Optional[int]
        """
        adj = 0 if base0_idxs else mod
        result = None
        if isinstance(idx, str):
            result = cls._convert_alpha_col_to_idx(idx)
        elif idx is not None:
            result = idx + adj
        return result


class OneDRange(_RangeInterface):
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
        """
        A one-dimensional range (i.e. a range with only one axis, like a row range
        or a column range).

        :param tab_id: The tab id this range resides in.
        :type tab_id: int
        :param start_idx: The first column/row in the range, assumed to not be 0-based
            if it's an integer (row), defaults to None.
        :type start_idx: str | int, optional
        :param end_idx: The last column/row in the range, assumed to not be
            0-based if it's an integer (row), defaults to None.
        :type end_idx: str | int, optional
        :param tab_title: The name of the tab this range resides in, defaults to None.
        :type tab_title: str, optional
        :param base0_idxs: Set to True if you'd like to pass 0-based indices to
            start_idx and end_idx params, above, defaults to False.
        :type base0_idxs: bool, optional
        :param column: Set to True if this OneDRange is a column range and you supplied
            the column indexes as integers, defaults to False.
        :type column: bool, optional
        """
        super().__init__(tab_id, tab_title)
        self.start_idx = self._parse_idx(start_idx, base0_idxs, -1)
        self.end_idx = self._parse_idx(end_idx, base0_idxs)
        self.column = column
        if isinstance(start_idx, str):
            self.column = True
        if self.column and self.end_idx and not base0_idxs:
            self.end_idx += 1

    def to_dict(self) -> Dict[str, int]:
        """
        :return: Outputs the OneDRange as a dictionary of properties usable in
            generating an api request to affect the target range of cells.
        :rtype: Dict[str, int]
        """
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
        """
        :return: The start_idx. Used to make OneDRanges and TwoDRanges
            interchangeable.
        :rtype: int
        """
        return self.start_idx or 0

    @property
    def end_row(self) -> int:
        """
        :return: The end_idx. Used to make OneDRanges and TwoDRanges
            interchangeable.
        :rtype: int
        """
        return self.end_idx + 1 if self.end_idx else 0

    @property
    def start_col(self) -> int:
        """
        :return: The start_idx. Used to make OneDRanges and TwoDRanges
            interchangeable.
        :rtype: int
        """
        return self.start_idx or 0

    @property
    def end_col(self) -> int:
        """
        :return: The end_idx. Used to make OneDRanges and TwoDRanges
            interchangeable.
        :rtype: int
        """
        return self.end_idx + 1 if self.end_idx else 0


class TwoDRange(_RangeInterface):
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
        """
        A two-dimensional range (i.e. a range with two axes).

        :param tab_id: The tab id this range resides in.
        :type tab_id: int
        :param start_row: The first row in the range, assumed to not be 0-based,
            defaults to None
        :type start_row: int, optional
        :param end_row: The last row in the range, assumed to not be 0-based,
            defaults to None
        :type end_row: int, optional
        :param start_col: The first column in the range, assumed to not be 0-based
            if it's an integer, defaults to None
        :type start_col: int | str, optional
        :param end_col: The last column in the range, assumed to not be 0-based if
            it's an integer, defaults to None
        :type end_col: int | str, optional
        :param range_str: A range string (e.g. Sheet1!A1:B3), which can be passed
            instead of specifying the start/end_row and start/end_col, defaults to
            None.
        :type range_str: str, optional
        :param base0_idxs: Set to True if you'd like to pass 0-based indices to
            start/end_row and start/end_col, defaults to False.
        :type base0_idxs: bool, optional
        :param tab_title: The name of the tab this range resides in, defaults to None
        :type tab_title: str, optional
        """
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
        """
        :return: The TwoDRange's row range as a OneDRange.
        :rtype: OneDRange
        """
        return OneDRange(
            self.tab_id,
            self.start_row,
            self.end_row,
            tab_title=self.tab_title,
            base0_idxs=True,
        )

    @property
    def col_range(self) -> OneDRange:
        """
        :return: The TwoDRange's column range as a OneDRange.
        :rtype: OneDRange
        """
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
        """
        :return: Outputs the TwoDRange as a dictionary of properties usable in
            generating an api request to affect the target range of cells.
        :rtype: Dict[str, int]
        """
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


NT = TypeVar("NT", int, float)


class Color(_Interface[float]):
    def __init__(
        self,
        red: int | float = 0,
        green: int | float = 0,
        blue: int | float = 0,
        alpha: int | float = 100,
    ) -> None:
        """
        An RGBA color value.

        :param red: Either an integer from 0 to 255 (from which a float value will
            be calculated), or the float representation of same. defaults to 0
        :type red: int | float, optional
        :param green: Either an integer from 0 to 255 (from which a float value will
            be calculated), or the float representation of same. defaults to 0
        :type green: int | float, optional
        :param blue: Either an integer from 0 to 255 (from which a float value will
            be calculated), or the float representation of same. defaults to 0
        :type blue: int | float, optional
        :param alpha: Either an integer from 0 to 100 (from which a float value will
            be calculated), or the float representation of same. defaults to 100
        :type alpha: int, optional
        """
        self.red = red if isinstance(red, float) else red / 255
        self.green = green if isinstance(green, float) else green / 255
        self.blue = blue if isinstance(blue, float) else blue / 255
        self.alpha = alpha if isinstance(alpha, float) else alpha / 100

    @staticmethod
    def _ensure_valid_input(input: NT) -> NT:
        return input

    def to_dict(self) -> Dict[str, float]:
        """
        :return: Outputs the Color as a dictionary of properties usable in generating
            an api request to affect the color of text or cell background.
        :rtype: Dict[str, float]
        """
        return {
            "red": self.red,
            "green": self.green,
            "blue": self.blue,
            "alpha": self.alpha,
        }


class _Format(_Interface[Any]):
    def __init__(self, format_key: str) -> None:
        """
        Underlying class for text/number formats.

        :param format_key: The format key as dictated by the Google Sheets api.
        :type format_key: str
        """
        self._format_key = format_key

    @property
    def format_key(self) -> str:
        """
        :return: The format's Google Sheets api key, used to generate the
            userEnteredFormat value.
        :rtype: str
        """
        return self._format_key

    def __str__(self) -> str:
        return f"userEnteredFormat({self._format_key})"

    def _fmt_contents(self) -> Dict[str, Any]:
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """
        :return: Outputs the Format as a dictionary of properties usable in generating
            an api request to affect the text/number format of one or more cells.
        :rtype: Dict[str, Any]
        """
        result = self._fmt_contents()
        return {"userEnteredFormat": {self._format_key: result}}


class TextFormat(_Format):
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
        """
        Available parameters available in updating the text formatting of a cell.

        :param font: The name of a font to change to, defaults to None.
        :type font: str, optional
        :param color: The Color properties to apply to the text, defaults to None
        :type color: Color, optional
        :param font_size: The size to apply to the text, defaults to None
        :type font_size: int, optional
        :param bold: Whether to turn bold on (True) or off (False),
            defaults to None, for unchanged.
        :type bold: bool, optional
        :param italic: Whether to turn italic on (True) or off (False),
            defaults to None, for unchanged.
        :type italic: bool, optional
        :param underline: Whether to turn underline on (True) or off (False),
            defaults to None, for unchanged.
        :type underline: bool, optional
        :param strikethrough: Whether to turn strikethrough on (True) or off (False),
            defaults to None, for unchanged.
        :type strikethrough: bool, optional
        """
        super().__init__("textFormat")
        self.font = font
        self.color = color
        self.font_size = font_size
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough

    def _fmt_contents(self) -> Dict[str, bool | str | int | Dict[str, float]]:
        """
        :return: The TextFormat as a request-ready dictionary.
        :rtype: Dict[str, bool | str | int | Dict[str, float]]
        """
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


class NumericFormat(_Format):
    def __init__(self, pattern: str = "") -> None:
        """
        A Google Sheet Number Format, which the value of the cell(s) will be
        parsed into.

        :param pattern: The name of a Google Sheet Number Format, defaults to "".
        :type pattern: str, optional
        """
        super().__init__("numberFormat")
        self.type = "NUMBER"
        self.pattern = pattern

    def _fmt_contents(self) -> Dict[str, str]:
        """
        :return: The NumericFormat as a request-ready dictionary.
        :rtype: Dict[str, str]
        """
        return {"type": self.type, "pattern": self.pattern}


StdNumericFormat = NumericFormat()
AccountingFormat = NumericFormat('_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)')
