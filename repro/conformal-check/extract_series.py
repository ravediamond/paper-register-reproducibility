"""Recompute the W1 surprise series of the stored run (posts/2026-10-23-paper-vs-hardware-contactguard, c2): per rollout,
per anchor the maximum L2 surprise over k in {15, 20, 25}. Same code as scripts/run_w1c_offline.py (road-to-robotics).
Run from the road-to-robotics repo: python3 extract_series.py --w1 W --latents L --root DS --out series.json"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

import os
RR = Path(os.environ.get("RR", Path.home() / "workspace/road-to-robotics"))
for p in (RR, RR / "src", RR / "scripts"):
    sys.path.insert(0, str(p))
LONG_K = (15, 20, 25)

ap = argparse.ArgumentParser()
ap.add_argument("--w1", required=True); ap.add_argument("--latents", type=Path, required=True)
ap.add_argument("--root", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
a = ap.parse_args()
from run_w1_offline_screening import anchor_curves
from so101_harness.episodes import EpisodeDataset
from so101_harness.w1_live import W1LiveMonitor

ds = EpisodeDataset(a.root)
o = pd.read_csv(RR / "data/rollouts/so101-bowls-policy-rollouts_labels.csv")
o = o[o.outcome.isin(["success", "failure"])]
mon = W1LiveMonitor.from_checkpoint(a.w1)
out = []
for r in o.itertuples():
    ep = int(r.episode_index)
    z, acts = np.load(a.latents / f"ep{ep:03d}.npy"), ds.actions(ep)
    T = len(acts)
    end = T if int(r.reset_start) < 0 else min(int(r.reset_start), T)
    mode = r.failure_mode if isinstance(r.failure_mode, str) and r.failure_mode else ("none" if r.outcome == "failure" else "")
    cur = anchor_curves(mon, z, acts, end)
    out.append({"ep": ep, "outcome": r.outcome, "mode": mode, "long": [max(c["l2"][k] for k in LONG_K) for c in cur]})
    print(ep, r.outcome, len(cur), flush=True)
a.out.write_text(json.dumps(out))
