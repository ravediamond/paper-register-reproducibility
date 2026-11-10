"""WS-213, Amendment 1: re-run W1-C1 (ContactGuard-style check) of scripts/run_w1c_offline.py and write the out-of-fold scores.
The c1 loop is that script's own (same functions imported, c2 left out); the new part is the dump of the per-rollout out-of-fold
decision scores of both probes, for each of the 5 seeds. Latents: outputs/reap/latents (the W1-A encode, 69 rollouts).
    python rerun_w1c.py --w1 <weights_final.pt> --latents <dir> --stored <w1c_summary.json> --out-dir <dir>"""
import argparse, csv, json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("/work")
for p in (ROOT, ROOT / "src", ROOT / "scripts"):
    sys.path.insert(0, str(p))
import run_w1c_offline as R  # noqa: E402
from run_w1_offline_screening import encode_episode  # noqa: E402
from so101_harness.episodes import EpisodeDataset, download  # noqa: E402
from so101_harness.w1_live import W1LiveMonitor  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--w1", required=True); ap.add_argument("--latents", type=Path, required=True)
ap.add_argument("--stored", type=Path, required=True); ap.add_argument("--out-dir", type=Path, required=True); a = ap.parse_args()
ds = EpisodeDataset(download("ravediamond/so101-bowls-policy-rollouts", with_videos=True))
o = pd.read_csv(ROOT / "data/rollouts/so101-bowls-policy-rollouts_labels.csv"); o = o[o.outcome.isin(["success", "failure"])]
mon = W1LiveMonitor.from_checkpoint(a.w1)
rows = []
for r in o.itertuples():
    ep = int(r.episode_index); f = a.latents / f"ep{ep:03d}.npy"
    assert f.exists(), f
    z, acts = np.load(f), ds.actions(ep); T = len(acts)
    end = T if int(r.reset_start) < 0 else min(int(r.reset_start), T)
    an = R.c1_anchor(acts[:end, 5])
    if an is None or an < 2 or an + R.K_IMAGINE > T or np.isnan(z[an - 2: an + 1]).any():
        continue
    rows.append({"ep": ep, "y": int(r.outcome == "failure"), "z_hat": R.imagine_at(mon, z, acts, an), "z": z[an].astype(np.float64)})
y = np.array([x["y"] for x in rows])
imag, cur = R.probe_cv(np.stack([x["z_hat"] for x in rows]), y), R.probe_cv(np.stack([x["z"] for x in rows]), y)
st = json.loads(a.stored.read_text())["c1"]
res = {"scored_episodes": len(rows), "stored_scored_episodes": st["scored_episodes"],
       "imagined": {"stored": st["imagined"]["auroc"], "rerun": imag["auroc"], "equal": st["imagined"]["auroc"] == imag["auroc"]},
       "current": {"stored": st["current"]["auroc"], "rerun": cur["auroc"], "equal": st["current"]["auroc"] == cur["auroc"]}}
a.out_dir.mkdir(parents=True, exist_ok=True)
(a.out_dir / "match_w1c.json").write_text(json.dumps(res, indent=1))
with open(a.out_dir / "w1c_rows.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["episode", "failure", "seed", "oof_imagined", "oof_current"])
    for i, x in enumerate(rows):
        for sd in imag["oof"]:
            w.writerow([x["ep"], x["y"], sd, f"{imag['oof'][sd][i]:.6f}", f"{cur['oof'][sd][i]:.6f}"])
print(res)
