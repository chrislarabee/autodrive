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


#     def apply_font(
#         self,
#         row_idxs: tuple = (None, None),
#         col_idxs: tuple = (None, None),
#         size: int = None,
#         style: Union[str, Tuple[str, ...]] = None,
#     ):
#         """
#         Adds a textFormat request to the GSheetFormatting object's
#         request queue.

#         Args:
#             row_idxs: A tuple of the start and end rows to apply font
#                 formatting to.
#             col_idxs: A tuple of the start and end columns to apply font
#                 formatting to.
#             size: Font size formatting.
#             style: Font style formatting (bold, italic?, underline?).
#                 Bold is the only current style tested.

#         Returns: self.

#         """
#         text_format = dict()
#         if size:
#             text_format["fontSize"] = size
#         if style:
#             style = (style,) if isinstance(style, str) else style
#             for s in style:
#                 text_format[s] = True
#         repeat_cell = self._build_repeat_cell_dict(
#             dict(textFormat=text_format), row_idxs, col_idxs, self.sheet_id
#         )
#         repeat_cell["fields"] = "userEnteredFormat(textFormat)"
#         request = dict(repeatCell=repeat_cell)
#         self.requests.append(request)
#         return self

#     def apply_nbr_format(
#         self, fmt: str, row_idxs: tuple = (None, None), col_idxs: tuple = (None, None)
#     ):
#         """
#         Adds a numberFormat request to the GSheetFormatting object's
#         request queue.

#         Args:
#             fmt: A _fmt property from this object (like
#                 accounting_fmt) with or without the _fmt suffix.
#             row_idxs: A tuple of the start and end rows to apply number
#                 formatting to.
#             col_idxs: A tuple of the start and end columns to apply
#                 number formatting to.

#         Returns: self.

#         """
#         fmt += "_fmt" if fmt[-4:] != "_fmt" else ""
#         t, p = getattr(self, fmt)
#         nbr_format = dict(type=t, pattern=p)

#         repeat_cell = self._build_repeat_cell_dict(
#             dict(numberFormat=nbr_format), row_idxs, col_idxs, self.sheet_id
#         )
#         repeat_cell["fields"] = "userEnteredFormat.numberFormat"
#         request = dict(repeatCell=repeat_cell)
#         self.requests.append(request)
#         return self

#     @classmethod
#     def _build_repeat_cell_dict(
#         cls,
#         fmt_dict: dict,
#         row_idxs: tuple = (None, None),
#         col_idxs: tuple = (None, None),
#         sheet_id: int = 0,
#     ) -> dict:
#         """
#         Quick method for building a repeatCell dictionary for use in a
#         request dictionary wrapper intended to change cell formatting or
#         contents (like changing font, borders, background, contents,
#         etc).

#         Args:
#             fmt_dict: A formatting dictionary.
#             row_idxs: A tuple of the start and stop row indexes.
#             col_idxs: A tuple of the start and stop column indexes.
#             sheet_id: The id of the sheet to apply the formatting to.
#                 Default is 0.

#         Returns: A dictionary ready to be slotted in at the repeatCell
#             key in a request.

#         """
#         return dict(
#             range=cls._build_range_dict(sheet_id, row_idxs, col_idxs),
#             cell=dict(userEnteredFormat=fmt_dict),
#         )
