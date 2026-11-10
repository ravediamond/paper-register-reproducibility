"""WS-220, Amendment 3: copy the per-clip Gate A errors of RoboJEPA 300M @ 300k (setting a) from the stored raw result into data/robojepa_rows.csv
and write the match gate against gateA_summary.json. No model is run; no value is recomputed except the means used for the gate.
    python extract_robojepa_rows.py <raw gateA_300m_300k_settinga.json> <gateA_summary.json> --out-dir <data dir>
Raw file: road-to-robotics, branch exp/robojepa-gate, commit 20f820d, projects/vla-jepa-world-model/robojepa_gate/results/gateA/ (git show <commit>:<path>)."""
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("raw", type=Path); ap.add_argument("summary", type=Path); ap.add_argument("--out-dir", type=Path, required=True)
a = ap.parse_args()
raw = json.loads(a.raw.read_text()); st = json.loads(a.summary.read_text())["300m_300k_settinga"]
pc = raw["per_clip"]
m = np.array([np.mean(c["l1"]["model_true"], axis=0) for c in pc]); b = np.array([np.mean(c["l1"]["copy_last"], axis=0) for c in pc])  # clips x 9, mean over prefixes
red = 1 - m.mean() / b.mean()
res = {"stored": {"model_true": st["mean_1_9"]["model_true"], "copy_last": st["mean_1_9"]["copy_last"], "reduction": st["crit1_reduction_vs_copy_last"]["value"]},
       "rerun": {"model_true": float(m.mean()), "copy_last": float(b.mean()), "reduction": float(red)}, "clips": len(pc), "episodes": len({c["episode"] for c in pc}),
       "source": "stored raw Gate A result (not a re-run), raw sha256 " + hashlib.sha256(a.raw.read_bytes()).hexdigest()[:16],
       "checkpoint_sha256": raw["checkpoint_sha256"], "robo_jepa_commit": raw["robo_jepa_commit"], "seed": raw["seed"]}
res["matches"] = all(abs(res["stored"][k] - res["rerun"][k]) < 1e-12 for k in res["stored"]) and res["clips"] == st["clips"] and res["episodes"] == st["episodes"]
a.out_dir.mkdir(parents=True, exist_ok=True)
(a.out_dir / "robojepa_match.json").write_text(json.dumps(res, indent=1) + "\n")
if res["matches"]:
    with open(a.out_dir / "robojepa_rows.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["clip", "episode", "start", "model_l1_mean_1_9", "copy_last_l1_mean_1_9", "model_l1_step9", "copy_last_l1_step9"])
        for i, c in enumerate(pc):
            w.writerow([i, c["episode"], c["start"], f"{m[i].mean():.12f}", f"{b[i].mean():.12f}", f"{m[i, 8]:.12f}", f"{b[i, 8]:.12f}"])
print(json.dumps(res, indent=1))
