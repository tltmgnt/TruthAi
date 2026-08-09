# Master Eventuality Matrix (E-001 … E-080)

Machine-readable source: [`data/master_eventuality_matrix.json`](../../data/master_eventuality_matrix.json)

Load via:

```python
from apl_omega.matrices import load_master_matrix, by_id, by_domain
```

## Columns

| Field | Meaning |
|-------|---------|
| ID | Stable eventuality identifier |
| Domain | State family |
| Eventuality | What happened |
| Topology Effect | ΔG description |
| TGA-Ω Response | Governed analysis/action |
| Desired State | Acceptable resulting state |
| Ω class | Ω0–Ω7 classification |

## Domain index

| Domain | IDs (representative) |
|--------|----------------------|
| Normal | E-001, E-002 |
| Payload | E-003 … E-006 |
| Interface | E-007 … E-010 |
| Digital | E-011 … E-013 |
| Power | E-014 … E-016 |
| Autonomy | E-017 … E-020 |
| Cyber | E-021 … E-025 |
| Safety | E-026 … E-029 |
| Verification | E-030 … E-033 |
| Configuration | E-034 … E-037 |
| Failure | E-038 … E-042 |
| Recovery | E-043 … E-045 |
| Maintenance | E-046 … E-048 |
| Supply Chain | E-049 … E-052 |
| Technology | E-053 … E-056 |
| Platform | E-057 … E-059 |
| Environment | E-060, E-061 |
| Human | E-062 … E-064 |
| Data | E-065 … E-067 |
| Training | E-068, E-069 |
| Acquisition | E-070 … E-072 |
| Production | E-073, E-074 |
| Lifecycle | E-075 … E-078 |
| Retirement | E-079, E-080 |

## State-transition machine

```
UNKNOWN → IDENTIFIED → COMPATIBILITY ASSESSED ─┬► INCOMPATIBLE
                                               ▼
                                         VERIFICATION ─┬► VERIFICATION GAP
                                                       ▼
                                         CONFIGURATION CONTROL ─┬► CONFIGURATION DRIFT
                                                                ▼
                                                              READY
                                                                ▼
                                                      ACTIVE SYSTEM STATE ─┬► DEGRADED → RECOVERY
                                                                           └──────────► VERIFIED STATE
```

**Critical rule:** No uncontrolled transition.
