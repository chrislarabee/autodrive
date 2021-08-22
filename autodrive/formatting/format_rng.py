from __future__ import annotations

from typing import List

from .._view import CellFormatting, GridFormatting, TextFormatting
from ..interfaces import Color, Format, BorderFormat
from . import _cell as cell, _grid as grid, _text as text
from ..dtypes import (
    BorderSide,
    BorderStyle,
    BorderSides,
    HorizontalAlign,
    VerticalAlign,
)


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
            RangeCellFormatting: This formatting object, so further requests can
            be queued if desired.

        """
        self.add_request(
            cell.add_alternating_row_background(
                self._parent.tab_id, self._parent.range, colors
            )
        )
        return self

    def set_background_color(self, color: Color) -> RangeCellFormatting:
        """
        Queues a request to set the background of the Range's cells to the
        indicated color.

        Args:
            color (Color): The desired Color to set the background to.

        Returns:
            RangeCellFormatting: This formatting object, so further requests can
            be queued if desired.
        """
        self.add_request(
            cell.set_background_color(self._parent.tab_id, self._parent.range, color)
        )
        return self

    def set_border_format(
        self,
        *sides: BorderSide,
        style: BorderStyle | None = None,
        color: Color | None = None
    ) -> RangeCellFormatting:
        """
        Queues a request to set the border properties of the Range's cells.

        Args:
            *sides: (BorderSide): One or more BorderSide objects, indicating
                which side(s) of the cells you want to apply the border
                properties to. If no sides are provided, set_border_format will
                apply border properties to all sides.
            style (BorderStyle, optional): The style to apply to all the
                indicated sides. Defaults to None, for the default border style.
            color (Color, optional): The color to set the border(s) to. Defaults
                to None, for black.

        Returns:
            RangeCellFormatting: This formatting object, so further requests can
            be queued if desired.
        """
        fmts: List[BorderFormat] = []
        if len(sides) == 0:
            sides = BorderSides
        for side in sides:
            fmts.append(BorderFormat(side, color, style))
        self.add_request(
            cell.set_border_format(self._parent.tab_id, self._parent.range, *fmts)
        )
        return self


class RangeGridFormatting(GridFormatting):
    """
    Contains request generation methods relating to formatting a Range's
    cells (like adding borders and backgrounds and such).
    """

    def auto_column_width(self) -> RangeGridFormatting:
        """
        Queues a request to set the column width of the Range's columns equal to
        the width of the values in the cells.

        Returns:
            RangeGridFormatting: This formatting object, so further requests can
            be queued if desired.

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
            RangeTextFormatting: This formatting object, so further requests can
            be queued if desired.

        """
        self.add_request(
            text.apply_format(self._parent.tab_id, self._parent.range, format)
        )
        return self

    def set_alignment(
        self, *aligns: HorizontalAlign | VerticalAlign
    ) -> RangeTextFormatting:
        """
        Queues a request to set the horizontal and/or vertical text alignment of
        the Range's cells.

        Args:
            aligns (HorizontalAlign | VerticalAlign): The desired horizontal
                and/or vertical alignment properties. Note that if you specify
                a HorizontalAlign more than once, or a VerticalAlign more than
                once, only the last of each will be used.

        Returns:
            RangeTextFormatting: This formatting object, so further requests can
            be queued if desired.
        """
        halign = None
        valign = None
        for align in aligns:
            if isinstance(align, HorizontalAlign):
                halign = align
            else:
                valign = align
        self.add_request(
            text.set_text_alignment(
                self._parent.tab_id, self._parent.range, halign, valign
            )
        )
        return self
