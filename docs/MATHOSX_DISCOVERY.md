# MathOS × research discovery adapter — TruthAi

This optional **offline, human-controlled** adapter was ported from [MathOS × PR #39](https://github.com/tltmgnt/MathOS/pull/39), source commit 98b9f39acedc9c0c2ebb9f265a615f2f9df7de89. It is not connected to the host project's runtime or any production, trading, medical, defense, or physical systems.

## What it does

The adapter provides 56 traceable mathematical research questions across seven frontiers, four directions (invent, conjecture, unify, foundations), and two depths (research and radical). Two exact offline probes examine *finite* interventional abstraction and parity constraint obstructions. Results are explicitly **NOT_CERTIFIED**, with no claim of novel results, independently verified proof, or broader domain effectiveness.

Human reviewers may record **useful/not_useful** evidence for a question; a simple Beta-smoothed heuristic and exploration bonus reprioritizes the question list on subsequent runs. The ratings are not truth probabilities and the program does **not** generate source edits, merge PRs, or advance claims. Reviewers must explicitly commit any feedback; CI is read-only.

## Commands

```sh
python -m unittest discover -s tests -p 'test_mathosx_discovery.py' -v
python -m mathosx.discovery --direction all --depth all --limit 16 --output-dir artifacts/mathosx
python -m mathosx.discovery --rate-question causal-abstraction:invent:research \\
  --outcome useful --evidence-ref evidence/review-001.json --reviewer local-reviewer
```

This repo may develop domain-specific research questions later, but the initial 56 questions are **mathematics-level generic questions**, not demonstrated or automatically customized theories for TruthAi. Independent prior-art checks, formal proof, empirical studies, responsible domain expertise, and human review remain necessary.

The workflow runs on relevant pull requests or manual dispatch only, with read-only permissions, no secrets, no paid model calls, no scheduled cost, no autonomous code updates, and no proof-status modification. See `mathosx/discovery.py` for exact methods, invariants and bounded scopes.
