"""Kaushal Radar Decision Engine v2. ALL DATA BELOW IS MOCK (illustrative, not government data).
Never outputs a funding recommendation; outputs a diagnostic status for human review only."""
import hashlib, json, random, time

STATUSES = ("NO_SIGNAL", "INVESTIGATE", "EVIDENCE_INSUFFICIENT", "SIGNALS_DIVERGE", "READY_FOR_HUMAN_REVIEW")
Q = ("graduate_demand", "local_employment", "training_capacity", "vacancies", "placement")
MIN_CELL = 10  # small-cell suppression threshold

# ---- Indicator + Denominator engines ----
def dgpi(reg, denom):
    return {d: (reg[d] / denom[d] * 1000 if denom[d] >= MIN_CELL else None) for d in reg}

def ranks(scores):
    ok = sorted((d for d in scores if scores[d] is not None), key=lambda d: -scores[d])
    return {d: i + 1 for i, d in enumerate(ok)}

def denominator_comparison(reg, denoms):
    """Rank every district under each alternative denominator; report max rank shift."""
    rk = {n: ranks(dgpi(reg, dn)) for n, dn in denoms.items()}
    shift = {d: max(r[d] for r in rk.values()) - min(r[d] for r in rk.values()) for d in reg}
    return {"ranks": rk, "max_rank_shift": shift}

# ---- Uncertainty engine (seeded => reproducible) ----
def rank_stability(reg, denom, district, draws=500, reg_noise=0.10, den_noise=0.05, tol=1, seed=42):
    rng = random.Random(seed)
    base = ranks(dgpi(reg, denom))[district]; hits = 0
    for _ in range(draws):
        r = {d: v * rng.uniform(1 - reg_noise, 1 + reg_noise) for d, v in reg.items()}
        n = {d: v * rng.uniform(1 - den_noise, 1 + den_noise) for d, v in denom.items()}
        if abs(ranks(dgpi(r, n))[district] - base) <= tol: hits += 1
    return hits / draws

# ---- Evidence engine ----
def card(question, source, value, supports_pressure, ref_year, mock=True):
    return dict(question=question, source=source, value=value, supports=supports_pressure,
                ref_year=ref_year, mock=mock)

def usable(c, now_year, max_age=3):
    return c is not None and now_year - c["ref_year"] <= max_age

# ---- Corroboration Gate ----
def gate(district, signal_high, stability, cards, now_year=2026):
    """cards: dict question->card or None. Returns status + auditable reasons."""
    if not signal_high:
        return {"district": district, "status": "NO_SIGNAL", "reasons": ["DGPI not in high band"]}
    good = {q: cards.get(q) for q in Q if usable(cards.get(q), now_year)}
    stale = [q for q in Q if cards.get(q) and q not in good]
    missing = [q for q in Q if not cards.get(q)]
    sup = [q for q, c in good.items() if c["supports"]]
    con = [q for q, c in good.items() if not c["supports"]]
    why = [f"supporting={sup}", f"contradicting={con}", f"missing={missing}", f"stale={stale}",
           f"rank_stability={stability:.2f}"]
    if len(good) < 4: st = "EVIDENCE_INSUFFICIENT"
    elif len(con) >= 2: st = "SIGNALS_DIVERGE"
    elif stability < 0.60: st = "INVESTIGATE"; why.append("rank unstable")
    elif len(sup) >= 3 and len(con) == 0: st = "READY_FOR_HUMAN_REVIEW"
    else: st = "INVESTIGATE"
    return {"district": district, "status": st, "reasons": why}

# ---- Decision Ledger (hash-chained, tamper-evident; prototype, not a production WORM store) ----
class Ledger:
    def __init__(self): self.rows = []
    def _h(self, body, prev): return hashlib.sha256((prev + json.dumps(body, sort_keys=True)).encode()).hexdigest()
    def record(self, actor, role, action, payload):
        body = dict(ts=time.time(), actor=actor, role=role, action=action, payload=payload)
        prev = self.rows[-1]["hash"] if self.rows else "GENESIS"
        self.rows.append(dict(body=body, prev=prev, hash=self._h(body, prev)))
    def human_decision(self, result, officer, role, decision, note):
        if result["status"] != "READY_FOR_HUMAN_REVIEW": raise PermissionError("Not ready for review")
        if role not in ("department_officer", "administrator"): raise PermissionError("Role cannot approve")
        if decision not in ("ACCEPT_FOR_INVESTIGATION", "REJECT", "DEFER"): raise ValueError("Invalid decision")
        self.record(officer, role, "HUMAN_DECISION", dict(district=result["district"], decision=decision, note=note))
    def verify(self):
        prev = "GENESIS"
        for r in self.rows:
            if r["prev"] != prev or r["hash"] != self._h(r["body"], prev): return False
            prev = r["hash"]
        return True

# ---- MOCK scenarios (the three policy scenarios from the brief) ----
def mock_cards(kind):
    y = 2025
    base = {"graduate_demand": card("graduate_demand", "MOCK Yuva Nidhi", 1, True, y)}
    if kind == "low_vacancy":
        base.update(local_employment=card("local_employment", "MOCK PLFS", 1, True, y),
                    training_capacity=card("training_capacity", "MOCK ITI/NCVT", 1, True, y),
                    vacancies=card("vacancies", "MOCK vacancy feed", 1, True, y),
                    placement=card("placement", "MOCK placement", 1, True, y))
    elif kind == "high_vacancy":
        base.update(local_employment=card("local_employment", "MOCK PLFS", 0, False, y),
                    training_capacity=card("training_capacity", "MOCK ITI/NCVT", 1, True, y),
                    vacancies=card("vacancies", "MOCK vacancy feed", 0, False, y),
                    placement=card("placement", "MOCK placement", 0, False, y))
    return base  # "insufficient" => only one card

if __name__ == "__main__":
    reg = {"Raichur": 9000, "Bengaluru": 30000, "Mysuru": 8000, "Kalaburagi": 8800, "Udupi": 2000}
    den = {"Raichur": 60000, "Bengaluru": 400000, "Mysuru": 70000, "Kalaburagi": 80000, "Udupi": 30000}
    s = rank_stability(reg, den, "Raichur")
    for k in ("low_vacancy", "high_vacancy", "insufficient"):
        print(k, gate("Raichur", True, s, mock_cards(k))["status"])
