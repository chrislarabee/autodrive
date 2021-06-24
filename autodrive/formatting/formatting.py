from __future__ import annotations

from typing import Tuple, Union

from ..core import Formatting
from . import grid


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
