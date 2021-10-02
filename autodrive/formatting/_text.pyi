from ..dtypes import (
    HorizontalAlign as HorizontalAlign,
    UserEnteredFmt as UserEnteredFmt,
    VerticalAlign as VerticalAlign,
)
from ..interfaces import Format as Format, FullRange as FullRange
from typing import Any, Dict, Union

def apply_format(tab_id: int, rng: FullRange, fmt: Format) -> Dict[str, Any]: ...
def set_text_alignment(
    tab_id: int,
    rng: FullRange,
    halign: Union[HorizontalAlign, None] = ...,
    valign: Union[VerticalAlign, None] = ...,
) -> Dict[str, Any]: ...
