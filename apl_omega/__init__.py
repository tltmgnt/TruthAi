"""
APL-Ω — Topology-Governed Advanced Payload Launcher Eventuality Framework.

TGA-Ω provides topology-governed intelligence that recognizes and governs
system, payload, interface, digital, autonomy, verification, cyber,
lifecycle, failure, acquisition, and technology-transition states.

Scope: architectural state governance — not weapon-employment scenarios.
"""

from apl_omega.models.state import SystemState, OmegaClass
from apl_omega.models.topology import TopologyGraph
from apl_omega.models.eventuality import Eventuality
from apl_omega.engine.tga_omega import TGAOmegaEngine

__version__ = "0.1.0"
__all__ = [
    "SystemState",
    "OmegaClass",
    "TopologyGraph",
    "Eventuality",
    "TGAOmegaEngine",
]
