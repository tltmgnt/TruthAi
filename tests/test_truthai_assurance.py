"""Behavioral acceptance tests for local assurance and invalidation."""
from dataclasses import replace
import hashlib
import json
import unittest
from truthai_assurance import (Artifact, Authorization, Capability, Claim, Dependency,
                               Registry, VerificationResult, analyze_capabilities)
from truthai_assurance.__main__ import demo
from truthai_assurance.contracts import from_record, record

NOW = '2026-11-08T12:00:00Z'
END = '2026-11-09T12:00:00Z'
LATER = '2026-11-10T12:00:00Z'


class GapTests(unittest.TestCase):
    def test_target_only_dimension_is_visible(self):
        result = analyze_capabilities([Capability('a', 'observed', 1)], {'a': 1, 'b': 1})
        self.assertEqual(result['capabilities']['b']['state'], 'absent')
        self.assertEqual(result['coverage'], 0.5)
        self.assertIsNone(result['total_shortfall'])
        self.assertFalse(result['ready'])

    def test_partial_measurement_never_claims_complete_gap(self):
        for state in ('unmeasured', 'failed', 'unavailable'):
            with self.subTest(state=state):
                result = analyze_capabilities([Capability('a', state)], {'a': 1})
                self.assertIsNone(result['total_shortfall'])
                self.assertIsNone(result['capabilities']['a']['deficit'])
                self.assertFalse(result['ready'])

    def test_surplus_does_not_offset_deficit(self):
        result = analyze_capabilities([Capability('a', 'observed', 1), Capability('b', 'observed', 0)],
                                      {'a': 0.5, 'b': 0.5})
        self.assertEqual(result['total_shortfall'], 0.5)
        self.assertFalse(result['ready'])

    def test_invalid_values_are_rejected(self):
        for value in (True, float('nan'), float('inf'), -1, 2):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Capability('a', 'observed', value)
        with self.assertRaises(ValueError):
            analyze_capabilities([], {})
        with self.assertRaises(ValueError):
            analyze_capabilities([], {'a': 1}, {'a': 0})
        with self.assertRaises(ValueError):
            analyze_capabilities([Capability('a'), Capability('a')], {'a': 1})

    def test_extras_do_not_increase_coverage(self):
        result = analyze_capabilities([Capability('extra', 'observed', 1)], {'required': 1})
        self.assertEqual(result['coverage'], 0)
        self.assertEqual(result['extra_capabilities'], ['extra'])


class RegistryFixture:
    def setUp(self):
        self.registry = Registry()
        self.payload = b'synthetic measurement'
        self.artifact = Artifact('data', hashlib.sha256(self.payload).hexdigest(),
                                 'synthetic:local', 'fixture', NOW, END)
        self.registry.add(self.artifact)
        self.registry.verify_artifact('data', self.payload, NOW)
        self.registry.add(Claim('child', 'math', 'Fixture claim', 'linear equations', 'owner'))
        self.registry.add(Claim('parent', 'manufacturing', 'Dependent fixture', 'study context', 'owner'))
        self.registry.link(Dependency('child', 'data', 'supports'))
        self.registry.link(Dependency('parent', 'child'))
        self.registry.review('child', 'reviewer', NOW, END)
        self.registry.review('parent', 'reviewer', NOW, END)
        self.auth = Authorization('operator', 'parent', 'export', self.registry.snapshot('parent'), NOW, END, 2)
        self.capabilities = {'current': [Capability('verification', 'observed', 1)],
                             'targets': {'verification': 1}, 'weights': {}}


class RegistryTests(RegistryFixture, unittest.TestCase):
    def gate(self, **overrides):
        args = {'authorization': self.auth, 'principal': 'operator', 'subject': 'parent',
                'action': 'export', 'estimated_cost': 1, 'capabilities': self.capabilities, 'now': NOW}
        args.update(overrides)
        return self.registry.gate(**args)

    def test_current_local_review_permits_gate_without_execution(self):
        result = self.gate()
        self.assertTrue(result['local_gate_permitted'])
        self.assertFalse(result['execution_performed'])
        self.assertFalse(result['identity_authenticated'])

    def test_artifact_change_invalidates_entire_path(self):
        affected = self.registry.replace(replace(self.artifact, source='synthetic:new-source'))
        self.assertEqual(affected, ['child', 'data', 'parent'])
        self.assertEqual(self.registry.status('child', NOW)['status'], 'NEEDS_REVIEW')
        self.assertEqual(self.registry.status('parent', NOW)['status'], 'NEEDS_REVIEW')
        self.assertIn('stale_authorization', self.gate()['reasons'])

    def test_same_content_rollback_cannot_resurrect_review(self):
        self.registry.replace(replace(self.artifact, source='synthetic:new'))
        self.registry.replace(self.artifact)
        self.registry.verify_artifact('data', self.payload, NOW)
        self.assertIn('stale_review_snapshot', self.registry.status('child', NOW)['reasons'])
        self.assertFalse(self.gate()['local_gate_permitted'])

    def test_failed_byte_check_removes_old_integrity(self):
        self.assertFalse(self.registry.verify_artifact('data', b'wrong', NOW))
        self.assertEqual(self.registry.status('data', NOW)['status'], 'NEEDS_EVIDENCE')
        self.assertFalse(self.gate()['local_gate_permitted'])

    def test_reverification_requires_explicit_bottom_up_review(self):
        self.registry.replace(replace(self.artifact, source='synthetic:new'))
        self.registry.verify_artifact('data', self.payload, NOW)
        with self.assertRaises(ValueError):
            self.registry.review('parent', 'reviewer', NOW, END)
        self.registry.review('child', 'reviewer', NOW, END)
        self.registry.review('parent', 'reviewer', NOW, END)
        self.assertEqual(self.registry.status('parent', NOW)['status'], 'REVIEW_RECORDED')
        self.assertFalse(self.gate()['local_gate_permitted'])

    def test_replacing_claim_scope_reopens_review(self):
        self.registry.replace(replace(self.registry.nodes['child'], scope='new scope'))
        self.assertFalse(self.gate()['local_gate_permitted'])

    def test_reviewer_change_reopens_downstream_review(self):
        self.registry.review('child', 'another-reviewer', NOW, END)
        self.assertIn('stale_review_snapshot', self.registry.status('parent', NOW)['reasons'])

    def test_expiry_and_future_time_fail_closed(self):
        self.assertFalse(self.gate(now=END)['local_gate_permitted'])
        self.assertFalse(self.gate(now='2026-11-07T12:00:00Z')['local_gate_permitted'])
        self.assertFalse(self.registry.verify_artifact('data', self.payload, LATER))

    def test_invalid_review_does_not_mutate_registry(self):
        before = self.registry.report(NOW)
        for reviewer, expiry in [('owner', END), ('reviewer', NOW), ('', END)]:
            with self.subTest(reviewer=reviewer, expiry=expiry):
                with self.assertRaises(ValueError):
                    self.registry.review('child', reviewer, NOW, expiry)
        self.assertEqual(before, self.registry.report(NOW))

    def test_graph_rejects_cycles_dangling_edges_and_duplicates(self):
        snapshot = self.registry.snapshot('parent')
        for edge in (Dependency('child', 'parent'), Dependency('child', 'missing'),
                     Dependency('parent', 'child'), Dependency('data', 'parent')):
            with self.assertRaises(ValueError):
                self.registry.link(edge)
        self.assertEqual(snapshot, self.registry.snapshot('parent'))

    def test_dependency_add_remove_does_not_restore_old_snapshot(self):
        self.registry.add(Artifact('extra', self.artifact.sha256, 'synthetic:extra', 'fixture', NOW, END))
        edge = Dependency('child', 'extra')
        self.registry.link(edge)
        self.registry.unlink(edge)
        self.assertFalse(self.gate()['local_gate_permitted'])

    def test_contradiction_blocks_review(self):
        self.registry.add(Claim('challenge', 'test', 'Challenge', 'fixture', 'owner'))
        self.registry.link(Dependency('child', 'challenge', 'contradicts'))
        self.assertIn('contradictory_dependency:challenge', self.registry.status('child', NOW)['reasons'])
        with self.assertRaises(ValueError):
            self.registry.review('child', 'reviewer', NOW, END)

    def test_budget_and_identity_scope_are_checked(self):
        for overrides in ({'estimated_cost': 3}, {'principal': 'intruder'}, {'action': 'execute'}):
            with self.subTest(overrides=overrides):
                self.assertFalse(self.gate(**overrides)['local_gate_permitted'])

    def test_caller_ready_boolean_is_not_trusted(self):
        with self.assertRaises(ValueError):
            self.gate(capabilities={'ready': True})
        self.capabilities['targets']['recovery'] = 1
        self.assertIn('capability_gap', self.gate()['reasons'])

    def test_records_are_immutable_and_scope_is_preserved(self):
        exported = json.loads(json.dumps(self.registry.report(NOW)))
        claim = next(n for n in exported['nodes'] if n['fields']['id'] == 'child')
        self.assertEqual(claim['fields']['domain'], 'math')
        self.assertEqual(claim['fields']['scope'], 'linear equations')
        with self.assertRaises(TypeError):
            self.registry.nodes['child'] = 'changed'
        copied = self.registry.events[0]
        copied['operation'] = 'tampered'
        self.assertEqual(self.registry.events[0]['operation'], 'add')
        self.assertNotIn(self.payload.decode(), json.dumps(exported))


class ExchangeTests(RegistryFixture, unittest.TestCase):
    def test_contract_validation(self):
        with self.assertRaises(ValueError):
            replace(self.artifact, schema_version=True)
        with self.assertRaises(ValueError):
            replace(self.artifact, observed_at='2026-11-08T12:00:00')
        with self.assertRaises(ValueError):
            replace(self.registry.nodes['child'], assumptions=['mutable'])
        with self.assertRaises(ValueError):
            replace(self.auth, max_cost=float('nan'))
        self.assertEqual(record(self.artifact)['type'], 'Artifact')
        with self.assertRaises(ValueError):
            VerificationResult('x', 'invalid', 'reviewer', 'scope', NOW, END)

    def test_contract_exchange_roundtrip_preserves_fields(self):
        records = [self.artifact, self.registry.nodes['child'], self.auth,
                   Capability('a'), Dependency('parent', 'child'),
                   VerificationResult('child', self.registry.snapshot('child'), 'reviewer', 'scope', NOW, END)]
        for value in records:
            with self.subTest(value=type(value).__name__):
                self.assertEqual(from_record(json.loads(json.dumps(record(value)))), value)

    def test_exchange_rejects_unknown_versions_fields_and_types(self):
        valid = record(self.artifact)
        for value in ({**valid, 'schema_version': 2}, {**valid, 'schema_version': True},
                      {**valid, 'type': 'Registry'}, {**valid, 'unexpected': 1},
                      {**valid, 'fields': {**valid['fields'], 'verified': True}}):
            with self.assertRaises(ValueError):
                from_record(value)
        registry = Registry()
        imported = from_record(valid)
        registry.add(imported)
        self.assertEqual(registry.status(imported.id, NOW)['status'], 'NEEDS_EVIDENCE')

    def test_synthetic_two_domain_rehearsal(self):
        result = demo()
        self.assertTrue(result['synthetic'])
        self.assertFalse(result['live_repository_integration'])
        self.assertFalse(result['missing_capability_gate']['local_gate_permitted'])
        self.assertTrue(result['before_change']['local_gate_permitted'])
        self.assertFalse(result['after_change']['local_gate_permitted'])
        self.assertEqual(result['affected_by_change'], ['integration', 'math', 'math-artifact'])


if __name__ == '__main__':
    unittest.main()
