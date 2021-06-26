from __future__ import annotations

from typing import Tuple, Union

from ..core import Formatting
from ..interfaces import Format, OneDRange, TwoDRange
from . import grid, text


class RangeGridFormatting(Formatting):
    def auto_column_width(self) -> RangeGridFormatting:
        self._parent.requests.append(
            grid.auto_column_width(self._parent.range.col_range)
        )
        return self


class RangeTextFormatting(Formatting):
    def apply_format(self, format: Format) -> RangeTextFormatting:
        self._parent.requests.append(text.apply_format(self._parent.range, format))
        return self


class RangeCellFormatting(Formatting):
    pass


class TabGridFormatting(Formatting):
    def auto_column_width(self, rng: OneDRange = None) -> TabGridFormatting:
        rng = rng if rng else self._parent.range.col_range
        self._parent.requests.append(grid.auto_column_width(rng))
        return self


class TabTextFormatting(Formatting):
    pass


class TabCellFormatting(Formatting):
    pass
