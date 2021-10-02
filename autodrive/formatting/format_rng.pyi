from .._view import (
    CellFormatting as CellFormatting,
    GridFormatting as GridFormatting,
    TextFormatting as TextFormatting,
)
from ..dtypes import (
    BorderSide as BorderSide,
    BorderSides as BorderSides,
    BorderStyle as BorderStyle,
    HorizontalAlign as HorizontalAlign,
    VerticalAlign as VerticalAlign,
)
from ..interfaces import BorderFormat as BorderFormat, Color as Color, Format as Format
from typing import Union

class RangeCellFormatting(CellFormatting):
    def add_alternating_row_background(self, colors: Color) -> RangeCellFormatting: ...
    def set_background_color(self, color: Color) -> RangeCellFormatting: ...
    def set_border_format(
        self,
        *sides: BorderSide,
        style: Union[BorderStyle, None] = ...,
        color: Union[Color, None] = ...
    ) -> RangeCellFormatting: ...

class RangeGridFormatting(GridFormatting):
    def auto_column_width(self) -> RangeGridFormatting: ...

class RangeTextFormatting(TextFormatting):
    def apply_format(self, format: Format) -> RangeTextFormatting: ...
    def set_alignment(
        self, *aligns: Union[HorizontalAlign, VerticalAlign]
    ) -> RangeTextFormatting: ...
