from __future__ import annotations

import re
import string
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Optional, Tuple, TypeVar

from .dtypes import UserEnteredFmt, BorderStyle, BorderSide, BorderSolid
from . import _google_terms as terms

DEFAULT_TOKEN = "gdrive_token.json"
"""Filepath for the token json file. Default="gdrive_token.json". """
DEFAULT_CREDS = "credentials.json"
"""Filepath for the credentials json file. Default="credentials.json" """


_T = TypeVar("_T")


class ParseRangeError(Exception):
    """
    Error raised when an invalid range string is passed to a FullRange.
    """

    def __init__(self, rng: str, msg_addon: str | None = None, *args: object) -> None:
        """
        Args:
            rng (str): The original range string.
            msg_addon (str, optional): An addendum to the error message. Defaults to
                None.
        """
        msg = f"{rng} is not a valid range.{' ' + msg_addon if msg_addon else ''}"
        super().__init__(msg, *args)


class AuthConfig:
    """
    Optional custom configuration for Autodrive's authentication processes using
    your Google api credentials.
    """

    def __init__(
        self,
        secrets_config: Dict[str, Any] | None = None,
        token_filepath: str | Path = DEFAULT_TOKEN,
        creds_filepath: str | Path = DEFAULT_CREDS,
    ) -> None:
        """
        Args:
            secrets_config (Dict[str, Any], optional): The dictionary of
                configuration used by a google.oath2.credentials Credentials
                object. Generally only useful if for some reason you are reading
                in your own token file, defaults to None.
            token_filepath (str | Path, optional): The filepath to your gdrive_token
                json file. This doesn't have to exist at time of authentication,
                and will be saved to this path when the authorization flow completes,
                defaults to DEFAULT_TOKEN, which is "gdrive_token.json" in your
                cwd.
            creds_filepath (str | Path, optional): The filepath to your api
                credentials json file. This file *does* need to exist at time of
                authentication, unless you pass a secrets_config dictionary,
                defaults to DEFAULT_CREDS, which is "credentials.json" from your
                cwd.

        """
        self.secrets_config = secrets_config
        self._token_filepath = Path(token_filepath)
        self._creds_filepath = Path(creds_filepath)

    @property
    def token_filepath(self) -> Path:
        """
        Returns:
            Path: The Path to your token json file.

        """
        return self._token_filepath

    @property
    def creds_filepath(self) -> Path:
        """
        Returns:
            Path: The Path to your credentials json file.

        """
        return self._creds_filepath


class _Interface(Mapping[str, _T]):
    """
    Base class for all Interfaces.
    """

    def to_dict(self) -> Dict[str, _T]:
        return {}

    def __iter__(self) -> Iterator[str]:
        return iter(self.to_dict())

    def __getitem__(self, k: str) -> _T:
        return self.to_dict()[k]

    def __len__(self) -> int:
        return len(self.to_dict())


class _RangeInterface(_Interface[int]):
    """
    Underlying class for HAlf and Full Range Interfaces.
    """

    def __init__(self, tab_title: str | None = None) -> None:
        self.tab_title = tab_title

    def to_dict(self) -> Dict[str, int]:
        return {}

    @classmethod
    def _construct_range_str(
        cls,
        start_row: int = 0,
        start_col: int = 0,
        end_row: Optional[int] = None,
        end_col: Optional[int] = None,
    ) -> str:
        """
        Reconstructs a standardized range string (Sheet1!A1:B3) from the passed
        properties.

        Args:
            start_row (int, optional): 0-based row index for the first
                row in the range, defaults to 0.
            start_col (int, optional): 0-based column index for the first
                column in the range, defaults to 0.
            end_row (int, optional): 0-based row index for the row after
                the range, defaults to None.
            end_col (int, optional): 0-based column index for the column
                after the range, defaults to None.

        Returns:
            str: A string in the format (tab_name!start_cell:end_cell)

        """
        start_letter = ""
        end_letter = ""
        end_row_int = end_row + 1 if end_row else end_row
        end_col_int = end_col if end_col is not None else start_col
        start_letter = cls._convert_col_idx_to_alpha(start_col)
        end_letter = cls._convert_col_idx_to_alpha(end_col_int)
        start_int = start_row + 1
        if end_col or end_row:
            end_part = f":{end_letter}{end_row_int or ''}"
        else:
            end_part = ""
        return f"{start_letter}{start_int}{end_part}"

    @staticmethod
    def _parse_range_str(rng: str) -> Tuple[Optional[str], str, Optional[str]]:
        """
        Parses a range string (Sheet1:A1:B3) into its component groups ("Sheet1",
        "A1", "B3").

        Args:
            rng (str): The range string, which must at least be one cell coordinate
                (e.g. A1), which will be returned as the start cell.

        Returns:
            Tuple[Optional[str], str, Optional[str]]: The sheet title (if present),
                a start cell, and an end cell (if present).

        Raises:
            ParseRangeError: If the range is invalid.

        """
        result = re.match(r"(?:(.*)!)?([A-Z]+\d+)(?::([A-Z]*\d*))?", rng)
        if result:
            grps = result.groups()
            return grps  # type: ignore
        else:
            raise ParseRangeError(rng)

    @staticmethod
    def _parse_cell_str(cell_str: str) -> Tuple[str, Optional[str]]:
        """
        Parses an individual cell string (A1) into its component strings ("A", "1")

        Args:
            cell_str (str: str): The cell string, which must at least have a
                column letter.

        Returns:
            Tuple[str, Optional[str]]: The column letter and the row number.

        Raises:
            ParseRangeError: If the range is invalid.

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
        Parses the passed cell string (e.g. A1) and returns its numeric (0-based)
        indices (e.g. 0, 0)

        Args:
            cell_str (str): The cell string.

        Returns:
            Tuple[int, Optional[int]]: The column index and the row index (if
            present).

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

        Args:
            alpha_col (str): A letter or set of letters.

        Returns:
            int: The numeric representation of the alpha_col's index.

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

        Args:
            idx (int): A (0-based) index value.

        Returns:
            str: The string representation of the idx's position.

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
    def _parse_idx(cls, idx: str | int, base0_idxs: bool = False) -> int:
        """
        Extracted logic for standardizing Half and Full start/end indices. Allows
        the end user to supply strings or integers as desired to the Ranges, and
        also allows them to use 0-based indices or not.

        Args:
            idx (str | int): An index (optionally 0-based) or a string
                column representation.
            base0_idxs (bool, optional): Set to True if passing 0-based indices,
                otherwise will assume it needs to adjust them. defaults to False.
            mod (int, optional): The value by which to adjust non-0-based indices,
                defaults to 1.

        Returns:
            Optional[int]: A 0-based numeric representation of the passed index.

        """
        adj = 0 if base0_idxs else -1
        if isinstance(idx, str):
            result = cls._convert_alpha_col_to_idx(idx)
        else:
            result = idx + adj
        return result


class HalfRange(_RangeInterface):
    """
    A partial range used in requests to the Google Sheets API when the axis of the
    range is obvious from context (such as when inserting rows or columns).

    Note that HalfRange parses your inputs into Google Sheets API row/column
    indices, which are 0-based, so if you call :attr:`start_idx` or :attr:`end_idx`
    expect them to be 1 lower than the value you passed.
    """

    def __init__(
        self,
        start_idx: str | int | None = None,
        end_idx: str | int | None = None,
        *,
        tab_title: str | None = None,
        base0_idxs: bool = False,
        column: bool = False,
    ) -> None:
        """

        Args:
            start_idx (str | int, optional): The first column/row in the range,
                assumed to not be 0-based if it's an integer (row), defaults to
                None.
            end_idx (str | int, optional): The last column/row in the range,
                assumed to not be 0-based if it's an integer (row), defaults to
                None.
            tab_title (str, optional): The name of the tab this range resides in,
                defaults to None.
            base0_idxs (bool, optional): Set to True if you'd like to pass 0-based
                indices to start_idx and end_idx params, above, defaults to False.
            column (bool, optional): Set to True if this HalfRange is a column range
                and you supplied the column indexes as integers, defaults to False.

        """
        super().__init__(tab_title)
        if start_idx is not None:
            self.start_idx = self._parse_idx(start_idx, base0_idxs)
        elif end_idx is not None:
            self.start_idx = 0
        if end_idx is not None:
            self.end_idx = self._parse_idx(end_idx, base0_idxs) if end_idx else None
        elif self.start_idx is not None:
            self.end_idx = self.start_idx
        self.column = column
        if isinstance(start_idx, str) or isinstance(end_idx, str):
            self.column = True

    def to_dict(self) -> Dict[str, int]:
        """
        The Google Sheets api ranges are end-value exclusive, so this method will
        produce a dictionary with an endIndex value 1 higher than the FullRange's
        attribute.

        Returns:
            Dict[str, int]: Outputs the HalfRange as a dictionary of properties
            usable in generating an api request to affect the target range of cells.

        """
        result: Dict[str, int] = {}
        # All of these must be is not None because any of them can be 0:
        if self.start_idx is not None:
            result[terms.STARTIDX] = self.start_idx
        if self.end_idx is not None:
            result[terms.ENDIDX] = self.end_idx + 1
        return result

    def __str__(self) -> str:
        if self.column:
            rng = self._construct_range_str(
                start_col=self.start_idx, end_col=self.end_idx
            )
        else:
            raise AttributeError(
                f"{self}.column indicator is False. Cannot convert row HalfRanges to "
                "strings."
            )
        return f"{self.tab_title or ''}{'!' if self.tab_title else ''}{rng}"

    # @property
    # def start_row(self) -> int:
    #     """
    #     Returns:
    #         int: The start_idx. Used to make HalfRanges and FullRanges
    #         interchangeable.

    #     """
    #     return self.start_idx or 0

    # @property
    # def end_row(self) -> int:
    #     """
    #     Returns:
    #         int: The end_idx. Used to make HalfRanges and FullRanges
    #         interchangeable.

    #     """
    #     return self.end_idx + 1 if self.end_idx else 0

    # @property
    # def start_col(self) -> int:
    #     """
    #     Returns:
    #         int: The start_idx. Used to make HalfRanges and FullRanges
    #         interchangeable.

    #     """
    #     return self.start_idx or 0

    # @property
    # def end_col(self) -> int:
    #     """
    #     Returns:
    #         int: The end_idx. Used to make HalfRanges and FullRanges
    #         interchangeable.

    #     """
    #     return self.end_idx + 1 if self.end_idx else 0


class FullRange(_RangeInterface):
    """
    A complete Google Sheets range (indicating start and end row and column as
    well as at least an end column, if not an end row).

    Note that FullRange parses your inputs into Google Sheets API row/column
    indices, which are 0-based, so if you call :attr:`start_row`, :attr:`end_row`,
    :attr:`start_col`, or :attr:`end_col`, expect them to be 1 lower than the
    value you passed.
    """

    def __init__(
        self,
        range_str: str | None = None,
        *,
        start_row: int | None = None,
        end_row: int | None = None,
        start_col: int | str | None = None,
        end_col: int | str | None = None,
        base0_idxs: bool = False,
        tab_title: str | None = None,
    ) -> None:
        """

        Args:
            range_str (str, optional): A range string (e.g. Sheet1!A1:B3, A1:B3, A1).
            start_row (int, optional): The first row in the range, assumed to not
                be 0-based, defaults to None.
            end_row (int, optional): The last row in the range, assumed to not be
                0-based, defaults to None.
            start_col (int | str, optional): The first column in the range, assumed
                to not be 0-based if it's an integer, defaults to None.
            end_col (int | str, optional): The last column in the range, assumed to
                not be 0-based if it's an integer, defaults to None.
            base0_idxs (bool, optional): Set to True if you'd like to pass 0-based
                indices to start/end_row and start/end_col, defaults to False.
            tab_title (str, optional): The name of the tab this range resides in,
                defaults to None.

        """
        super().__init__(tab_title)
        self._single_cell = False
        if range_str:
            title, start, end = self._parse_range_str(range_str)
            if title and not self.tab_title:
                self.tab_title = title
            cstart, rstart = self._convert_cell_str_to_coord(start)
            if rstart is None:
                raise ParseRangeError(range_str)
            if end:
                cend, rend = self._convert_cell_str_to_coord(end)
            else:
                cend = cstart + 1
                rend = rstart + 1
                self._single_cell = True
            self.start_row = rstart
            self.end_row = rend
            self.start_col = cstart
            self.end_col = cend
        else:
            self.start_row = self._parse_idx(start_row, base0_idxs) if start_row else 0
            self.start_col = self._parse_idx(start_col, base0_idxs) if start_col else 0
            if end_row is None:
                self.end_row = self.start_row
            else:
                self.end_row = self._parse_idx(end_row, base0_idxs)
            if end_col is None:
                self.end_col = self.start_col
            else:
                self.end_col = self._parse_idx(end_col, base0_idxs)
            if end_row is None and end_col is None:
                self._single_cell = True

    @property
    def row_range(self) -> HalfRange:
        """
        Returns:
            HalfRange: The FullRange's row range as a HalfRange.

        """
        return HalfRange(
            self.start_row,
            self.end_row,
            tab_title=self.tab_title,
            base0_idxs=True,
        )

    @property
    def col_range(self) -> HalfRange:
        """
        Returns:
            HalfRange: The FullRange's column range as a HalfRange.

        """
        return HalfRange(
            self.start_col,
            self.end_col,
            tab_title=self.tab_title,
            base0_idxs=True,
            column=True,
        )

    def __str__(self) -> str:
        if self._single_cell:
            rng = self._construct_range_str(self.start_row, self.start_col)
        else:
            rng = self._construct_range_str(
                self.start_row, self.start_col, self.end_row, self.end_col
            )
        return f"{self.tab_title or ''}{'!' if self.tab_title else ''}{rng}"

    def to_dict(self) -> Dict[str, int]:
        """
        The Google Sheets api ranges are end-value exclusive, so this method will
        produce a dictionary with endRowIndex and endColumnIndex values 1 higher
        than the FullRange's attribute.

        Returns:
            Dict[str, int]: Outputs the FullRange as a dictionary of properties
            usable in generating an api request to affect the target range of cells.

        """
        result: Dict[str, int] = {}
        # All of these must be is not None because any of them can be 0:
        if self.start_row is not None:
            result[terms.STARTROW] = self.start_row
        if self.end_row is not None:
            result[terms.ENDROW] = self.end_row + 1
        if self.start_col is not None:
            result[terms.STARTCOL] = self.start_col
        if self.end_col is not None:
            result[terms.ENDCOL] = self.end_col + 1
        return result


class BorderFormat(_Interface[Any]):
    """
    The settings for the border of a single side of a cell.
    """

    def __init__(
        self,
        side: BorderSide,
        color: Color | None = None,
        style: BorderStyle | None = None,
    ) -> None:
        """

        Args:
            side (BorderSide): The BorderSide to apply settings to.
            color (Color, optional): The color of the side of the border.
                Defaults to None, for a black border.
            style (BorderStyle, optional): The BorderStyle of the side of the
                border. Defaults to None, for the default border style.
        """
        self.side = side
        self.color = color if color else Color(0, 0, 0)
        self.style = style if style else BorderSolid

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns:
            Dict[str, Any]: Outputs the BorderFormat as a dictionary of properties
            usable in generating an api request to affect cell border properties.

        """
        return {
            str(self.side): {
                "color": dict(self.color),
                "style": str(self.style),
            }
        }


class Color(_Interface[float]):
    """
    An RGBA color value.
    """

    def __init__(
        self,
        red: int | float = 0,
        green: int | float = 0,
        blue: int | float = 0,
        alpha: int | float = 100,
    ) -> None:
        """

        Args:
            red (int | float, optional): Either an integer from 0 to 255 (from
                which a float value will be calculated), or the float representation
                of same. defaults to 0.
            green (int | float, optional): Either an integer from 0 to 255 (from
                which a float value will be calculated), or the float representation
                of same. defaults to 0.
            blue (int | float, optional): Either an integer from 0 to 255 (from
                which a float value will be calculated), or the float representation
                of same. defaults to 0.
            alpha (int, optional): Either an integer from 0 to 100 (from which a
                float value will be calculated), or the float representation of
                same. defaults to 100.

        """
        self.red = self._ensure_valid_input(red, 255)
        self.green = self._ensure_valid_input(green, 255)
        self.blue = self._ensure_valid_input(blue, 255)
        self.alpha = self._ensure_valid_input(alpha, 100)

    @staticmethod
    def _ensure_valid_input(input: int | float, intmax: int = 100) -> float:
        """
        Ensures the passed input is between 0 and 1, or the passed maximum int
        value if input is an integer. Any value below 0 will be set to 0, and
        any value above 1 or the intmax will be set to 1 or the intmax.

        Args:
            input (int | float): Any integer or float.
            intmax (int, optional): Maximum allowed value of integers. Defaults
                to 100.

        Returns:
            float: A float representation of the input. Integers will be divided
                by the intmax to calculate the return value.
        """
        if input < 0:
            input = 0
        elif isinstance(input, float):
            if input > 1:
                input = 1.0
        else:
            if input > intmax:
                input = intmax
            input = input / intmax
        return input

    def to_dict(self) -> Dict[str, float]:
        """
        Returns:
            Dict[str, float]: Outputs the Color as a dictionary of properties
            usable in generating an api request to affect the color of text or
            cell background.

        """
        return {
            "red": self.red,
            "green": self.green,
            "blue": self.blue,
            "alpha": self.alpha,
        }

    @classmethod
    def from_hex(cls, hex_code: str, alpha: int | float = 100) -> Color:
        """
        Instantiates a Color object from the supplied hex code.

        Args:
            hex_code (str): A hexadecimal color code.
            alpha (int | float, optional): Optional alpha parameter (not included in hex
                codes). Defaults to 100.

        Returns:
            Color: The new Color object.
        """
        hex_code = hex_code.replace("#", "")
        r, g, b = tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))
        return Color(r, g, b, alpha)


class Format(_Interface[Any]):
    """
    Underlying class for text/number formats.
    """

    def __init__(self, format_key: str) -> None:
        """
        Args:
            format_key (str): The format key as dictated by the Google Sheets api.

        """
        self._format_key = format_key

    @property
    def format_key(self) -> str:
        """
        Returns:
            str: The format's Google Sheets api key, used to generate the
            userEnteredFormat value.

        """
        return self._format_key

    def __str__(self) -> str:
        return f"{UserEnteredFmt}({self._format_key})"

    def _fmt_contents(self) -> Dict[str, Any]:
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns:
            Dict[str, Any]: Outputs the Format as a dictionary of properties
            usable in generating an api request to affect the text/number format
            of one or more cells.

        """
        result = self._fmt_contents()
        return {str(UserEnteredFmt): {self._format_key: result}}


class TextFormat(Format):
    """
    Provides parameters available in updating the text formatting of a cell.
    """

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
        Args:
            font (str, optional): The name of a font to change to, defaults to None.
            color (Color, optional): The Color properties to apply to the text,
                defaults to None.
            font_size (int, optional): The size to apply to the text, defaults to
                None.
            bold (bool, optional): Whether to turn bold on (True) or off (False),
                defaults to None, for unchanged.
            italic (bool, optional): Whether to turn italic on (True) or off (False),
                defaults to None, for unchanged.
            underline (bool, optional): Whether to turn underline on (True) or off
                (False), defaults to None, for unchanged.
            strikethrough (bool, optional): Whether to turn strikethrough on (True)
                or off (False), defaults to None, for unchanged.

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
        Returns:
            Dict[str, bool | str | int | Dict[str, float]]: The TextFormat as a
            request-ready dictionary.

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


# TODO: Add AlignmentFormat?


class NumericFormat(Format):
    """
    A Google Sheet Number Format, which the value of the cell (s) will be parsed
    into.
    """

    def __init__(self, pattern: str = "") -> None:
        """
        Args:
            pattern (str, optional): A pattern valid as a Google Sheet Number
                Format, defaults to "", for automatic number format.

        """
        super().__init__("numberFormat")
        self.type = "NUMBER"
        self.pattern = pattern

    def _fmt_contents(self) -> Dict[str, str]:
        """
        Returns:
            Dict[str, str]: The NumericFormat as a request-ready dictionary.

        """
        return {"type": self.type, "pattern": self.pattern}


AutomaticFormat = NumericFormat()
"""Corresponds to the Automatic ``1000.12`` format."""

NumberFormat = NumericFormat("#,##0.00")
"""Corresponds to the Number ``1,000.12`` format."""

AccountingFormat = NumericFormat('_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)')
"""Corresponds to the Accounting ``$ (1,000.12)`` format."""

PercentFormat = NumericFormat("0.00%")
"""Corresponds to the Percent ``10.12%`` format."""

ScientificFormat = NumericFormat("0.00E+00")
"""Corresponds to the Scientific ``1.01E+03`` format."""

FinancialFormat = NumericFormat("#,##0.00;(#,##0.00)")
"""Corresponds to the Financial ``(1,000.12)`` format."""

CurrencyFormat = NumericFormat('"$"#,##0.00')
"""Corresponds to the Currency ``$1,000.12`` format."""

CurRoundFormat = NumericFormat('"$"#,##0')
"""Corresponds to the Currency (rounded) ``$1,000`` format."""

DateFormat = NumericFormat("M/d/yyyy")
"""Corresponds to the Date ``9/26/2008`` format."""

TimeFormat = NumericFormat("h:mm:ss am/pm")
"""Corresponds to the Time ``3:59:00 PM`` format."""

DatetimeFormat = NumericFormat("M/d/yyyy H:mm:ss")
"""Corresponds to the Date time ``9/26/2008 15:59:00`` format."""

DurationFormat = NumericFormat("[h]:mm:ss")
"""Corresponds to the Duration ``24:01:00`` format."""
