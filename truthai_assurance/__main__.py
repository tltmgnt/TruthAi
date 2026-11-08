"""Run a synthetic two-domain integration rehearsal without external calls."""
import argparse
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from .contracts import Artifact, Authorization, Capability, Claim, Dependency
from .gaps import analyze_capabilities
from .registry import Registry


def demo(now=None):
    """Illustrative exchange records, not live MathOS or ManufacturingOS adapters."""
    instant = now or datetime.now(timezone.utc)
    if instant.tzinfo is None:
        raise ValueError('timezone required')
    observed = instant.isoformat()
    expires = (instant + timedelta(days=1)).isoformat()
    registry = Registry()
    # These hand-calculated fixtures are not outputs retrieved from other repositories.
    fixtures = {'math': b'{"equation":"2x+5=13","solution":4}',
                'manufacturing': b'{"pieces":3,"total_cost":225,"unit_cost":75}'}
    for domain, payload in fixtures.items():
        registry.add(Artifact(domain + '-artifact', hashlib.sha256(payload).hexdigest(),
                              'synthetic:' + domain, 'fixture arithmetic only', observed, expires))
        registry.verify_artifact(domain + '-artifact', payload, observed)
        registry.add(Claim(domain, domain, 'Synthetic calculation record is ready for local review',
                           'fixture arithmetic only', 'fixture-author', ('Synthetic input',)))
        registry.link(Dependency(domain, domain + '-artifact', 'supports'))
        registry.review(domain, 'declared-reviewer', observed, expires)
    registry.add(Claim('integration', 'software-assurance', 'Both fixture records are current',
                       'local exchange rehearsal only', 'fixture-author'))
    registry.link(Dependency('integration', 'math'))
    registry.link(Dependency('integration', 'manufacturing'))
    registry.review('integration', 'declared-reviewer', observed, expires)
    auth = Authorization('demo-operator', 'integration', 'export-review',
                         registry.snapshot('integration'), observed, expires, 1.0)
    inputs = {'current': [Capability('verification', 'observed', 1.0)],
              'targets': {'verification': 1.0, 'recovery': 1.0}, 'weights': {}}
    missing = analyze_capabilities(**inputs)
    missing_gate = registry.gate(auth, 'demo-operator', 'integration', 'export-review', 0.1, inputs, observed)
    inputs['current'].append(Capability('recovery', 'observed', 1.0))
    before = registry.gate(auth, 'demo-operator', 'integration', 'export-review', 0.1, inputs, observed)
    changed_payload = b'{"equation":"2x+5=13","solution":5}'
    changed = replace(registry.nodes['math-artifact'], sha256=hashlib.sha256(changed_payload).hexdigest())
    affected = registry.replace(changed)
    after = registry.gate(auth, 'demo-operator', 'integration', 'export-review', 0.1, inputs, observed)
    return {'synthetic': True, 'live_repository_integration': False,
            'missing_capability_report': missing, 'missing_capability_gate': missing_gate,
            'before_change': before, 'affected_by_change': affected, 'after_change': after,
            'report': registry.report(observed)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['demo'])
    parser.parse_args()
    print(json.dumps(demo(), sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
