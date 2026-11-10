"""WS-213, Amendment 1: evaluate the stored HWM F2 checkpoints (learned, disp) and write per-anchor cosines (no training).
Code: projects/hwm-crossover/scripts/hwm_train.py (imported; evaluate() unchanged). Checkpoints: results_gate0_v2/f2_<kind>.pt.
    python rerun_hwm.py <hwm project dir> --out-dir <dir>"""
import argparse, csv, json, sys
from pathlib import Path
import numpy as np, torch

ap = argparse.ArgumentParser(); ap.add_argument("proj", type=Path); ap.add_argument("--out-dir", type=Path, required=True); a = ap.parse_args()
sys.path.insert(0, str(a.proj / "scripts"))
import hwm_train as H  # noqa: E402
d = dict(np.load(a.proj / "out_v2/latents.npz")); low = dict(np.load(a.proj / "out_v2/lowlevel.npz"))
stored = json.loads((a.proj / "results_gate0_v2/gate0.json").read_text())
res, cos = {}, {}
for kind in ("learned", "disp"):
    m = H.F2(kind).to(H.DEV); m.load_state_dict(torch.load(a.proj / f"results_gate0_v2/f2_{kind}.pt", map_location=H.DEV)); m.eval()
    _, c = H.evaluate(m, d, low); cos[kind] = c.mean(1)
    res[kind] = {"stored": stored[kind]["cos_mean"], "rerun": round(float(c.mean()), 4)}
    res[kind]["equal"] = res[kind]["stored"] == res[kind]["rerun"]
eps = d["episode"][low["anchors"]]
a.out_dir.mkdir(parents=True, exist_ok=True)
(a.out_dir / "match_hwm.json").write_text(json.dumps(res, indent=1))
with open(a.out_dir / "hwm_rows.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["episode", "anchor", "cos_learned", "cos_disp"])
    for e, t, x, y in zip(eps, low["anchors"], cos["learned"], cos["disp"]):
        w.writerow([int(e), int(t), f"{x:.6f}", f"{y:.6f}"])
print(res, "episodes", len(set(eps.tolist())))
