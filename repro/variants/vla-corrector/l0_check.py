"""L0: the Learned Verifier of PROTOCOL.md (frozen in the commit that added it). Recomputes the pooled counts, AUROCs and the
bar verdict from expected/rows.csv (one row per seed, held-out episode and control) and compares them with
expected/result.json. `python3 l0_check.py --write` regenerates result.json. Training itself is `run_verifier.py`."""
import hashlib, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
EXP = HERE / "expected/result.json"
HASH = {"data/episodes.npz": "7b6bec5970efd54f9cb231fe46c0769358bf11c295ac8a98a7a7adf15f577b6f",
        "data/episodes_meta.csv": "d7ee2fb5051f1dcbf62d7c9f42b5a699e86d60e2ad1e78738091cd5683e39375"}


def auroc(y, s):
    from scipy.stats import rankdata
    y = np.asarray(y, bool); n1, n0 = y.sum(), (~y).sum()
    return float((rankdata(s)[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def compute():
    for f, h in HASH.items():
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == h, f
    d = pd.read_csv(HERE / "expected/rows.csv")
    out = {}
    for reading in sorted(d.reading.unique()):
        per = []
        for seed in range(5):
            t = d[(d.reading == reading) & (d.seed == seed) & (d.control == "true")]
            s = d[(d.reading == reading) & (d.seed == seed) & (d.control == "shuffled")]
            assert len(t) == 50 and t.episode.nunique() == 50 and int(t.y.sum()) == 8
            assert (s.sort_values("episode").y.values == t.sort_values("episode").y.values).all()
            r = {"caught": int(t[t.y == 1].fire_tau040.sum()), "fi": int(t[t.y == 0].fire_tau040.sum()),
                 "auroc": auroc(t.y, t.score), "auroc_shuffled": auroc(s.y, s.score),
                 "caught_shuffled": int(s[s.y == 1].fire_tau040.sum()), "fi_shuffled": int(s[s.y == 0].fire_tau040.sum())}
            if reading == "R1":
                r["caught_cal"] = int(t[t.y == 1].fire_cal.sum()); r["fi_cal"] = int(t[t.y == 0].fire_cal.sum())
            per.append(r)
        med = {k: float(np.median([p[k] for p in per])) for k in per[0]}
        med["pass_bar"] = bool(med["caught"] >= 5 and med["fi"] <= 2)
        med["action_conditioned"] = bool(med["auroc"] >= med["auroc_shuffled"] + 0.05)
        if reading == "R1":
            med["pass_bar_cal"] = bool(med["caught_cal"] >= 5 and med["fi_cal"] <= 2)
        out[reading] = {"median": med, "per_seed": per}
    return out


if __name__ == "__main__":
    got = compute()
    if "--write" in sys.argv:
        EXP.write_text(json.dumps(got, indent=1)); print("written")
    else:
        want = json.loads(EXP.read_text())
        assert json.dumps(got, sort_keys=True) == json.dumps(want, sort_keys=True), "recomputed result differs from expected/result.json"
        m = got["R1"]["median"]
        print(f"R1 caught {m['caught']:.0f}/8 at {m['fi']:.0f}/42, AUROC {m['auroc']:.3f}, shuffled {m['auroc_shuffled']:.3f}")
        print("L0 PASS")
