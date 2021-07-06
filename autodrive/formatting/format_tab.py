from __future__ import annotations

from .._view import CellFormatting, GridFormatting, TextFormatting
from ..interfaces import Color, Format, OneDRange, TwoDRange
from . import _cell as cell, _grid as grid, _text as text


class TabCellFormatting(CellFormatting):
    def add_alternating_row_background(
        self, colors: Color, rng: TwoDRange | None = None
    ) -> TabCellFormatting:
        """
        Queues a request to add an alternating row background of the indicated
        color to this Tab's cells, or to a range within the Tab.

        :param colors: The desired Color to apply to every other row.
        :type colors: Color
        :param rng: A TwoDRange within the tab to apply the alternating row colors
            to.
        :type: rng: TwoDRange, optional
        :return: This formatting object, so further requests can be queued if
            desired.
        :rtype: TabCellFormatting
        """
        rng = rng if rng else self._parent.range
        self.add_request(cell.add_alternating_row_background(rng, colors))
        return self


class TabGridFormatting(GridFormatting):
    def auto_column_width(self, rng: OneDRange | None = None) -> TabGridFormatting:
        """
        Queues a request to set the column width of the Tab's columns equal to the
        width of the values in the cells.

        :param rng: The range of columns to be affected, defaults to None for all
            columns in the Tab.
        :type rng: OneDRange, optional
        :return: This formatting object, so further requests can be queued if
            desired.
        :rtype: TabGridFormatting
        """
        rng = rng if rng else self._parent.range.col_range
        self.add_request(grid.auto_column_width(rng))
        return self

    def append_rows(self, num_rows: int) -> TabGridFormatting:
        """
        Queues a request to add new empty rows at the bottom of the Tab.

        :param num_rows: The number of rows to add to the bottom of the Tab.
        :type num_rows: int
        :return: This formatting object, so further requests can be queued if
            desired.
        :rtype: TabGridFormatting
        """
        self.add_request(grid.append_rows(self._parent.tab_id, num_rows))
        return self

    def insert_rows(self, num_rows: int, at_row: int) -> TabGridFormatting:
        """
        Queues a request to insert new empty rows at the specified row number.

        :param num_rows: The number of rows to insert.
        :type num_rows: int
        :param at_row: The row number to insert after.
        :type at_row: int
        :return: This formatting object, so further requests can be queued if
            desired.
        :rtype: TabGridFormatting
        """
        self.add_request(grid.insert_rows(self._parent.tab_id, num_rows, at_row - 1))
        return self

    def delete_rows(self, rng: OneDRange) -> TabGridFormatting:
        """
        Queues a request to delete rows in the selected row range.

        :param rng: The range of rows to delete.
        :type rng: OneDRange
        :return: This formatting object, so further requests can be queued if
            desired.
        :rtype: TabGridFormatting
        """
        self.add_request(grid.delete_rows(rng))
        return self


class TabTextFormatting(TextFormatting):
    def apply_format(
        self, format: Format, rng: TwoDRange | None = None
    ) -> TabTextFormatting:
        """
        Queues a request to set the text/number format of the Range's cells.

        :param format: A format instance, such as TextFormat or NumberFormat.
        :type format: _Format
        :param rng: Optional rnage within the Tab to apply the format to, defaults
            to None, for all cells in the Tab.
        :type rng: TwoDRange, optional
        :return: This formatting object, so further requests can be queued if
            desired.
        :rtype: TabTextFormatting
        """
        rng = self.ensure_2d_range(rng)
        self.add_request(text.apply_format(rng, format))
        return self
