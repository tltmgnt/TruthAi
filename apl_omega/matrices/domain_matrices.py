"""Domain-specific eventuality matrices (payload, interface, cyber, failure, etc.)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


class FailureType(str, Enum):
    """Topological failure classification F1–F7."""

    F1_LOCAL = "F1"
    F2_INTERFACE = "F2"
    F3_DEPENDENCY = "F3"
    F4_CASCADING = "F4"
    F5_OBSERVABILITY = "F5"
    F6_CONFIGURATION = "F6"
    F7_VERIFICATION = "F7"


@dataclass(frozen=True)
class PayloadRow:
    payload_state: str
    classification: str
    required_action: str


PAYLOAD_MATRIX: List[PayloadRow] = [
    PayloadRow("Known + compatible + verified", "Green state", "Maintain"),
    PayloadRow("Known + compatible + unverified", "Verification gap", "Do not promote to qualified state"),
    PayloadRow("Known + partially compatible", "Topology gap", "Identify required interface changes"),
    PayloadRow("Unknown", "Identity gap", "Resolve identity"),
    PayloadRow("Modified", "Configuration change", "Reverify"),
    PayloadRow("Software updated", "Digital transition", "Reassess dependencies"),
    PayloadRow("Hardware replaced", "Physical transition", "Revalidate configuration"),
    PayloadRow("Obsolete", "Lifecycle gap", "Replacement planning"),
    PayloadRow("Damaged", "Health degradation", "Maintenance assessment"),
    PayloadRow("Removed", "Topology contraction", "Reconcile system graph"),
]


@dataclass(frozen=True)
class InterfaceRow:
    condition: str
    physical: str
    digital: str
    result: str


INTERFACE_MATRIX: List[InterfaceRow] = [
    InterfaceRow("Fully compatible", "Valid", "Valid", "Qualified"),
    InterfaceRow("Physical only", "Valid", "Invalid", "Digital gap"),
    InterfaceRow("Digital only", "Invalid", "Valid", "Physical gap"),
    InterfaceRow("Power mismatch", "Invalid", "Valid", "Energy gap"),
    InterfaceRow("Data mismatch", "Valid", "Invalid", "Digital gap"),
    InterfaceRow("Safety incompatibility", "Restricted", "Valid", "Safety gap"),
    InterfaceRow("Cyber incompatibility", "Valid", "Untrusted", "Trust gap"),
    InterfaceRow("Verification absent", "Valid", "Valid", "Evidence gap"),
    InterfaceRow("Interface degraded", "Partial", "Partial", "Degraded topology"),
]


@dataclass(frozen=True)
class CyberRow:
    event: str
    topological_meaning: str
    response: str


CYBER_MATRIX: List[CyberRow] = [
    CyberRow("Valid authentication", "Trust edge established", "Continue"),
    CyberRow("Authentication failure", "Trust edge absent", "Isolate/hold"),
    CyberRow("Configuration anomaly", "Expected edge changed", "Flag"),
    CyberRow("Integrity concern", "Trust confidence reduced", "Contain"),
    CyberRow("Unknown software", "Identity gap", "Prevent promotion"),
    CyberRow("Unauthorized modification", "Governance violation", "Reject transition"),
    CyberRow("Data anomaly", "Information edge questionable", "Validate"),
    CyberRow("Recovery", "Trust restored", "Reverify"),
]


@dataclass(frozen=True)
class ResilienceRow:
    failure: str
    local_recovery: str
    alternative_path: str
    reconfiguration: str
    reverification: str


RESILIENCE_MATRIX: List[ResilienceRow] = [
    ResilienceRow("Single node", "Yes", "Possible", "Possible", "As required"),
    ResilienceRow("Interface degradation", "Yes", "Possible", "Likely", "Required"),
    ResilienceRow("Digital failure", "Yes", "Possible", "Possible", "Required"),
    ResilienceRow("Power degradation", "Yes", "Possible", "Possible", "Required"),
    ResilienceRow("Sensor failure", "Yes", "Alternative sensing", "Possible", "As required"),
    ResilienceRow("Multiple failures", "Case-dependent", "Case-dependent", "Likely", "Required"),
    ResilienceRow("Unknown state", "No automatic promotion", "Human/system review", "Possible", "Required"),
]


TECHNOLOGY_INSERTION_STAGES: List[Tuple[str, str]] = [
    ("Discovery", "What is the technology?"),
    ("Characterization", "What capabilities does it provide?"),
    ("Topology mapping", "Where does it connect?"),
    ("Gap analysis", "What interfaces are missing?"),
    ("Dependency analysis", "What systems are affected?"),
    ("Cyber assessment", "What trust relationships change?"),
    ("Verification planning", "What evidence is required?"),
    ("Prototype", "Can the concept be demonstrated?"),
    ("Integration", "Can it operate within the architecture?"),
    ("Qualification", "Has required evidence been established?"),
    ("Configuration", "Has the baseline been updated?"),
    ("Lifecycle", "Can it be sustained?"),
]


STATE_MACHINE_PATH: List[str] = [
    "UNKNOWN",
    "IDENTIFIED",
    "COMPATIBILITY_ASSESSED",
    "VERIFICATION",
    "CONFIGURATION_CONTROL",
    "READY",
    "ACTIVE_SYSTEM_STATE",
]

STATE_MACHINE_BRANCHES: Dict[str, List[str]] = {
    "COMPATIBILITY_ASSESSED": ["INCOMPATIBLE"],
    "VERIFICATION": ["VERIFICATION_GAP"],
    "CONFIGURATION_CONTROL": ["CONFIGURATION_DRIFT"],
    "ACTIVE_SYSTEM_STATE": ["DEGRADED"],
    "DEGRADED": ["RECOVERY"],
    "RECOVERY": ["VERIFIED_STATE"],
}


CLOSED_LOOP: List[str] = [
    "OBSERVE",
    "MODEL",
    "DETECT",
    "ANALYZE",
    "GAP",
    "TRANSITION",
    "VERIFY",
    "REBASELINE",
    "MONITOR",
]


INVARIANTS: Dict[str, str] = {
    "I_safety": "Safety invariants must hold across transitions",
    "I_security": "Trust ≠ Connectivity",
    "I_configuration": "Baseline integrity must be preserved or explicitly rebaselined",
    "I_verification": "Stale evidence must not silently become current evidence",
    "I_authority": "System intelligence does not eliminate human authority",
    "I_unknown": "Unknown ≠ Normal; Unknown → Uncertainty",
    "I_twin": "Digital representation must not claim greater certainty than available evidence",
    "I_failure": "Component failure ≠ system failure unless topology proves criticality",
    "I_control": "No uncontrolled material state transition",
}
