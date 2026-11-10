"""WS-213, Amendment 1: re-run G1b for W2' (best-val weights) and write per-anchor hits (episode, t, d, model_hit; H = d).
Code: wm_train/g1_suite.py (W2Cand, run_rollouts logic) and g6a.py's DINOv2-small extraction. The DINO tokens of the 25 val
episodes are not written to disk (about 4 GB at 16 x 16; the disk has less): each episode is extracted, 2 x 2 average-pooled to
8 x 8 per view (the pooling the stored W2' features used, WS-090 note) and kept in memory.
    WM_SPLIT=<split.json> python rerun_g1b_w2.py <weights_best.pt> --data <snapshot> --out-dir <dir> --stored <g1_final_w2prime_best.json>"""
import argparse, csv, json, os, sys
from pathlib import Path
import numpy as np, torch, torch.nn.functional as F
sys.path.insert(0, os.environ.get("WM_CODE", "/code"))
import g1b_range as G, g1_suite as S, probe as P, train_w2 as W  # noqa: E402


def extract(data, tab, eps, workers):
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    from transformers import AutoModel
    dino = AutoModel.from_pretrained("facebook/dinov2-small").to(P.DEV).eval()
    ds = LeRobotDataset(f"local/{data.name}", root=data, delta_timestamps={c: [0.0] for c in P.CAMS.values()})
    out = {}
    for ep in eps:
        start, act, _ = tab[ep]
        loader = torch.utils.data.DataLoader(G.FrameSet(ds, np.arange(start, start + len(act))), batch_size=64, num_workers=workers, shuffle=False)
        tok = {v: [] for v in W.VIEWS}
        with torch.no_grad():
            for b in loader:
                for v in W.VIEWS:
                    t = dino(pixel_values=b[v].to(P.DEV)).last_hidden_state[:, 1:].half().cpu()      # (B, 256, 384), as g6a.py
                    t = t.float().view(len(t), 16, 16, 384).permute(0, 3, 1, 2)
                    tok[v].append(F.avg_pool2d(t, 2).flatten(2).transpose(1, 2).half())             # (B, 64, 384)
        out[ep] = W.ln(torch.cat([torch.cat(tok[v]) for v in W.VIEWS], 1))
        print("extracted episode", ep, len(act), flush=True)
    return out


def hits(s, k=8):
    s = s[:, :k]
    return ((s[:, 1:] <= s[:, :1]).sum(1) == 0).numpy().astype(int)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("weights", type=Path); ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True); ap.add_argument("--stored", type=Path, required=True); ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    torch.manual_seed(0)
    split = json.loads(Path(os.environ["WM_SPLIT"]).read_text()); eps = split["val_episodes"]
    a_mean, a_std = P.action_stats(a.data, split["train_episodes"]); tab = P.frame_table(a.data)
    a_norm = {e: ((tab[e][1] - a_mean) / a_std).astype(np.float32) for e in eps}
    Z = extract(a.data, tab, eps, a.workers)
    cand = S.W2Cand.__new__(S.W2Cand)
    ckpt = torch.load(a.weights, map_location="cpu", weights_only=False)
    cand.model = W.W2Predictor(ckpt["config"]["tokens"], feat=ckpt["config"].get("feat", 384)); cand.model.load_state_dict(ckpt["state_dict"]); cand.model.to(S.DEV).eval()
    anchors, chunks = G.build_chunks(a_norm, eps, np.random.default_rng(0))
    chunks = np.concatenate([chunks, np.zeros_like(chunks[:, :1])], 1)             # chunk 8 as g1_suite.run_rollouts
    dist, _, _ = G.rollout_stream(cand, Z, anchors, chunks, extra={})
    cells = G.cells_from(dist, anchors, k_rank=8)
    st = json.loads(a.stored.read_text())["g1b"]["cells"]
    match = {k: {"stored": st[k]["accuracy"], "rerun": cells[k]["accuracy"], "equal": st[k]["accuracy"] == cells[k]["accuracy"]} for k in st}
    a.out_dir.mkdir(parents=True, exist_ok=True)
    (a.out_dir / "match_g1b_w2.json").write_text(json.dumps({"model": match, "anchors": len(anchors)}, indent=1))
    with open(a.out_dir / "g1b_rows_w2.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["episode", "t", "d", "model_hit"])
        for d in G.DS:
            for (ep, t), x in zip(anchors, hits(dist[(d, "d")])):
                w.writerow([ep, t, d, int(x)])
    print("cells equal:", sum(v["equal"] for v in match.values()), "/", len(match), {k: (v["stored"], v["rerun"]) for k, v in match.items() if k.endswith("Hd")})


main()
