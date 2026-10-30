"""Governance controls (prototype). A: RBAC  B: tamper-evident audit  C: small-cell suppression, encryption at rest, TLS in transit.
Prototype only: needs independent security review before any production use."""
import sys, os, json, ssl, threading, subprocess, tempfile, http.server, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from decision_engine import Ledger
from cryptography.fernet import Fernet

PERMS = {  # role -> allowed actions (see access_control.csv, generated from this)
 "administrator":      {"ingest","read_indicators","read_evidence","read_routing","read_audit","decide","manage_users"},
 "department_officer": {"ingest","read_indicators","read_evidence","read_routing","decide"},
 "district_officer":   {"read_indicators","read_evidence","read_routing"},   # own district only
 "auditor":            {"read_indicators","read_evidence","read_routing","read_audit"},  # read-only
}
def authorize(role, action, district=None, user_district=None):
    if action not in PERMS.get(role, set()): return False
    if role == "district_officer" and district is not None and district != user_district: return False
    return True

class AuditedStore:
    """Every access attempt (allowed or denied) is logged: who, what, when, outcome. Decisions record the approver."""
    def __init__(self): self.ledger = Ledger()
    def access(self, user, role, action, district=None, user_district=None):
        ok = authorize(role, action, district, user_district)
        self.ledger.record(user, role, "ACCESS_" + ("ALLOWED" if ok else "DENIED"), dict(action=action, district=district))
        if not ok: raise PermissionError(f"{role} may not {action} on {district}")

def suppress(cells, k=10, total=None):
    """cells: {label: count}. Primary suppression of counts <k; if exactly one is suppressed and a total is published,
    also suppress the smallest remaining cell (complementary suppression) so it cannot be recovered by subtraction."""
    out = {l: (None if 0 < c < k else c) for l, c in cells.items()}
    hidden = [l for l, v in out.items() if v is None]
    if len(hidden) == 1 and total is not None:
        rest = {l: c for l, c in cells.items() if out[l] is not None}
        if rest: out[min(rest, key=rest.get)] = None
    return out

PII = ("name","aadhaar","phone","email","bank","address","dob")
def reject_pii(columns): return [c for c in columns if any(p in c.lower() for p in PII)]

def encrypt_at_rest(path, data: bytes, key: bytes):
    open(path, "wb").write(Fernet(key).encrypt(data))
def decrypt_at_rest(path, key: bytes): return Fernet(key).decrypt(open(path, "rb").read())

def tls_roundtrip():
    """Starts a local HTTPS server with a self-signed cert; client verifies the cert and fetches data. Returns (ok, plaintext_visible_on_wire=False)."""
    d = tempfile.mkdtemp(); crt, key = f"{d}/c.pem", f"{d}/k.pem"
    subprocess.run(["openssl","req","-x509","-newkey","rsa:2048","-nodes","-keyout",key,"-out",crt,"-days","1","-subj","/CN=localhost",
                    "-addext","subjectAltName=DNS:localhost"], check=True, capture_output=True)
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(s): s.send_response(200); s.end_headers(); s.wfile.write(b"aggregate-only payload")
        def log_message(s,*a): pass
    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(crt, key); ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    threading.Thread(target=srv.handle_request, daemon=True).start()
    cctx = ssl.create_default_context(cafile=crt)
    body = urllib.request.urlopen(f"https://localhost:{srv.server_address[1]}/", context=cctx, timeout=10).read()
    srv.server_close(); return body == b"aggregate-only payload"
