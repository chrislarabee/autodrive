from __future__ import annotations

from typing import Dict, Any

from ..interfaces import FullRange, Format
from .. import _google_terms as terms


def apply_format(tab_id: int, rng: FullRange, fmt: Format) -> Dict[str, Any]:
    return {
        terms.RPT_CELL: {
            terms.RNG: {terms.TAB_ID: tab_id, **dict(rng)},
            terms.FIELDS: str(fmt),
            terms.CELL: dict(fmt),
        }
    }
