import unittest, tempfile, os, pandas as pd, pipeline as P
def good(): return pd.DataFrame({"district_code":[101,101,103],"period":["2025-01","2025-06","2026-08"],"records":[10,20,30],"source":["a"]*3})
class T(unittest.TestCase):
    def setUp(self): self.out=os.path.join(tempfile.mkdtemp(),"out.csv")
    def test_clean_publishes(self): self.assertTrue(P.run(good(),self.out)["published"])
    def test_missing_records_flagged(self):
        r=P.run(good(),self.out,expected_districts=[101,103,104]); self.assertTrue(any("MISSING_DISTRICTS" in w for w in r["report"]["warnings"])); self.assertTrue(r["flag_for_review"])
    def test_missing_values_rejected(self):
        d=good(); d.loc[0,"records"]=None; d["records"]=d.records; r=P.run(d,self.out); self.assertFalse(r["published"])
    def test_duplicates_identified_and_removed(self):
        d=pd.concat([good(),good().iloc[[0]].assign(records=99)]); r=P.run(d,self.out); self.assertTrue(any("DUPLICATES" in w for w in r["report"]["warnings"])); self.assertEqual(r["rows"],2)
    def test_schema_drift_rejected(self):
        self.assertFalse(P.run(good().rename(columns={"records":"count"}),self.out)["published"])
        self.assertFalse(P.run(good().astype({"records":"float64"}),self.out)["published"])
    def test_late_data_marks_stale(self):
        d=good(); d["period"]="2025-01"; r=P.run(d,self.out); self.assertTrue(r["report"]["stale"]); self.assertTrue(r["flag_for_review"])
    def test_district_change_preserves_history(self):
        d=P.harmonise(pd.DataFrame({"district_code":[101,101],"period":["2025-01","2025-06"],"records":[1,2],"source":["a","a"]}))
        self.assertEqual(list(d.district_code),[101,102])
    def test_failure_prevents_partial_publication(self):
        P.run(good(),self.out); before=open(self.out).read()
        for stage in ("aggregate","write"):
            with self.assertRaises(RuntimeError): P.run(good().assign(records=[1,1,1]),self.out,fail_at=stage)
            self.assertEqual(open(self.out).read(),before); self.assertEqual(len(os.listdir(os.path.dirname(self.out))),1)
    def test_conflicts_trigger_review(self):
        a=good(); b=good().assign(records=[10,40,30]); c=P.conflicts(a,b); self.assertEqual(len(c),1)
    def test_repeat_runs_reproducible(self):
        self.assertEqual(P.run(good(),self.out)["sha256"],P.run(good().sample(frac=1,random_state=3),self.out)["sha256"])
unittest.main()
