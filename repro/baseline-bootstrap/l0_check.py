"""L0: paired episode bootstrap on the 11 baseline comparisons (protocol: PROTOCOL.md, frozen in commit 7ac1567).
Recomputes the intervals of the rows whose per-unit rows are stored (data/), reads the two reused intervals, and compares
with expected/bootstrap.json. `python3 l0_check.py --write` regenerates expected/bootstrap.json."""
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
N_RES, SEED = 2000, 0
EXP = HERE / "expected/bootstrap.json"


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


NA = {  # claim -> (comparison, file that would be needed)
    "C-001-1": ("LeWorldModel vs copy-last, latent error at K = 30", "per-anchor open-loop error of the model and of copy-last at K = 30 with the episode id, written by g1_suite.py (not stored; only means)"),
    "C-001-2": ("LeWorldModel ranking vs action-only, top-1", "per-anchor top-1 hit of the model and of the action-only baseline for each target distance d, with the episode id, written by g1b_range.py (not stored; g1b_range_w1.json has accuracy per cell only)"),
    "C-002-1": ("DINO-WM ranking vs action-only, top-1", "per-anchor top-1 hits of W2 and of the action-only baseline per target distance, with the episode id (g1_w2prime_best_g1b.json has accuracy per cell only)"),
    "C-003-1": ("RoboJEPA 300M vs copy-last, 9-step latent L1", "per-clip model and copy-last errors, written by gate_a_eval.py (gateA_summary.json has per-horizon means only)"),
    "C-006-1": ("ContactGuard imagined-latent vs current-latent probe, failure AUROC", "per-rollout out-of-fold scores of both probes for the 65 scored rollouts (w1c_summary.json has fold means only)"),
    "C-008-1": ("ReAP risk head vs shuffled actions, failure AUROC", "per-rollout risk scores, true and shuffled actions, for the 50 rollouts (monitors_v2.json has aggregates only)"),
    "C-016-2": ("HWM learned macro-actions vs net joint displacement, cosine", "per-anchor cosines of the learned and displacement macro-actions for the 700 anchors, written by hwm_train.py (gate0.json has means and standard errors only)"),
}


def compute():
    rows = {r["claim"]: r for r in [robometer(), aac()] + reused()}
    for c, (cmp_, need) in NA.items():
        rows[c] = {"claim": c, "comparison": cmp_, "outcome": "rows not available", "needed_file": need}
    order = ["C-001-1", "C-001-2", "C-002-1", "C-003-1", "C-006-1", "C-008-1", "C-010-2", "C-016-2", "C-019-2", "C-020-1", "C-022-1"]
    claims = [rows[c] for c in order]
    cnt = {k: sum(r["outcome"] == k for r in claims) for k in ["beats", "loses", "unclear", "rows not available"]}
    return {"protocol": "repro/baseline-bootstrap/PROTOCOL.md", "resamples": N_RES, "seed": SEED, "interval": "percentile 95 %",
            "counts": cnt, "claims": claims}


def main():
    got = compute()
    if "--write" in sys.argv:
        EXP.write_text(json.dumps(got, indent=1, ensure_ascii=False) + "\n"); print("written", EXP)
    want = json.loads(EXP.read_text())
    ok = got == want
    for r in got["claims"]:
        print(f"{r['claim']}: {r['outcome']}", r.get("ci95", ""))
    print("counts", got["counts"])
    print("L0 PASS" if ok else "L0 FAIL (differs from expected/bootstrap.json)")


main()
