"""WS-214: the stored band (in-sample) and the papers' band (FAIL-Detect appendix B, SAFE B.4) on the same series and splits.
Pure numpy; reads series.json (extract_series.py) and writes expected/conformal_check.json. Protocol: PROTOCOL.md."""
import json, math, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ALPHA, N_SPLITS, N_CAL, N_A = 0.05, 20, 22, 11
BAR = {"success_flagged_max": 1 / 20, "failure_flagged_min": 0.5}


def carry(a, t):
    return float(a[min(t, len(a) - 1)])


# ---- stored band (copied from run_w1c_offline.py: fit_band / flagged) ----
def fit_old(cal):
    L = max(len(s) for s in cal); mu, sd = [], []
    for t in range(L):
        v = np.array([s[t] for s in cal if len(s) > t])
        if len(v) < 2: break
        mu.append(float(v.mean())); sd.append(float(v.std(ddof=1)))
    mu, sd = np.array(mu), np.array(sd)
    R = np.array([max((s[t] - carry(mu, t)) / max(carry(sd, t), 1e-12) for t in range(len(s))) for s in cal])
    n = len(cal); rank = math.ceil((n + 1) * (1 - ALPHA))
    q = float(np.sort(R)[min(rank, n) - 1]) if rank <= n else float("inf")
    return {"mu": mu, "w": sd, "h": q}


# ---- the papers' band: split A / B, Eq. (2) or Eq. (1) modulation, (1-alpha)-quantile of D ----
def fit_new(cal, eq=2):
    A, B = cal[:N_A], cal[N_A:]
    TA = min(len(s) for s in A)
    mu = np.array([np.mean([s[t] for s in A]) for t in range(TA)])
    if eq == 2:
        w = np.array([max(abs(s[t] - mu[t]) for s in A) for t in range(TA)])
    else:
        w = np.ones(TA)  # Eq. (1): constant; the 1/T factor cancels in D and in the band
    D = np.array([max((s[t] - carry(mu, t)) / max(carry(w, t), 1e-12) for t in range(len(s))) for s in B])
    return {"mu": mu, "w": w, "h": float(np.quantile(D, 1 - ALPHA)), "TA": TA, "N1": len(A), "N2": len(B)}


def flagged(s, b):
    return any(s[t] > carry(b["mu"], t) + b["h"] * carry(b["w"], t) for t in range(len(s)))


def splits(succ, fail, fit, **kw):
    fpr, rec, tas = [], [], []
    for seed in range(N_SPLITS):
        perm = np.random.default_rng(seed).permutation(len(succ))
        cal = [succ[i] for i in perm[:N_CAL]]; test = [succ[i] for i in perm[N_CAL:]]
        b = fit(cal, **kw)
        fpr.append(float(np.mean([flagged(s, b) for s in test])))
        rec.append(float(np.mean([flagged(s, b) for s in fail])))
        tas.append(b.get("TA"))
    q = lambda v: {"median": round(float(np.median(v)), 4), "min": round(float(np.min(v)), 4), "max": round(float(np.max(v)), 4),
                   "iqr": [round(float(np.percentile(v, 25)), 4), round(float(np.percentile(v, 75)), 4)]}
    ok1 = q(fpr)["median"] <= BAR["success_flagged_max"]; ok2 = q(rec)["median"] >= BAR["failure_flagged_min"]
    return {"success_flagged": q(fpr), "failure_flagged": q(rec), "c007_1": "pass" if ok1 else "fail",
            "c007_2": "pass" if ok2 else "fail", "per_split": {"fpr": fpr, "recall": rec}, "band_T_A": tas}


def toy_check():  # PROTOCOL 6.2: hand-computed. A = 11 copies of [0,0], offset +-1 at t=1 for two of them; B = [[0,1],[0,3]]
    A = [np.array([0., 0.])] * 9 + [np.array([0., 1.]), np.array([0., -1.])]
    mu = np.mean(A, axis=0); w = np.array([max(abs(s[t] - mu[t]) for s in A) for t in range(2)])
    assert abs(mu[1]) < 1e-12 and w[1] == 1.0 and w[0] == 0.0
    cal = A + [np.array([0., 1.])] * 10 + [np.array([0., 3.])]  # B = 10 x [0,1] and [0,3]
    b = fit_new(cal)
    D = np.sort([1.0] * 10 + [3.0]); assert abs(b["h"] - np.quantile(D, 0.95)) < 1e-12 and abs(b["h"] - 2.0) < 1e-9
    assert flagged(np.array([0., 2.5]), b) and not flagged(np.array([0., 1.5]), b)


def main():
    ser = json.loads((HERE / "series.json").read_text())
    succ = [np.array(x["long"]) for x in ser if x["outcome"] == "success"]
    fail = [np.array(x["long"]) for x in ser if x["outcome"] == "failure"]
    assert len(ser) == 69 and len(succ) == 44 and len(fail) == 25, (len(ser), len(succ), len(fail))
    toy_check()
    old = splits(succ, fail, fit_old)
    new = splits(succ, fail, fit_new, eq=2)
    exp = splits(succ, fail, fit_new, eq=1)
    out = {"alpha": ALPHA, "splits": N_SPLITS, "calibration": N_CAL, "n_A": N_A, "n_B": N_CAL - N_A, "test_successes": len(succ) - N_CAL,
           "failures": len(fail), "bar": BAR, "stored_band_replay": old, "papers_band_eq2": new, "exploratory_eq1": exp}
    (HERE / "expected").mkdir(exist_ok=True)
    (HERE / "expected" / "conformal_check.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    o = main()
    for k in ("stored_band_replay", "papers_band_eq2", "exploratory_eq1"):
        print(k, o[k]["success_flagged"]["median"], o[k]["failure_flagged"]["median"], o[k]["c007_1"], o[k]["c007_2"])
