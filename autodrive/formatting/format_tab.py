from __future__ import annotations

from .._view import CellFormatting, GridFormatting, TextFormatting
from ..interfaces import Color, Format, HalfRange, FullRange
from . import _cell as cell, _grid as grid, _text as text


class TabCellFormatting(CellFormatting):
    """
    Contains request generation methods relating to formatting this Tab's cells
    (like adding borders and backgrounds and such).
    """

    def add_alternating_row_background(
        self, colors: Color, rng: FullRange | None = None
    ) -> TabCellFormatting:
        """
        Queues a request to add an alternating row background of the indicated
        color to this Tab's cells, or to a range within the Tab.

        Args:
          colors (Color): The desired Color to apply to every other row.
          rng (FullRange, optional): A FullRange within the tab to apply the
            alternating row colors to.

        Returns:
          TabCellFormatting: This formatting object, so further requests can be
            queued if desired.

        """
        rng = rng if rng else self._parent.range
        rng.validate(self._parent.tab_id)
        self.add_request(cell.add_alternating_row_background(rng, colors))
        return self


class TabGridFormatting(GridFormatting):
    """
    Contains request generation methods related to formatting this Tab's grid
    (number of columns, rows, width and height, etc).
    """

    def auto_column_width(self, rng: HalfRange | None = None) -> TabGridFormatting:
        """
        Queues a request to set the column width of the Tab's columns equal to the
        width of the values in the cells.

        Args:
          rng (HalfRange, optional): The range of columns to be affected, defaults to
            None for all columns in the Tab.

        Returns:
          TabGridFormatting: This formatting object, so further requests can be
            queued if desired.

        """
        rng = rng if rng else self._parent.range.col_range
        rng.validate(self._parent.tab_id)
        self.add_request(grid.auto_column_width(rng))
        return self

    def append_rows(self, num_rows: int) -> TabGridFormatting:
        """
        Queues a request to add new empty rows at the bottom of the Tab.

        Args:
          num_rows (int): The number of rows to add to the bottom of the Tab.

        Returns:
          TabGridFormatting: This formatting object, so further requests can be
             queued if desired.

        """
        self.add_request(grid.append_rows(self._parent.tab_id, num_rows))
        return self

    def insert_rows(self, num_rows: int, at_row: int) -> TabGridFormatting:
        """
        Queues a request to insert new empty rows at the specified row number.

        Args:
          num_rows (int): The number of rows to insert.
          at_row (int): The row number to insert after.

        Returns:
          TabGridFormatting: This formatting object, so further requests can be
            queued if desired.

        """
        self.add_request(grid.insert_rows(self._parent.tab_id, num_rows, at_row - 1))
        return self

    def delete_rows(self, rng: HalfRange) -> TabGridFormatting:
        """
        Queues a request to delete rows in the selected row range.

        Args:
          rng (HalfRange): The range of rows to delete.

        Returns:
          TabGridFormatting: This formatting object, so further requests can be
            queued if desired.

        """
        rng.validate(self._parent.tab_id)
        self.add_request(grid.delete_rows(rng))
        return self


class TabTextFormatting(TextFormatting):
    """
    Contains request generation methods relating to formatting this Tab's text
    (the text format of any cells, even those containing non-text values like
    integers or null values).
    """

    def apply_format(
        self, format: Format, rng: FullRange | None = None
    ) -> TabTextFormatting:
        """
        Queues a request to set the text/number format of the Range's cells.

        Args:
          format (Format): A format instance, such as TextFormat or NumberFormat.
          rng (FullRange, optional): Optional rnage within the Tab to apply the
            format to, defaults to None, for all cells in the Tab.

        Returns:
          TabTextFormatting: This formatting object, so further requests can be
            queued if desired.

        """
        rng = self.ensure_full_range(rng)
        rng.validate(self._parent.tab_id)
        self.add_request(text.apply_format(rng, format))
        return self
