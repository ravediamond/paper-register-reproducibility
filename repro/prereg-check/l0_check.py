"""L0: recount the pre-registration classes of every gate from expected/prereg_check.json and check them against the
paper's wording (36 bar-first, 0 result-first, 31 same-commit, 19 no-bar)."""
import collections, json
from pathlib import Path

rows = json.loads((Path(__file__).resolve().parent / "expected/prereg_check.json").read_text())
c = collections.Counter(r["class"] for r in rows); want = {"bar-first": 36, "result-first": 0, "same-commit": 31, "no-bar": 19}
fails = 0
for k, v in want.items():
    ok = c.get(k, 0) == v; fails += not ok; print(f"{'ok ' if ok else 'BAD'} {k}: {c.get(k, 0)} (paper {v})")
print(f"ok  gates: {len(rows)}; other classes: {dict((k, v) for k, v in c.items() if k not in want)}")
print("L0 PASS" if not fails else "L0 FAIL")
