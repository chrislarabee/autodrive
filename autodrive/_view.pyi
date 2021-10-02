from ._core import GoogleDtype as GoogleDtype
from .connection import SheetsConnection as SheetsConnection
from .dtypes import (
    EffectiveFmt as EffectiveFmt,
    EffectiveVal as EffectiveVal,
    Formula as Formula,
    GOOGLE_DTYPES as GOOGLE_DTYPES,
    GoogleValueType as GoogleValueType,
    String as String,
    TYPE_MAP as TYPE_MAP,
    UserEnteredVal as UserEnteredVal,
)
from .interfaces import AuthConfig as AuthConfig, FullRange as FullRange
from abc import ABC
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Type, TypeVar, Union, Generic

T = TypeVar("T", bound="GSheetView")
FC = TypeVar("FC", bound="CellFormatting")
FG = TypeVar("FG", bound="GridFormatting")
FT = TypeVar("FT", bound="TextFormatting")

class NoConnectionError(Exception):
    def __init__(self, vtype: Type[GSheetView], *args: object) -> None: ...

class OutputError(Exception): ...

class Formatting:
    _parent: Component[Any, Any, Any] = ...
    def __init__(self, parent: Component[Any, Any, Any]) -> None: ...
    def add_request(self, request: Dict[str, Any]) -> None: ...
    def ensure_full_range(
        self, rng: Union[FullRange, str, None] = ...
    ) -> FullRange: ...

class CellFormatting(Formatting): ...
class GridFormatting(Formatting): ...
class TextFormatting(Formatting): ...

class GSheetView(ABC):
    _conn: Union[SheetsConnection, None] = ...
    _auth: Union[AuthConfig, None] = ...
    _gsheet_id: str = ...
    _requests: List[Dict[str, Any]] = ...
    def __init__(
        self,
        gsheet_id: str,
        *,
        auth_config: Union[AuthConfig, None] = ...,
        sheets_conn: Union[SheetsConnection, None] = ...,
        autoconnect: bool = ...
    ) -> None: ...
    @property
    def requests(self) -> List[Dict[str, Any]]: ...
    @property
    def conn(self) -> SheetsConnection: ...
    @property
    def auth(self) -> AuthConfig: ...
    @property
    def gsheet_id(self) -> str: ...
    def commit(self) -> Dict[str, Any]: ...
    def ensure_full_range(
        self, backup: FullRange, rng: Union[FullRange, str, None] = ...
    ) -> FullRange: ...
    @staticmethod
    def _parse_properties(
        properties: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, Any]]]: ...
    @classmethod
    def _parse_row_data(
        cls: Any,
        row_data: List[Dict[str, List[Dict[str, Any]]]],
        value_type: GoogleValueType = ...,
    ) -> Tuple[List[List[Any]], List[List[Dict[str, Any]]]]: ...
    def _get_data(
        self, gsheet_id: str, rng_str: str, value_type: GoogleValueType = ...
    ) -> Tuple[List[List[Any]], List[List[Dict[str, Any]]]]: ...
    def _write_values(
        self: T,
        data: Sequence[Union[Sequence[Any], Dict[str, Any]]],
        tab_id: int,
        rng_dict: Union[Dict[str, int], None] = ...,
    ) -> T: ...
    @staticmethod
    def _gen_cell_write_value(python_val: Any) -> Dict[str, Any]: ...
    @staticmethod
    def gen_alpha_keys(num: int) -> List[str]: ...

class Component(GSheetView, Generic[FC, FG, FT]):
    _rng: FullRange = ...
    _tab_id: int = ...
    _values: List[List[Any]] = ...
    _formats: List[List[Dict[str, Any]]] = ...
    _format_grid: FG = ...
    _format_text: FT = ...
    _format_cell: FC = ...
    def __init__(
        self,
        gsheet_range: FullRange,
        gsheet_id: str,
        tab_id: int,
        grid_formatting: Type[FG],
        text_formatting: Type[FT],
        cell_formatting: Type[FC],
        *,
        auth_config: Union[AuthConfig, None] = ...,
        sheets_conn: Union[SheetsConnection, None] = ...,
        autoconnect: bool = ...
    ) -> None: ...
    @property
    def tab_id(self) -> int: ...
    @property
    def range_str(self) -> str: ...
    @property
    def range(self) -> FullRange: ...
    @property
    def format_grid(self) -> FG: ...
    @property
    def format_text(self) -> FT: ...
    @property
    def format_cell(self) -> FC: ...
    @property
    def values(self) -> List[List[Any]]: ...
    @values.setter
    def values(self, new_values: List[List[Any]]) -> None: ...
    @property
    def formats(self) -> List[List[Dict[str, Any]]]: ...
    @formats.setter
    def formats(self, new_formats: List[List[Dict[str, Any]]]) -> None: ...
    @property
    def data_shape(self) -> Tuple[int, int]: ...
    def to_csv(
        self, p: Union[str, Path], header: Union[Sequence[Any], None] = ...
    ) -> None: ...
    def to_json(
        self, p: Union[str, Path], header: Union[Sequence[str], int] = ...
    ) -> None: ...
    def _verify_header_len(self, header: Sequence[Any]) -> bool: ...