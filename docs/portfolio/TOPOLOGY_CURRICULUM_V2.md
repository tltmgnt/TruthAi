# Topology compatibility and curriculum v2 — TruthAi

Version 2 adapts the explicit-molecular-graph teaching pattern to this repository's actual role. This is documentation and a learning/decision framework; it introduces no mathematical engine, runtime dependency or operational permission.

## Repository decision

| Question | Repository-specific answer |
| --- | --- |
| Architectural role | foundational platform |
| Minimum useful mathematics | Typed directed graphs and explicit state transitions |
| Relationships to preserve | Claim dependencies, artifact snapshots and review bindings |
| Concrete operation / capstone | Change one upstream artifact and trace which dependent reviews must reopen |
| Necessity and scope boundary | Category theory is optional design language until explicit composition laws and tests are needed |

The decision is a source-based recommendation, not measured proof that a new specialty improves this repository. Start with the existing implementation and compare any proposed abstraction against a simpler alternative.

## Six-criterion compatibility scorecard

Complete one scorecard per proposed candidate and per concrete operation. Leave unmeasured entries unknown. Scores are human judgments from 0 (no fit) to 5 (strong evidenced fit); unknown is not zero. Do not sum an incomplete card. A total out of 30 is a heuristic, not adoption approval, and feasibility or necessity can veto a high total.

| Criterion | Score | Required evidence |
| --- | --- | --- |
| Structural compatibility | Not yet scored | Map the repository objects and the relationships above without losing direction, labels, units or missingness. |
| Transformation support | Not yet scored | Demonstrate the capstone operation on accepted and rejected inputs. |
| Invariant preservation | Not yet scored | State the property preserved and supply a counterexample or perturbation. |
| Computational feasibility | Not yet scored | Measure size, time and memory on bounded fixtures; record limits. |
| Integration compatibility | Not yet scored | Verify existing schemas, APIs and neighboring contracts remain compatible. |
| Mathematical necessity | Not yet scored | Compare with typed directed graphs and explicit state transitions and explain the additional capability, if any. |

## Curriculum

Prerequisites: basic programming, sets, functions and graph vocabulary. Work in six competency-gated sessions, approximately 60–90 minutes each; empirical evaluation is a separate research activity.

| Session | Learning objective | Exercise | Completion evidence |
| --- | --- | --- | --- |
| 1. Model | Identify claim dependencies, artifact snapshots and review bindings. | Draw a minimal valid example and one excluded relationship. | Annotated object/relation inventory with explicit assumptions. |
| 2. Contract | Distinguish schema validity from substantive correctness. | Trace validation and propose malformed, missing and boundary inputs. | Input-to-rejection table grounded in current source. |
| 3. Operation | Explain typed directed graphs and explicit state transitions. | Change one upstream artifact and trace which dependent reviews must reopen. | Hand trace compared with existing software, or a clearly labeled specification when no runtime exists. |
| 4. Preservation | State what a transformation must preserve. | Rename identifiers, reorder records, then alter one meaningful relation; predict each effect under the actual contract. | Separate invariant, expected change and unsupported transformation. |
| 5. Comparison | Justify mathematical necessity and cost. | Complete the six-criterion card for the existing approach and one proposed alternative; record unknowns honestly. | Evidence-backed recommendation with baseline and explicit veto conditions. |
| 6. Reproduction | Communicate the bounded result. | Reproduce the capstone using existing offline fixtures and record software version, inputs, outputs and limitations. | Reviewable notebook or report distinguishing computation, replay, independent evaluation and authorization. |

## Source-linked reading laboratory

The table is a guided selection of source lines, not an assertion that the whole repository is covered. Line numbers refer to the inspected source blob `b06331ff6d5c894050a76cc716b577bdb39b8bd4` in [truthai_assurance/registry.py](../../truthai_assurance/registry.py). Recheck anchors after source changes.

| Line | Statement | Learning check |
| --- | --- | --- |
| [16](../../truthai_assurance/registry.py#L16) | `class Registry:` | State the input/output contract and trace one normal and one failing case. |
| [19](../../truthai_assurance/registry.py#L19) | `def __init__(self):` | State the input/output contract and trace one normal and one failing case. |
| [28](../../truthai_assurance/registry.py#L28) | `def nodes(self):` | State the input/output contract and trace one normal and one failing case. |
| [29](../../truthai_assurance/registry.py#L29) | `return MappingProxyType(self._nodes)` | Predict the returned value and distinguish a computed result from authorization. |
| [32](../../truthai_assurance/registry.py#L32) | `def events(self):` | State the input/output contract and trace one normal and one failing case. |
| [33](../../truthai_assurance/registry.py#L33) | `return tuple(dict(event) for event in self._events)` | Predict the returned value and distinguish a computed result from authorization. |
| [35](../../truthai_assurance/registry.py#L35) | `def _event(self, operation, subject, affected):` | State the input/output contract and trace one normal and one failing case. |
| [40](../../truthai_assurance/registry.py#L40) | `def affected(self, subject):` | State the input/output contract and trace one normal and one failing case. |
| [43](../../truthai_assurance/registry.py#L43) | `raise ValueError('unknown subject')` | Construct the triggering input and explain why rejection preserves the contract. |
| [51](../../truthai_assurance/registry.py#L51) | `return sorted(found)` | Predict the returned value and distinguish a computed result from authorization. |
| [53](../../truthai_assurance/registry.py#L53) | `def _changed(self, subject, operation):` | State the input/output contract and trace one normal and one failing case. |
| [57](../../truthai_assurance/registry.py#L57) | `return affected` | Predict the returned value and distinguish a computed result from authorization. |
| [59](../../truthai_assurance/registry.py#L59) | `def add(self, node):` | State the input/output contract and trace one normal and one failing case. |
| [61](../../truthai_assurance/registry.py#L61) | `raise ValueError('new unique Artifact or Claim required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [63](../../truthai_assurance/registry.py#L63) | `raise ValueError('node limit reached')` | Construct the triggering input and explain why rejection preserves the contract. |
| [67](../../truthai_assurance/registry.py#L67) | `def replace(self, node):` | State the input/output contract and trace one normal and one failing case. |
| [69](../../truthai_assurance/registry.py#L69) | `raise ValueError('existing node required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [71](../../truthai_assurance/registry.py#L71) | `raise ValueError('node type cannot change')` | Construct the triggering input and explain why rejection preserves the contract. |
| [74](../../truthai_assurance/registry.py#L74) | `return self._changed(node.id, 'replace')` | Predict the returned value and distinguish a computed result from authorization. |
| [76](../../truthai_assurance/registry.py#L76) | `def _closure(self, subject):` | State the input/output contract and trace one normal and one failing case. |
| [78](../../truthai_assurance/registry.py#L78) | `raise ValueError('unknown subject')` | Construct the triggering input and explain why rejection preserves the contract. |
| [85](../../truthai_assurance/registry.py#L85) | `return sorted(found)` | Predict the returned value and distinguish a computed result from authorization. |
| [87](../../truthai_assurance/registry.py#L87) | `def link(self, dependency):` | State the input/output contract and trace one normal and one failing case. |
| [89](../../truthai_assurance/registry.py#L89) | `raise ValueError('Dependency required')` | Construct the triggering input and explain why rejection preserves the contract. |
## Assessment and verification

A learner must explain the model, trace the capstone, identify a counterexample and state the scope boundary. Assess these four competencies equally; a numerical score cannot compensate for an unsupported scientific or operational claim.

Relevant existing checks:

- [tests/test_engine.py](../../tests/test_engine.py)
- [tests/test_formulas.py](../../tests/test_formulas.py)
- [tests/test_master_matrix.py](../../tests/test_master_matrix.py)

Follow [README](../../README.md) for environment and installed-package instructions. Read scripts before execution; source-reading exercises do not authorize provider calls, model downloads, live orders, hardware actions or messages. Synthetic fixtures establish software behavior only. This documentation change does not report those exercises as already executed.

## Interoperability and adoption gate

Retain explicit domain contracts. Shared assurance records should refer to domain evidence and its assumptions rather than relabeling graph reachability, homology, statistical calibration and epistemic acceptance as interchangeable quantities. The canonical ResearchOs controller remains owned by ResearchOs; this curriculum does not create another controller fork.

Adopt additional mathematics only after a versioned experiment demonstrates a useful operation, the scorecard has evidence, the simpler baseline is inadequate and existing conformance checks remain satisfied. Category theory is optional design language until explicit composition laws and tests are needed.
