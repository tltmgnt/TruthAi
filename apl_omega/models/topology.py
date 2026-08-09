"""Weighted attributed dynamic topology model.

G_t = (V_t, E_t, W_t, X_t)
ΔG_t = G_{t+1} ⊖ G_t
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


@dataclass
class Node:
    node_id: str
    kind: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    health: float = 1.0  # [0, 1]
    criticality: float = 0.5


@dataclass
class Edge:
    source: str
    target: str
    relation: str
    weight: float = 1.0
    integrity: float = 1.0  # D_ij dependency integrity
    attributes: Dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> Tuple[str, str, str]:
        return (self.source, self.target, self.relation)


@dataclass
class TopologyDiff:
    """Structured difference between two topology graphs."""

    added_nodes: List[str] = field(default_factory=list)
    removed_nodes: List[str] = field(default_factory=list)
    changed_nodes: List[str] = field(default_factory=list)
    added_edges: List[Tuple[str, str, str]] = field(default_factory=list)
    removed_edges: List[Tuple[str, str, str]] = field(default_factory=list)
    changed_edges: List[Tuple[str, str, str]] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not (
            self.added_nodes
            or self.removed_nodes
            or self.changed_nodes
            or self.added_edges
            or self.removed_edges
            or self.changed_edges
        )

    def magnitude(self) -> float:
        return float(
            len(self.added_nodes)
            + len(self.removed_nodes)
            + 0.5 * len(self.changed_nodes)
            + len(self.added_edges)
            + len(self.removed_edges)
            + 0.5 * len(self.changed_edges)
        )


class TopologyGraph:
    """APL ecosystem topology G_t = (V, E, W, X)."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[Tuple[str, str, str], Edge] = {}

    def add_node(self, node: Node) -> None:
        self.nodes[node.node_id] = node

    def remove_node(self, node_id: str) -> None:
        self.nodes.pop(node_id, None)
        doomed = [k for k in self.edges if node_id in (k[0], k[1])]
        for k in doomed:
            del self.edges[k]

    def add_edge(self, edge: Edge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError(
                f"Edge endpoints must exist: {edge.source} -> {edge.target}"
            )
        self.edges[edge.key] = edge

    def remove_edge(self, source: str, target: str, relation: str) -> None:
        self.edges.pop((source, target, relation), None)

    def neighbors(self, node_id: str) -> Set[str]:
        return {e.target for e in self.edges.values() if e.source == node_id}

    def reachability(self, node_id: str) -> Set[str]:
        seen: Set[str] = set()
        stack = [node_id]
        while stack:
            current = stack.pop()
            for nxt in self.neighbors(current):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return seen

    def dependency_integrity(self) -> float:
        """D_G weighted average of edge integrity."""
        if not self.edges:
            return 1.0
        num = sum(e.weight * e.integrity for e in self.edges.values())
        den = sum(e.weight for e in self.edges.values())
        return num / den if den else 1.0

    def propagation_score(self, node_id: str) -> float:
        """P_F(v_i) = sum of weights over reachable nodes."""
        reach = self.reachability(node_id)
        score = 0.0
        for edge in self.edges.values():
            if edge.source == node_id or edge.target in reach:
                score += edge.weight
        return score

    def topology_distance(self, other: "TopologyGraph") -> float:
        """Normalized topology distance d_G(G_t, G*)."""
        diff = self.diff(other)
        denom = max(len(self.nodes) + len(self.edges) + len(other.nodes) + len(other.edges), 1)
        return diff.magnitude() / denom

    def diff(self, other: "TopologyGraph") -> TopologyDiff:
        """Structured difference ΔG = G_other ⊖ G_self (toward other)."""
        result = TopologyDiff()
        self_ids = set(self.nodes)
        other_ids = set(other.nodes)
        result.added_nodes = sorted(other_ids - self_ids)
        result.removed_nodes = sorted(self_ids - other_ids)
        for nid in sorted(self_ids & other_ids):
            a, b = self.nodes[nid], other.nodes[nid]
            if a.kind != b.kind or a.health != b.health or a.attributes != b.attributes:
                result.changed_nodes.append(nid)

        self_edges = set(self.edges)
        other_edges = set(other.edges)
        result.added_edges = sorted(other_edges - self_edges)
        result.removed_edges = sorted(self_edges - other_edges)
        for key in sorted(self_edges & other_edges):
            a, b = self.edges[key], other.edges[key]
            if a.weight != b.weight or a.integrity != b.integrity or a.attributes != b.attributes:
                result.changed_edges.append(key)
        return result

    def clone(self) -> "TopologyGraph":
        g = TopologyGraph()
        for n in self.nodes.values():
            g.add_node(
                Node(
                    n.node_id,
                    n.kind,
                    dict(n.attributes),
                    n.health,
                    n.criticality,
                )
            )
        for e in self.edges.values():
            g.add_edge(
                Edge(
                    e.source,
                    e.target,
                    e.relation,
                    e.weight,
                    e.integrity,
                    dict(e.attributes),
                )
            )
        return g

    @classmethod
    def baseline_apl(cls) -> "TopologyGraph":
        """Minimal APL baseline topology for examples and tests."""
        g = cls()
        for nid, kind, crit in [
            ("platform", "platform", 0.9),
            ("launcher", "launcher", 1.0),
            ("interface", "interface", 0.95),
            ("digital_twin", "digital", 0.8),
            ("power", "energy", 0.85),
            ("safety", "safety", 1.0),
            ("cyber", "cyber", 0.95),
            ("config_baseline", "configuration", 0.9),
            ("human_authority", "human", 1.0),
        ]:
            g.add_node(Node(nid, kind, criticality=crit))

        relations = [
            ("platform", "launcher", "hosts", 1.0),
            ("launcher", "interface", "exposes", 1.0),
            ("interface", "digital_twin", "mirrors", 0.9),
            ("power", "launcher", "energizes", 1.0),
            ("safety", "launcher", "constrains", 1.0),
            ("cyber", "digital_twin", "trusts", 0.95),
            ("config_baseline", "launcher", "authorizes", 1.0),
            ("human_authority", "launcher", "authorizes", 1.0),
        ]
        for src, tgt, rel, w in relations:
            g.add_edge(Edge(src, tgt, rel, weight=w, integrity=1.0))
        return g
