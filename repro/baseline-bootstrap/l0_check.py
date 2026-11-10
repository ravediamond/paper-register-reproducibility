"""L0: paired episode bootstrap on the 11 baseline comparisons (protocol: PROTOCOL.md, frozen in commit 7ac1567; Amendment 1, WS-213; Amendment 2, near-match gate).
Recomputes the intervals of the rows whose per-unit rows are stored (data/), reads the two reused intervals, and compares
with expected/bootstrap.json. `python3 l0_check.py --write` regenerates expected/bootstrap.json.
Rows written by the re-runs of Amendment 1 are in data/*_rows*.csv; data/rerun_match.json holds, per re-run, the stored
aggregate and the recomputed one (the match gate); a comparison that does not match is not bootstrapped."""
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
N_RES, SEED = 2000, 0
EXP = HERE / "expected/bootstrap.json"
NOMATCH = "rerun does not match the stored result"
NA_TXT = "rows not available"


def auroc(y, s):
    from scipy.stats import rankdata
    y = np.asarray(y, bool); n1, n0 = y.sum(), (~y).sum()
    if n1 == 0 or n0 == 0:
        return None
    return float((rankdata(s)[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def outcome(lo, hi, null=0.0):
    return "beats" if lo > null else "loses" if hi < null else "unclear"


def pct(v):
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def robometer():
    d = np.genfromtxt(HERE / "data/robometer_rollouts.csv", delimiter=",", skip_header=1, dtype=None, encoding=None)
    cls = np.array([r[1] for r in d]); length = np.array([r[2] for r in d], float); p = np.array([r[3] for r in d], float)
    assert len(d) == 2099
    k = np.isin(cls, ["successful", "failure"]); y = cls[k] == "successful"; m, bl = p[k], -length[k]
    assert k.sum() == 2047
    a, b = auroc(y, m), auroc(y, bl)
    assert abs(a - 0.8184) < 5e-4 and abs(b - 0.9383) < 5e-4, (a, b)  # PROTOCOL.md section 6, check 1
    rng = np.random.default_rng(SEED); n = len(y); diffs = []
    while len(diffs) < N_RES:
        i = rng.integers(0, n, n)
        x, z = auroc(y[i], m[i]), auroc(y[i], bl[i])
        if x is None:
            continue
        diffs.append(x - z)
    ci = pct(diffs)
    return {"claim": "C-010-2", "comparison": "Robometer-4B zero-shot vs episode length (failure AUROC)", "unit": "rollout",
            "n_units": int(n), "method": round(a, 4), "baseline": round(b, 4), "point_difference": round(a - b, 4),
            "ci95": [round(c, 4) for c in ci], "outcome": outcome(*ci),
            "source_files": ["ravediamond/paper-vs-hardware posts/2026-10-23-paper-vs-hardware-robometer (g9a-ab ab_top.jsonl + ab_top_rescore.jsonl)",
                             "repro/baseline-bootstrap/data/robometer_rollouts.csv"]}


def aac():
    d = np.genfromtxt(HERE / "data/aac_boundaries.csv", delimiter=",", skip_header=1)
    ep, aacj, fixj = d[:, 0].astype(int), d[:, 3], d[:, 4]
    assert len(d) == 254 and len(set(ep)) == 20
    eps = sorted(set(ep)); idx = {e: np.where(ep == e)[0] for e in eps}
    stat = lambda ii: float(np.median(fixj[ii]) - np.median(aacj[ii]))  # positive = AAC better (lower jump)
    am, fm = float(np.median(aacj)), float(np.median(fixj))
    assert abs(am - 0.9728) < 5e-4 and abs(fm - 0.9395) < 5e-4
    rng = np.random.default_rng(SEED); out = []
    for _ in range(N_RES):
        ii = np.concatenate([idx[e] for e in rng.choice(eps, len(eps))])
        out.append(stat(ii))
    ci = pct(out)
    return {"claim": "C-019-2", "comparison": "AAC + overwrite vs fixed chunk + overwrite (median boundary jump, delay 8; positive = AAC lower)",
            "unit": "episode (all boundaries of a resampled episode kept together)", "n_units": 20, "n_boundaries": 254,
            "method": round(am, 4), "baseline": round(fm, 4), "point_difference": round(stat(np.arange(len(d))), 4),
            "ci95": [round(c, 4) for c in ci], "outcome": outcome(*ci),
            "source_files": ["ravediamond/paper-vs-hardware posts/2026-10-30-paper-vs-hardware-adaptive-chunking/out/aac_gate0/rows.jsonl",
                             "repro/baseline-bootstrap/data/aac_boundaries.csv"]}


def boot_groups(ep, stat, seed=SEED, n_res=N_RES):
    """Episode bootstrap: resample episodes with replacement (their rows stay together), stat(row indices) per resample."""
    eps = sorted(set(ep.tolist())); idx = {e: np.where(ep == e)[0] for e in eps}
    rng = np.random.default_rng(seed); out = []
    while len(out) < n_res:
        v = stat(np.concatenate([idx[e] for e in rng.choice(eps, len(eps))]))
        if v is not None:
            out.append(v)
    return out, len(eps)


def pack(claim, comparison, unit, n_units, m, b, diff, ci, **kw):
    return {"claim": claim, "comparison": comparison, "unit": unit, "n_units": int(n_units), "method": m, "baseline": b,
            "point_difference": diff, "ci95": [round(c, 4) for c in ci], "outcome": outcome(*ci), **kw}


def matches():
    return json.loads((HERE / "data/rerun_match.json").read_text())


def g1b_w1():
    """C-001-2: top-1 of W1 minus top-1 of the action-only baseline, H = d, at each target distance d."""
    d = np.genfromtxt(HERE / "data/g1b_rows_w1.csv", delimiter=",", skip_header=1, dtype=int)
    mt = matches()["g1b_w1"]; per = {}
    assert len(set(d[:, 0])) == 25 and (d[:, 2] == 5).sum() == 703
    for dd in sorted(set(d[:, 2].tolist())):
        r = d[d[:, 2] == dd]; mo, ac = r[:, 3].astype(float), r[:, 4].astype(float)
        assert round(mo.mean(), 4) == mt["model"][f"d{dd}_Hd"]["stored"] and round(ac.mean(), 4) == mt["action_only"][f"d{dd}_Hd"]["stored"], dd
        v, n = boot_groups(r[:, 0], lambda ii: float(mo[ii].mean() - ac[ii].mean()))
        ci = pct(v)
        per[f"d{dd}"] = pack("C-001-2", "", "episode", n, round(mo.mean(), 4), round(ac.mean(), 4), round(mo.mean() - ac.mean(), 4), ci, n_anchors=len(r))
        del per[f"d{dd}"]["claim"], per[f"d{dd}"]["comparison"]
    lo_ub = min(per, key=lambda k: (per[k]["ci95"][1], per[k]["point_difference"]))      # worst case: lowest upper bound
    hi_lb = max(per, key=lambda k: (per[k]["ci95"][0], per[k]["point_difference"]))      # best case: highest lower bound
    outs = {p["outcome"] for p in per.values()}
    return {"claim": "C-001-2", "comparison": "LeWorldModel ranking vs action-only, top-1", "unit": "episode", "n_units": 25, "n_anchors": 703,
            "per_d": per, "worst_d": lo_ub, "best_d": hi_lb, "point_difference": per[lo_ub]["point_difference"], "ci95": per[lo_ub]["ci95"],
            "outcome": outs.pop() if len(outs) == 1 else "unclear",
            "source_files": ["projects/vla-jepa-world-model/wm_train/g1b_range.py, g1_diag.py (re-run WS-213)", "repro/baseline-bootstrap/data/g1b_rows_w1.csv"]}


def mismatch(claim, comparison, key, what, stored, rerun):
    """The re-run does not reproduce the stored aggregate: both values are written, nothing is bootstrapped (PROTOCOL.md Amendment 1)."""
    assert matches()[key]["matches"] is False
    return {"claim": claim, "comparison": comparison, "outcome": NOMATCH, "compared": what, "stored": stored, "rerun": rerun,
            "source_files": ["repro/baseline-bootstrap/data/rerun_match.json", "repro/baseline-bootstrap/data/not_matched/"]}


def hwm():
    """C-016-2: mean cosine of the learned macro-actions minus that of net joint displacement; unit = episode."""
    d = np.genfromtxt(HERE / "data/hwm_rows.csv", delimiter=",", skip_header=1)
    ep, a, b = d[:, 0].astype(int), d[:, 2], d[:, 3]; mt = matches()["hwm"]
    assert len(d) == 700 and round(a.mean(), 4) == mt["learned"]["stored"] and round(b.mean(), 4) == mt["disp"]["stored"]
    v, n = boot_groups(ep, lambda ii: float(a[ii].mean() - b[ii].mean()))
    return pack("C-016-2", "HWM learned macro-actions vs net joint displacement, cosine", "episode", n, round(a.mean(), 4), round(b.mean(), 4),
                round(a.mean() - b.mean(), 4), pct(v), n_anchors=len(d),
                source_files=["projects/hwm-crossover/scripts/hwm_train.py evaluate(), stored f2_*.pt (re-run WS-213)", "repro/baseline-bootstrap/data/hwm_rows.csv"])


def auroc_seeds(rows, col, agg, idx=None):
    """rows: dict seed -> (y, scores per column); AUROC per seed on idx, aggregated; None if a seed has one class only."""
    out = []
    for sd, (y, sc) in rows.items():
        a = auroc(y if idx is None else y[idx], sc[col] if idx is None else sc[col][idx])
        if a is None:
            return None
        out.append(a)
    return float(agg(out))


def w1c():
    """C-006-1: AUROC of the imagined-latent probe minus the current-latent probe; per seed on the out-of-fold scores of the
    resampled rollouts, mean over the 5 seeds; unit = rollout."""
    d = np.genfromtxt(HERE / "data/w1c_rows.csv", delimiter=",", skip_header=1)
    ep, y, sd = d[:, 0].astype(int), d[:, 1].astype(int), d[:, 2].astype(int); mt = matches()["w1c"]
    eps = sorted(set(ep.tolist())); assert len(eps) == 65
    rows = {}
    for s in sorted(set(sd.tolist())):
        k = np.where(sd == s)[0]; o = np.argsort(ep[k]); k = k[o]
        rows[s] = (y[k].astype(bool), {"imag": d[k, 3], "cur": d[k, 4]})
    a0, b0 = auroc_seeds(rows, "imag", np.mean), auroc_seeds(rows, "cur", np.mean)
    assert round(a0, 4) == mt["imagined"]["stored"] and round(b0, 4) == mt["current"]["stored"], (a0, b0)
    rng = np.random.default_rng(SEED); out = []; n = len(eps)
    while len(out) < N_RES:
        i = rng.integers(0, n, n)
        x, z = auroc_seeds(rows, "imag", np.mean, i), auroc_seeds(rows, "cur", np.mean, i)
        if x is None or z is None:
            continue
        out.append(x - z)
    return pack("C-006-1", "ContactGuard imagined-latent vs current-latent probe, failure AUROC", "rollout", n, round(a0, 4), round(b0, 4),
                round(a0 - b0, 4), pct(out), source_files=["scripts/run_w1c_offline.py c1 (re-run WS-213)", "repro/baseline-bootstrap/data/w1c_rows.csv"])


def reused():
    p = json.loads((HERE / "data/pact_gate_b_k8.json").read_text())["k8_pact_minus_random"]
    lo, hi = p["ci95"]  # PACT minus random on an error: lower is better, so sign flipped
    pact = {"claim": "C-020-1", "comparison": "PACT selection vs random pick (executed-window error, degrees; positive = PACT lower)", "unit": "episode (20), 254 boundaries",
            "n_units": 20, "point_difference": round(-p["mean"], 4), "ci95": [round(-hi, 4), round(-lo, 4)], "outcome": outcome(-hi, -lo),
            "reused_stored_ci": True, "source_files": ["ravediamond/paper-vs-hardware posts/2026-10-30-paper-vs-hardware-pact/expected/gate_b.json: k8.pact_minus_random.ci95",
                                                         "repro/baseline-bootstrap/data/pact_gate_b_k8.json"]}
    r = json.loads((HERE / "data/remora_paired.json").read_text())
    lo, hi = r["paired"]["flips_ratio_ci95"]
    rem = {"claim": "C-022-1", "comparison": "REMORA nearest-peak vs per-frame readout (flips ratio, null = 1, lower is better)", "unit": "episode (34 test rollouts)",
           "n_units": r["test_episodes"], "point_difference": round(r["paired"]["flips_R3_over_R1"], 4), "point_is": "ratio",
           "ci95": [round(lo, 4), round(hi, 4)], "outcome": ("beats" if hi < 1 else "loses" if lo > 1 else "unclear"),
           "reused_stored_ci": True, "source_files": ["ravediamond/paper-vs-hardware posts/2026-10-31-paper-vs-hardware-remora-readout/expected/summary.json: paired.flips_ratio_ci95",
                                                      "repro/baseline-bootstrap/data/remora_paired.json"]}
    return [pact, rem]


NEAR = 0.02  # Amendment 2: every re-run aggregate within 0.02 of the stored one


def near(stored, rerun):
    return all(abs(stored[k] - rerun[k]) <= NEAR for k in stored)


def per_d_rows(claim, comparison, mo_all, ac_all, d, src, **kw):
    """Per target distance d: paired episode bootstrap of model top-1 minus action-only top-1; worst and best case (Amendment 1)."""
    per = {}
    for dd in sorted(set(d[:, 2].tolist())):
        m = d[:, 2] == dd; r = d[m]; mo, ac = mo_all[m], ac_all[m]
        v, n = boot_groups(r[:, 0], lambda ii: float(mo[ii].mean() - ac[ii].mean()))
        per[f"d{dd}"] = pack(claim, "", "episode", n, round(mo.mean(), 4), round(ac.mean(), 4), round(mo.mean() - ac.mean(), 4), pct(v), n_anchors=int(m.sum()))
        del per[f"d{dd}"]["claim"], per[f"d{dd}"]["comparison"]
    lo_ub = min(per, key=lambda k: (per[k]["ci95"][1], per[k]["point_difference"]))
    hi_lb = max(per, key=lambda k: (per[k]["ci95"][0], per[k]["point_difference"]))
    outs = {p["outcome"] for p in per.values()}
    return {"claim": claim, "comparison": comparison, "unit": "episode", "n_units": len(set(d[:, 0].tolist())), "n_anchors": int((d[:, 2] == 5).sum()),
            "per_d": per, "worst_d": lo_ub, "best_d": hi_lb, "point_difference": per[lo_ub]["point_difference"], "ci95": per[lo_ub]["ci95"],
            "outcome": outs.pop() if len(outs) == 1 else "unclear", "source_files": src, **kw}


def g1b_w2():
    """C-002-1 (Amendment 2): DINO-WM top-1 minus action-only top-1 on the re-run rows; action-only hits from the W1 rows, same anchors."""
    w2 = np.genfromtxt(HERE / "data/not_matched/g1b_rows_w2.csv", delimiter=",", skip_header=1, dtype=int)
    w1 = np.genfromtxt(HERE / "data/g1b_rows_w1.csv", delimiter=",", skip_header=1, dtype=int)
    ac = {(e, t, dd): a for e, t, dd, _, a in w1.tolist()}
    a = np.array([ac[(e, t, dd)] for e, t, dd, _ in w2.tolist()], float)
    mt = matches()["g1b_w2"]
    assert len(w2) == len(w1) and near(mt["stored"], mt["rerun"])
    for dd in sorted(set(w2[:, 2].tolist())):
        assert round(w2[w2[:, 2] == dd, 3].mean(), 4) == mt["rerun"][f"d{dd}_Hd"], dd
    return per_d_rows("C-002-1", "DINO-WM ranking vs action-only, top-1", w2[:, 3].astype(float), a, w2,
                      ["repro/baseline-bootstrap/data/not_matched/g1b_rows_w2.csv (re-run WS-213)", "repro/baseline-bootstrap/data/g1b_rows_w1.csv (action-only)"],
                      near_match={"stored": mt["stored"], "rerun": mt["rerun"]})


def sens_w1():
    """C-001-1 (Amendment 2): copy-last error minus model error at K = 30 (positive = model better); unit = window (no episode ids)."""
    d = np.genfromtxt(HERE / "data/not_matched/sens_rows_w1.csv", delimiter=",", skip_header=1)
    d = d[d[:, 2] == 30]; mt = matches()["sens_w1"]
    assert len(d) == 192 and near(mt["stored"], mt["rerun"])
    m, c = d[:, 3], d[:, 4]
    assert round(m.mean(), 5) == mt["rerun"]["model_mse_k30"] and round(c.mean(), 5) == mt["rerun"]["copy_last_mse_k30"]
    v, n = boot_groups(d[:, 0].astype(int), lambda ii: float(c[ii].mean() - m[ii].mean()))
    return pack("C-001-1", "LeWorldModel vs copy-last, latent error at K = 30 (positive = model lower)", "window (episode ids not written by the re-run; narrower than an episode interval)",
                n, round(m.mean(), 5), round(c.mean(), 5), round(c.mean() - m.mean(), 5), pct(v),
                near_match={"stored": mt["stored"], "rerun": mt["rerun"]}, source_files=["repro/baseline-bootstrap/data/not_matched/sens_rows_w1.csv (re-run WS-213)"])


def reap():
    """C-008-1 (Amendment 2): AUROC true actions minus shuffled actions, per seed on the resampled rollouts, median over 5 seeds; unit = rollout."""
    import csv
    rows = {}
    for r in csv.DictReader(open(HERE / "data/not_matched/reap_rows.csv")):
        rows.setdefault(int(r["seed"]), {}).setdefault(r["monitor"], []).append((int(r["episode"]), int(r["y"]), float(r["score"])))
    seeds = {}
    for sd, mons in rows.items():
        t = sorted(mons["true"]); s = sorted(mons["shuffled"])
        assert [x[:2] for x in t] == [x[:2] for x in s]
        seeds[sd] = (np.array([x[1] for x in t], bool), {"true": np.array([x[2] for x in t]), "shuffled": np.array([x[2] for x in s])})
    mt = matches()["reap"]; st = {k: mt[k]["stored"] for k in ("true", "shuffled")}; rr = {k: mt[k]["rerun"] for k in ("true", "shuffled")}
    a0, b0 = auroc_seeds(seeds, "true", np.median), auroc_seeds(seeds, "shuffled", np.median)
    assert near(st, rr) and round(a0, 4) == rr["true"] and round(b0, 4) == rr["shuffled"], (a0, b0)
    n = len(next(iter(seeds.values()))[0]); rng = np.random.default_rng(SEED); out = []
    while len(out) < N_RES:
        i = rng.integers(0, n, n)
        x, z = auroc_seeds(seeds, "true", np.median, i), auroc_seeds(seeds, "shuffled", np.median, i)
        if x is None or z is None:
            continue
        out.append(x - z)
    return pack("C-008-1", "ReAP risk head vs shuffled actions, failure AUROC", "rollout", n, round(a0, 4), round(b0, 4), round(a0 - b0, 4), pct(out),
                near_match={"stored": st, "rerun": rr}, source_files=["repro/baseline-bootstrap/data/not_matched/reap_rows.csv (re-run WS-213)"])


def robojepa():
    """C-003-1 (Amendment 3): 1 - mean model L1 / mean copy-last L1 (steps 1 to 9, clips of the resampled episodes), RoboJEPA 300M @ 300k, setting a; unit = episode.
    Rows copied from the stored raw Gate A result (data/robojepa_match.json, not a re-run); the bar 0.15 is the register's."""
    import csv
    r = list(csv.DictReader(open(HERE / "data/robojepa_rows.csv")))
    ep = np.array([x["episode"] for x in r]); m = np.array([float(x["model_l1_mean_1_9"]) for x in r]); c = np.array([float(x["copy_last_l1_mean_1_9"]) for x in r])
    mt = matches()["robojepa"]; assert mt["matches"] is True and len(r) == mt["clips"] == 60
    red = lambda ii: float(1 - m[ii].mean() / c[ii].mean())  # noqa: E731
    allr = red(np.arange(len(r)))
    assert abs(m.mean() - mt["stored"]["model_true"]) < 1e-9 and abs(c.mean() - mt["stored"]["copy_last"]) < 1e-9 and abs(allr - mt["stored"]["reduction"]) < 1e-9
    codes = {e: i for i, e in enumerate(sorted(set(ep.tolist())))}
    v, n = boot_groups(np.array([codes[e] for e in ep]), red); lo, hi = pct(v)
    assert n == mt["episodes"] == 25
    return pack("C-003-1", "RoboJEPA 300M vs copy-last, 9-step latent L1 (reduction = 1 - model / copy-last; bar 0.15)", "episode", n,
                round(float(m.mean()), 4), round(float(c.mean()), 4), round(allr, 4), (lo, hi), point_is="fraction below copy-last",
                bar=0.15, bar_inside_interval=bool(lo <= 0.15 <= hi), n_clips=len(r), outcome_note="outcome = interval against 0; the bar 0.15 is reported beside it",
                source_files=["road-to-robotics branch exp/robojepa-gate commit 20f820d, results/gateA/gateA_300m_300k_settinga.json (stored raw result, per_clip)",
                              "repro/baseline-bootstrap/data/robojepa_rows.csv", "repro/baseline-bootstrap/data/robojepa_match.json"])


NA = {}  # every comparison has rows now


def compute():
    rows = {r["claim"]: r for r in [robometer(), aac(), g1b_w1(), hwm(), w1c()] + reused()}
    rows["C-002-1"], rows["C-001-1"], rows["C-008-1"] = g1b_w2(), sens_w1(), reap()  # Amendment 2
    rows["C-003-1"] = robojepa()  # Amendment 3
    for c, (cmp_, need) in NA.items():
        rows[c] = {"claim": c, "comparison": cmp_, "outcome": NA_TXT, "needed_file": need}
    order = ["C-001-1", "C-001-2", "C-002-1", "C-003-1", "C-006-1", "C-008-1", "C-010-2", "C-016-2", "C-019-2", "C-020-1", "C-022-1"]
    claims = [rows[c] for c in order]
    cnt = {k: sum(r["outcome"] == k for r in claims) for k in ["beats", "loses", "unclear", NOMATCH, NA_TXT]}
    return {"protocol": "repro/baseline-bootstrap/PROTOCOL.md", "resamples": N_RES, "seed": SEED, "interval": "percentile 95 %",
            "comparisons": len(claims), "counts": cnt, "claims": claims}


def main():
    got = compute()
    if "--write" in sys.argv:
        EXP.write_text(json.dumps(got, indent=1, ensure_ascii=False) + "\n"); print("written", EXP)
    want = json.loads(EXP.read_text())
    ok = got == want
    for r in got["claims"]:
        print(f"{r['claim']}: {r['outcome']}", r.get("ci95", ""), r.get("worst_d", ""), r.get("best_d", ""))
    print("counts", got["counts"])
    print("L0 PASS" if ok else "L0 FAIL (differs from expected/bootstrap.json)")


main()
