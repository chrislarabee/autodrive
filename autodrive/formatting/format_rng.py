from __future__ import annotations

from ..core import CellFormatting, GridFormatting, TextFormatting
from ..interfaces import Color, Format
from . import cell, grid, text


class RangeCellFormatting(CellFormatting):
    def add_alternating_row_background(self, colors: Color) -> RangeCellFormatting:
        """
        Queues a request to add an alternating row background of the indicated
        color to this Range's cells.

        :param colors: The desired Color to apply to every other row.
        :type colors: Color
        :return: This formatting object, so further requests can be queued if
            desired.
        :rtype: RangeCellFormatting
        """
        self.add_request(
            cell.add_alternating_row_background(self._parent.range, colors)
        )
        return self


class RangeGridFormatting(GridFormatting):
    def auto_column_width(self) -> RangeGridFormatting:
        """
        Queues a request to set the column width of the Range's columns equal to the
        width of the values in the cells.

        :return: This formatting object, so further requests can be queued if
            desired.
        :rtype: RangeGridFormatting
        """
        self.add_request(grid.auto_column_width(self._parent.range.col_range))
        return self


class RangeTextFormatting(TextFormatting):
    def apply_format(self, format: Format) -> RangeTextFormatting:
        """
        Queues a request to set the text/number format of the Range's cells.

        :param format: A format instance, such as TextFormat or NumberFormat.
        :type format: _Format
        :return: This formatting object, so further requests can be queued if
            desired.
        :rtype: RangeTextFormatting
        """
        self.add_request(text.apply_format(self._parent.range, format))
        return self
