"""APL-Ω mathematical metrics layer.

Maps state → topology → gap → risk → transition → verification → recovery.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Sequence

from apl_omega.models.state import SystemState
from apl_omega.models.topology import TopologyGraph


def topological_gap(
    state: SystemState,
    target: SystemState,
    graph: TopologyGraph,
    target_graph: TopologyGraph,
    lambda_g: float = 1.0,
    state_weights: Optional[Dict[str, float]] = None,
) -> float:
    """Δ_Ω(S_t, S*) = d_S(S_t, S*) + λ_G d_G(G_t, G*)."""
    return state.distance(target, state_weights) + lambda_g * graph.topology_distance(
        target_graph
    )


def weighted_dimension_gap(
    current: Mapping[str, float],
    target: Mapping[str, float],
    weights: Optional[Mapping[str, float]] = None,
) -> float:
    """Δ_Ω = Σ w_j d_j(S_{t,j}, S_j*)."""
    keys = set(current) | set(target)
    weights = weights or {}
    total = 0.0
    for key in keys:
        w = weights.get(key, 1.0)
        total += w * abs(current.get(key, 0.0) - target.get(key, 0.0))
    return total


def capability_gap(current: float, target: float) -> float:
    """ΔC_c = C_c* - C_c(t). >0 deficiency, <0 excess, 0 satisfied."""
    return target - current


def aggregate_capability_gap(
    currents: Sequence[float],
    targets: Sequence[float],
    weights: Optional[Sequence[float]] = None,
) -> float:
    """ΔC = Σ w_c |ΔC_c|."""
    if len(currents) != len(targets):
        raise ValueError("currents and targets must align")
    weights = list(weights) if weights is not None else [1.0] * len(currents)
    return sum(w * abs(capability_gap(c, t)) for c, t, w in zip(currents, targets, weights))


def interface_compatibility_strict(components: Sequence[float]) -> float:
    """Γ_I = Π I_j for binary/graded factors in [0,1]."""
    if not components:
        return 0.0
    product = 1.0
    for value in components:
        product *= max(0.0, min(1.0, value))
    return product


def interface_compatibility_graded(
    components: Sequence[float],
    weights: Optional[Sequence[float]] = None,
) -> float:
    """Γ_I = Σ w_j I_j (normalized)."""
    if not components:
        return 0.0
    weights = list(weights) if weights is not None else [1.0] * len(components)
    num = sum(w * max(0.0, min(1.0, c)) for c, w in zip(components, weights))
    den = sum(weights) or 1.0
    return num / den


def configuration_integrity(delta_size: float, baseline_size: float) -> float:
    """CI_t = 1 - |ΔK_t| / |K_B|."""
    if baseline_size <= 0:
        return 1.0 if delta_size <= 0 else 0.0
    return max(0.0, min(1.0, 1.0 - (delta_size / baseline_size)))


def digital_twin_consistency(distance: float) -> float:
    """DTI_t = 1 - Δ_DT(t), distance expected in [0,1]."""
    return max(0.0, min(1.0, 1.0 - distance))


def twin_confidence_cap(evidence_confidence: float, claimed_confidence: float) -> float:
    """Confidence(DT) ≤ Confidence(Evidence)."""
    return min(claimed_confidence, evidence_confidence)


def verification_coverage(verified_count: int, applicable_count: int) -> float:
    """VC = |R_V| / |R|."""
    if applicable_count <= 0:
        return 1.0
    return max(0.0, min(1.0, verified_count / applicable_count))


def weighted_verification_coverage(
    verified_flags: Sequence[float],
    weights: Optional[Sequence[float]] = None,
) -> float:
    """VC_w = Σ w_i V_i / Σ w_i."""
    if not verified_flags:
        return 0.0
    weights = list(weights) if weights is not None else [1.0] * len(verified_flags)
    num = sum(w * v for w, v in zip(weights, verified_flags))
    den = sum(weights) or 1.0
    return num / den


def evidence_freshness(delta_t: float, lam: float = 0.01) -> float:
    """F_e(t) = e^{-λ Δt}."""
    return math.exp(-lam * max(0.0, delta_t))


def entropy(probabilities: Sequence[float]) -> float:
    """H(X) = -Σ P(x) log P(x)."""
    h = 0.0
    for p in probabilities:
        if p > 0:
            h -= p * math.log(p)
    return h


def confidence_from_entropy(probabilities: Sequence[float]) -> float:
    """Conf(X) = 1 - H(X)/H_max."""
    if not probabilities:
        return 0.0
    h = entropy(probabilities)
    h_max = math.log(len(probabilities)) if len(probabilities) > 1 else 1.0
    if h_max <= 0:
        return 1.0
    return max(0.0, min(1.0, 1.0 - h / h_max))


def unknown_state_index(
    identity: float,
    configuration: float,
    topology: float,
    evidence: float,
    environment: float,
    weights: Optional[Sequence[float]] = None,
) -> float:
    """U_t weighted unknown-state index. Unknown ≠ Normal."""
    values = [identity, configuration, topology, evidence, environment]
    weights = list(weights) if weights is not None else [1.0] * 5
    num = sum(w * max(0.0, min(1.0, v)) for w, v in zip(weights, values))
    den = sum(weights) or 1.0
    return num / den


def event_priority(
    impact: float,
    uncertainty: float,
    propagation: float,
    irreversibility: float,
) -> float:
    """Π_i = I · U · P · R."""
    return max(0.0, impact) * max(0.0, uncertainty) * max(0.0, propagation) * max(
        0.0, irreversibility
    )


def normalize_priorities(priorities: Sequence[float]) -> list[float]:
    """Normalize priorities to [0,1] by max."""
    peak = max(priorities) if priorities else 0.0
    if peak <= 0:
        return [0.0 for _ in priorities]
    return [p / peak for p in priorities]


def node_criticality(
    dependency_centrality: float,
    capability_impact: float,
    propagation_potential: float,
    recovery_difficulty: float,
    weights: Optional[Sequence[float]] = None,
) -> float:
    """C_i = w1 D + w2 I + w3 P + w4 R."""
    values = [
        dependency_centrality,
        capability_impact,
        propagation_potential,
        recovery_difficulty,
    ]
    weights = list(weights) if weights is not None else [0.25, 0.25, 0.25, 0.25]
    return sum(w * v for w, v in zip(weights, values))


def resilience_score(
    detection: float,
    isolation: float,
    adaptation: float,
    recovery: float,
    verification: float,
    weights: Optional[Sequence[float]] = None,
) -> float:
    """R_Ω = w_D D + w_I I + w_A A + w_R R + w_V V."""
    values = [detection, isolation, adaptation, recovery, verification]
    weights = list(weights) if weights is not None else [0.2] * 5
    return sum(w * max(0.0, min(1.0, v)) for w, v in zip(weights, values))


def recovery_quality(capability_after: float, capability_before: float) -> float:
    """Q_R = Capability_after / Capability_before."""
    if capability_before <= 0:
        return 1.0 if capability_after >= 0 else 0.0
    return capability_after / capability_before


def eventuality_risk(
    probability: float,
    impact: float,
    propagation: float,
    uncertainty: float,
    recovery_difficulty: float = 1.0,
) -> float:
    """Risk_Ω(E_i) = P · I · P' · U · R."""
    return (
        max(0.0, probability)
        * max(0.0, impact)
        * max(0.0, propagation)
        * max(0.0, uncertainty)
        * max(0.0, recovery_difficulty)
    )


def objective_score(
    capability: float,
    verification: float,
    resilience: float,
    trust: float,
    digital_consistency: float,
    lifecycle_readiness: float,
    gaps: float,
    uncertainty: float,
    transition_cost: float,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """J = w_C C + w_V V + w_R R + w_T T + w_D D + w_L L - w_G G - w_U U - w_K K."""
    w = {
        "C": 1.0,
        "V": 1.0,
        "R": 1.0,
        "T": 1.0,
        "D": 1.0,
        "L": 1.0,
        "G": 1.0,
        "U": 1.0,
        "K": 1.0,
    }
    if weights:
        w.update(weights)
    return (
        w["C"] * capability
        + w["V"] * verification
        + w["R"] * resilience
        + w["T"] * trust
        + w["D"] * digital_consistency
        + w["L"] * lifecycle_readiness
        - w["G"] * gaps
        - w["U"] * uncertainty
        - w["K"] * transition_cost
    )


@dataclass
class TrustFactors:
    identity: float
    authorization: float
    configuration_integrity: float
    evidence_integrity: float


def trust_state(factors: TrustFactors) -> float:
    """T_t = f(I, A, K, E). Trust ≠ Connectivity; Identity ≠ Authorization."""
    # Multiplicative: weak identity or auth collapses trust.
    return (
        max(0.0, min(1.0, factors.identity))
        * max(0.0, min(1.0, factors.authorization))
        * max(0.0, min(1.0, factors.configuration_integrity))
        * max(0.0, min(1.0, factors.evidence_integrity))
    )


def transition_feasibility(
    compatibility: float,
    safety: float,
    verification: float,
    configuration: float,
    trust: float,
    resources: float,
    weights: Optional[Sequence[float]] = None,
) -> float:
    """Φ(T_i) feasibility score."""
    values = [compatibility, safety, verification, configuration, trust, resources]
    weights = list(weights) if weights is not None else [1.0] * 6
    # Mandatory hard gates: safety and trust must be non-zero for feasibility > 0
    if safety <= 0 or trust < 0:
        return 0.0
    num = sum(w * max(0.0, min(1.0, v)) for w, v in zip(weights, values))
    den = sum(weights) or 1.0
    return num / den
