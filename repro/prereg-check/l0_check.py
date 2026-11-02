"""L0: recount the audited pre-registration classes (WS-136, by commit order) from expected/prereg_check.json and check
them against the paper's wording: of the 89 gate rows of 2026-10-31, 58 bar-first, 6 same-commit, 0 result-first,
23 no-bar, 2 not-run; of the 93 rows of the log today, 61 / 7 / 0 / 23 / 2. The WS-078 class is kept as class_v1
(36 / 31 / 19 / 3 unresolved). Also recount the flip-under-CI gates of expected/recompute_early.json."""
import collections, json
from pathlib import Path

E = Path(__file__).resolve().parent / "expected"
rows = json.loads((E / "prereg_check.json").read_text())
fails = 0
for label, sub, want in (("89 rows (2026-10-31)", rows[:89], {"bar-first": 58, "same-commit": 6, "result-first": 0, "no-bar": 23, "not-run": 2}),
                         ("93 rows (today)", rows, {"bar-first": 61, "same-commit": 7, "result-first": 0, "no-bar": 23, "not-run": 2})):
    c = collections.Counter(r["class"] for r in sub)
    for k, v in want.items():
        ok = c.get(k, 0) == v; fails += not ok; print(f"{'ok ' if ok else 'BAD'} {label} {k}: {c.get(k, 0)} (paper {v})")
    other = {k: v for k, v in c.items() if k not in want}; fails += bool(other); print(f"{'ok ' if not other else 'BAD'} {label} other classes: {other}")
v1 = dict(collections.Counter(r["class_v1"] for r in rows[:89]))
ok = v1 == {"bar-first": 36, "same-commit": 31, "no-bar": 19, "unresolved": 3}; fails += not ok
print(f"{'ok ' if ok else 'BAD'} WS-078 class_v1: {v1}")
flips = [r["gate"] for r in json.loads((E / "recompute_early.json").read_text()) if r["flip_under_ci"]]
ok = flips == ["G14", "G9c-3", "Judge τ"]; fails += not ok; print(f"{'ok ' if ok else 'BAD'} flip-under-CI: {flips}")
print("L0 PASS" if not fails else "L0 FAIL")
