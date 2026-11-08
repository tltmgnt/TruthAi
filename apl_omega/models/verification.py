"""Verification evidence graph and freshness rules.

V = {Unknown, Under Review, Partially Verified, Verified, Expired, Invalidated}
Material configuration change ⇒ reverification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Set

from apl_omega.formulas.metrics import evidence_freshness, verification_coverage
from apl_omega.models.state import VerificationEvidenceState


class ObsolescenceReplacementType(str, Enum):
    A_DROP_IN = "A"  # drop-in compatible
    B_INTERFACE_VERIFY = "B"  # interface-compatible with verification
    C_ADAPTER = "C"  # requires adapter
    D_ARCHITECTURE = "D"  # requires architecture modification
    E_REDESIGN = "E"  # requires capability redesign


@dataclass
class EvidenceItem:
    evidence_id: str
    requirement_id: str
    state: VerificationEvidenceState = VerificationEvidenceState.UNKNOWN
    age: float = 0.0
    weight: float = 1.0
    config_dependencies: Set[str] = field(default_factory=set)

    def freshness(self, lam: float = 0.01) -> float:
        return evidence_freshness(self.age, lam)


@dataclass
class VerificationGraph:
    """Tracks requirement evidence and invalidation on config change."""

    items: Dict[str, EvidenceItem] = field(default_factory=dict)
    requirements: Set[str] = field(default_factory=set)

    def add_evidence(self, item: EvidenceItem) -> None:
        self.items[item.evidence_id] = item
        self.requirements.add(item.requirement_id)

    def coverage(self) -> float:
        verified_reqs = {
            i.requirement_id
            for i in self.items.values()
            if i.state == VerificationEvidenceState.VERIFIED
        }
        return verification_coverage(len(verified_reqs), len(self.requirements))

    def invalidate_for_config_change(self, changed_keys: Iterable[str]) -> List[str]:
        """ΔK ≠ 0 on a dependency ⇒ reverification for dependent evidence."""
        changed = set(changed_keys)
        invalidated: List[str] = []
        for item in self.items.values():
            if item.config_dependencies & changed:
                item.state = VerificationEvidenceState.INVALIDATED
                invalidated.append(item.evidence_id)
        return invalidated

    def aggregate_state(self) -> VerificationEvidenceState:
        if not self.items:
            return VerificationEvidenceState.UNKNOWN
        states = {i.state for i in self.items.values()}
        if VerificationEvidenceState.INVALIDATED in states:
            return VerificationEvidenceState.INVALIDATED
        if VerificationEvidenceState.EXPIRED in states:
            return VerificationEvidenceState.EXPIRED
        if states == {VerificationEvidenceState.VERIFIED}:
            return VerificationEvidenceState.VERIFIED
        if VerificationEvidenceState.VERIFIED in states:
            return VerificationEvidenceState.PARTIALLY_VERIFIED
        if VerificationEvidenceState.UNDER_REVIEW in states:
            return VerificationEvidenceState.UNDER_REVIEW
        return VerificationEvidenceState.UNKNOWN

    def transition(self, evidence_id: str, new_state: VerificationEvidenceState) -> None:
        """Enforce ordered verification progression where applicable."""
        item = self.items[evidence_id]
        order = [
            VerificationEvidenceState.UNKNOWN,
            VerificationEvidenceState.UNDER_REVIEW,
            VerificationEvidenceState.PARTIALLY_VERIFIED,
            VerificationEvidenceState.VERIFIED,
        ]
        # Allow regression to expired/invalidated from any state
        if new_state in (
            VerificationEvidenceState.EXPIRED,
            VerificationEvidenceState.INVALIDATED,
            VerificationEvidenceState.UNKNOWN,
        ):
            item.state = new_state
            return
        if item.state in (
            VerificationEvidenceState.EXPIRED,
            VerificationEvidenceState.INVALIDATED,
        ):
            # Must re-enter under review
            if new_state != VerificationEvidenceState.UNDER_REVIEW:
                raise ValueError("Reverification must start at UNDER_REVIEW")
            item.state = new_state
            return
        # Forward-only along the chain
        if order.index(new_state) < order.index(item.state):
            raise ValueError(f"Cannot regress from {item.state} to {new_state}")
        item.state = new_state
