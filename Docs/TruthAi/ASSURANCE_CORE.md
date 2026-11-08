# TruthAi shared assurance core

The `truthai_assurance` package implements explicit capability coverage, versioned
exchange records, a bounded dependency graph, and snapshot-bound local review.
It has no runtime dependencies. It is separate from `apl_omega` and has no connection
to equipment, brokers, model APIs, or repository administration.

## Run the synthetic integration rehearsal

```sh
python -m truthai_assurance demo
python -m unittest discover -s tests -v
```

The demo exchanges two synthetic domain records (linear-equation arithmetic and
manufacturing cost arithmetic) through the same contracts. These are illustrative
fixtures, not live adapters importing MathOS or ManufacturingOS. It checks actual
fixture bytes against declared SHA256 values, links the artifacts to scoped claims
and a downstream integration claim, and records local reviews in dependency order.
A missing recovery capability blocks the local export gate. Supplying an observed
capability permits it; changing an artifact then reopens the dependent claims and
blocks the stale authorization.

Exit 0 means the rehearsal ran, not that a real system is approved. Inspect
`synthetic`, `live_repository_integration`, `before_change`, `after_change` and
`execution_performed`. The command does not upload reports or call external systems.
Use only synthetic inputs in public CI logs.

## Shared contracts and exchange

`Artifact`, `Claim`, `Dependency`, `Capability`, `VerificationResult` and
`Authorization` are immutable dataclasses. `record(value)` produces an exact v1
JSON-compatible envelope. `from_record(envelope)` validates the version, type and
exact fields and reconstructs the dataclass. Unknown fields, schemas and types
fail instead of silently dropping information. Domain, scope, owner and assumptions
are retained. All six envelope types use `schema_version: 1`.

```python
import json
from truthai_assurance import Claim, from_record, record

claim = Claim('example', 'mathematics', 'Example statement',
              'declared assumptions only', 'author', ('Synthetic example',))
assert from_record(json.loads(json.dumps(record(claim)))) == claim
```

Imported records are data, not trusted registry state. `Registry.add` accepts only
claims and artifacts. Importing a verification result does not install it as a
review; importing an artifact never marks its contents checked. Supply actual bytes
to `verify_artifact` and record local reviews through the registry.

## Missingness and capability comparison

Targets define the required capability universe. Every target is inspected, including
those absent from current observations. States are `observed`, `unmeasured`,
`unavailable`, `failed`, plus the report-only state `absent`. Only observed records
carry a finite normalized value in [0, 1]. Other states never receive invented zero
measurements.

`measured_shortfall = sqrt(sum(weight * max(0, target - observed_value)^2))`

Weights must be finite, strictly positive and reference known targets. Surplus cannot
offset another capability's deficit. Coverage reports the observed fraction;
`total_shortfall` is null unless every target is observed. `ready` requires full
coverage and no shortfall. Empty target maps are invalid. Extra capabilities cannot
inflate coverage. Values are supplied assessments, not calibrated probabilities or
measured scientific utility.

## Dependencies and invalidation

`Dependency(source, target)` means the source requires the target. `supports` also
requires a current prerequisite. `contradicts` conservatively blocks review until
explicitly removed or resolved through a separate process. The software does not
infer contradiction truth or relevance. Endpoints must exist; only claims declare
dependencies. Self-links, duplicate edges and directed cycles are rejected.

`affected(subject)` reports the subject and all transitive dependents. A snapshot
binds the complete dependency closure, contract fields, edges and local monotonic
revisions. Replacements, edge additions/removals, artifact checks and review changes
advance revisions. Restoring previous bytes or removing a newly added edge does not
resurrect previous reviews or authorizations. Even a successful recheck or identical
replacement conservatively requires dependent review again.

Every status query reevaluates prerequisites, artifact validity and review validity at
the supplied aware timestamp. Artifacts use `NEEDS_EVIDENCE` or `INTEGRITY_CHECKED`.
Claims use `NEEDS_REVIEW` or `REVIEW_RECORDED`. The latter means only that local
review declarations and prerequisites remain current. It does not establish scientific
truth, mathematical correctness, empirical validity or certification.

Review bottom-up after evidence changes: check bytes, review direct claims, then
review their dependents. Reviewer names must differ from owners but are not
authenticated identities. Historical review results remain visible as stale; no
approval or expiry is automatically renewed. Upstream re-review invalidates dependent
reviews even when data is unchanged. A fresh review does not renew old authorization.

## Local authorization and estimated cost

`Registry.gate` checks the requested principal, subject and action against an
`Authorization`, verifies the full snapshot and validity interval, requires a current
claim review, recomputes capability coverage, and compares estimated cost with the
maximum. A caller-supplied `ready: true` report is not accepted. Denials include
explicit reasons. No action is executed.

This is a local policy rehearsal, not an execution gateway. Authorization, identity,
capabilities and cost estimates are caller-provided declarations. There is no identity
provider, signature verification, budget reservation, cumulative spend accounting,
concurrency control, actual usage metering, or time-of-check/time-of-use protection.
Do not wire its output directly to consequential external actions. A real executor
needs authenticated policy, atomic budgets, snapshot rechecks and reconciliation.

## State and report boundaries

The registry is in memory, bounded to 256 nodes and 2048 edges. Status traversal
memoizes shared dependencies. `report(now)` exports contracts, dependencies, reviews,
statuses and sequential events. Reports and event history are mutable by a process
owner and are not an authenticated audit store. Raw payload bytes are not retained,
but sources, statements, scopes and reviewer names are included; protect sensitive
reports and do not publish them as public CI artifacts.

Reports support inspection at a fixed timestamp but are not resumable trust stores.
Restarting requires artifact rechecking and local review. Timestamps are caller-supplied;
a real service requires a trusted clock. Exchange helpers accept Python objects,
not hostile file/network JSON ingestion. Hashes establish content consistency only.

## Validation and remaining milestones

Tests cover target-only dimensions, missingness, malformed/non-finite values,
contract roundtrips, untrusted import, hash mismatch, expiry, transitive invalidation,
rollback, edge changes, contradictions, reviewer separation, stale authorization,
budget checks and the complete synthetic two-domain rehearsal. Existing APL tests
remain part of the full suite. Software checks do not validate the larger architecture.

Next milestones are actual version-pinned MathOS/ManufacturingOS adapters; durable
transactional storage and recovery; authenticated reviewer trust with revocation;
a separate authenticated executor with atomic budgets; held-out matched-budget
benchmarks; and domain-specific digital-twin calibration and empirical acceptance.

This implementation changes no repository visibility, settings, secrets, branch
protection, schedulers, equipment interfaces or paid-service configuration.
