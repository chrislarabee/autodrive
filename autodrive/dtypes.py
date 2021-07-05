from __future__ import annotations


class _GoogleDtype(type):
    """
    Metaclass for the four data types used in Google Sheets.
    """

    python_type: type
    type_key: str

    def __str__(cls) -> str:
        return cls.type_key

    @classmethod
    def parse(cls, value: str) -> str:
        return cls.python_type(value)


class String(metaclass=_GoogleDtype):
    """
    String datatype, covers all non-numeric/date text that isn't a formula.
    """

    python_type = str
    type_key = "stringValue"

    @classmethod
    def parse(cls, value: str) -> str:
        """
        Converts a string into a string.

        :param value: Any string.
        :type value: str
        :return: The passed value as a string.
        :rtype: str
        """
        return cls.python_type(value)


class Formula(metaclass=_GoogleDtype):
    """
    Formula datatype, essentially a string, but begins with =.
    """

    python_type = str
    type_key = "formulaValue"

    @classmethod
    def parse(cls, value: str) -> str:
        """
        Converts a string into a formula (string).

        :param value: Any string.
        :type value: str
        :return: The passed value as a string.
        :rtype: str
        """
        return cls.python_type(value)


class Number(metaclass=_GoogleDtype):
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

        :param value: Any numeric string.
        :type value: str
        :return: The passed value as an integer or float.
        :rtype: float | int
        """
        if value.isnumeric():
            return int(value)
        else:
            return cls.python_type(value)


class Boolean(metaclass=_GoogleDtype):
    """
    Boolean datatype, appears in Google Sheets as FALSE or TRUE.
    """

    python_type = bool
    type_key = "boolValue"

    @classmethod
    def parse(cls, value: str) -> bool:
        """
        Converts a string into a boolean.

        :param value: Any string.
        :type value: str
        :return: False if the string is some variation of FALSE, otherwise True for
            all other strings.
        :rtype: bool
        """
        if value.lower() == "false":
            return False
        else:
            return True


class _GoogleValueType(type):
    """
    Metaclass for the three different ways values are stored in Google Sheets.
    """

    value_key: str
    has_dtype: bool = True

    def __str__(cls) -> str:
        return cls.value_key


class UserEnteredVal(metaclass=_GoogleValueType):
    """
    UserEnteredVal is the value as entered by the user, without any calculations
    applied to it. It is always a string, but is accompanied by metadata that
    indicates what datatype the value is.
    """

    value_key = "userEnteredValue"


class EffectiveVal(metaclass=_GoogleValueType):
    """
    EffectiveVal is the value as displayed in Google Sheets, and is appropriately
    typed when read from the api. So if the formula "=A1+A2" would equal 3, then
    the EffectiveVal of that cell is 3.
    """

    value_key = "effectiveValue"


class FormattedVal(metaclass=_GoogleValueType):
    """
    The untyped string value of the cell as displayed in Google Sheets. Essentially
    equivalent to EffectiveVal, but without appropriate typing.
    """

    value_key = "formattedValue"
    has_dtype = False


GOOGLE_VAL_TYPES = (UserEnteredVal, EffectiveVal, FormattedVal)
GOOGLE_DTYPES = (String, Formula, Number, Boolean)
TYPE_MAP = {
    str: String,
    int: Number,
    float: Number,
    bool: Boolean,
}
REV_TYPE_MAP = {
    String: String.python_type,
    Formula: Formula.python_type,
    Number: Number.python_type,
    Boolean: Boolean.python_type,
}


class _GoogleFormatType(type):
    """
    Metaclass for the three different ways format information is stored in
    Google Sheets.
    """

    format_key: str

    def __str__(cls) -> str:
        return cls.format_key


class UserEnteredFmt(metaclass=_GoogleFormatType):
    """
    The formatting properties the user as applied to the cell.
    """

    format_key = "userEnteredFormat"


class EffectiveFmt(metaclass=_GoogleFormatType):
    """
    The final dictionary of formatting information about a cell and its values,
    includes the effects of conditional formatting and the like.
    """

    format_key = "effectiveFormat"


class DefaultFmt(metaclass=_GoogleFormatType):
    """
    The default formatting properties of a cell, dictated by the settings of the
    tab.
    """

    format_key = "defaultFormat"
