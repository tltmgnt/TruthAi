"""Tests for APL-Ω mathematical metrics."""

import unittest

from apl_omega.formulas.metrics import (
    TrustFactors,
    capability_gap,
    confidence_from_entropy,
    digital_twin_consistency,
    evidence_freshness,
    event_priority,
    eventuality_risk,
    interface_compatibility_strict,
    normalize_priorities,
    objective_score,
    recovery_quality,
    topological_gap,
    trust_state,
    twin_confidence_cap,
    unknown_state_index,
    verification_coverage,
)
from apl_omega.models.state import SystemState
from apl_omega.models.topology import TopologyGraph


class FormulaTests(unittest.TestCase):
    def test_capability_gap_signs(self):
        self.assertEqual(capability_gap(0.8, 0.8), 0.0)
        self.assertGreater(capability_gap(0.5, 1.0), 0.0)
        self.assertLess(capability_gap(1.2, 1.0), 0.0)

    def test_interface_strict_requires_all(self):
        self.assertEqual(interface_compatibility_strict([1, 1, 1, 1, 1, 1]), 1.0)
        self.assertEqual(interface_compatibility_strict([1, 1, 0, 1, 1, 1]), 0.0)

    def test_verification_coverage(self):
        self.assertAlmostEqual(verification_coverage(3, 4), 0.75)

    def test_evidence_freshness_decays(self):
        self.assertLess(evidence_freshness(100, 0.01), evidence_freshness(0, 0.01))

    def test_trust_multiplicative(self):
        t = trust_state(
            TrustFactors(
                identity=1.0,
                authorization=0.0,
                configuration_integrity=1.0,
                evidence_integrity=1.0,
            )
        )
        self.assertEqual(t, 0.0)

    def test_twin_confidence_cap(self):
        self.assertEqual(twin_confidence_cap(0.4, 0.9), 0.4)

    def test_unknown_not_zero_when_uncertain(self):
        u = unknown_state_index(0.8, 0.7, 0.6, 0.9, 0.5)
        self.assertGreater(u, 0.5)

    def test_priority_and_normalize(self):
        p = event_priority(1, 1, 1, 1)
        self.assertEqual(p, 1.0)
        norms = normalize_priorities([1, 2, 4])
        self.assertEqual(norms[-1], 1.0)

    def test_risk_and_objective(self):
        r = eventuality_risk(0.5, 0.5, 0.5, 0.5, 0.5)
        self.assertAlmostEqual(r, 0.5**5)
        j = objective_score(1, 1, 1, 1, 1, 1, 0, 0, 0)
        self.assertEqual(j, 6.0)

    def test_recovery_and_dti(self):
        self.assertAlmostEqual(recovery_quality(0.8, 1.0), 0.8)
        self.assertAlmostEqual(digital_twin_consistency(0.2), 0.8)

    def test_topological_gap_identical_zero(self):
        s = SystemState.ready_baseline()
        g = TopologyGraph.baseline_apl()
        self.assertAlmostEqual(topological_gap(s, s, g, g), 0.0)

    def test_confidence_from_entropy(self):
        # Uniform distribution → low confidence
        conf = confidence_from_entropy([0.25, 0.25, 0.25, 0.25])
        self.assertLess(conf, 0.1)
        # Certain distribution → high confidence
        conf2 = confidence_from_entropy([1.0, 0.0, 0.0, 0.0])
        self.assertGreater(conf2, 0.99)


if __name__ == "__main__":
    unittest.main()
