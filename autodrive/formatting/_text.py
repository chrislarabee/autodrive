from __future__ import annotations

from typing import Any, Dict

from .. import _google_terms as terms
from ..dtypes import HorizontalAlign, UserEnteredFmt, VerticalAlign
from ..interfaces import Format, FullRange


def apply_format(tab_id: int, rng: FullRange, fmt: Format) -> Dict[str, Any]:
    return {
        terms.RPT_CELL: {
            terms.RNG: {terms.TAB_ID: tab_id, **dict(rng)},
            terms.FIELDS: str(fmt),
            terms.CELL: dict(fmt),
        }
    }


def set_text_alignment(
    tab_id: int,
    rng: FullRange,
    halign: HorizontalAlign | None = None,
    valign: VerticalAlign | None = None,
) -> Dict[str, Any]:
    align_dict: Dict[str, str] = {}
    if halign:
        align_dict["horizontalAlignment"] = str(halign)
    if valign:
        align_dict["verticalAlignment"] = str(valign)
    return {
        terms.RPT_CELL: {
            terms.RNG: {terms.TAB_ID: tab_id, **dict(rng)},
            terms.FIELDS: "*",
            terms.CELL: {str(UserEnteredFmt): align_dict},
        }
    }
