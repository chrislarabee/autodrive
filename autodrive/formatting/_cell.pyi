from ..dtypes import UserEnteredFmt as UserEnteredFmt, UserEnteredVal as UserEnteredVal
from ..interfaces import (
    BorderFormat as BorderFormat,
    Color as Color,
    FullRange as FullRange,
)
from typing import Any, Dict

def add_alternating_row_background(
    tab_id: int, rng: FullRange, colors: Color
) -> Dict[str, Any]: ...
def set_background_color(tab_id: int, rng: FullRange, color: Color) -> Any: ...
def set_border_format(tab_id: int, rng: FullRange, *borders: BorderFormat) -> Any: ...
