import unittest, decision_engine as E
REG = {"A": 9000, "B": 30000, "C": 8000, "D": 8800, "E": 2000}
DEN = {"A": 60000, "B": 400000, "C": 70000, "D": 80000, "E": 30000}
class T(unittest.TestCase):
    def test_dgpi_value(self): self.assertAlmostEqual(E.dgpi(REG, DEN)["A"], 150.0)
    def test_small_cell_suppressed(self): self.assertIsNone(E.dgpi({"A": 5}, {"A": 5})["A"])
    def test_denominator_shift(self):
        alt = {d: v * (2 if d == "A" else 1) for d, v in DEN.items()}
        out = E.denominator_comparison(REG, {"x": DEN, "y": alt})
        self.assertGreater(out["max_rank_shift"]["A"], 0)
    def test_stability_reproducible(self):
        self.assertEqual(E.rank_stability(REG, DEN, "A"), E.rank_stability(REG, DEN, "A"))
    def test_three_scenarios_route_differently(self):
        r = {k: E.gate("A", True, 0.9, E.mock_cards(k))["status"] for k in ("low_vacancy", "high_vacancy", "insufficient")}
        self.assertEqual(r, {"low_vacancy": "READY_FOR_HUMAN_REVIEW", "high_vacancy": "SIGNALS_DIVERGE", "insufficient": "EVIDENCE_INSUFFICIENT"})
    def test_unstable_rank_blocks_ready(self):
        self.assertEqual(E.gate("A", True, 0.3, E.mock_cards("low_vacancy"))["status"], "INVESTIGATE")
    def test_stale_evidence_not_counted(self):
        c = E.mock_cards("low_vacancy"); c["vacancies"]["ref_year"] = 2015; c["placement"]["ref_year"] = 2015
        self.assertEqual(E.gate("A", True, 0.9, c)["status"], "EVIDENCE_INSUFFICIENT")
    def test_low_signal(self): self.assertEqual(E.gate("A", False, 0.9, {})["status"], "NO_SIGNAL")
    def test_never_recommends_funding(self):
        for k in ("low_vacancy", "high_vacancy", "insufficient"):
            self.assertNotIn("fund", str(E.gate("A", True, 0.9, E.mock_cards(k))).lower())
    def test_ledger_tamper_detected(self):
        L = E.Ledger(); L.record("u", "auditor", "VIEW", {}); self.assertTrue(L.verify())
        L.rows[0]["body"]["actor"] = "evil"; self.assertFalse(L.verify())
    def test_decision_requires_ready_and_role(self):
        L = E.Ledger(); ok = E.gate("A", True, 0.9, E.mock_cards("low_vacancy")); bad = E.gate("A", True, 0.9, E.mock_cards("insufficient"))
        with self.assertRaises(PermissionError): L.human_decision(bad, "o", "department_officer", "REJECT", "")
        with self.assertRaises(PermissionError): L.human_decision(ok, "o", "auditor", "REJECT", "")
        L.human_decision(ok, "o", "department_officer", "DEFER", "check"); self.assertTrue(L.verify())
if __name__ == "__main__":
    unittest.main()
