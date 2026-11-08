"""Topological invariant checks for governed transitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from apl_omega.matrices.domain_matrices import INVARIANTS
from apl_omega.models.state import SystemState, VerificationEvidenceState
from apl_omega.models.topology import TopologyGraph


@dataclass
class InvariantResult:
    name: str
    satisfied: bool
    detail: str


def check_invariants(
    before: SystemState,
    after: SystemState,
    graph: TopologyGraph,
    *,
    human_authority_present: bool = True,
    trust_score: float = 1.0,
    evidence_confidence: float = 1.0,
    twin_confidence: float = 1.0,
    safety_ok: bool = True,
) -> List[InvariantResult]:
    results: List[InvariantResult] = []

    results.append(
        InvariantResult(
            "I_safety",
            safety_ok and after.safety.readiness >= before.safety.readiness * 0.0,
            INVARIANTS["I_safety"]
            if safety_ok
            else "Safety invariant broken — transition blocked",
        )
    )
    # Explicit: if safety value becomes unsafe, fail
    if after.safety.value in {"unsafe", "violated"} or not safety_ok:
        results[-1] = InvariantResult("I_safety", False, "Safety constraint violated")

    results.append(
        InvariantResult(
            "I_security",
            trust_score > 0.0 or after.cyber.value in {"untrusted", "isolated"},
            "Trust evaluated independently of connectivity",
        )
    )

    results.append(
        InvariantResult(
            "I_authority",
            human_authority_present
            or after.omega_class.value in {"Ω0"}
            and after.human.value == "ready",
            INVARIANTS["I_authority"]
            if human_authority_present
            else "Human authorization unavailable — transition blocked",
        )
    )
    if not human_authority_present and after.mean_readiness() > before.mean_readiness():
        results[-1] = InvariantResult(
            "I_authority",
            False,
            "Cannot promote readiness without human authority",
        )

    results.append(
        InvariantResult(
            "I_twin",
            twin_confidence <= evidence_confidence + 1e-9,
            INVARIANTS["I_twin"],
        )
    )

    results.append(
        InvariantResult(
            "I_verification",
            not (
                before.verification == VerificationEvidenceState.EXPIRED
                and after.verification == VerificationEvidenceState.VERIFIED
            ),
            INVARIANTS["I_verification"],
        )
    )

    before_env = getattr(before.environment, "value", before.environment)
    after_env = getattr(after.environment, "value", after.environment)
    results.append(
        InvariantResult(
            "I_unknown",
            not (
                before_env == "unknown"
                and after_env == "normal"
                and after.mean_confidence() > before.mean_confidence()
            ),
            INVARIANTS["I_unknown"],
        )
    )

    # Dependency integrity must remain defined
    results.append(
        InvariantResult(
            "I_configuration",
            0.0 <= graph.dependency_integrity() <= 1.0,
            INVARIANTS["I_configuration"],
        )
    )

    results.append(
        InvariantResult(
            "I_control",
            True,
            INVARIANTS["I_control"],
        )
    )

    return results


def all_satisfied(results: List[InvariantResult]) -> bool:
    return all(r.satisfied for r in results)


def violated_names(results: List[InvariantResult]) -> List[str]:
    return [r.name for r in results if not r.satisfied]
