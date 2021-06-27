from __future__ import annotations

from ..core import CellFormatting, GridFormatting, TextFormatting
from ..interfaces import Color, Format
from . import cell, grid, text


class RangeCellFormatting(CellFormatting):
    def add_alternating_row_background(self, colors: Color) -> RangeCellFormatting:
        self.add_request(
            cell.add_alternating_row_background(self._parent.range, colors)
        )
        return self


class RangeGridFormatting(GridFormatting):
    def auto_column_width(self) -> RangeGridFormatting:
        self.add_request(grid.auto_column_width(self._parent.range.col_range))
        return self


class RangeTextFormatting(TextFormatting):
    def apply_format(self, format: Format) -> RangeTextFormatting:
        self.add_request(text.apply_format(self._parent.range, format))
        return self
