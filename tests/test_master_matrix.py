"""Tests for master eventuality matrix catalog."""

import unittest

from apl_omega.matrices.master import (
    by_domain,
    by_id,
    by_omega_class,
    domain_summary,
    load_master_matrix,
)
from apl_omega.models.state import OmegaClass


class MasterMatrixTests(unittest.TestCase):
    def test_eighty_eventualities(self):
        items = load_master_matrix()
        self.assertEqual(len(items), 80)
        self.assertEqual(items[0].eventuality_id, "E-001")
        self.assertEqual(items[-1].eventuality_id, "E-080")

    def test_unique_ids(self):
        ids = [e.eventuality_id for e in load_master_matrix()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_by_id(self):
        e = by_id("E-022")
        self.assertEqual(e.domain, "Cyber")
        self.assertEqual(e.omega_class, OmegaClass.TOPOLOGY_DISRUPTION)

    def test_unknown_class_present(self):
        unknowns = by_omega_class(OmegaClass.UNKNOWN_UNCERTAIN)
        self.assertTrue(any(e.eventuality_id == "E-006" for e in unknowns))
        self.assertTrue(len(unknowns) >= 5)

    def test_domain_summary_covers_expected(self):
        summary = domain_summary()
        for domain in ("Payload", "Cyber", "Safety", "Verification", "Lifecycle"):
            self.assertIn(domain, summary)
            self.assertGreaterEqual(summary[domain], 1)

    def test_payload_domain(self):
        payload = by_domain("Payload")
        self.assertEqual(len(payload), 4)


if __name__ == "__main__":
    unittest.main()
