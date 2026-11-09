# TruthAi

TruthAi is a research platform for topology-governed claim, evidence and capability workflows across heterogeneous AI systems and domain tools. The broader operating-system vision is a research objective, not a demonstrated frontier-model or autonomous infrastructure capability.

## Implemented platform core

`truthai_assurance` provides typed artifacts and claims, explicit dependency relationships, snapshot-bound local review, freshness/integrity checks, conservative change propagation and capability-gap accounting. It is offline and does not establish source authenticity or scientific correctness. See [assurance core](Docs/TruthAi/ASSURANCE_CORE.md) and [portfolio integration](docs/portfolio/INTEGRATION.md).

The authoritative TECT controller lives in [ResearchOs](https://github.com/tltmgnt/ResearchOs). This repository's platform integration CI installs pinned public Spatial, Formal and ResearchOs packages and exercises their actual functions with the local TruthAi registry. A changed network input changes the model-check result and invalidates the prior review. Inputs are synthetic and correlated; independent reproduction remains open.

## Install and run

```sh
python -m pip install .
python -m truthai_assurance demo
python -m unittest discover -s tests -v
```

The distribution retains its existing `apl-omega` name for compatibility. Its APL application modules remain a separate legacy application; [their existing overview](docs/legacy/APL_OVERVIEW.md) is preserved. The domain-neutral assurance package does not control equipment or financial accounts.

## Framework map and next experiments

[All repositories](https://github.com/tltmgnt/ResearchOs/blob/main/docs/portfolio/INDEX.md) · [Contract and mathematical boundaries](https://github.com/tltmgnt/ResearchOs/blob/main/docs/INTEROPERABILITY.md) · [Curriculum](https://github.com/tltmgnt/ResearchOs/blob/main/docs/portfolio/CURRICULUM.md) · [New repository proposals](https://github.com/tltmgnt/ResearchOs/blob/main/docs/portfolio/NEW_REPOSITORIES.md).

Real provider access, externally established identity/key custody, independent empirical evaluation and deployment approval are not completed by these software checks. No paid service, schedule or external communication is enabled by this change.

**∞**
