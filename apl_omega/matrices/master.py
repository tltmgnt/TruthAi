"""Master Eventuality Matrix loader (E-001 … E-080)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from apl_omega.models.eventuality import Eventuality
from apl_omega.models.state import OmegaClass

def _default_data_path() -> Path:
    """Resolve matrix JSON from repo root or packaged location."""
    candidates = [
        Path(__file__).resolve().parents[2] / "data" / "master_eventuality_matrix.json",
        Path(__file__).resolve().parents[1] / "data" / "master_eventuality_matrix.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _omega(value: str) -> OmegaClass:
    for item in OmegaClass:
        if item.value == value:
            return item
    return OmegaClass.UNKNOWN_UNCERTAIN


@lru_cache(maxsize=1)
def load_master_matrix(path: Optional[str] = None) -> List[Eventuality]:
    matrix_path = Path(path) if path else _default_data_path()
    raw = json.loads(matrix_path.read_text(encoding="utf-8"))
    items: List[Eventuality] = []
    for row in raw["eventualities"]:
        items.append(
            Eventuality(
                eventuality_id=row["id"],
                domain=row["domain"],
                name=row["eventuality"],
                topology_effect=row["topology_effect"],
                tga_response=row["tga_response"],
                desired_state=row["desired_state"],
                omega_class=_omega(row.get("omega_class", "Ω7")),
                automatic_analysis=row.get("automatic_analysis", True),
                human_review_required=row.get("human_review_required", False),
                verification_required=row.get("verification_required", False),
            )
        )
    return items


def by_id(eventuality_id: str) -> Eventuality:
    for item in load_master_matrix():
        if item.eventuality_id == eventuality_id:
            return item
    raise KeyError(eventuality_id)


def by_domain(domain: str) -> List[Eventuality]:
    return [e for e in load_master_matrix() if e.domain.lower() == domain.lower()]


def by_omega_class(omega: OmegaClass) -> List[Eventuality]:
    return [e for e in load_master_matrix() if e.omega_class == omega]


def index_by_id() -> Dict[str, Eventuality]:
    return {e.eventuality_id: e for e in load_master_matrix()}


def domain_summary() -> Dict[str, int]:
    summary: Dict[str, int] = {}
    for e in load_master_matrix():
        summary[e.domain] = summary.get(e.domain, 0) + 1
    return summary
