from __future__ import annotations

from .._view import CellFormatting, GridFormatting, TextFormatting
from ..interfaces import Color, Format
from . import _cell as cell, _grid as grid, _text as text


class RangeCellFormatting(CellFormatting):
    """
    Contains request generation methods related to formatting a Range's grid
    (width and height, etc).
    """

    def add_alternating_row_background(self, colors: Color) -> RangeCellFormatting:
        """
        Queues a request to add an alternating row background of the indicated
        color to a Range's cells.

        Args:
          colors (Color): The desired Color to apply to every other row.

        Returns:
          RangeCellFormatting: This formatting object, so further requests can be
            queued if desired.

        """
        self.add_request(
            cell.add_alternating_row_background(
                self._parent.tab_id, self._parent.range, colors
            )
        )
        return self


class RangeGridFormatting(GridFormatting):
    """
    Contains request generation methods relating to formatting a Range's
    cells (like adding borders and backgrounds and such).
    """

    def auto_column_width(self) -> RangeGridFormatting:
        """
        Queues a request to set the column width of the Range's columns equal to the
        width of the values in the cells.

        Returns:
          RangeGridFormatting: This formatting object, so further requests can be
            queued if desired.

        """
        self.add_request(
            grid.auto_column_width(self._parent.tab_id, self._parent.range.col_range)
        )
        return self


class RangeTextFormatting(TextFormatting):
    """
    Contains request generation methods methods relating to formatting this
    Range's text (the text format of any cells, even those containing non-text
    values like integers or null values).
    """

    def apply_format(self, format: Format) -> RangeTextFormatting:
        """
        Queues a request to set the text/number format of the Range's cells.

        Args:
          format (Format): A format instance, such as TextFormat or NumberFormat.

        Returns:
          RangeTextFormatting: This formatting object, so further requests can be
            queued if desired.

        """
        self.add_request(
            text.apply_format(self._parent.tab_id, self._parent.range, format)
        )
        return self
