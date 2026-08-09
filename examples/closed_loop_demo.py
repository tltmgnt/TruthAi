#!/usr/bin/env python3
"""Demonstrate the APL-Ω closed loop on selected eventualities."""

from __future__ import annotations

from apl_omega.engine.tga_omega import TGAOmegaEngine
from apl_omega.matrices.master import domain_summary


def main() -> None:
    engine = TGAOmegaEngine()
    print("APL-Ω / TGA-Ω Closed-Loop Demo")
    print("Domains:", domain_summary())
    print()

    for eid in ["E-001", "E-006", "E-022", "E-027", "E-041", "E-053"]:
        report = engine.closed_loop_step(eid)
        e = report.eventuality
        print(
            f"{e.eventuality_id} | {e.domain:12} | {e.name:40} | "
            f"{report.decision.value:12} | gap={report.gap:.3f} "
            f"U={report.uncertainty:.3f} Π={report.priority:.3f} "
            f"risk={report.risk:.3f}"
        )

    print()
    print("Principle: No uncontrolled material state transition.")
    print("Unknown ≠ Normal. Trust ≠ Connectivity. Identity ≠ Authorization.")


if __name__ == "__main__":
    main()
