#!/usr/bin/env python3
"""L0 for repro/classes: the protocol and the blind form are present, the form has the 20 fail rows, no class filled."""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE / "form.csv")))
ok = (HERE / "PROTOCOL.md").exists() and len(rows) == 20 and all(not r["class (A/B/C/none)"] for r in rows) \
    and len({r["claim_id"] for r in rows}) == 20
print(f"form rows {len(rows)}, blank classes {sum(not r['class (A/B/C/none)'] for r in rows)}")
print("L0 PASS" if ok else "L0 FAIL")
