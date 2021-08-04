from __future__ import annotations

from typing import List

from .._view import CellFormatting, GridFormatting, TextFormatting
from ..interfaces import BorderFormat, Color, Format, HalfRange, FullRange
from . import _cell as cell, _grid as grid, _text as text
from ..dtypes import BorderSide, BorderStyle, BorderSides


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
        self.add_request(
            cell.add_alternating_row_background(self._parent.tab_id, rng, colors)
        )
        return self

    def set_background_color(
        self, color: Color, rng: FullRange | None = None
    ) -> TabCellFormatting:
        """
        Queues a request to set the background of the Tab's cells (or the
        specified cells within the Tab) to the indicated color

        Args:
            color (Color): The desired Color to set the background to.
            rng (FullRange, optional): A FullRange within the tab to apply the
                background color to.

        Returns:
            TabCellFormatting: This formatting object, so further requests can be
            queued if desired.
        """
        rng = rng if rng else self._parent.range
        self.add_request(cell.set_background_color(self._parent.tab_id, rng, color))
        return self

    def set_border_format(
        self,
        *sides: BorderSide,
        style: BorderStyle | None = None,
        color: Color | None = None,
        rng: FullRange | None = None
    ) -> TabCellFormatting:
        """
        Queues a request to set the border properties of the Tab's cells (or the
        specified cells within the Tab).

        Args:
            *sides: (BorderSide): One or more BorderSide objects, indicating
                which side(s) of the cells you want to apply the border
                properties to. If no sides are provided, set_border_format will
                apply border properties to all sides.
            style (BorderStyle, optional): The style to apply to all the
                indicated sides. Defaults to None, for the default border style.
            color (Color, optional): The color to set the border(s) to. Defaults
                to None, for black.
            rng (FullRange, optional): A FullRange within the tab to apply the
                border properties to.

        Returns:
            TabCellFormatting: This formatting object, so further requests can be
            queued if desired.
        """
        rng = rng if rng else self._parent.range
        fmts: List[BorderFormat] = []
        if len(sides) == 0:
            sides = BorderSides
        for side in sides:
            fmts.append(BorderFormat(side, color, style))
        self.add_request(cell.set_border_format(self._parent.tab_id, rng, *fmts))
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
            rng (HalfRange, optional): The range of columns to be affected,
                defaults to None for all columns in the Tab.

        Returns:
            TabGridFormatting: This formatting object, so further requests can be
            queued if desired.

        """
        rng = rng if rng else self._parent.range.col_range
        self.add_request(grid.auto_column_width(self._parent.tab_id, rng))
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
        self.add_request(grid.delete_rows(self._parent.tab_id, rng))
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
        self.add_request(text.apply_format(self._parent.tab_id, rng, format))
        return self
