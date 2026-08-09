"""Universal APL-Ω system state representation.

S_t = (P_t, L_t, I_t, D_t, E_t, A_t, C_t, Q_t, K_t, F_t, R_t, M_t, T_t, H_t)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, Optional


class OmegaClass(str, Enum):
    """Master TGA-Ω event classification (Ω0–Ω7)."""

    NORMAL = "Ω0"
    CAPABILITY_EXPANSION = "Ω1"
    CAPABILITY_DEGRADATION = "Ω2"
    CONFIGURATION_CHANGE = "Ω3"
    TOPOLOGY_DISRUPTION = "Ω4"
    VERIFICATION_GAP = "Ω5"
    RECOVERY_TRANSITION = "Ω6"
    UNKNOWN_UNCERTAIN = "Ω7"


class LifecyclePhase(str, Enum):
    DESIGN = "design"
    MANUFACTURE = "manufacture"
    INTEGRATE = "integrate"
    VERIFY = "verify"
    DEPLOY = "deploy"
    OPERATE = "operate"
    MAINTAIN = "maintain"
    UPGRADE = "upgrade"
    REVERIFY = "reverify"
    RETIRE = "retire"


class VerificationEvidenceState(str, Enum):
    UNKNOWN = "unknown"
    UNDER_REVIEW = "under_review"
    PARTIALLY_VERIFIED = "partially_verified"
    VERIFIED = "verified"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"


class DigitalTwinState(str, Enum):
    SYNCHRONIZED = "synchronized"
    LAGGING = "lagging"
    INCONSISTENT = "inconsistent"
    UNKNOWN = "unknown"
    RECOVERED = "recovered"


class EnvironmentBand(str, Enum):
    NORMAL = "normal"
    MARGINAL = "marginal"
    CONSTRAINED = "constrained"
    UNKNOWN = "unknown"
    RECOVERY = "recovery"


class DecisionAction(str, Enum):
    """TGA-Ω decision outputs — analysis/governance, not employment."""

    MAINTAIN = "maintain"
    INVESTIGATE = "investigate"
    RESTRICT = "restrict"
    ISOLATE = "isolate"
    RECONFIGURE = "reconfigure"
    REVERIFY = "reverify"
    RECOVER = "recover"
    REBASELINE = "rebaseline"
    ESCALATE = "escalate"


@dataclass
class DimensionState:
    """Generic named dimension with readiness and confidence."""

    name: str
    value: str = "normal"
    readiness: float = 1.0  # [0, 1]
    confidence: float = 1.0  # [0, 1]
    attributes: Dict[str, Any] = field(default_factory=dict)

    def clamp(self) -> "DimensionState":
        self.readiness = max(0.0, min(1.0, self.readiness))
        self.confidence = max(0.0, min(1.0, self.confidence))
        return self


@dataclass
class SystemState:
    """Complete APL-Ω state vector S_t."""

    platform: DimensionState = field(default_factory=lambda: DimensionState("platform"))
    launcher: DimensionState = field(default_factory=lambda: DimensionState("launcher"))
    interface: DimensionState = field(default_factory=lambda: DimensionState("interface"))
    digital: DimensionState = field(default_factory=lambda: DimensionState("digital"))
    energy: DimensionState = field(default_factory=lambda: DimensionState("energy"))
    autonomy: DimensionState = field(default_factory=lambda: DimensionState("autonomy"))
    cyber: DimensionState = field(default_factory=lambda: DimensionState("cyber"))
    safety: DimensionState = field(default_factory=lambda: DimensionState("safety"))
    configuration: DimensionState = field(
        default_factory=lambda: DimensionState("configuration")
    )
    failure: DimensionState = field(default_factory=lambda: DimensionState("failure"))
    recovery: DimensionState = field(default_factory=lambda: DimensionState("recovery"))
    maintenance: DimensionState = field(
        default_factory=lambda: DimensionState("maintenance")
    )
    technology: DimensionState = field(
        default_factory=lambda: DimensionState("technology")
    )
    human: DimensionState = field(default_factory=lambda: DimensionState("human"))

    verification: VerificationEvidenceState = VerificationEvidenceState.UNKNOWN
    digital_twin: DigitalTwinState = DigitalTwinState.UNKNOWN
    environment: EnvironmentBand = EnvironmentBand.UNKNOWN
    lifecycle: LifecyclePhase = LifecyclePhase.DESIGN
    omega_class: OmegaClass = OmegaClass.UNKNOWN_UNCERTAIN

    def dimensions(self) -> Dict[str, DimensionState]:
        return {
            "platform": self.platform,
            "launcher": self.launcher,
            "interface": self.interface,
            "digital": self.digital,
            "energy": self.energy,
            "autonomy": self.autonomy,
            "cyber": self.cyber,
            "safety": self.safety,
            "configuration": self.configuration,
            "failure": self.failure,
            "recovery": self.recovery,
            "maintenance": self.maintenance,
            "technology": self.technology,
            "human": self.human,
        }

    def mean_readiness(self) -> float:
        dims = list(self.dimensions().values())
        return sum(d.readiness for d in dims) / len(dims)

    def mean_confidence(self) -> float:
        dims = list(self.dimensions().values())
        return sum(d.confidence for d in dims) / len(dims)

    def distance(self, other: "SystemState", weights: Optional[Dict[str, float]] = None) -> float:
        """State-space distance d_S(S_t, S*)."""
        weights = weights or {}
        total = 0.0
        weight_sum = 0.0
        for key, dim in self.dimensions().items():
            w = weights.get(key, 1.0)
            other_dim = other.dimensions()[key]
            delta = abs(dim.readiness - other_dim.readiness)
            if dim.value != other_dim.value:
                delta += 0.25
            total += w * delta
            weight_sum += w
        return total / weight_sum if weight_sum else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def ready_baseline(cls) -> "SystemState":
        """Canonical ready / S* baseline for monitoring."""
        state = cls(
            verification=VerificationEvidenceState.VERIFIED,
            digital_twin=DigitalTwinState.SYNCHRONIZED,
            environment=EnvironmentBand.NORMAL,
            lifecycle=LifecyclePhase.OPERATE,
            omega_class=OmegaClass.NORMAL,
        )
        for dim in state.dimensions().values():
            dim.value = "ready"
            dim.readiness = 1.0
            dim.confidence = 1.0
        state.cyber.value = "secure"
        state.safety.value = "safe"
        return state
