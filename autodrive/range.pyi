from ._view import Component as Component
from .connection import SheetsConnection as SheetsConnection
from .dtypes import EffectiveVal as EffectiveVal, GoogleValueType as GoogleValueType
from .formatting.format_rng import (
    RangeCellFormatting as RangeCellFormatting,
    RangeGridFormatting as RangeGridFormatting,
    RangeTextFormatting as RangeTextFormatting,
)
from .interfaces import AuthConfig as AuthConfig, FullRange as FullRange
from typing import Any, Dict, Sequence, Union

class Range(Component[RangeCellFormatting, RangeGridFormatting, RangeTextFormatting]):
    _tab_title: Any = ...
    _rng: Any = ...
    def __init__(
        self,
        gsheet_range: Union[FullRange, str],
        gsheet_id: str,
        tab_title: str,
        tab_id: int,
        *,
        auth_config: Union[AuthConfig, None] = ...,
        sheets_conn: Union[SheetsConnection, None] = ...,
        autoconnect: bool = ...
    ) -> None: ...
    @property
    def format_grid(self) -> RangeGridFormatting: ...
    @property
    def format_text(self) -> RangeTextFormatting: ...
    @property
    def format_cell(self) -> RangeCellFormatting: ...
    def get_data(self, value_type: GoogleValueType = ...) -> Range: ...
    def write_values(
        self, data: Sequence[Union[Sequence[Any], Dict[str, Any]]]
    ) -> Range: ...
