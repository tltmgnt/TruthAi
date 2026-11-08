# APL-Ω — Topology-Governed Advanced Payload Launcher

**Design Once. Model Everything. Detect Every Gap. Govern Every Transition. Verify Every State. Continuously Evolve.**

APL-Ω is a comprehensive **state, gap, transition, risk, and recovery framework** for topology-governed payload-launcher architectures. TGA-Ω is the intelligence layer that continuously evaluates system topology and governs material state changes.

> **Scope.** “All eventualities” means the major system, payload, interface, digital, autonomy, verification, cyber, lifecycle, failure, acquisition, and technology-transition states the architecture can recognize and govern — **not** weapon-employment scenarios.

Part of the [TruthAi](.) topology-governed intelligence platform.


## Domain neutral TruthAi assurance core

A separate dependency-free `truthai_assurance` package now implements versioned
claim/artifact exchange, missingness-aware capability coverage, transitive review
invalidation, and a snapshot-bound local authorization and estimated-cost gate.
It is a bounded research prototype, not the complete frontier AI operating system.

```sh
python -m truthai_assurance demo
```

The synthetic two-domain rehearsal demonstrates a missing capability blocking the
local gate and a changed artifact reopening dependent claims. It does not call
MathOS or ManufacturingOS, authenticate reviewers, execute external actions, or
provide scientific certification. See [scope, contracts and acceptance checks](Docs/TruthAi/ASSURANCE_CORE.md).

## Master principle

\[
\textbf{APL-Ω} = \textbf{A Payload Interface That Can Continuously Understand Its Own Evolution}
\]

\[
S_t \xrightarrow{\Delta G} \Delta_\Omega \xrightarrow{\text{Risk + Constraints}} T_i \xrightarrow{\text{Verification}} S_{t+1}
\]

**No uncontrolled material state transition.** Every material change must be observable, classifiable, and governed.

## What this repository contains

| Path | Purpose |
|------|---------|
| `apl_omega/` | Python package: state, topology, eventualities, formulas, TGA-Ω engine |
| `data/master_eventuality_matrix.json` | Master matrix **E-001 … E-080** |
| `Docs/APL-Omega/` | Framework documentation (matrices, invariants, math) |
| `examples/closed_loop_demo.py` | Observe → Model → Detect → … → Monitor demo |
| `tests/` | Unit tests for matrix, formulas, and governance engine |

## Universal eventuality model

Every eventuality is:

\[
\mathcal{E}_i = (S^{\text{before}}, \theta, \Delta G, \Delta_\Omega, C, T, V, S^{\text{after}})
\]

\[
\text{Eventuality} = \text{State} \rightarrow \text{Change} \rightarrow \text{Gap} \rightarrow \text{Decision} \rightarrow \text{Verified State}
\]

TGA-Ω continuously evaluates \(G_t = (V_t, E_t, W_t)\) and detects \(\Delta G = G_{t+1} - G_t\).

## Event classification (Ω0–Ω7)

| Class | Meaning |
|-------|---------|
| Ω0 | Normal |
| Ω1 | Capability expansion |
| Ω2 | Capability degradation |
| Ω3 | Configuration change |
| Ω4 | Topology disruption |
| Ω5 | Verification gap |
| Ω6 | Recovery / transition |
| Ω7 | **Unknown / uncertain** (explicitly represented) |

Critical rule: **Unknown ≠ Normal**.

## Closed loop

```
REAL SYSTEM → OBSERVE → DIGITAL TWIN → TOPOLOGY MODEL → TGA-Ω ANALYSIS
                → NORMAL | GAP | ANOMALY
                → TRANSITION / ISOLATE → VERIFY → RECONFIGURE → NEW STATE → OBSERVE
```

## Quick start

```bash
# From repository root
python -m pip install -e .
python examples/closed_loop_demo.py
python -m unittest discover -s tests -v
```

```python
from apl_omega import TGAOmegaEngine

engine = TGAOmegaEngine()
report = engine.analyze_eventuality("E-006")  # Unknown payload
print(report.decision, report.uncertainty, report.risk)
```

## Domain coverage

The master matrix spans: Normal · Payload · Interface · Digital · Power · Autonomy · Cyber · Safety · Verification · Configuration · Failure · Recovery · Maintenance · Supply Chain · Technology · Platform · Environment · Human · Data · Training · Acquisition · Production · Lifecycle · Retirement.

Supporting matrices cover payload readiness, interface compatibility, cyber trust, failure topology (F1–F7), resilience, digital-twin consistency, technology insertion, obsolescence (Type A–E), platform generations, environment bands, human–system authority, acquisition lifecycle, and supply-chain topology.

## Core invariants

- Trust ≠ Connectivity
- Identity ≠ Authorization
- Digital twin confidence ≤ evidence confidence
- System intelligence does not eliminate human authority
- Component failure ≠ system failure unless topology proves criticality
- Stale evidence must not silently become current evidence

## Stack roles

| Layer | Role |
|-------|------|
| APL | Payload interface |
| Digital twin | Persistent representation |
| Digital thread | Lifecycle continuity |
| Verification | Evidence |
| Cybersecurity | Trust boundaries |
| Configuration management | Baseline integrity |
| **TGA-Ω** | Topology-governed intelligence connecting all of them |

## License / status

Research and architecture framework for topology-governed systems engineering. Extend via additional eventualities, platform-specific topology packs, and verification evidence adapters.
