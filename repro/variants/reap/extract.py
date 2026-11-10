#!/usr/bin/env python3
"""WS-217 feature extraction (PROTOCOL.md section 4, items 2-4): DINOv2-small patch tokens, 224x392 input, pooled 4x4 to
4x7 = 28 tokens, int8 with a per-frame scale, one frame every 0.5 s, plus the next 10 commanded actions (ArmnetBench) or
the next 15 resampled to 10 (ours). Modes: `ours` (69 episodes), `ab` (ArmnetBench top camera, streamed file by file)."""
import argparse, concurrent.futures as cf, fcntl, json, os, sys, threading, time, urllib.request
from pathlib import Path
import numpy as np, pandas as pd, torch, av, cv2
sys.path.insert(0, "/r/src")
from transformers import AutoModel

OUT = Path("/s/feat"); OUT.mkdir(parents=True, exist_ok=True)
MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1); STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
REV = "1db69c82b589c7172ee31a6b8f7ef58d1fc2c663"; REPO = "armnet/armnetbench_v01_lerobot_so101"
_model = None

def dino(imgs):  # list of (224,392,3) uint8 -> int8 (n,28,384), fp16 scale (n,)
    global _model
    if _model is None:
        _model = AutoModel.from_pretrained("facebook/dinov2-small").cuda().half().eval()
    outs = []
    for i in range(0, len(imgs), 64):
        x = torch.from_numpy(np.stack(imgs[i:i + 64])).permute(0, 3, 1, 2).float() / 255
        x = ((x - MEAN) / STD).cuda().half()
        with open("/s/gpu.lock", "a") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            with torch.no_grad():
                h = _model(pixel_values=x).last_hidden_state[:, 1:].float()
            fcntl.flock(lk, fcntl.LOCK_UN)
        h = h.view(-1, 16, 28, 384).permute(0, 3, 1, 2)
        h = torch.nn.functional.avg_pool2d(h, 4).flatten(2).permute(0, 2, 1)  # (n,28,384)
        outs.append(h.cpu())
    h = torch.cat(outs); sc = h.abs().amax((1, 2)).clamp_min(1e-6) / 127
    return torch.round(h / sc.view(-1, 1, 1)).clamp(-127, 127).to(torch.int8).numpy(), sc.half().numpy()

def chunks(a, idx, n_in, n_out):  # a (T,6); chunk a[f:f+n_in] padded by repeat, resampled to n_out
    sel = np.round(np.linspace(0, n_in - 1, n_out)).astype(int)
    return np.stack([a[np.minimum(f + sel, len(a) - 1)] for f in idx]).astype(np.float32)

def ours():
    from so101_harness.episodes import EpisodeDataset, download
    ds = EpisodeDataset(download("ravediamond/so101-bowls-policy-rollouts"))
    lab = pd.read_csv(Path(ds.root) / "meta" / "rollout_labels.csv").set_index("episode_index")
    cam = "observation.images.front_top_camera"; res = {}
    for e in ds.episode_indices():
        fr = list(ds.iter_frames(e, cam, stride=15, size=(392, 224)))
        idx = np.array([i for i, _ in fr]); tok, sc = dino([im for _, im in fr])
        a = ds.actions(e)
        res[f"tok{e}"], res[f"sc{e}"], res[f"idx{e}"], res[f"act{e}"] = tok, sc, idx, chunks(a, idx, 15, 10)
        res[f"meta{e}"] = np.array([int(lab.loc[e, "outcome"] == "success"), len(a), lab.loc[e, "reset_start"]])
        print(e, len(idx), flush=True)
    np.savez_compressed(OUT / "ours.npz", **res)

def dl(url, dst):
    for k in range(5):
        try:
            urllib.request.urlretrieve(url, dst); return
        except Exception as ex:
            print("retry", dst, ex, flush=True); time.sleep(5)
    raise RuntimeError(dst)

def ab():
    cam = "observation.images.top"; raw = Path("/s/raw"); raw.mkdir(exist_ok=True)
    m = pd.read_parquet("/s/ab/meta/episodes/chunk-000/file-000.parquet")
    m = m[m["success_class"].isin(["successful", "failure"]) & (m["policy_type"] != "teleoperated")]
    m = m.assign(task=m["tasks"].map(lambda x: str(x if isinstance(x, str) else x[0])))
    fc = f"videos/{cam}/"; m = m.assign(ch=m[fc + "chunk_index"], fi=m[fc + "file_index"], t0=m[fc + "from_timestamp"], t1=m[fc + "to_timestamp"])
    data = {}
    for f in sorted(set(zip(m.ch, m.fi))):
        pass
    files = sorted(set(zip(m.ch, m.fi)))
    print(len(m), "episodes", len(files), "files", flush=True)
    ex = cf.ThreadPoolExecutor(3); fut = {}
    def start(k):
        ch, fi = files[k]; p = raw / f"{ch}_{fi}.mp4"
        fut[k] = (p, ex.submit(dl, f"https://huggingface.co/datasets/{REPO}/resolve/{REV}/videos/{cam}/chunk-{ch:03d}/file-{fi:03d}.mp4", p))
    for k in range(min(3, len(files))): start(k)
    for k, (ch, fi) in enumerate(files):
        done = OUT / f"ab_{ch}_{fi}.npz"
        p, fu = fut.pop(k); fu.result()
        if k + 3 < len(files): start(k + 3)
        if done.exists():
            p.unlink(); continue
        sub = m[(m.ch == ch) & (m.fi == fi)].sort_values("t0"); res = {}
        eps = [(int(r.episode_index), float(r.t0), float(r.t1)) for r in sub.itertuples()]
        imgs = {e: [] for e, _, _ in eps}; fidx = {e: [] for e, _, _ in eps}
        with av.open(str(p)) as c:
            s = c.streams.video[0]; s.thread_type = "AUTO"; j = 0
            for fr in c.decode(s):
                t = fr.time
                while j < len(eps) and t >= eps[j][2] - 0.025: j += 1
                if j >= len(eps): break
                e, t0, _ = eps[j]
                if t < t0 - 0.025: continue
                i = int(round((t - t0) * 20))
                if i % 10 == 0:
                    imgs[e].append(cv2.resize(fr.to_ndarray(format="rgb24"), (392, 224), interpolation=cv2.INTER_AREA)); fidx[e].append(i)
        for e, _, _ in eps:
            if not imgs[e]: continue
            row = sub[sub.episode_index == e].iloc[0]
            tok, sc = dino(imgs[e]); idx = np.array(fidx[e])
            d0 = int(row["dataset_from_index"]); d1 = int(row["dataset_to_index"])
            a = pd.read_parquet(f"/s/ab/data/chunk-{int(row['data/chunk_index']):03d}/file-{int(row['data/file_index']):03d}.parquet")
            a = np.stack(a.loc[(a["index"] >= d0) & (a["index"] < d1), "action"].values)
            res[f"tok{e}"], res[f"sc{e}"], res[f"idx{e}"], res[f"act{e}"] = tok, sc, idx, chunks(a, idx, 10, 10)
            res[f"meta{e}"] = np.array([int(row["success_class"] == "successful"), len(a), ["act","diffusion","smolvla","pi0","pi0.5","grootn1.7","molmoact2"].index(row["policy_type"]),
                                        sorted(m["task"].unique()).index(row["task"])])
        np.savez_compressed(done, **res); p.unlink()
        print("file", k, "/", len(files), len(res) // 5, "eps", time.strftime("%H:%M:%S"), flush=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode"); {"ours": ours, "ab": ab}[ap.parse_args().mode]()
