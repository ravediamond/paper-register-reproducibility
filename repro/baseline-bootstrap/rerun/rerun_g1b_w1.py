"""WS-213, Amendment 1: re-run G1b for W1 (and the action-only baseline) and write per-anchor hits.
Same code as wm_train/g1b_range.py and g1_diag.py (imported, not copied); only the per-anchor dump is new.
    WM_SPLIT=<split.json> python rerun_g1b_w1.py <w1 dir> --data <snapshot> --out-dir <dir> --stored-g1b <g1b_range_w1.json> --stored-diag <g1_diag_exploratory.json>
Writes g1b_rows_w1.csv (episode,t,d,model_hit,action_only_hit; H = d) and match_g1b_w1.json (all 20 stored cells + 5 action-only cells)."""
import argparse, csv, json, os, sys
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, os.environ.get("WM_CODE", "/code"))
import g1b_range as G, g1_diag as D, probe as P  # noqa: E402


def hits(s, k=8):
    s = s[:, :k]
    return ((s[:, 1:] <= s[:, :1]).sum(1) == 0).numpy().astype(int)  # ties count against the true chunk, as cells_from


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("weights", type=Path); ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True); ap.add_argument("--stored-g1b", type=Path, required=True)
    ap.add_argument("--stored-diag", type=Path, required=True); ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    torch.manual_seed(0)
    split = json.loads(Path(os.environ["WM_SPLIT"]).read_text()); eps = split["val_episodes"]
    cand = G.W1(a.weights)
    a_mean, a_std = P.action_stats(a.data, split["train_episodes"]); tab = P.frame_table(a.data)
    a_norm = {e: ((tab[e][1] - a_mean) / a_std).astype(np.float32) for e in eps}
    s_norm = {e: ((tab[e][2] - a_mean) / a_std).astype(np.float32) for e in eps}
    Z = G.embed_episodes(cand, a.data, tab, eps, a.workers)
    anchors, chunks = G.build_chunks(a_norm, eps, np.random.default_rng(0))
    dist, _, _ = G.rollout_stream(cand, Z, anchors, chunks)
    cells = G.cells_from(dist, anchors)
    cost = D.end_state_dist(chunks, anchors, s_norm)
    act_cells = G.cells_from({(d, "d"): cost[d] for d in G.DS}, anchors)
    st = json.loads(a.stored_g1b.read_text())["cells"]; sd = json.loads(a.stored_diag.read_text())["action_only_g1b"]
    match = {"model": {k: {"stored": st[k]["accuracy"], "rerun": cells[k]["accuracy"], "equal": st[k]["accuracy"] == cells[k]["accuracy"]} for k in st},
             "action_only": {k: {"stored": sd[k]["accuracy"], "rerun": act_cells[k]["accuracy"], "equal": sd[k]["accuracy"] == act_cells[k]["accuracy"]} for k in sd},
             "anchors": len(anchors)}
    a.out_dir.mkdir(parents=True, exist_ok=True)
    (a.out_dir / "match_g1b_w1.json").write_text(json.dumps(match, indent=1))
    with open(a.out_dir / "g1b_rows_w1.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["episode", "t", "d", "model_hit", "action_only_hit"])
        for d in G.DS:
            m, o = hits(dist[(d, "d")]), hits(cost[d])
            for (ep, t), x, y in zip(anchors, m, o):
                w.writerow([ep, t, d, int(x), int(y)])
    print("model cells equal:", sum(v["equal"] for v in match["model"].values()), "/", len(match["model"]),
          " action-only equal:", sum(v["equal"] for v in match["action_only"].values()), "/", len(match["action_only"]))


main()
