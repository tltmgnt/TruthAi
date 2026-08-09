"""TGA-Ω decision engine.

A_Ω: (S_t, G_t, E_t) → Δ_Ω → T → V → S_{t+1}

Observe → Model → Detect → Measure Gap → Evaluate Risk →
Select Valid Transition → Verify → Rebaseline
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from apl_omega.engine.invariants import all_satisfied, check_invariants, violated_names
from apl_omega.formulas.metrics import (
    TrustFactors,
    event_priority,
    eventuality_risk,
    objective_score,
    topological_gap,
    transition_feasibility,
    trust_state,
    unknown_state_index,
)
from apl_omega.matrices.master import by_id, load_master_matrix
from apl_omega.models.eventuality import Eventuality, TransitionResult
from apl_omega.models.state import (
    DecisionAction,
    OmegaClass,
    SystemState,
    VerificationEvidenceState,
)
from apl_omega.models.topology import TopologyDiff, TopologyGraph


RESPONSE_TO_ACTION: Dict[str, DecisionAction] = {
    "Monitor": DecisionAction.MAINTAIN,
    "Maintain baseline": DecisionAction.MAINTAIN,
    "Maintain": DecisionAction.MAINTAIN,
    "Compatibility analysis": DecisionAction.INVESTIGATE,
    "Reconcile topology": DecisionAction.RECONFIGURE,
    "Reverification": DecisionAction.REVERIFY,
    "Quarantine/assessment": DecisionAction.ISOLATE,
    "Confirm evidence": DecisionAction.REVERIFY,
    "Gap analysis": DecisionAction.INVESTIGATE,
    "Reject/redirect": DecisionAction.RESTRICT,
    "Detect gap": DecisionAction.INVESTIGATE,
    "Configuration analysis": DecisionAction.INVESTIGATE,
    "Dependency analysis": DecisionAction.INVESTIGATE,
    "Flag discrepancy": DecisionAction.ESCALATE,
    "Capability-gap analysis": DecisionAction.RESTRICT,
    "Isolate/analyze": DecisionAction.ISOLATE,
    "Verify integration": DecisionAction.REVERIFY,
    "Recalculate capability": DecisionAction.RECONFIGURE,
    "Enter controlled state": DecisionAction.RESTRICT,
    "Isolate": DecisionAction.ISOLATE,
    "Contain/verify": DecisionAction.ISOLATE,
    "Block transition": DecisionAction.RESTRICT,
    "Monitor/isolate": DecisionAction.ISOLATE,
    "Prevent transition": DecisionAction.RESTRICT,
    "Cross-check": DecisionAction.INVESTIGATE,
    "Restrict capability": DecisionAction.RESTRICT,
    "Identify missing evidence": DecisionAction.REVERIFY,
    "Arbitration/review": DecisionAction.ESCALATE,
    "Requalification": DecisionAction.REVERIFY,
    "Detect/reconcile": DecisionAction.RECONFIGURE,
    "Resolve identity": DecisionAction.INVESTIGATE,
    "Impact analysis": DecisionAction.INVESTIGATE,
    "Cascading-gap analysis": DecisionAction.ESCALATE,
    "Recalculate dependencies": DecisionAction.RECONFIGURE,
    "Reconcile": DecisionAction.RECONFIGURE,
    "Identify blind spots": DecisionAction.INVESTIGATE,
    "Evaluate transition": DecisionAction.RECOVER,
    "Generate alternatives": DecisionAction.INVESTIGATE,
    "Verify": DecisionAction.REVERIFY,
    "Update model": DecisionAction.REBASELINE,
    "Recalculate state": DecisionAction.INVESTIGATE,
    "Lifecycle alert": DecisionAction.ESCALATE,
    "Technology-gap analysis": DecisionAction.INVESTIGATE,
    "Resilience analysis": DecisionAction.INVESTIGATE,
    "Qualification": DecisionAction.REVERIFY,
    "Technology insertion analysis": DecisionAction.INVESTIGATE,
    "Identify adapter/upgrade": DecisionAction.RECONFIGURE,
    "Transition analysis": DecisionAction.RECONFIGURE,
    "Rebaseline": DecisionAction.REBASELINE,
    "Model future topology": DecisionAction.INVESTIGATE,
    "Recalculate margins": DecisionAction.INVESTIGATE,
    "Restrict affected function": DecisionAction.RESTRICT,
    "Require resolution": DecisionAction.ESCALATE,
    "Do not transition": DecisionAction.RESTRICT,
    "Identify training gap": DecisionAction.INVESTIGATE,
    "Restrict applicable functions": DecisionAction.RESTRICT,
    "Root-cause/topology analysis": DecisionAction.INVESTIGATE,
    "Replan": DecisionAction.RECONFIGURE,
    "Verify conformity": DecisionAction.REVERIFY,
    "Contain/reinspect": DecisionAction.ISOLATE,
    "Predictive analysis": DecisionAction.INVESTIGATE,
    "Transition planning": DecisionAction.RECONFIGURE,
    "Replacement analysis": DecisionAction.INVESTIGATE,
    "Reconcile graph": DecisionAction.REBASELINE,
}


@dataclass
class AnalysisReport:
    eventuality: Eventuality
    gap: float
    uncertainty: float
    priority: float
    risk: float
    trust: float
    decision: DecisionAction
    topology_diff: Optional[TopologyDiff] = None
    invariants_ok: bool = True
    violated_invariants: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


class TGAOmegaEngine:
    """Topology-Governed Analysis engine for APL-Ω eventualities."""

    def __init__(
        self,
        state: Optional[SystemState] = None,
        graph: Optional[TopologyGraph] = None,
        target_state: Optional[SystemState] = None,
        target_graph: Optional[TopologyGraph] = None,
    ) -> None:
        self.state = state or SystemState.ready_baseline()
        self.graph = graph or TopologyGraph.baseline_apl()
        self.target_state = target_state or SystemState.ready_baseline()
        self.target_graph = target_graph or TopologyGraph.baseline_apl()
        self.history: List[AnalysisReport] = []

    def catalog(self) -> List[Eventuality]:
        return load_master_matrix()

    def detect_gap(self) -> float:
        return topological_gap(
            self.state, self.target_state, self.graph, self.target_graph
        )

    def compute_uncertainty(self) -> float:
        return unknown_state_index(
            identity=1.0 - self.state.configuration.confidence,
            configuration=1.0 - self.state.configuration.readiness,
            topology=1.0 - self.graph.dependency_integrity(),
            evidence=0.0
            if self.state.verification == VerificationEvidenceState.VERIFIED
            else 0.6,
            environment=0.8 if self.state.environment.value == "unknown" else 0.1,
        )

    def compute_trust(self) -> float:
        return trust_state(
            TrustFactors(
                identity=self.state.configuration.confidence,
                authorization=self.state.human.readiness,
                configuration_integrity=self.state.configuration.readiness,
                evidence_integrity=1.0
                if self.state.verification == VerificationEvidenceState.VERIFIED
                else 0.4,
            )
        )

    def analyze_eventuality(
        self,
        eventuality_id: str,
        *,
        topology_diff: Optional[TopologyDiff] = None,
        impact: float = 0.5,
        propagation: float = 0.5,
        irreversibility: float = 0.5,
        probability: float = 0.5,
        human_authority_present: bool = True,
    ) -> AnalysisReport:
        eventuality = by_id(eventuality_id)
        gap = self.detect_gap()
        uncertainty = self.compute_uncertainty()
        if eventuality.omega_class == OmegaClass.UNKNOWN_UNCERTAIN:
            uncertainty = max(uncertainty, 0.75)

        priority = event_priority(impact, uncertainty, propagation, irreversibility)
        risk = eventuality_risk(
            probability, impact, propagation, uncertainty, irreversibility
        )
        trust = self.compute_trust()
        action = RESPONSE_TO_ACTION.get(
            eventuality.tga_response, DecisionAction.INVESTIGATE
        )

        # Unknown never auto-promotes to normal
        if eventuality.omega_class == OmegaClass.UNKNOWN_UNCERTAIN:
            if action == DecisionAction.MAINTAIN:
                action = DecisionAction.INVESTIGATE

        # Safety / cyber hard responses
        if eventuality.domain in {"Safety", "Cyber"} and eventuality.omega_class in {
            OmegaClass.TOPOLOGY_DISRUPTION,
            OmegaClass.UNKNOWN_UNCERTAIN,
        }:
            if action not in {
                DecisionAction.ISOLATE,
                DecisionAction.RESTRICT,
                DecisionAction.ESCALATE,
            }:
                action = DecisionAction.RESTRICT

        proposed = self._propose_state(eventuality, action)
        inv = check_invariants(
            self.state,
            proposed,
            self.graph,
            human_authority_present=human_authority_present,
            trust_score=trust,
            evidence_confidence=self.state.mean_confidence(),
            twin_confidence=min(self.state.digital.confidence, self.state.mean_confidence()),
            safety_ok=eventuality.domain != "Safety"
            or "violat" not in eventuality.name.lower(),
        )
        ok = all_satisfied(inv)
        if not ok and action not in {
            DecisionAction.RESTRICT,
            DecisionAction.ISOLATE,
            DecisionAction.ESCALATE,
        }:
            action = DecisionAction.RESTRICT

        report = AnalysisReport(
            eventuality=eventuality,
            gap=gap,
            uncertainty=uncertainty,
            priority=priority,
            risk=risk,
            trust=trust,
            decision=action,
            topology_diff=topology_diff,
            invariants_ok=ok,
            violated_invariants=violated_names(inv),
            notes=[
                f"class={eventuality.omega_class.value}",
                f"response={eventuality.tga_response}",
                f"desired={eventuality.desired_state}",
            ],
        )
        eventuality.gap_score = gap
        eventuality.priority = priority
        eventuality.risk = risk
        eventuality.decision = action
        eventuality.topology_diff = topology_diff
        self.history.append(report)
        return report

    def evaluate_transition(
        self,
        action: DecisionAction,
        *,
        compatibility: float = 1.0,
        safety: float = 1.0,
        verification: float = 1.0,
        configuration: float = 1.0,
        resources: float = 1.0,
        phi_min: float = 0.5,
        human_authority_present: bool = True,
    ) -> TransitionResult:
        trust = self.compute_trust()
        phi = transition_feasibility(
            compatibility, safety, verification, configuration, trust, resources
        )
        proposed = self.state
        # Non-mutating proposal for invariant check
        from copy import deepcopy

        proposed = deepcopy(self.state)
        if action == DecisionAction.RESTRICT:
            proposed.launcher.readiness = min(proposed.launcher.readiness, 0.4)
            proposed.omega_class = OmegaClass.CAPABILITY_DEGRADATION
        elif action == DecisionAction.ISOLATE:
            proposed.cyber.value = "isolated"
            proposed.cyber.readiness = min(proposed.cyber.readiness, 0.2)
        elif action == DecisionAction.RECOVER:
            proposed.recovery.value = "recovering"
        elif action == DecisionAction.REBASELINE:
            proposed.configuration.value = "rebaselined"

        inv = check_invariants(
            self.state,
            proposed,
            self.graph,
            human_authority_present=human_authority_present,
            trust_score=trust,
            evidence_confidence=self.state.mean_confidence(),
            twin_confidence=self.state.digital.confidence,
            safety_ok=safety > 0,
        )
        violated = violated_names(inv)
        permitted = phi >= phi_min and all_satisfied(inv)
        reason = "Transition permitted" if permitted else "Transition blocked by constraints"
        if violated:
            reason = f"Invariant violation: {', '.join(violated)}"
        elif phi < phi_min:
            reason = f"Feasibility {phi:.2f} below minimum {phi_min:.2f}"

        return TransitionResult(
            permitted=permitted,
            action=action,
            reason=reason,
            state_after=proposed if permitted else None,
            verification_required=action
            in {
                DecisionAction.REVERIFY,
                DecisionAction.RECOVER,
                DecisionAction.REBASELINE,
                DecisionAction.RECONFIGURE,
            },
            violated_invariants=violated,
            feasibility=phi,
        )

    def apply_transition(self, result: TransitionResult) -> SystemState:
        if not result.permitted or result.state_after is None:
            raise RuntimeError(f"Cannot apply blocked transition: {result.reason}")
        self.state = result.state_after
        return self.state

    def select_best_action(
        self,
        candidates: List[DecisionAction],
        scores: Optional[Dict[DecisionAction, Dict[str, float]]] = None,
    ) -> DecisionAction:
        """T* = argmax_{T_i ∈ T_valid} J(T_i)."""
        uncertainty = self.compute_uncertainty()
        # Hard governance: high uncertainty forbids automatic Maintain
        if uncertainty > 0.7:
            cautious = [
                a
                for a in candidates
                if a
                in {
                    DecisionAction.INVESTIGATE,
                    DecisionAction.RESTRICT,
                    DecisionAction.ISOLATE,
                    DecisionAction.ESCALATE,
                }
            ]
            if cautious:
                candidates = cautious

        best_action = candidates[0]
        best_j = float("-inf")
        for action in candidates:
            metrics = (scores or {}).get(action, {})
            j = objective_score(
                capability=metrics.get("capability", self.state.mean_readiness()),
                verification=metrics.get("verification", 0.8),
                resilience=metrics.get("resilience", 0.7),
                trust=metrics.get("trust", self.compute_trust()),
                digital_consistency=metrics.get("digital", 0.8),
                lifecycle_readiness=metrics.get("lifecycle", 0.7),
                gaps=metrics.get("gaps", self.detect_gap()),
                uncertainty=metrics.get("uncertainty", uncertainty),
                transition_cost=metrics.get("cost", 0.2),
            )
            if uncertainty > 0.7 and action in {
                DecisionAction.RESTRICT,
                DecisionAction.ISOLATE,
                DecisionAction.INVESTIGATE,
                DecisionAction.ESCALATE,
            }:
                j += 0.5
            if j > best_j:
                best_j = j
                best_action = action
        return best_action

    def closed_loop_step(self, eventuality_id: str) -> AnalysisReport:
        """Execute one Observe→…→Monitor cycle for a catalog eventuality."""
        report = self.analyze_eventuality(eventuality_id)
        transition = self.evaluate_transition(
            report.decision,
            human_authority_present=True,
            safety=0.0
            if report.eventuality.domain == "Safety"
            and "violat" in report.eventuality.name.lower()
            else 1.0,
        )
        if transition.permitted and report.decision in {
            DecisionAction.MAINTAIN,
            DecisionAction.RECOVER,
            DecisionAction.REBASELINE,
            DecisionAction.RECONFIGURE,
            DecisionAction.REVERIFY,
        }:
            # Maintain does not mutate; others may
            if report.decision != DecisionAction.MAINTAIN:
                self.apply_transition(transition)
        report.notes.append(f"transition={transition.reason}")
        return report

    def _propose_state(
        self, eventuality: Eventuality, action: DecisionAction
    ) -> SystemState:
        from copy import deepcopy

        proposed = deepcopy(self.state)
        proposed.omega_class = eventuality.omega_class
        if action == DecisionAction.RESTRICT:
            proposed.launcher.readiness = min(proposed.launcher.readiness, 0.5)
        if action == DecisionAction.ISOLATE:
            proposed.cyber.value = "isolated"
        if eventuality.verification_required:
            if proposed.verification == VerificationEvidenceState.VERIFIED:
                proposed.verification = VerificationEvidenceState.UNDER_REVIEW
        return proposed
