from ._core import GoogleDtype as GoogleDtype
from typing import Any, Union

class String(metaclass=GoogleDtype):
    python_type: Any = ...
    type_key: str = ...
    @classmethod
    def parse(cls: Any, value: str) -> str: ...

class Formula(metaclass=GoogleDtype):
    python_type: Any = ...
    type_key: str = ...
    @classmethod
    def parse(cls: Any, value: str) -> str: ...

class Number(metaclass=GoogleDtype):
    python_type: Any = ...
    type_key: str = ...
    @classmethod
    def parse(cls: Any, value: str) -> Union[float, int]: ...

class Boolean(metaclass=GoogleDtype):
    python_type: Any = ...
    type_key: str = ...
    @classmethod
    def parse(cls: Any, value: str) -> bool: ...

class GoogleValueType(type):
    value_key: str
    has_dtype: bool = ...
    def __str__(cls: Any) -> str: ...

class UserEnteredVal(metaclass=GoogleValueType):
    value_key: str = ...

class EffectiveVal(metaclass=GoogleValueType):
    value_key: str = ...

class FormattedVal(metaclass=GoogleValueType):
    value_key: str = ...
    has_dtype: bool = ...

GOOGLE_VAL_TYPES: Any
GOOGLE_DTYPES: Any
TYPE_MAP: Any
REV_TYPE_MAP: Any

class _Property:
    prop: Any = ...
    def __init__(self, property: str) -> None: ...
    def __str__(self) -> str: ...

UserEnteredFmt: Any
EffectiveFmt: Any
DefaultFmt: Any

class BorderStyle(_Property):
    def __init__(self, style: str) -> None: ...

BorderSolid: Any
BorderSolidMedium: Any
BorderSolidThick: Any
BorderDashed: Any
BorderDotted: Any
BorderDoubleLine: Any

class BorderSide(_Property):
    def __init__(self, side: str) -> None: ...

BorderLeft: Any
BorderRight: Any
BorderTop: Any
BorderBottom: Any
BorderSides: Any

class VerticalAlign(_Property):
    def __init__(self, align_str: str) -> None: ...

class HorizontalAlign(_Property):
    def __init__(self, align_str: str) -> None: ...

AlignTop: Any
AlignMiddle: Any
AlignBottom: Any
AlignLeft: Any
AlignCenter: Any
AlignRight: Any
