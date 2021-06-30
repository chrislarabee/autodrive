from __future__ import annotations

from ..core import CellFormatting, GridFormatting, TextFormatting
from ..interfaces import Color, Format, OneDRange, TwoDRange
from . import cell, grid, text


class TabCellFormatting(CellFormatting):
    def add_alternating_row_background(
        self, colors: Color, rng: TwoDRange | None = None
    ) -> TabCellFormatting:
        rng = rng if rng else self._parent.range
        self.add_request(cell.add_alternating_row_background(rng, colors))
        return self


class TabGridFormatting(GridFormatting):
    def auto_column_width(self, rng: OneDRange | None = None) -> TabGridFormatting:
        rng = rng if rng else self._parent.range.col_range
        self.add_request(grid.auto_column_width(rng))
        return self

    def append_rows(self, num_rows: int) -> TabGridFormatting:
        self.add_request(grid.append_rows(self._parent.tab_id, num_rows))
        return self

    def insert_rows(self, num_rows: int, at_row: int) -> TabGridFormatting:
        self.add_request(grid.insert_rows(self._parent.tab_id, num_rows, at_row - 1))
        return self

    def delete_rows(self, rng: OneDRange) -> TabGridFormatting:
        self.add_request(grid.delete_rows(rng))
        return self


class TabTextFormatting(TextFormatting):
    def apply_format(
        self, format: Format, rng: TwoDRange | None = None
    ) -> TabTextFormatting:
        rng = self.ensure_2d_range(rng)
        self.add_request(text.apply_format(rng, format))
        return self
