# Domain Eventuality Matrices

## Payload

| Payload State | Classification | Required Action |
|---------------|----------------|-----------------|
| Known + compatible + verified | Green | Maintain |
| Known + compatible + unverified | Verification gap | Do not promote |
| Known + partially compatible | Topology gap | Identify interface changes |
| Unknown | Identity gap | Resolve identity |
| Modified / software / hardware change | Config / digital / physical transition | Reverify / reassess / revalidate |
| Obsolete / damaged / removed | Lifecycle / health / contraction | Plan / maintain / reconcile |

## Interface

Interface vector: \(I=(I_P,I_D,I_E,I_S,I_C,I_V)\)

Strict compatibility: \(\Gamma_I=\prod I_j\). Graded: \(\Gamma_I=\sum w_j I_j\).

Conditions map physical × digital validity onto Qualified / gap classes (digital, physical, energy, safety, trust, evidence) or Degraded topology.

## Cyber

| Event | Topological meaning | Response |
|-------|---------------------|----------|
| Valid authentication | Trust edge established | Continue |
| Authentication failure | Trust edge absent | Isolate/hold |
| Integrity / unknown software / unauthorized mod | Trust/identity/governance gap | Contain / prevent / reject |
| Recovery | Trust restored | Reverify |

Invariants: **Trust ≠ Connectivity**, **Identity ≠ Authorization**.

## Verification evidence states

\(V=\{\text{Unknown},\text{Under Review},\text{Partially Verified},\text{Verified},\text{Expired},\text{Invalidated}\}\)

Progression is ordered; configuration change or anomaly forces **reverification**. Stale evidence must not silently become current evidence.

## Failure types (topological)

| Type | Meaning |
|------|---------|
| F1 Local | One node |
| F2 Interface | One relationship |
| F3 Dependency | Multiple downstream nodes |
| F4 Cascading | Propagation across dependencies |
| F5 Observability | Cannot reliably determine own state |
| F6 Configuration | Physical vs authoritative digital disagree |
| F7 Verification | Evidence no longer establishes configuration |

**Component failure ≠ system failure** unless topology shows mission-critical dependency.

## Digital twin

\(DT=\{\text{Synchronized},\text{Lagging},\text{Inconsistent},\text{Unknown},\text{Recovered}\}\)

Invariant: digital representation must not claim greater certainty than available evidence.

## Technology insertion

Discovery → Characterization → Topology mapping → Gap analysis → Dependency analysis → Cyber assessment → Verification planning → Prototype → Integration → Qualification → Configuration → Lifecycle

## Obsolescence replacement types

| Type | Meaning |
|------|---------|
| A | Drop-in compatible |
| B | Interface-compatible with verification |
| C | Requires adapter |
| D | Requires architecture modification |
| E | Requires capability redesign |

## Platform

Common architecture + platform-specific implementation across existing, late-block, future, modernized, and mixed-fleet topologies.

## Environment bands

Normal · Marginal · Constrained · Unknown · Recovery — never treat Unknown as Normal.

## Human–system

System intelligence does not eliminate human authority. Missing authorization blocks transition.

## Acquisition / supply / lifecycle

Single architecture spans concept → prototype → qualification → production → fielding → sustainment → retirement, with supply-chain edges as first-class topology and lifecycle:

Design → Manufacture → Integrate → Verify → Deploy → Operate → Maintain → Upgrade → Reverify → Retire
