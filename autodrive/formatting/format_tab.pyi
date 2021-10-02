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
from ..interfaces import (
    BorderFormat as BorderFormat,
    Color as Color,
    Format as Format,
    FullRange as FullRange,
    HalfRange as HalfRange,
)
from typing import Union

class TabCellFormatting(CellFormatting):
    def add_alternating_row_background(
        self, colors: Color, rng: Union[FullRange, str, None] = ...
    ) -> TabCellFormatting: ...
    def set_background_color(
        self, color: Color, rng: Union[FullRange, str, None] = ...
    ) -> TabCellFormatting: ...
    def set_border_format(
        self,
        *sides: BorderSide,
        style: Union[BorderStyle, None] = ...,
        color: Union[Color, None] = ...,
        rng: Union[FullRange, str, None] = ...
    ) -> TabCellFormatting: ...

class TabGridFormatting(GridFormatting):
    def auto_column_width(
        self, rng: Union[HalfRange, None] = ...
    ) -> TabGridFormatting: ...
    def append_rows(self, num_rows: int) -> TabGridFormatting: ...
    def insert_rows(self, num_rows: int, at_row: int) -> TabGridFormatting: ...
    def delete_rows(self, rng: HalfRange) -> TabGridFormatting: ...
    def append_columns(self, num_cols: int) -> TabGridFormatting: ...
    def insert_columns(self, num_cols: int, at_col: int) -> TabGridFormatting: ...
    def delete_columns(self, rng: HalfRange) -> TabGridFormatting: ...

class TabTextFormatting(TextFormatting):
    def apply_format(
        self, format: Format, rng: Union[FullRange, str, None] = ...
    ) -> TabTextFormatting: ...
    def set_alignment(
        self,
        *aligns: Union[HorizontalAlign, VerticalAlign],
        rng: Union[FullRange, str, None] = ...
    ) -> TabTextFormatting: ...
