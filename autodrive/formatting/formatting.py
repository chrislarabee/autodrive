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


# class SubFormatting:
#     def __init(self, parent: Formatting):
#         self._parent = parent


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

#     def alternate_row_background(
#         self, *rgb_vals, row_idxs: tuple = (None, None), col_idxs: tuple = (None, None)
#     ):
#         """
#         Adds a background of the specified color to every other row in
#         the passed range.

#         Args:
#             row_idxs: A tuple of the start and stop row indexes.
#             col_idxs: A tuple of the start and stop column indexes.
#             *rgb_vals: Red, green, and blue values, in order. More than
#                 3 values will be ignored, default value is 0, so you
#                 only need to specify up to the last non-zero value.

#         Returns: self.

#         """
#         request = dict(
#             addConditionalFormatRule=dict(
#                 rule=dict(
#                     ranges=[self._build_range_dict(self.sheet_id, row_idxs, col_idxs)],
#                     booleanRule=dict(
#                         condition=dict(
#                             type="CUSTOM_FORMULA",
#                             values=[dict(userEnteredValue="=MOD(ROW(), 2)")],
#                         ),
#                         format=dict(backgroundColor=self._build_color_dict(*rgb_vals)),
#                     ),
#                 ),
#                 index=0,
#             )
#         )
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

#     @staticmethod
#     def _build_range_dict(
#         sheet_id: int = 0,
#         row_idxs: tuple = (None, None),
#         col_idxs: tuple = (None, None),
#     ) -> dict:
#         """
#         Quick method for building a range dictionary for use in a
#         request dictionary wrapper intended to change cell formatting or
#         contents (like changing font, borders, background, contents,
#         etc).

#         Args:
#             sheet_id: The id of the sheet to build a range for,
#                 default is 0, the first sheet.
#             row_idxs: A tuple of the start and stop row indexes.
#             col_idxs: A tuple of the start and stop column indexes.

#         Returns: A dictionary ready to be slotted into a format request
#             generating function.

#         """
#         range_dict = dict(sheetId=sheet_id)

#         range_ = (*row_idxs, *col_idxs)
#         non_nulls = 0
#         for r in range_:
#             non_nulls += 1 if r is not None else 0
#         if non_nulls < 2:
#             raise ValueError("Must pass one or both of row_idxs, col_idxs.")

#         start_row_idx, end_row_idx = row_idxs
#         start_col_idx, end_col_idx = col_idxs
#         # Must specify is not None because python interprets 0 as false.
#         if start_row_idx is not None:
#             range_dict["startRowIndex"] = start_row_idx
#         if end_row_idx is not None:
#             range_dict["endRowIndex"] = end_row_idx
#         if start_col_idx is not None:
#             range_dict["startColumnIndex"] = start_col_idx
#         if end_col_idx is not None:
#             range_dict["endColumnIndex"] = end_col_idx
#         return range_dict

#     @staticmethod
#     def _build_color_dict(*rgb_vals) -> Dict[str, float]:
#         """
#         Quick method for building a color dictionary for use in a
#         foreground, background, or font color dictionary.

#         Args:
#             *rgb_vals: Red, green, and blue values, in order. More than
#                 3 values will be ignored, default value is 0, so you
#                 only need to specify up to the last non-zero value.

#         Returns: A dictionary containing RGB color names and values.

#         """
#         rgb_vals = list(rgb_vals)
#         rgb = ["red", "green", "blue"]
#         rgb_vals += [0] * (3 - len(rgb_vals))
#         return {k: v for k, v in dict(zip(rgb, rgb_vals)).items()}
