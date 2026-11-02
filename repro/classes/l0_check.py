#!/usr/bin/env python3
"""L0 for repro/classes: the protocol and the blind form are present, the form has the 20 fail rows, no class filled;
reader 1's labels (if present) parse, 20 rows, one label each, and the prompt's sha256 is the one in the amendment."""
import csv
import hashlib
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE / "form.csv")))
ok = (HERE / "PROTOCOL.md").exists() and len(rows) == 20 and all(not r["class (A/B/C/none)"] for r in rows) \
    and len({r["claim_id"] for r in rows}) == 20
print(f"form rows {len(rows)}, blank classes {sum(not r['class (A/B/C/none)'] for r in rows)}")
lab = HERE / "labels_reader1_gemini.csv"
if lab.exists():
    got = list(csv.DictReader(open(lab)))
    sha = hashlib.sha256((HERE / "reader1_prompt.txt").read_bytes()).hexdigest()
    frozen = re.search(r"sha256\s+`([0-9a-f]{64})`", (HERE / "PROTOCOL.md").read_text())
    ok_lab = len(got) == 20 and all(r["label"] in {"A", "B", "C", "none"} for r in got) \
        and [r["claim_id"] for r in got] == [r["claim_id"] for r in rows] and bool(frozen) and frozen.group(1) == sha
    print(f"reader-1 rows {len(got)}, prompt sha256 {'matches' if frozen and frozen.group(1) == sha else 'MISMATCH'}")
    ok = ok and ok_lab
print("L0 PASS" if ok else "L0 FAIL")
