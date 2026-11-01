"""L0: recount the cold-reproduction table (L0 and L1 classes per post) from expected/REPORT.md."""
import collections, re
from pathlib import Path

t = (Path(__file__).resolve().parent / "expected/REPORT.md").read_text()
rows = [l.split("|")[1:-1] for l in t.splitlines() if re.match(r"\| \d+ \|", l)]
l0 = collections.Counter("PASS" if c[2].strip().startswith("PASS") else "FAIL" for c in rows)
l1 = collections.Counter(c[3].strip().split(" ")[0] for c in rows)
fails = 0
for name, got, want in (("posts", len(rows), 29), ("L0 PASS", l0["PASS"], 29), ("L1 REPRO", l1["REPRO"], 6), ("L1 DIFF", l1["DIFF"], 0)):
    ok = got == want; fails += not ok; print(f"{'ok ' if ok else 'BAD'} {name}: {got} (report {want})")
print(f"ok  L1 classes: {dict(l1)}")
print("L0 PASS" if not fails else "L0 FAIL")
