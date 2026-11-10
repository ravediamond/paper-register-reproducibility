"""Copy the stored per-unit rows this bootstrap needs into data/ (small extracts; run once, on the Orin).
Sources (stored results, not rebuilt):
  Robometer: ~/scratch/robometer-scores/out/ab_top.jsonl + rescore/ab_top_rescore.jsonl (the g9a-ab scores of
             ravediamond/paper-vs-hardware posts/2026-10-23-paper-vs-hardware-robometer; combined as analyze_g9a_ab_complete.py)
  AAC:       paper-vs-hardware posts/2026-10-30-paper-vs-hardware-adaptive-chunking/out/aac_gate0/rows.jsonl
  PACT:      posts/2026-10-30-paper-vs-hardware-pact/expected/gate_b.json
  REMORA:    posts/2026-10-31-paper-vs-hardware-remora-readout/expected/summary.json (= road-to-robotics projects/remora-readout/results/summary.json)"""
import json, os, csv, hashlib
H = os.path.expanduser("~")
PVH = f"{H}/workspace/pvh-repro-2026-10-31/posts"
here = os.path.dirname(os.path.abspath(__file__)) + "/data"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
src = {}

top = f"{H}/scratch/robometer-scores/out/ab_top.jsonl"; res = f"{H}/scratch/robometer-scores/rescore/ab_top_rescore.jsonl"
part = [json.loads(l) for l in open(top) if l.strip()]; rs = [json.loads(l) for l in open(res) if l.strip()]
rs_ok = {int(r["episode_index"]): r for r in rs if r.get("p_succ") not in (None, "") and r["p_succ"] == r["p_succ"]}
rows = []
for r in part:
    e = int(r["episode_index"]); r = rs_ok.get(e, r)
    rows.append((e, r["success_class"], int(r["length"]), r["p_succ"]))
rows.sort()
with open(f"{here}/robometer_rollouts.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["episode_index", "success_class", "length", "p_succ"]); w.writerows(rows)
src["robometer_rollouts.csv"] = {"ab_top.jsonl": sha(top), "ab_top_rescore.jsonl": sha(res)}

a = f"{PVH}/2026-10-30-paper-vs-hardware-adaptive-chunking/out/aac_gate0/rows.jsonl"
with open(f"{here}/aac_boundaries.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["episode", "episode_index", "t", "jump_aac_overwrite_d8", "jump_fixed_overwrite_d8"])
    for l in open(a):
        r = json.loads(l); w.writerow([r["episode"], r["episode_index"], r["t"], r["jump"]["aac+overwrite|8"], r["jump"]["fixed+overwrite|8"]])
src["aac_boundaries.csv"] = {"rows.jsonl": sha(a)}

g = f"{PVH}/2026-10-30-paper-vs-hardware-pact/expected/gate_b.json"; d = json.load(open(g))
json.dump({"episodes": d["episodes"], "boundaries_k8": d["boundaries"]["8"], "k8_pact_minus_random": d["k8"]["pact_minus_random"]},
          open(f"{here}/pact_gate_b_k8.json", "w"), indent=1)
src["pact_gate_b_k8.json"] = {"gate_b.json": sha(g)}

s = f"{H}/workspace/road-to-robotics/projects/remora-readout/results/summary.json"; d = json.load(open(s))
json.dump({"test_episodes": d["test_episodes"], "paired": d["paired"]}, open(f"{here}/remora_paired.json", "w"), indent=1)
src["remora_paired.json"] = {"summary.json": sha(s)}
json.dump(src, open(f"{here}/SOURCES.json", "w"), indent=1)
