#!/usr/bin/env python3
"""WS-136 Part 1 step 2: early gates (dated 2026-10-08 to 10-19) recomputed with the episode bootstrap (METHOD I.4 /
RECOMPUTED.md: 2,000 resamples over episodes, numpy default_rng(0), percentile 95 % CI) from the rows stored in the repo.

A rate is resampled over the episodes it is defined on (failed episodes for G14, the 42 successes / 8 failures for the
judge gates); event-level rates (G15, W1-B) are ratio estimates over resampled episodes. Binary per-episode outcomes
stored only as counts (G9c, G9c-3, judge τ) are rebuilt as 0/1 rows from the counts: for a proportion the bootstrap
depends on nothing else. flip-under-CI: the verdict on the point estimate and the verdict read on the CI bound
nearest the bar differ (pass whose bound crosses the bar, or fail whose CI includes it). No verdict is edited.
Writes recompute_early.json.
"""
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RR = HERE.parents[2]
D = RR / "shared/gate/data"
VJ = RR / "projects/vla-jepa-world-model"
B, SEED = 2000, 0


def boot(num, den):
    num, den = np.asarray(num, float), np.asarray(den, float)
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(num), size=(B, len(num)))
    r = num[idx].sum(1) / np.maximum(den[idx].sum(1), 1)
    return num.sum() / den.sum(), float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5)), len(num)


def counts(k, n):
    return boot([1] * k + [0] * (n - k), [1] * n)


def rows_csv(p):
    return list(csv.DictReader(open(p)))


def per_event(p, mode=None):
    j = json.load(open(p))
    t = (j["modes"][mode] if mode else j)["test"]["per_event"]
    eps = sorted({e["episode"] for e in t})
    pre = [sum(e["result"] == "premature" for e in t if e["episode"] == ep) for ep in eps]
    ev = [sum(1 for e in t if e["episode"] == ep) for ep in eps]
    mis = [sum(e["result"] == "missed" for e in t if e["episode"] == ep) for ep in eps]
    pres = [sum(e["truth"] >= 0 for e in t if e["episode"] == ep) for ep in eps]
    return (pre, ev), (mis, pres)


def verdicts(est, lo, hi, op, bar):
    ok = (lambda v: v >= bar) if op == ">=" else (lambda v: v <= bar)
    point = ok(est)
    bound = lo if op == ">=" else hi  # the conservative end
    other = hi if op == ">=" else lo
    flip = (point and not ok(bound)) or (not point and ok(other))
    return ("pass" if point else "fail"), flip


def main():
    out = []

    def add(gate, metric, src, res, op, bar, note=""):
        est, lo, hi, n = res
        v, flip = verdicts(est, lo, hi, op, bar)
        out.append({"gate": gate, "metric": metric, "source": src, "n_units": n, "estimate": round(est, 4),
                    "ci95": [round(lo, 4), round(hi, 4)], "bar": f"{op} {bar}", "point_verdict": v,
                    "flip_under_ci": flip, "note": note})

    g14 = [r for r in rows_csv(D / "2026-10-18_g14/g14_episodes.csv") if r["outcome"] != "success"]
    add("G14", "failed episodes oscillating", "shared/gate/data/2026-10-18_g14/g14_episodes.csv",
        boot([r["oscillating"] == "True" for r in g14], [1] * len(g14)), ">=", 0.10)

    for gate, p, mode in [("G15", D / "2026-10-19_g15/g15_summary.json", "both"),
                          ("W1-B", D / "2026-10-19_w1_screening/w1b_summary.json", None)]:
        (pre, ev), (mis, pres) = per_event(p, mode)
        src = str(p.relative_to(RR))
        add(gate, "premature rate (test)", src, boot(pre, ev), "<=", 0.02)
        add(gate, "missed rate (test)", src, boot(mis, pres), "<=", 0.10)

    g16 = [r for r in rows_csv(D / "2026-10-19_g16b/g16b_episodes.csv") if r["in_g16_set"] == "True"]
    s = [r["flagged"] == "True" for r in g16 if r["outcome"] == "success"]
    f = [r["flagged"] == "True" for r in g16 if r["outcome"] != "success"]
    src = "shared/gate/data/2026-10-19_g16b/g16b_episodes.csv"
    add("G16-B", "successes flagged", src, boot(s, [1] * len(s)), "<=", round(2 / 42, 4))
    add("G16-B", "failures flagged", src, boot(f, [1] * len(f)), ">=", 0.75)

    g9c = json.load(open(VJ / "judge/results/g9c/g9c_results.json"))
    add("G9c", "accuracy", "projects/vla-jepa-world-model/judge/results/g9c/g9c_results.json",
        counts(round(g9c["accuracy"] * g9c["n"]), g9c["n"]), ">=", 0.95, "rows rebuilt from counts")
    g3 = json.load(open(VJ / "judge/results/g9c3/g9c3_test_results.json"))["result"]
    add("G9c-3", "accuracy on judged", "projects/vla-jepa-world-model/judge/results/g9c3/g9c3_test_results.json",
        counts(round(g3["accuracy_on_judged"] * g3["judged"]), g3["judged"]), ">=", 0.95, "rows rebuilt from counts")
    jt = json.load(open(D / "2026-10-19_judge_tau/judge_tau.json"))
    add("Judge τ", "false interventions on successes", "shared/gate/data/2026-10-19_judge_tau/judge_tau.json",
        counts(round(jt["false_intervention_rate"] * jt["success_episodes"]), jt["success_episodes"]), "<=", 0.05,
        "τ is fitted to meet this; the CI is descriptive")
    (HERE / "recompute_early.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    return out


if __name__ == "__main__":
    for x in main():
        print(x["gate"], x["metric"], x["n_units"], x["estimate"], x["ci95"], x["bar"], x["point_verdict"],
              "FLIP" if x["flip_under_ci"] else "")
