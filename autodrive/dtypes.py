from __future__ import annotations

from ._core import GoogleDtype, GoogleFormatType


class String(metaclass=GoogleDtype):
    """
    String datatype, covers all non-numeric/date text that isn't a formula.
    """

    python_type = str
    type_key = "stringValue"

    @classmethod
    def parse(cls, value: str) -> str:
        """
        Converts a string into a string.

        Args:
            value (str): Any string.

        Returns:
            str: The passed value as a string.

        """
        return cls.python_type(value)


class Formula(metaclass=GoogleDtype):
    """
    Formula datatype, essentially a string, but begins with =.
    """

    python_type = str
    type_key = "formulaValue"

    @classmethod
    def parse(cls, value: str) -> str:
        """
        Converts a string into a formula (string).

        Args:
            value (str): Any string.

        Returns:
            str: The passed value as a string.

        """
        return cls.python_type(value)


class Number(metaclass=GoogleDtype):
    """
    Number datatype, covers both floats and integers, though internally Number is
    treated as a float so as to not lose significant digits.
    """

    python_type = float
    type_key = "numberValue"

    @classmethod
    def parse(cls, value: str) -> float | int:
        """
        Converts a string into an integer (if it has no decimal point) or float.

        Args:
            value (str): Any numeric string.

        Returns:
            float | int: The passed value as an integer or float.

        """
        if value.isnumeric():
            return int(value)
        else:
            return cls.python_type(value)


class Boolean(metaclass=GoogleDtype):
    """
    Boolean datatype, appears in Google Sheets as FALSE or TRUE.
    """

    python_type = bool
    type_key = "boolValue"

    @classmethod
    def parse(cls, value: str) -> bool:
        """
        Converts a string into a boolean.

        Args:
            value (str): Any string.

        Returns:
            bool: False if the string is some variation of FALSE, otherwise True for
            all other strings.

        """
        if value.lower() == "false":
            return False
        else:
            return True


class GoogleValueType(type):
    """
    Metaclass for the three different ways values are stored in Google Sheets.
    """

    value_key: str
    """The API key for the GoogleValueType."""
    has_dtype: bool = True
    """Whether dtype information can be extracted from the GoogleValueType."""

    def __str__(cls) -> str:
        return cls.value_key


class UserEnteredVal(metaclass=GoogleValueType):
    """
    UserEnteredVal is the value as entered by the user, without any calculations
    applied to it. It is always a string, but is accompanied by metadata that
    indicates what datatype the value is.
    """

    value_key = "userEnteredValue"


class EffectiveVal(metaclass=GoogleValueType):
    """
    EffectiveVal is the value as displayed in Google Sheets, and is appropriately
    typed when read from the api. So if the formula "=A1+A2" would equal 3, then
    the EffectiveVal of that cell is 3.
    """

    value_key = "effectiveValue"


class FormattedVal(metaclass=GoogleValueType):
    """
    The untyped string value of the cell as displayed in Google Sheets. Essentially
    equivalent to EffectiveVal, but without appropriate typing.
    """

    value_key = "formattedValue"
    has_dtype = False


GOOGLE_VAL_TYPES = (UserEnteredVal, EffectiveVal, FormattedVal)
"""A tuple of UserEnteredVal, EffectiveVal, and FormattedVal google value types."""

GOOGLE_DTYPES = (String, Formula, Number, Boolean)
"""A tuple of String, Formula, Number, and Boolean google data types."""

TYPE_MAP = {
    str: String,
    int: Number,
    float: Number,
    bool: Boolean,
}
"""Dictionary mapping python data types to corresponding google data types."""

REV_TYPE_MAP = {
    String: String.python_type,
    Formula: Formula.python_type,
    Number: Number.python_type,
    Boolean: Boolean.python_type,
}
"""Dictionary mapping google data types to corresponding python types."""


class UserEnteredFmt(metaclass=GoogleFormatType):
    """
    The formatting properties the user as applied to the cell.
    """

    format_key = "userEnteredFormat"


class EffectiveFmt(metaclass=GoogleFormatType):
    """
    The final dictionary of formatting information about a cell and its values,
    includes the effects of conditional formatting and the like.
    """

    format_key = "effectiveFormat"


class DefaultFmt(metaclass=GoogleFormatType):
    """
    The default formatting properties of a cell, dictated by the settings of the
    tab.
    """

    format_key = "defaultFormat"


class _BorderProperty:
    """
    Abstract base class for the various border properties.
    """

    def __init__(self, format_str: str) -> None:
        self.format_str = format_str

    def __str__(self) -> str:
        return self.format_str


class BorderStyle(_BorderProperty):
    """
    An object describing the style of border to apply to part of a cell.
    """

    def __init__(self, style: str) -> None:
        """
        Args:
            style (str): The name of the style.
        """
        super().__init__(style)


BorderSolid = BorderStyle("SOLID")
"""The default border style, a thin, solid line."""

BorderSolidMedium = BorderStyle("SOLID_MEDIUM")
"""Same as BorderSolid, but slightly thicker."""

BorderSolidThick = BorderStyle("SOLID_THICK")
"""Same as BorderSolid, but much thicker."""

BorderDashed = BorderStyle("DASHED")
"""A thin line comprised of dashes."""

BorderDotted = BorderStyle("DOTTED")
"""A thin line comprised of dots."""

BorderDoubleLine = BorderStyle("DOUBLE")
"""A set of two parallel lines."""


class BorderSide(_BorderProperty):
    """
    An object describing which side of a cell to apply border properties to.
    """

    def __init__(self, side: str) -> None:
        """
        Args:
            side (str): The name of the side.
        """
        super().__init__(side)


BorderLeft = BorderSide("left")
"""The border for the left side of a cell."""

BorderRight = BorderSide("right")
"""The border for the right side of a cell."""

BorderTop = BorderSide("top")
"""The border for the top side of a cell."""

BorderBottom = BorderSide("bottom")
"""The border for the bottom side of a cell."""

BorderSides = (BorderLeft, BorderRight, BorderTop, BorderBottom)
"""Convenience reference for all BorderSide objects."""
