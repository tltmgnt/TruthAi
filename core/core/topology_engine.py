"""
TruthAI Topology Engine — thin adapter over APL-Ω TGA-Ω.

Prefer importing from `apl_omega` directly for new code.
"""

from apl_omega.engine.tga_omega import TGAOmegaEngine
from apl_omega.models.topology import Edge, Node, TopologyGraph
from apl_omega.models.state import SystemState

__all__ = ["TGAOmegaEngine", "TopologyGraph", "Node", "Edge", "SystemState"]
