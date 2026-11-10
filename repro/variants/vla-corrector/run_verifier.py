"""Step 2 (host python, torch CPU): trains and scores the Learned Verifier of PROTOCOL.md; writes expected/rows.csv and
expected/window_metrics.json. Usage: run_verifier.py RGBFEAT_DIR OUT_DIR READING SEED   (RGBFEAT_DIR: road-to-robotics/outputs/reap/rgbfeat; one process per
reading and seed, parts in OUT_DIR/parts), then run_verifier.py RGBFEAT_DIR OUT_DIR merge"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd, torch
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score

HERE = Path(__file__).resolve().parent
RGB, OUT = Path(sys.argv[1]), Path(sys.argv[2])
torch.set_num_threads(1)
MEAN = np.array((3.823351, -32.272697, 30.039783, 74.51135, -10.073078, 5.0724087), np.float32)
STD = np.array((17.493738, 42.95796, 40.683086, 9.202332, 7.6247225, 10.140567), np.float32)
WIN, STRIDE, TAU, EPOCHS, BATCH, LR, WD = 8, 2, 0.40, 30, 32, 1e-3, 1e-4
POS, NEG, CONFIRM = 10, 20, 4
meta = pd.read_csv(HERE / "data/episodes_meta.csv").set_index("episode")
npz = np.load(HERE / "data/episodes.npz")
E = {int(e): {"y": int(r.y), "end": int(r.end), "onset": int(r.onset), "main": int(r.main50),
              "s": (npz[f"s{e}"] - MEAN) / STD, "a": (npz[f"a{e}"] - MEAN) / STD,
              "v": np.load(RGB / f"ep{e:03d}.npy")} for e, r in meta.iterrows()}
MAIN = sorted(e for e in E if E[e]["main"]); NONTEST = sorted(e for e in E if not E[e]["main"])
T_COMMON = min(E[e]["end"] for e in MAIN)


class Verifier(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.vis = torch.nn.Sequential(torch.nn.Linear(108, 64), torch.nn.ReLU())
        self.sa = torch.nn.Sequential(torch.nn.Linear(12, 32), torch.nn.ReLU())
        self.gru, self.head = torch.nn.GRU(96, 64, batch_first=True), torch.nn.Linear(64, 1)

    def forward(self, v, sa):
        h, _ = self.gru(torch.cat([self.vis(v), self.sa(sa)], -1))
        return self.head(h[:, -1])[:, 0]


def windows(e, ts, act_from=None):
    ix = np.clip(np.asarray(ts)[:, None] + np.arange(-(WIN - 1) * STRIDE, 1, STRIDE)[None], 0, E[e]["end"] - 1)
    a = E[act_from if act_from is not None else e]["a"][ix]
    return E[e]["v"][ix], np.concatenate([E[e]["s"][ix], a], -1).astype(np.float32)


def label(e, t):
    """1 within POS of the failure event, 0 beyond NEG (or on a success), None in between."""
    if E[e]["y"] == 0:
        return 0.0
    d = abs(E[e]["onset"] - t)
    return 1.0 if d <= POS else 0.0 if d > NEG else None


def train_set(eps):
    V, S, Y = [], [], []
    for e in eps:
        ts = [t for t in range(0, E[e]["end"], STRIDE) if label(e, t) is not None]
        v, s = windows(e, ts); V.append(v); S.append(s); Y.append([label(e, t) for t in ts])
    return np.concatenate(V), np.concatenate(S), np.concatenate(Y).astype(np.float32)


def fit(eps, seed, weighted):
    V, S, Y = map(torch.as_tensor, train_set(eps))
    torch.manual_seed(seed)
    m = Verifier(); opt = torch.optim.AdamW(m.parameters(), lr=LR, weight_decay=WD)
    pw = torch.tensor((Y == 0).sum() / max((Y == 1).sum(), 1)) if weighted else None
    g = torch.Generator().manual_seed(seed)
    for _ in range(EPOCHS):
        for b in torch.randperm(len(Y), generator=g).split(BATCH):
            opt.zero_grad()
            torch.nn.functional.binary_cross_entropy_with_logits(m(V[b], S[b]), Y[b], pos_weight=pw).backward()
            opt.step()
    return m, int(len(Y)), int((Y == 1).sum())


def episode_score(m, e, act_from=None):
    ts = list(range(2, T_COMMON, STRIDE))
    with torch.no_grad():
        p = torch.sigmoid(m(*map(torch.as_tensor, windows(e, ts, act_from)))).numpy()
    run = np.minimum.reduce([p[i:len(p) - CONFIRM + 1 + i] for i in range(CONFIRM)])
    return float(run.max()), p, ts, run


def merge():
    parts = sorted((OUT / "parts").glob("rows_*.csv"))
    pd.concat([pd.read_csv(f) for f in parts]).sort_values(["reading", "seed", "control", "episode"]).to_csv(OUT / "rows.csv", index=False)
    wm = {}
    for f in sorted((OUT / "parts").glob("win_*.json")):
        for k, v in json.loads(f.read_text()).items():
            wm.setdefault(k, {}).update(v)
    wm = {k: {"median_auroc": float(np.median([o["auroc"] for o in v.values()])), "median_auprc": float(np.median([o["auprc"] for o in v.values()])),
              "per_seed": v} for k, v in wm.items()}
    (OUT / "window_metrics.json").write_text(json.dumps(wm, indent=1))
    print("merged", len(parts), "parts")


def main(only_reading, only_seed):
    rng0 = np.random.default_rng(0)
    partner = {e: int(rng0.choice([x for x in MAIN if x != e])) for e in MAIN}
    y_main = np.array([E[e]["y"] for e in MAIN])
    rows, win = [], {}
    for reading, weighted, extra in (("R1", False, False), ("R2", True, False), ("R4", False, True)):
        for seed in range(5):
            if reading != only_reading or seed != only_seed:
                continue
            for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(np.zeros(50), y_main):
                rest, test = [MAIN[i] for i in tr], [MAIN[i] for i in te]
                train, val = train_test_split(rest, test_size=0.25, stratify=[E[e]["y"] for e in rest], random_state=seed)
                m, nwin, npos = fit(train + (NONTEST if extra else []), seed, weighted)
                print(reading, seed, "train windows", nwin, "positives", npos, flush=True)
                tau_cal = max([episode_score(m, e)[0] for e in val if E[e]["y"] == 0] or [1.0])
                for e in test:
                    for ctl, src in (("true", None), ("shuffled", partner[e])):
                        sc, p, ts, run = episode_score(m, e, src)
                        fire = np.flatnonzero(run >= TAU)
                        rows.append({"reading": reading, "seed": seed, "episode": e, "y": E[e]["y"], "control": ctl, "score": sc,
                                     "fire_tau040": int(sc >= TAU), "tau_cal": tau_cal if reading == "R1" else "",
                                     "fire_cal": int(sc > tau_cal) if reading == "R1" else "",
                                     "first_fire_frame": ts[fire[0] + CONFIRM - 1] if len(fire) else -1})
                        # window level: p vs f on the test windows with f defined (per-query p, within the horizon)
                        if reading in ("R1", "R2"):
                            for t, pt in zip(ts, p):
                                f = label(e, t)
                                if f is not None:
                                    win.setdefault((reading, ctl), []).append((seed, f, float(pt)))
    (OUT / "parts").mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / f"parts/rows_{only_reading}_{only_seed}.csv", index=False)
    wm = {}
    for (reading, ctl), v in win.items():
        v = np.array(v)
        wm[f"{reading}:{ctl}"] = {str(only_seed): {"auroc": float(roc_auc_score(v[:, 1], v[:, 2])), "auprc": float(average_precision_score(v[:, 1], v[:, 2])),
                                                  "n": int(len(v)), "positives": int(v[:, 1].sum())}}
    (OUT / f"parts/win_{only_reading}_{only_seed}.json").write_text(json.dumps(wm))
    print("T_common", T_COMMON)


if __name__ == "__main__":
    merge() if sys.argv[-1] == "merge" else main(sys.argv[3], int(sys.argv[4]))
