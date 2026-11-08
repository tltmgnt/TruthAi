"""Missingness-aware capability comparison over an explicit target universe."""
import math
from .contracts import Capability, number, text


def analyze_capabilities(current, targets, weights=None):
    """Keep unknown coverage separate from measured shortfall; never fill missing values."""
    if not isinstance(targets, dict) or not targets:
        raise ValueError('nonempty target mapping required')
    weights = {} if weights is None else weights
    if not isinstance(weights, dict) or set(weights) - set(targets):
        raise ValueError('weights must reference target capabilities')
    indexed = {}
    for capability in current:
        if not isinstance(capability, Capability) or capability.id in indexed:
            raise ValueError('unique Capability records required')
        indexed[capability.id] = capability
    details, measured, total = {}, 0, 0.0
    blocked = False
    for key, target in sorted(targets.items()):
        text(key)
        number(target)
        weight = weights.get(key, 1.0)
        number(weight, minimum=1e-12, maximum=1e12)
        item = indexed.get(key)
        state = item.state if item else 'absent'
        deficit = None
        if state == 'observed':
            measured += 1
            deficit = max(0.0, target - item.value)
            total += weight * deficit ** 2
        blocked = blocked or state != 'observed' or (deficit is not None and deficit > 0)
        details[key] = {'state': state, 'target': target, 'deficit': deficit}
    complete = measured == len(targets)
    return {'schema_version': 1, 'capabilities': details,
            'coverage': measured / len(targets),
            'measured_shortfall': math.sqrt(total),
            'total_shortfall': math.sqrt(total) if complete else None,
            'ready': not blocked,
            'extra_capabilities': sorted(set(indexed) - set(targets))}
