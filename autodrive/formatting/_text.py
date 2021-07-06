from __future__ import annotations

from typing import Dict, Any

from ..interfaces import TwoDRange, Format
from .. import _google_terms as terms


def apply_format(rng: TwoDRange, fmt: Format) -> Dict[str, Any]:
    return {
        terms.RPT_CELL: {
            terms.RNG: dict(rng),
            terms.FIELDS: str(fmt),
            terms.CELL: dict(fmt),
        }
    }
