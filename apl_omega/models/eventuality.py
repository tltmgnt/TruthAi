"""Eventuality representation.

E_i = (S_before, trigger, ΔTopology, Gap, Constraint, Response, Verification, S_after)

Eventuality = State → Change → Gap → Decision → Verified State
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from apl_omega.models.state import DecisionAction, OmegaClass, SystemState
from apl_omega.models.topology import TopologyDiff


@dataclass
class Eventuality:
    """Universal TGA-Ω eventuality model."""

    eventuality_id: str
    domain: str
    name: str
    topology_effect: str
    tga_response: str
    desired_state: str
    omega_class: OmegaClass = OmegaClass.NORMAL
    trigger: str = ""
    constraints: List[str] = field(default_factory=list)
    automatic_analysis: bool = True
    human_review_required: bool = False
    verification_required: bool = False
    attributes: Dict[str, Any] = field(default_factory=dict)

    # Runtime / evaluation fields
    state_before: Optional[SystemState] = None
    state_after: Optional[SystemState] = None
    topology_diff: Optional[TopologyDiff] = None
    gap_score: float = 0.0
    priority: float = 0.0
    risk: float = 0.0
    decision: Optional[DecisionAction] = None

    def to_record(self) -> Dict[str, Any]:
        return {
            "id": self.eventuality_id,
            "domain": self.domain,
            "eventuality": self.name,
            "topology_effect": self.topology_effect,
            "tga_response": self.tga_response,
            "desired_state": self.desired_state,
            "omega_class": self.omega_class.value,
            "trigger": self.trigger,
            "constraints": list(self.constraints),
            "automatic_analysis": self.automatic_analysis,
            "human_review_required": self.human_review_required,
            "verification_required": self.verification_required,
        }


@dataclass
class TransitionResult:
    """Governed transition outcome S_t → S_{t+1}."""

    permitted: bool
    action: DecisionAction
    reason: str
    state_after: Optional[SystemState] = None
    verification_required: bool = False
    violated_invariants: List[str] = field(default_factory=list)
    feasibility: float = 0.0
