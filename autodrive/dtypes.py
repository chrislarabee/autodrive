from __future__ import annotations


class GoogleDtype(type):
    python_type: type
    type_key: str

    def __str__(cls) -> str:
        return cls.type_key


class String(metaclass=GoogleDtype):
    python_type = str
    type_key = "stringValue"

    @classmethod
    def parse(cls, value: str) -> str:
        return cls.python_type(value)


class Formula(metaclass=GoogleDtype):
    python_type = str
    type_key = "formulaValue"

    @classmethod
    def parse(cls, value: str) -> str:
        return cls.python_type(value)


class Number(metaclass=GoogleDtype):
    python_type = float
    type_key = "numberValue"

    @classmethod
    def parse(cls, value: str) -> float | int:
        if value.isnumeric():
            return int(value)
        else:
            return cls.python_type(value)


class Boolean(metaclass=GoogleDtype):
    python_type = bool
    type_key = "boolValue"

    @classmethod
    def parse(cls, value: str) -> bool:
        if value.lower() == "false":
            return False
        else:
            return True


class GoogleValueType(type):
    value_key: str
    has_dtype: bool = True

    def __str__(cls) -> str:
        return cls.value_key


class UserEnteredVal(metaclass=GoogleValueType):
    value_key = "userEnteredValue"


class EffectiveVal(metaclass=GoogleValueType):
    value_key = "effectiveValue"


class FormattedVal(metaclass=GoogleValueType):
    value_key = "formattedValue"
    has_dtype = False


GOOGLE_VAL_TYPES = (UserEnteredVal, EffectiveVal, FormattedVal)
GOOGLE_DTYPES = (String, Formula, Number, Boolean)
TYPE_MAP = {
    String: String.python_type,
    Formula: Formula.python_type,
    Number: Number.python_type,
    Boolean: Boolean.python_type,
    str: String,
    int: Number,
    float: Number,
    bool: Boolean,
}


class GoogleFormatType(type):
    format_key: str

    def __str__(cls) -> str:
        return cls.format_key


class UserEnteredFmt(metaclass=GoogleFormatType):
    format_key = "userEnteredFormat"


class EffectiveFmt(metaclass=GoogleFormatType):
    format_key = "effectiveFormat"


class DefaultFmt(metaclass=GoogleFormatType):
    format_key = "defaultFormat"
