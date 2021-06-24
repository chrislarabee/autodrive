from __future__ import annotations

from typing import Tuple, Union

from ..core import Formatting
from ..interfaces import Format, TwoDRange
from . import grid, text


class RangeGridFormatting(Formatting):
    def auto_column_width(self) -> RangeGridFormatting:
        self._parent.requests.append(
            grid.auto_column_width(
                self._parent.tab_id,
                self._parent.start_col_idx,
                self._parent.end_col_idx,
            )
        )
        return self


class RangeTextFormatting(Formatting):
    def apply_format(self, format: Format) -> RangeTextFormatting:
        p = self._parent
        rng = TwoDRange(
            p.tab_id, p.start_row_idx, p.end_row_idx, p.start_col_idx, p.end_col_idx
        )
        self._parent.requests.append(text.apply_format(rng, format))
        return self


class RangeCellFormatting(Formatting):
    pass


class TabGridFormatting(Formatting):
    def auto_column_width(
        self, start_col: int = None, end_col: int = None
    ) -> TabGridFormatting:
        self._parent.requests.append(
            grid.auto_column_width(
                self._parent.tab_id,
                start_col or self._parent.start_col_idx,
                end_col or self._parent.end_col_idx,
            )
        )
        return self


class TabTextFormatting(Formatting):
    pass


class TabCellFormatting(Formatting):
    pass
