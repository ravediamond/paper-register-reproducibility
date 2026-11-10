#!/usr/bin/env python3
"""WS-217: ReAP Stage 1 (detector on DINOv2 patch tokens) + Stage 2 (action-conditioned predictor), runs M, T, A of PROTOCOL.md.
    reap_stage.py M|T|A [--seeds 5] [--steps 5000] [--check]   (inside the lerobot image, features from /s/feat)"""
import argparse, glob, json, sys, time
from pathlib import Path
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from sklearn.model_selection import StratifiedKFold
FEAT = Path("/s/feat"); dev = "cuda"
FI_BAR, FI_UNION = 1 / 20, 1 / 40
POL = ["act", "diffusion", "smolvla", "pi0", "pi0.5", "grootn1.7", "molmoact2"]

def auroc(y, s):
    y, s = np.asarray(y), np.asarray(s, float); r = s.argsort().argsort() + 1.0
    for v in np.unique(s):
        k = s == v
        if k.sum() > 1: r[k] = r[k].mean()
    p, n = y.sum(), (1 - y).sum()
    return float((r[y == 1].sum() - p * (p + 1) / 2) / (p * n))

def load(files, prefix, drop_reset=False):
    E = {}
    for f in files:
        z = np.load(f)
        for k in z.files:
            if k.startswith("tok"):
                e = int(k[3:]); m = z[f"meta{e}"]; idx = z[f"idx{e}"]; n = len(idx)
                if drop_reset and m[2] >= 0: n = int((idx < m[2]).sum())
                if n < 3: continue
                E[(prefix, e)] = dict(tok=torch.from_numpy(z[k][:n]), sc=torch.from_numpy(z[f"sc{e}"][:n].astype(np.float32)),
                                      act=z[f"act{e}"][:n], idx=idx[:n], fail=1 - int(m[0]), n=n, length=int(m[1]),
                                      pol=int(m[2]) if prefix == "ab" else -1, task=int(m[3]) if prefix == "ab" else 0)
    return E

def normalise(E):
    a = np.concatenate([v["act"].reshape(-1, 6) for v in E.values()]); mu, sd = a.mean(0), a.std(0) + 1e-6
    for v in E.values(): v["actn"] = ((v["act"] - mu) / sd).astype(np.float32)

class Block(nn.Module):
    def __init__(s, d, dkv, h=4):
        super().__init__(); s.q = nn.LayerNorm(d); s.kv = nn.Linear(dkv, d); s.at = nn.MultiheadAttention(d, h, batch_first=True)
        s.n2 = nn.LayerNorm(d); s.mlp = nn.Sequential(nn.Linear(d, 2 * d), nn.GELU(), nn.Linear(2 * d, d))
    def forward(s, x, kv):
        k = s.kv(kv); x = x + s.at(s.q(x), k, k, need_weights=False)[0]; return x + s.mlp(s.n2(x))

class Stage1(nn.Module):
    def __init__(s, d=256, M=32, nb=2, dz=128):
        super().__init__(); s.proj = nn.Linear(384, d); s.pos = nn.Parameter(torch.randn(28, d) * .02)
        s.lat = nn.Parameter(torch.randn(M, d) * .02); s.blocks = nn.ModuleList([Block(d, d) for _ in range(nb)])
        s.zp = nn.Linear(d, dz); s.head = nn.Sequential(nn.Linear(dz, 64), nn.ReLU(), nn.Linear(64, 1))
    def forward(s, tok):
        t = s.proj(tok) + s.pos; x = s.lat.expand(len(tok), -1, -1)
        for b in s.blocks: x = b(x, t)
        return s.zp(x.mean(1)), x   # z, L

class Stage2(nn.Module):
    def __init__(s, d=128, nb=3, dl=256, dz=128, H=10):
        super().__init__(); s.ap = nn.Linear(6, d); s.step = nn.Parameter(torch.randn(H, d) * .02)
        s.blocks = nn.ModuleList([Block(d, dl) for _ in range(nb)])
        s.mlp = nn.Sequential(nn.Linear(2 * d + dz, 256), nn.GELU(), nn.Linear(256, dz))
    def forward(s, z, L, a):
        x = s.ap(a) + s.step; a0 = x.mean(1)
        for b in s.blocks: x = b(x, L)
        return z + s.mlp(torch.cat([a0, x.mean(1), z], 1))

def cat_ep(E, keys):
    tok = torch.cat([E[k]["tok"] for k in keys]); sc = torch.cat([E[k]["sc"] for k in keys])
    y = torch.cat([torch.tensor([0. if E[k]["fail"] == 0 else j / (E[k]["n"] - 1) for j in range(E[k]["n"])]) for k in keys])
    act = torch.cat([torch.from_numpy(E[k]["actn"]) for k in keys])
    nxt = torch.cat([torch.tensor([i + 1 if j < E[k]["n"] - 1 else -1 for j in range(E[k]["n"])]) for i, k in
                     [(sum(E[q]["n"] for q in keys[:m]), keys[m]) for m in range(len(keys))]])
    # fix: nxt index of the following frame inside the concatenated arrays, computed with offsets
    off = np.cumsum([0] + [E[k]["n"] for k in keys[:-1]]); nxt = torch.cat([torch.tensor([o + j + 1 if j < E[k]["n"] - 1 else -1 for j in range(E[k]["n"])]) for o, k in zip(off, keys)])
    return tok.to(dev), sc.to(dev), y.to(dev), act.to(dev), nxt.to(dev)

def deq(tok, sc): return tok.float() * sc.view(-1, 1, 1)

def wbce(logit, y, wp, wn): return -(wp * y * F.logsigmoid(logit) + wn * (1 - y) * F.logsigmoid(-logit)).mean()

def train(E, keys, seed, steps, log=None):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    tok, sc, y, act, nxt = cat_ep(E, keys); N = len(y)
    pos = (y > 0).float().mean().item(); wp, wn = 0.5 / max(pos, 1e-3), 0.5 / max(1 - pos, 1e-3)
    def fit(params, lossf, steps):
        opt = torch.optim.AdamW(params, 1e-4, weight_decay=0.01)
        sch = torch.optim.lr_scheduler.LambdaLR(opt, lambda i: min(1, (i + 1) / 200) * 0.5 * (1 + np.cos(np.pi * i / steps)))
        for i in range(steps):
            b = torch.from_numpy(rng.integers(0, N, 64)).to(dev); l = lossf(b); opt.zero_grad(); l.backward(); opt.step(); sch.step()
            if log and i % 1000 == 0: log(i, l.item())
    s1 = Stage1().to(dev)
    def l1(b): z, _ = s1(deq(tok[b], sc[b])); return wbce(s1.head(z)[:, 0], y[b], wp, wn)
    fit(s1.parameters(), l1, steps)
    for p in s1.parameters(): p.requires_grad_(False)
    s1.eval(); ok = (nxt >= 0).nonzero()[:, 0]; s2 = Stage2().to(dev)
    def l2(b):
        b = ok[torch.randint(0, len(ok), (len(b),), device=dev)]; n = nxt[b]
        with torch.no_grad():
            z, L = s1(deq(tok[b], sc[b])); zt, _ = s1(deq(tok[n], sc[n]))
        zh = s2(z, L, act[b])
        return F.mse_loss(zh, zt) + wbce(s1.head(zh)[:, 0], y[n], wp, wn)
    fit(s2.parameters(), l2, steps)
    return s1.eval(), s2.eval()

@torch.no_grad()
def scores(s1, s2, e, ctl, partner=None):
    tok = deq(e["tok"], e["sc"]).to(dev); z, L = s1(tok); det = torch.sigmoid(s1.head(z)[:, 0]).cpu().numpy()
    a = e["actn"] if ctl == "true" else (np.zeros_like(e["actn"]) if ctl == "zero" else partner)
    zh = s2(z, L, torch.from_numpy(np.asarray(a, np.float32)).to(dev)); pred = torch.sigmoid(s1.head(zh)[:, 0]).cpu().numpy()
    pred = np.concatenate([pred[:-1] * 0 + pred[:-1], [-1.0]])   # last step has no future frame: never alarms
    return det, pred

def tau(arr, frac):
    a = np.sort(arr)[::-1]; return float(a[int(np.floor(frac * len(a)))])

def monitor(s1, s2, E, cal_keys, test_keys, seed, T_of=None):
    rng = np.random.default_rng(seed + 1000)
    S = {k: scores(s1, s2, E[k], "true") for k in cal_keys if E[k]["fail"] == 0}
    mx = lambda i, ks: np.array([S[k][i].max() for k in ks])
    succ = [k for k in cal_keys if E[k]["fail"] == 0]
    t = dict(det1=tau(mx(0, succ), FI_BAR), pred1=tau(mx(1, succ), FI_BAR), det2=tau(mx(0, succ), FI_UNION), pred2=tau(mx(1, succ), FI_UNION))
    out = {}
    keys = list(test_keys)
    for ctl in ("true", "shuffled", "zero"):
        for k in keys:
            n = T_of(k) if T_of else E[k]["n"]; e = E[k]
            pa = None
            if ctl == "shuffled":
                same = [q for q in keys if q != k and E[q]["task"] == e["task"] and E[q]["n"] > 1] or [q for q in keys if q != k]
                q = same[rng.integers(len(same))]; pa = np.resize(E[q]["actn"], e["actn"].shape) if len(E[q]["actn"]) < len(e["actn"]) else E[q]["actn"][:len(e["actn"])]
            d, p = scores(s1, s2, e, ctl, pa); d, p = d[:n], p[:n]
            out[(ctl, k)] = dict(det=float(d.max()), pred=float(p.max()),
                                 comb=float(max((d / t["det2"]).max(), (p / t["pred2"]).max())),
                                 fire_comb=bool((d > t["det2"]).any() or (p > t["pred2"]).any()), fire_det=bool((d > t["det1"]).any()), fire_pred=bool((p > t["pred1"]).any()), n=n)
    return out, t

def summarize(out, keys, E):
    y = np.array([E[k]["fail"] for k in keys]); r = {}
    for ctl in ("true", "shuffled", "zero"):
        for m, f in (("comb", "fire_comb"), ("det", "fire_det"), ("pred", "fire_pred")):
            if m == "det" and ctl != "true": continue
            fire = np.array([out[(ctl, k)][f] for k in keys]); r[f"{m}:{ctl}"] = dict(
                caught=int((fire & (y == 1)).sum()), fi=int((fire & (y == 0)).sum()), auroc=auroc(y, [out[(ctl, k)][m] for k in keys]))
    return r

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--seeds", type=int, default=5); ap.add_argument("--steps", type=int, default=5000)
    ap.add_argument("--check", action="store_true"); ap.add_argument("--out", default="/s/out")
    a = ap.parse_args(); Path(a.out).mkdir(exist_ok=True); t0 = time.time()
    log = lambda i, l: print(f"   step {i} loss {l:.4f} {time.time()-t0:.0f}s", flush=True)
    AB = load(sorted(glob.glob(str(FEAT / "ab_*.npz"))), "ab"); OU = load([FEAT / "ours.npz"], "ours", drop_reset=True)
    normalise(AB); normalise(OU)
    g16 = set(json.load(open("/r/shared/gate/data/2026-10-19_w1_screening/w1a_summary.json"))["in_g16_set"]) if False else None
    main50 = json.load(open("/s/main50.json")); main = sorted(k for k in OU if k[1] in main50); non = sorted(k for k in OU if k[1] not in main50)
    print("AB", len(AB), "ours", len(OU), "main", len(main), "non-test", len(non), flush=True)
    if a.check:
        k = main[0]; print("check shapes", OU[k]["tok"].shape, OU[k]["act"].shape, OU[k]["n"], "ramp", [round(j / (OU[k]["n"] - 1), 3) for j in range(3)])
        keys = list(AB)[:2] + main[:2]; s1, s2 = train({**AB, **OU}, keys, 0, 300, log); print("ok"); return
    Tc = 374; res = {"protocol": "repro/variants/reap/PROTOCOL.md", "steps": a.steps}
    if a.run in ("M", "T"):
        trbase = list(AB) + non if a.run == "M" else list(AB) + non
        E = {**AB, **OU}; yv = np.array([E[k]["fail"] for k in main]); T_of = lambda k: int((E[k]["idx"] < Tc).sum())
        per = []
        for seed in range(a.seeds):
            held = {}
            for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(np.zeros(len(main)), yv):
                trm, tem = [main[i] for i in tr], [main[i] for i in te]
                s1, s2 = train(E, trbase + (trm if a.run == "M" else []), seed, a.steps, log)
                o, t = monitor(s1, s2, E, trm, tem, seed, T_of); held.update(o); print("fold done", seed, t, f"{time.time()-t0:.0f}s", flush=True)
            r = summarize(held, main, E); per.append(r); print("seed", seed, {k: (v["caught"], v["fi"], round(v["auroc"], 3)) for k, v in r.items()}, flush=True)
            res["per_seed"] = per; json.dump(res, open(f"{a.out}/run{a.run}.json", "w"), indent=1)
            json.dump([[ctl, k[1], v] for (ctl, k), v in held.items()], open(f"{a.out}/run{a.run}_rows_seed{seed}.json", "w"))
        res["median"] = {m: {q: float(np.median([p[m][q] for p in per])) for q in ("caught", "fi", "auroc")} for m in per[0]}
        json.dump(res, open(f"{a.out}/run{a.run}.json", "w"), indent=1)
    else:
        E = AB; res["policies"] = {}
        for pi, pn in enumerate(POL):
            te = [k for k in AB if AB[k]["pol"] == pi]; tr = [k for k in AB if AB[k]["pol"] != pi]
            mn = {}
            for k in te: mn[AB[k]["task"]] = min(mn.get(AB[k]["task"], 99), AB[k]["n"])
            te = [k for k in te if mn[AB[k]["task"]] >= 5]; T_of = lambda k, mn=mn: mn[AB[k]["task"]]
            s1, s2 = train(AB, tr, 0, a.steps, log); o, t = monitor(s1, s2, AB, tr, te, 0, T_of)
            y = np.array([AB[k]["fail"] for k in te]); r = summarize(o, te, AB)
            r["n"] = len(te); r["failures"] = int(y.sum()); r["length_auroc"] = auroc(y, [AB[k]["length"] for k in te])
            res["policies"][pn] = r; print(pn, {k: v for k, v in r.items() if k in ("n", "failures", "length_auroc", "comb:true", "pred:true", "pred:shuffled")}, f"{time.time()-t0:.0f}s", flush=True)
            json.dump(res, open(f"{a.out}/runA.json", "w"), indent=1)
main()
