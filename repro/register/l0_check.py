"""L0: recount the register (expected/register.json, the site's public/data/register.json at site commit 7d48b9e):
22 papers (4 reproduce, 13 fail, 3 not proven, 1 not tested, 1 withdrawn), 45 claim rows (42 tested; 20 fail,
17 reproduces, 4 not tested, 3 not proven, 1 withdrawn), their rig class, and the compute total ($45.10)."""
import collections, json
from pathlib import Path

d = json.loads((Path(__file__).resolve().parent / "expected/register.json").read_text())["papers"]
cl = [c for p in d for c in p.get("claims", [])]
checks = [
    ("papers", len(d), 22),
    ("paper verdicts", dict(collections.Counter(p["verdict"] for p in d)), {"fail": 13, "reproduces": 4, "not proven": 3, "not tested": 1, "withdrawn": 1}),
    ("their rig class", dict(collections.Counter(p["their_rig_cost_class"] for p in d)), {"sim": 9, ">$20k": 7, "$5–20k": 3, "<$5k": 2, "unstated": 1}),
    ("claim rows", len(cl), 45),
    ("tested claim rows", sum(c["tested"] for c in cl), 42),
    ("claim verdicts", dict(collections.Counter(c["verdict"] for c in cl)), {"fail": 20, "reproduces": 17, "not tested": 4, "not proven": 3, "withdrawn": 1}),
    ("cost_usd total", round(sum(float(p.get("cost_usd") or 0) for p in d), 2), 45.1),
]
fails = 0
for name, got, want in checks:
    ok = got == want; fails += not ok; print(f"{'ok ' if ok else 'BAD'} {name}: {got} (paper {want})")
print("L0 PASS" if not fails else "L0 FAIL")
