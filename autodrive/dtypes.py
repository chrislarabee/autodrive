from __future__ import annotations

from ._core import GoogleDtype, GoogleValueType, GoogleFormatType


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
