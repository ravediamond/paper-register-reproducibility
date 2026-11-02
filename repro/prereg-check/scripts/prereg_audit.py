#!/usr/bin/env python3
"""WS-136 Part 1 step 1: resolve the same-commit, no-bar and unresolved rows of prereg_check.json by commit order.

For each such row, SPEC gives fixed strings that carry the bar (threshold text as first written, in the gate's protocol,
plan, scorer or spec) and strings that carry the first result number. Each string is looked up with git's pickaxe
(`git log --all --reverse -S<string>`, noise paths excluded: tick logs, bench dumps, JSONL logs, this folder); the
earliest commit over a row's bar strings is its bar commit, the earliest over its result strings its result commit, and
the added line is kept as evidence. Class, derived only from the commits: bar-first (bar commit a strict ancestor of the
result commit), same-commit (the same commit), result-first (result commit a strict ancestor of the bar commit),
no-bar (the bar cell declares none: empty, "—", "none (…)", "(dev only …)", "(fit only …)"), not-run (a bar, no result
ever produced). Writes prereg_audit.json (read by prereg_check.py) and PREREG_AUDIT.md. No verdict is edited.
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
RR = HERE.parents[2]
EXCL = [":(exclude,glob)**/ticks/**", ":(exclude,glob)data/bench/**", ":(exclude,glob)**/*_orin_nx_*",
        ":(exclude)journal/papers/reproducibility-study", ":(exclude,glob)**/*.jsonl"]

# row index in prereg_check.json -> (bar strings, result strings, note). None = class fixed by the bar cell / no run.
VJ = "projects/vla-jepa-world-model"
G = lambda d: f":(glob)**/{d}/**"  # a gate folder under any of its past paths (data/gate → shared/gate/data)
ALL = ["."]

# row index in prereg_check.json -> (bar strings, bar paths, result strings, result paths, note).
# "no-bar": the bar cell declares none. Result strings None: the gate never ran.
SPEC = {
    8: (["<= ~0.7"], ALL, ["1.84x"], ALL, "H0 plan and report"),
    9: (["beat gripper aperture", "| B2 | measured gripper aperture"], ALL, None, None, "never run"),
    10: (["losses fall"], ALL, ["passed** on an RTX 5060"], ALL, "the bar text first appears inside the result line"),
    11: ("no-bar", None, None, None, "bar cell: none (diagnostic)"),
    12: ("no-bar", None, None, None, "bar cell: none (diagnostic)"),
    13: ([">= 1.3 at K=30", ">= 1.3 rule"], ALL, ["K=30 error 0.31 vs copy-last 0.89"], ALL,
         "rule written with the 5-epoch diagnostic (row 12), gated on the later W1 run"),
    16: (["R² > 0.57"], ALL, ["clears the \"arm pose R2 > 0.57\""], ALL, ""),
    17: (["before the next chunk starts executing"], ALL, ["1814", "1793"], [":(glob)**/*g2_mac*", "journal/EXPERIMENTS.md"], ""),
    21: (["2-view encoder p50 <= 200 ms"], ALL, ["526 ms"], ALL, "pre-registration commit on branch exp/robojepa-gate"),
    22: (["2-view encoder p50 <= 200 ms"], ALL, ["1025 ms"], ALL, "same bar, Mac run"),
    23: (["at least 15% lower than copy-last"], ALL, ["11.8"], [G("robojepa_gate")], "branch exp/robojepa-gate"),
    24: (["(top-1 of 8) >= 0.8"], ALL, None, None, "never run"),
    25: (["| <= -0.8 |"], [f"{VJ}/wm_train"], ["\"t1_median_spearman\": -0.3202"], ALL, ""),
    26: (["a >= 0.85 and res"], ALL, ["0.861"], [G("g9a_ab"), "journal/EXPERIMENTS.md"], "bar first in the scorer"),
    27: (["a >= 0.85 and res"], ALL, ["0.818"], [G("g9a_ab"), "journal/EXPERIMENTS.md"], "same rule on the complete set (owner decision)"),
    28: (["AUROC >= 0.9 and accuracy", "AUROC ≥ 0.9 and accuracy"], ALL, ["0.577"], [G("g9a_own"), "journal/EXPERIMENTS.md"], ""),
    29: (["**accuracy >= 95%** (at most 4 errors in 88)"], ALL, ["86.4"], [G("g9c"), f"{VJ}/README.md", "journal/EXPERIMENTS.md"], ""),
    31: (["**accuracy on judged >= 95%**"], ALL, ["94.3"], [G("g9c3"), f"{VJ}/README.md", "journal/EXPERIMENTS.md"], ""),
    32: (["**Pass (per encoder): AUROC >= 0.90**"], ALL, ["0.9760"], [G("g10"), f"{VJ}/README.md", "journal/EXPERIMENTS.md"], ""),
    33: (["\\rho \\le -0.80 \\quad"], ALL, ["0.7268"], [G("g6b"), "EXPERIMENTS_SUMMARY.md", "journal/EXPERIMENTS.md"], ""),
    34: (["< 20.00 ms", "Tick latency during check"], [f"{VJ}/jetson", "journal", "EXPERIMENTS_SUMMARY.md"], ["12.78"], [f"{VJ}/jetson", "journal", "EXPERIMENTS_SUMMARY.md"], ""),
    36: (["8.0 GB"], [f"{VJ}/jetson", "journal", "EXPERIMENTS_SUMMARY.md"], ["3.46 GB"], ALL, ""),
    38: (["≥ 10 % of failed episodes oscillate"], ALL, ["24.0 %"], [G("2026-10-18_g14"), "journal/EXPERIMENTS.md"], ""),
    42: (["cuts the median boundary jump by ≥ 50 %"], ALL, ["72–74", "72.8"], [G("2026-10-19_g13b_offline"), "journal/EXPERIMENTS.md"], ""),
    43: (["premature ≤ 2"], ALL, ["48.5"], [G("2026-10-19_g15"), "journal/EXPERIMENTS.md"], ""),
    44: (["smallest threshold"], ALL, ["0.98"], [G("2026-10-19_judge_tau"), "journal/EXPERIMENTS.md"], "bar in the G16 code commit"),
    46: (["cuts the median boundary jump by ≥ 50 %"], ALL, ["71.0 / 73.3", "73.3"], [G("2026-10-19_vlacpp_prefix_overwrite"), "journal/EXPERIMENTS.md"], "bar = G13b's"),
    47: ("no-bar", None, None, None, "bar cell: (dev only; the gate is fresh rollouts)"),
    51: ("no-bar", None, None, None, "bar cell: (fit only; the gate is the fresh robot-day test)"),
    59: (["tol-deg"], ["scripts"], ["0.80°"], [G("2026-10-22_vlacpp_parity_cubes_bowls"), "journal/EXPERIMENTS.md"], "bar = check script tolerance (1.0°)"),
    76: (["Bar 1a"], ALL, ["182/182", "182 / 182"], ["projects/aw0-code-plan", "journal/EXPERIMENTS.md"], ""),
    77: (["per-frame accuracy ≥ 85"], ALL, ["75.7"], ["projects/aw0-code-plan", "journal/EXPERIMENTS.md"], ""),
    78: (["#35f4600"], None, ["+0.748", "0.748"], [G("2026-10-24_inverse_dynamics"), "journal/EXPERIMENTS.md"], "pre-registered at the cited hash 35f4600"),
    79: (["$18 line", "$18"], ["projects/reki-so101", "journal"], ["0.008 (3,500)"], ["projects/reki-so101", "journal/EXPERIMENTS.md"],
         "bar = the $18 line the owner set before the full run"),
}


def git(*a):
    return subprocess.run(["git", "-C", str(RR), *a], capture_output=True, text=True).stdout


def earliest(strings, paths):
    """(hash, iso date, file, added line) of the earliest commit adding any of `strings` under `paths`."""
    best = None
    for s in strings:
        if s.startswith("#"):  # a cited pre-registration commit
            h = s[1:]
            return (h, git("show", "-s", "--format=%ad", "--date=iso-strict", h).strip(), "(commit)",
                    git("show", "-s", "--format=%s", h).strip()[:120].replace("|", "\\|"), s)
        o = git("log", "--all", "--reverse", "--format=%h|%ad", "--date=iso-strict", f"-S{s}", "--", *paths, *EXCL)
        for h_d in [x for x in o.split("\n") if x]:
            h, d = h_d.split("|")
            f, line = "?", ""
            for l in git("show", "--format=", "-U0", h, "--", *paths, *EXCL).split("\n"):
                if l.startswith("+++ "):
                    f = l[6:]
                elif l.startswith("+") and s in l:
                    line = l[1:].strip()
                    break
            if line:  # the commit adds the string (not only removes it)
                if best is None or d < best[1]:
                    i = line.find(s)
                    best = (h, d, f, line[max(0, i - 70): i + len(s) + 50].replace("|", "\\|"), s)
                break
    return best


def ancestor(a, b):
    return subprocess.run(["git", "-C", str(RR), "merge-base", "--is-ancestor", a, b]).returncode == 0


def main():
    rows = json.loads((HERE / "prereg_check.json").read_text())
    out = []
    for i, (bar_s, bar_p, res_s, res_p, note) in SPEC.items():
        r = rows[i]
        b = res = None
        if bar_s == "no-bar":
            cls = "no-bar"
        else:
            b = earliest(bar_s, bar_p)
            res = earliest(res_s, res_p) if res_s else None
            if res_s is None:
                cls = "not-run"
            elif b is None or res is None:
                cls = "unresolved"
            elif b[0] == res[0]:
                cls = "same-commit"
            elif ancestor(b[0], res[0]):
                cls = "bar-first"
            elif ancestor(res[0], b[0]):
                cls = "result-first"
            else:
                cls = "bar-first (by date)" if b[1] < res[1] else "result-first (by date)"
        out.append({"row": i, "date": r["date"], "gate": r["gate"], "old_class": r.get("class_v1", r["class"]), "class": cls,
                    "bar_commit": b[0] if b else None, "bar_date": b[1][:16] if b else None,
                    "bar_file": b[2] if b else None, "bar_line": b[3] if b else None,
                    "result_commit": res[0] if res else None, "result_date": res[1][:16] if res else None,
                    "result_file": res[2] if res else None, "result_line": res[3] if res else None, "note": note})
    (HERE / "prereg_audit.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    write_md(out)
    return out


def write_md(out):
    import collections
    c = collections.Counter(x["class"] for x in out)
    L = ["# WS-136 · Pre-registration audit: the same-commit, no-bar and unresolved rows resolved by commit order", "",
         "Generated by `prereg_audit.py` (method in its docstring); `prereg_check.py` reads `prereg_audit.json` and writes "
         "the audited class into `prereg_check.json`. A class comes only from the order of two commits; the evidence "
         "column is the line each commit adds. Searched: road-to-robotics, all refs (`git log --all`, incl. "
         "`origin/exp/robojepa-gate`); `paper-vs-hardware` starts 2026-10-26, after every row here but 76–79, and adds "
         "no earlier bar. Folder timestamps are not used (not a commit ordering).", "",
         f"Rows audited: {len(out)} · " + " · ".join(f"{k} {v}" for k, v in sorted(c.items())), "",
         "| row | date | gate | was | class | bar commit | bar evidence | result commit | result evidence | note |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for x in out:
        bc = f"`{x['bar_commit']}` {x['bar_date']}" if x["bar_commit"] else "—"
        rc = f"`{x['result_commit']}` {x['result_date']}" if x["result_commit"] else "—"
        be = f"{x['bar_file']}: {x['bar_line']}" if x["bar_line"] else "—"
        re_ = f"{x['result_file']}: {x['result_line']}" if x["result_line"] else "—"
        L.append(f"| {x['row']} | {x['date']} | {x['gate'][:40]} | {x['old_class']} | **{x['class']}** | {bc} | "
                 f"{be[:160]} | {rc} | {re_[:160]} | {x['note']} |")
    (HERE / "PREREG_AUDIT_TABLE.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    import collections
    o = main()
    print(len(o), collections.Counter(x["class"] for x in o))
