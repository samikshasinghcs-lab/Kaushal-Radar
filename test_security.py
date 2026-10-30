import unittest, tempfile, os, security as S
from cryptography.fernet import Fernet
class T(unittest.TestCase):
    def test_matrix(self):
        self.assertTrue(S.authorize("department_officer","decide")); self.assertFalse(S.authorize("auditor","decide"))
        self.assertFalse(S.authorize("auditor","ingest")); self.assertFalse(S.authorize("district_officer","decide"))
        self.assertFalse(S.authorize("district_officer","read_indicators","Mysuru","Raichur")); self.assertTrue(S.authorize("district_officer","read_indicators","Raichur","Raichur"))
        self.assertFalse(S.authorize("ghost","read_audit"))
    def test_denials_are_logged_and_chain_verifies(self):
        s=S.AuditedStore()
        with self.assertRaises(PermissionError): s.access("u1","auditor","decide")
        s.access("u2","auditor","read_audit"); self.assertEqual([r["body"]["action"] for r in s.ledger.rows],["ACCESS_DENIED","ACCESS_ALLOWED"]); self.assertTrue(s.ledger.verify())
    def test_small_cell(self):
        self.assertEqual(S.suppress({"a":4,"b":50,"c":30})["a"],None)
        o=S.suppress({"a":4,"b":50,"c":30},total=84); self.assertEqual(sum(v is None for v in o.values()),2)  # complementary
        self.assertEqual(S.suppress({"a":0,"b":10})["a"],0)  # zero is not a small cell; 10 is not < k
    def test_pii_rejected(self): self.assertEqual(S.reject_pii(["district","aadhaar_no","Phone"]),["aadhaar_no","Phone"])
    def test_encryption_at_rest(self):
        k=Fernet.generate_key(); p=tempfile.mktemp(); S.encrypt_at_rest(p,b"district,count\nRaichur,9000",k)
        self.assertNotIn(b"Raichur",open(p,"rb").read()); self.assertEqual(S.decrypt_at_rest(p,k),b"district,count\nRaichur,9000")
        with self.assertRaises(Exception): S.decrypt_at_rest(p,Fernet.generate_key())
    def test_tls(self): self.assertTrue(S.tls_roundtrip())
unittest.main()
