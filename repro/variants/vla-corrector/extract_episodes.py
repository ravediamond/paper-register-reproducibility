"""Step 1 (needs pyarrow; run in lerobot-jetson:public): joint positions, commanded actions, task, usable end frame and
outcome of the 69 rollouts -> data/episodes.npz. No video is read. See PROTOCOL.md section 4."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from huggingface_hub import snapshot_download

OUT = Path(sys.argv[1]); LABELS = Path(sys.argv[2]); W1A = Path(sys.argv[3]); ONSETS = Path(sys.argv[4])
root = Path(snapshot_download("ravediamond/so101-bowls-policy-rollouts", repo_type="dataset", allow_patterns=["data/*", "meta/*"]))
fr = pd.concat([pd.read_parquet(f) for f in sorted((root / "data").glob("chunk-*/file-*.parquet"))], ignore_index=True)
tasks = pd.concat([pd.read_parquet(f) for f in sorted((root / "meta/episodes").glob("chunk-*/file-*.parquet"))])
oc = pd.read_csv(LABELS); oc = oc[oc.outcome.isin(["success", "failure"])]
g16 = {e["episode_index"] for e in json.loads(W1A.read_text())["episodes"] if e["in_g16_set"]}
on = pd.read_csv(ONSETS).groupby("episode_index").last()
d = {}
meta = []
for r in oc.itertuples():
    ep = int(r.episode_index); rows = fr[fr.episode_index == ep].sort_values("frame_index")
    s = np.stack(rows["observation.state"].to_numpy()).astype(np.float32); a = np.stack(rows["action"].to_numpy()).astype(np.float32)
    end = len(s) if int(r.reset_start) < 0 else min(int(r.reset_start), len(s))
    d[f"s{ep}"], d[f"a{ep}"] = s, a
    t = tasks[tasks.episode_index == ep]["tasks"].iloc[0]
    meta.append({"episode": ep, "y": int(r.outcome == "failure"), "task": str(t[0] if not isinstance(t, str) else t), "n": len(s), "end": end,
                 "main50": int(ep in g16), "onset": int(on.loc[ep, "onset_frame"]) if ep in on.index else -1, "policy": r.policy})
pd.DataFrame(meta).to_csv(OUT.parent / "episodes_meta.csv", index=False)
np.savez_compressed(OUT, **d)
print(len(meta), "episodes; fps", json.loads((root / "meta/info.json").read_text())["fps"])
