#!/usr/bin/env python3
"""WS-078 step 1, part 2: PREREG_CHECK.md from prereg_check.json (run prereg_check.py first)."""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
o = json.load(open(HERE / "prereg_check.json"))
PAPERS = {  # register id -> paper, gate-row prefixes (EXPERIMENTS.md ID column); first published 2026-10-23 = the 14 early ones
    1: ("LeWorldModel", ["G0", "G1b W1", "G1 diagnosis"]), 2: ("DINO-WM", ["G1 probes", "G1 W2 dynamics", "W2′"]),
    3: ("RoboJEPA", ["RoboJEPA Gate"]), 4: ("H-JEPA", ["G6a", "G6b"]), 5: ("D-JEPA", ["W1-R"]), 6: ("ContactGuard", ["W1-C1"]),
    7: ("FAIL-Detect and SAFE", ["W1-C2"]), 8: ("ReAP", ["REAP monitors", "REAP v2"]), 9: ("VLA-Corrector", ["W1-A", "REAP v2"]),
    10: ("Robometer", ["G9a-AB", "G9a-own", "G9b"]), 11: ("SmolVLA", ["SmolVLA", "21-task SmolVLA via vla.cpp"]),
    12: ("TurboVLA", ["TurboVLA faithful"]), 13: ("VLA-JEPA", ["H0", "VLA-JEPA"]), 14: ("REKI", ["G14"]),
    15: ("Real-Time Chunking", ["G13b"]), 16: ("HWM", ["HWM crossover"]), 17: ("LeJEPA identifiability", ["LeJEPA identifiability"]),
    18: ("SURVEYOR", ["SURVEYOR"]), 19: ("AAC", ["AAC, gate"]), 20: ("PACT-VLA", ["PACT-VLA, gate"]),
    21: ("Horizon × depth", ["Horizon × depth"]), 22: ("REMORA", ["REMORA readout"]),
}
EARLY = set(range(1, 16))  # first published 2026-10-23 (15 papers; the prompt says 14: TurboVLA is withdrawn)
c = collections.Counter(x["class"] for x in o)
imp = sum(1 for x in o if x["class"] == "same-commit" and x["result_commit"] == "5fc1779")
L = ["# WS-078 · Pre-registration check: bar commit vs result commit, every gate (2026-10-31)", "",
     "Source: `journal/EXPERIMENTS.md`, every dated row of §1 (arm gates, 8) and §2 (gates, 81) = **89 rows** (the site's",
     "count of 85 uses the site's gate rule on its own copy of the log). Built by `prereg_check.py` (git history of this",
     "repo, 732 commits) and `prereg_table.py`. **No verdict is edited; this table is the finding.**", "",
     "**Bar commit** = the earliest of: the pre-registration hash cited in the row; the first commit adding a protocol file",
     "the row names (or the row's project `PROTOCOL.md`); the first commit adding the gate to §3 \"Pending gates\"; the",
     "first commit containing the bar text. **Result commit** = the first commit containing the result text.", "",
     "| class | rows | meaning |", "|---|---|---|",
     f"| bar-first | {c['bar-first']} | the bar's commit is an ancestor of the result's commit |",
     f"| same-commit | {c['same-commit']} | bar and result first appear in the same commit — {imp} of them in `5fc1779` (2026-10-16), the commit that created this log from earlier notes; the bar may predate it elsewhere (research notes, the old Mac), unverifiable from this repo |",
     f"| result-first | {c.get('result-first', 0)} | the result was committed before the bar |",
     f"| no-bar | {c['no-bar']} | §1 arm rows (10-trial operator-judged runs, no bar column) and rows with no bar (`—`, measured only) |",
     f"| unresolved | {c['unresolved']} | the text was not found by git (H3 plan and G1b-RJ never ran; RoboJEPA Gate B′ bar not found) |", "",
     "**No row is result-first.**", "", "## Per register paper", "",
     "| # | paper | gates | classes | flag |", "|---|---|---|---|---|"]
for pid, (name, pre) in PAPERS.items():
    gs = [x for x in o if any(x["gate"].startswith(p) for p in pre)]
    cl = collections.Counter(x["class"] for x in gs)
    flag = ""
    if pid in EARLY:
        flag = "early (2026-10-23): " + ("all bars before results" if gs and all(x["class"] == "bar-first" for x in gs if x["class"] != "no-bar")
                                       and any(x["class"] == "bar-first" for x in gs) else "**not shown bar-first**")
    L.append(f"| {pid} | {name} | {len(gs)} | {', '.join(f'{k} {v}' for k, v in sorted(cl.items()))} | {flag} |")
L += ["", "## All rows", "", "| § | date | gate | bar commit (how) | result commit | class | verdict |", "|---|---|---|---|---|---|---|"]
for x in o:
    L.append(f"| {x['section']} | {x['date']} | {x['gate']} | {x['bar_commit'] or '—'} {x['bar_date'] or ''} ({x['bar_how']}) | "
             f"{x['result_commit'] or '—'} {x['result_date'] or ''} | {x['class']} | {x['verdict']} |")
(HERE / "PREREG_CHECK.md").write_text("\n".join(L) + "\n")
print(c)
