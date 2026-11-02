#!/usr/bin/env python3
"""Build the blind second-reader form: every claim row of the site register with verdict `fail` (20 rows at site
commit 7d48b9e), in register order, with only the fields a reader needs (no class, no owner note).

usage: python3 make_form.py <site>/data/register.yaml > form.csv
"""
import csv
import sys

import yaml

d = yaml.safe_load(open(sys.argv[1]))
w = csv.writer(sys.stdout)
w.writerow(["row", "claim_id", "paper", "claim", "conditions", "theirs", "ours", "bar", "class (A/B/C/none)"])
n = 0
for p in d["papers"]:
    for c in p.get("claims") or []:
        if c.get("verdict") != "fail":
            continue
        n += 1
        cond = "; ".join(f"{k}: {v}" for k, v in (c.get("conditions") or {}).items())
        w.writerow([n, c["id"], p["paper"], f'{c["subject"]} {c["relation"]} {c["object"]} on {c["metric"]}', cond,
                    c.get("theirs", ""), c.get("ours", ""), c.get("bar", ""), ""])
