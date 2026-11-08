"""Local dependency graph with snapshot-bound review and conservative invalidation.

No external execution, identity authentication, or scientific certification occurs.
"""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
from types import MappingProxyType
from .contracts import (Artifact, Authorization, Claim, Dependency,
                        VerificationResult, digest, number, record, timestamp)

MAX_NODES = 256
MAX_EDGES = 2048


class Registry:
    """Bounded in-memory registry; source-to-target means source requires target."""

    def __init__(self):
        self._nodes = {}
        self._edges = set()
        self._revisions = {}
        self._checks = {}
        self._reviews = {}
        self._events = []

    @property
    def nodes(self):
        return MappingProxyType(self._nodes)

    @property
    def events(self):
        return tuple(dict(event) for event in self._events)

    def _event(self, operation, subject, affected):
        self._events.append({'sequence': len(self._events) + 1,
                             'operation': operation, 'subject': subject,
                             'affected': tuple(sorted(affected))})

    def affected(self, subject):
        """Return every transitive dependent including subject, without recursion."""
        if subject not in self._nodes:
            raise ValueError('unknown subject')
        found, pending = {subject}, [subject]
        while pending:
            target = pending.pop()
            for edge in self._edges:
                if edge.target == target and edge.source not in found:
                    found.add(edge.source)
                    pending.append(edge.source)
        return sorted(found)

    def _changed(self, subject, operation):
        self._revisions[subject] = self._revisions.get(subject, 0) + 1
        affected = self.affected(subject)
        self._event(operation, subject, affected)
        return affected

    def add(self, node):
        if not isinstance(node, (Artifact, Claim)) or node.id in self._nodes:
            raise ValueError('new unique Artifact or Claim required')
        if len(self._nodes) >= MAX_NODES:
            raise ValueError('node limit reached')
        self._nodes[node.id] = node
        self._changed(node.id, 'add')

    def replace(self, node):
        if not isinstance(node, (Artifact, Claim)) or node.id not in self._nodes:
            raise ValueError('existing node required')
        if type(node) is not type(self._nodes[node.id]):
            raise ValueError('node type cannot change')
        self._nodes[node.id] = node
        self._checks.pop(node.id, None)
        return self._changed(node.id, 'replace')

    def _closure(self, subject):
        if subject not in self._nodes:
            raise ValueError('unknown subject')
        found, pending = set(), [subject]
        while pending:
            item = pending.pop()
            if item not in found:
                found.add(item)
                pending.extend(edge.target for edge in self._edges if edge.source == item)
        return sorted(found)

    def link(self, dependency):
        if not isinstance(dependency, Dependency):
            raise ValueError('Dependency required')
        if dependency.source not in self._nodes or dependency.target not in self._nodes:
            raise ValueError('dependency endpoints must exist')
        if not isinstance(self._nodes[dependency.source], Claim):
            raise ValueError('only claims declare dependencies')
        if dependency in self._edges or len(self._edges) >= MAX_EDGES:
            raise ValueError('duplicate dependency or edge limit')
        if dependency.source in self._closure(dependency.target):
            raise ValueError('circular support or dependency rejected')
        self._edges.add(dependency)
        return self._changed(dependency.source, 'link')

    def unlink(self, dependency):
        if dependency not in self._edges:
            raise ValueError('unknown dependency')
        self._edges.remove(dependency)
        return self._changed(dependency.source, 'unlink')

    def snapshot(self, subject):
        """Bind the full dependency closure, including local monotonic revisions."""
        closure = self._closure(subject)
        return digest({'nodes': {key: {'record': record(self._nodes[key]),
                                      'revision': self._revisions[key]} for key in closure},
                       'edges': [asdict(edge) for edge in sorted(self._edges,
                                 key=lambda e: (e.source, e.target, e.relation))
                                 if edge.source in closure]})

    def verify_artifact(self, subject, payload, now):
        """Check supplied bytes; do not trust a caller-supplied verified boolean."""
        node = self._nodes.get(subject)
        if not isinstance(node, Artifact) or not isinstance(payload, bytes):
            raise ValueError('artifact ID and bytes required')
        instant = timestamp(now)
        valid = (timestamp(node.observed_at) <= instant < timestamp(node.expires_at)
                 and hashlib.sha256(payload).hexdigest() == node.sha256)
        self._checks.pop(subject, None)
        self._changed(subject, 'artifact_check')
        if valid:
            self._checks[subject] = self.snapshot(subject)
        return valid

    def _input_gaps(self, subject, now, cache=None):
        cache = {} if cache is None else cache
        edges = [edge for edge in self._edges if edge.source == subject]
        gaps = []
        if not edges:
            gaps.append('missing_dependencies')
        for edge in edges:
            if edge.relation == 'contradicts':
                gaps.append('contradictory_dependency:' + edge.target)
            elif self._status(edge.target, now, cache)['status'] not in {'INTEGRITY_CHECKED', 'REVIEW_RECORDED'}:
                gaps.append('dependency_not_current:' + edge.target)
        return sorted(gaps)

    def review(self, subject, reviewer, now, expires_at):
        """Record a local review declaration after checking every prerequisite."""
        node = self._nodes.get(subject)
        if not isinstance(node, Claim):
            raise ValueError('claim required')
        timestamp(now)
        if reviewer == node.owner or self._input_gaps(subject, now):
            raise ValueError('separate reviewer and current prerequisites required')
        VerificationResult(subject, self.snapshot(subject), reviewer, node.scope, now, expires_at)
        self._changed(subject, 'review')
        result = VerificationResult(subject, self.snapshot(subject), reviewer,
                                    node.scope, now, expires_at)
        self._reviews[subject] = result
        return result

    def status(self, subject, now):
        """Re-evaluate freshness and transitive prerequisites on every query."""
        return self._status(subject, now, {})

    def _status(self, subject, now, cache):
        if subject in cache:
            return cache[subject]
        instant = timestamp(now)
        node = self._nodes.get(subject)
        if node is None:
            raise ValueError('unknown subject')
        if isinstance(node, Artifact):
            current = timestamp(node.observed_at) <= instant < timestamp(node.expires_at)
            checked = self._checks.get(subject) == self.snapshot(subject)
            state = 'INTEGRITY_CHECKED' if current and checked else 'NEEDS_EVIDENCE'
            cache[subject] = {'subject': subject, 'status': state,
                              'reasons': [] if state == 'INTEGRITY_CHECKED' else ['missing_check_or_outside_validity']}
            return cache[subject]
        gaps = self._input_gaps(subject, now, cache)
        review = self._reviews.get(subject)
        if review is None:
            gaps.append('missing_review')
        elif review.snapshot != self.snapshot(subject):
            gaps.append('stale_review_snapshot')
        elif not timestamp(review.reviewed_at) <= instant < timestamp(review.expires_at):
            gaps.append('review_outside_validity')
        cache[subject] = {'subject': subject, 'status': 'NEEDS_REVIEW' if gaps else 'REVIEW_RECORDED',
                          'reasons': sorted(gaps)}
        return cache[subject]

    def gate(self, authorization, principal, subject, action, estimated_cost, capabilities, now):
        """Evaluate a local declaration; never execute an action or authenticate a principal."""
        number(estimated_cost, maximum=1e12)
        if not isinstance(authorization, Authorization):
            raise ValueError('Authorization required')
        if not isinstance(capabilities, dict) or set(capabilities) != {'current', 'targets', 'weights'}:
            raise ValueError('capability inputs required, not a caller-supplied ready flag')
        from .gaps import analyze_capabilities
        coverage = analyze_capabilities(**capabilities)
        reasons = []
        if (authorization.principal, authorization.subject, authorization.action) != (principal, subject, action):
            reasons.append('authorization_scope_mismatch')
        if authorization.snapshot != self.snapshot(subject):
            reasons.append('stale_authorization')
        if not timestamp(authorization.granted_at) <= timestamp(now) < timestamp(authorization.expires_at):
            reasons.append('authorization_outside_validity')
        if self.status(subject, now)['status'] != 'REVIEW_RECORDED':
            reasons.append('claim_not_currently_reviewed')
        if not coverage['ready']:
            reasons.append('capability_gap')
        if estimated_cost > authorization.max_cost:
            reasons.append('budget_exceeded')
        return {'local_gate_permitted': not reasons, 'reasons': sorted(reasons),
                'execution_performed': False, 'identity_authenticated': False}

    def report(self, now=None):
        """Export a deterministic status snapshot; no evidence payload bytes are retained."""
        now = now or datetime.now(timezone.utc).isoformat()
        timestamp(now)
        return {'schema_version': 1, 'assessed_at': now,
                'nodes': [record(self._nodes[key]) for key in sorted(self._nodes)],
                'dependencies': [asdict(edge) for edge in sorted(self._edges,
                                 key=lambda e: (e.source, e.target, e.relation))],
                'statuses': [self.status(key, now) for key in sorted(self._nodes)],
                'reviews': [asdict(self._reviews[key]) for key in sorted(self._reviews)],
                'events': list(self.events), 'execution_performed': False,
                'limitations': ['Local declarations do not authenticate reviewers or authority',
                                'Integrity and review records do not establish scientific truth',
                                'In-memory state; exported reports are not resumable trust stores']}
