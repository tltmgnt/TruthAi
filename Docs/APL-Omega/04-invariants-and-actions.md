# Invariants, Priority, and Event-to-Action

## Permanent invariants

| ID | Rule |
|----|------|
| I_safety | Safety invariants hold across transitions |
| I_security | Trust ≠ Connectivity |
| I_configuration | Baseline integrity preserved or explicitly rebaselined |
| I_verification | Stale evidence must not silently become current |
| I_authority | System intelligence does not eliminate human authority |
| I_unknown | Unknown ≠ Normal; Unknown → Uncertainty |
| I_twin | Twin confidence ≤ evidence confidence |
| I_failure | Component failure ≠ system failure unless topology proves criticality |
| I_control | No uncontrolled material state transition |

## Priority

\[
\Pi_i = Impact \times Uncertainty \times Propagation \times Irreversibility
\]

High-priority events combine high impact, high uncertainty, large dependency propagation, and difficult recovery.

## Event-to-action matrix

| Event state | Auto analysis | Human/system review | Verification | Return state |
|-------------|---------------|---------------------|--------------|--------------|
| Normal | ✓ | As required | Existing evidence | Normal |
| Known degradation | ✓ | As required | As required | Degraded/Recovered |
| Unknown | ✓ | ✓ | Required | Validated |
| Configuration change | ✓ | As required | Required | Qualified |
| Cyber anomaly | ✓ | ✓ | Required | Trusted/Restricted |
| Safety violation | ✓ | ✓ | Required | Safe |
| Failure | ✓ | As required | As required | Recovered/Restricted |
| New technology | ✓ | ✓ | Required | Qualified |
| Obsolescence | ✓ | ✓ | Required | Reconfigured |

## TGA-Ω decision vocabulary

`Maintain` · `Investigate` · `Restrict` · `Isolate` · `Reconfigure` · `Reverify` · `Recover` · `Rebaseline` · `Escalate`

These are **analysis/governance** outputs, not employment actions.

## Final master principle

APL-Ω represents not only what the system is, but what it could become, what prevents that state, which relationships must change, what evidence is required, and whether the resulting configuration remains within the governing architecture.

\[
\textbf{Observe}\rightarrow\textbf{Model}\rightarrow\textbf{Detect}\rightarrow\textbf{Analyze}\rightarrow\textbf{Gap}\rightarrow\textbf{Transition}\rightarrow\textbf{Verify}\rightarrow\textbf{Rebaseline}\rightarrow\textbf{Monitor}
\]
