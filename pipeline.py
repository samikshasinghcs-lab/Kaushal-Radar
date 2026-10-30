"""Kaushal Radar reliability pipeline (pandas/numpy). Parquet/DuckDB/PostgreSQL NOT available in the build sandbox: not tested here.
Stages: validate -> dedupe -> map districts (effective-dated LGD) -> aggregate -> atomic publish."""
import os, io, json, hashlib, tempfile
import pandas as pd
SCHEMA = {"district_code":"int64","period":"object","records":"int64","source":"object"}
# Effective-dated district mapping: (old_code -> new_code, effective period). Example: a district split (MOCK codes).
LGD_CHANGES = [(101, 102, "2025-04")]  # 101 re-coded to 102 from 2025-04; history stays under 101
class DataError(Exception): pass

def validate(df, now_period="2026-10", max_age_months=6, required=SCHEMA):
    rep = {"errors": [], "warnings": [], "stale": False}
    if set(df.columns) != set(required): rep["errors"].append(f"SCHEMA_DRIFT cols={sorted(df.columns)}"); return rep
    for c, t in required.items():
        if str(df[c].dtype) != t: rep["errors"].append(f"SCHEMA_DRIFT dtype {c}={df[c].dtype}, expected {t}")
    if rep["errors"]: return rep
    if df.isna().any().any(): rep["errors"].append(f"MISSING_VALUES n={int(df.isna().any(axis=1).sum())}")
    if (df.records < 0).any(): rep["errors"].append("NEGATIVE_COUNTS")
    d = int(df.duplicated(["district_code","period"]).sum())
    if d: rep["warnings"].append(f"DUPLICATES n={d}")
    y, m = map(int, now_period.split("-")); latest = df.period.max(); ly, lm = map(int, latest.split("-"))
    if (y*12+m)-(ly*12+lm) > max_age_months: rep["stale"] = True; rep["warnings"].append(f"STALE latest={latest}")
    return rep

def expected_missing(df, expected_districts):
    return sorted(set(expected_districts) - set(df.district_code))

def harmonise(df):
    df = df.copy()
    for old, new, eff in LGD_CHANGES:   # remap only rows on/after effective period; keep history
        df.loc[(df.district_code == old) & (df.period >= eff), "district_code"] = new
    return df

def conflicts(a, b, tol=0.10):
    """Two sources for same district/period that differ by more than tol -> needs review."""
    m = a.merge(b, on=["district_code","period"], suffixes=("_a","_b"))
    bad = m[(m.records_a - m.records_b).abs() > tol * m[["records_a","records_b"]].max(axis=1)]
    return bad[["district_code","period","records_a","records_b"]]

def run(df, out_path, expected_districts=None, fail_at=None):
    """Returns dict. Output file is written atomically (temp + rename): a failure never leaves a partial/half-new file."""
    rep = validate(df)
    if rep["errors"]: return {"published": False, "report": rep}
    df = df.drop_duplicates(["district_code","period"], keep="last"); df = harmonise(df)
    if fail_at == "aggregate": raise RuntimeError("injected failure")
    agg = df.groupby("district_code", as_index=False).records.sum().sort_values("district_code")
    miss = expected_missing(agg, expected_districts) if expected_districts else []
    if miss: rep["warnings"].append(f"MISSING_DISTRICTS {miss}")
    body = agg.to_csv(index=False).encode(); digest = hashlib.sha256(body).hexdigest()
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(out_path) or "."); 
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(body)
            if fail_at == "write": raise RuntimeError("injected failure mid-write")
        os.replace(tmp, out_path)
    except Exception:
        if os.path.exists(tmp): os.remove(tmp)
        raise
    return {"published": True, "sha256": digest, "report": rep, "rows": len(agg), "flag_for_review": rep["stale"] or bool(miss)}
