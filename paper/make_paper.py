#!/usr/bin/env python3
"""paper-register-reproducibility: fill paper/DRAFT_4p.md.in from repro/*/expected/ into numbers.json, DRAFT_4p.md,
main.tex and refs.bib. Every number has an anchor; a literal that is not found in its source file fails the build.
Table 1 is generated from the register. Citations are written [@<arXiv id>] in the template."""
import collections, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
R = ROOT / "repro"
REG = R / "register/expected"
PC = R / "prereg-check/expected"
CR = R / "cold-reproduction/expected"
N, A = {}, {}


def put(key, value, anchor):
    N[key] = value; A[key] = anchor


def lit_file(key, rel, text, value):
    assert text in (R / rel).read_text(), f"{text!r} not in {rel}"
    put(key, value, f"repro/{rel}: '{text}'")


def pct(x):
    return f"{100 * x:.1f}"


def own(c):
    return "not a paper claim" in (c.get("stated_in") or "")


def register():
    """Only claims stated in the papers count. Rows that are our own claims (stated_in 'not a paper claim') belong to the other
    papers of the series and are left out, and so is a paper with no claim of its own (TurboVLA, kept in the text as an example)."""
    allp = json.loads((REG / "register.json").read_text())["papers"]
    papers = [p for p in allp if any(not own(c) for c in p["claims"])]
    dropped = [p["paper"] for p in allp if p not in papers]
    assert dropped == ["TurboVLA"], dropped
    a = "repro/register/expected/register.json papers with at least one paper claim (TurboVLA has none)"
    wt = lambda p: len(p["arxiv"].split(",")) if re.fullmatch(r"[\d. ,]+", p["arxiv"]) else 1  # noqa: E731  FAIL-Detect and SAFE: two papers, one row
    a += "; a row citing two arXiv ids counts as two papers"
    put("papers", str(sum(wt(p) for p in papers)), a + ", sum of papers")
    put("rows", str(len(papers)), "repro/register/expected/register.json papers with at least one paper claim, rows")
    v = collections.Counter()
    for p in papers: v[p["verdict"]] += wt(p)
    for k in ("reproduces", "fail", "not proven", "not tested"):
        put("p_" + k.replace(" ", "_"), str(v[k]), a + f", verdict = {k}")
    assert not v["withdrawn"]
    rc = collections.Counter()
    for p in papers: rc[p["their_rig_cost_class"]] += wt(p)
    for k, name in (("sim", "sim"), ("gt20k", ">$20k"), ("5to20k", "$5–20k"), ("lt5k", "<$5k"), ("unstated", "unstated")):
        put("rig_" + k, str(rc[name]), a + f", their_rig_cost_class = {name}")
    put("rig_far", str(rc["sim"] + rc[">$20k"]), a + ", their_rig_cost_class = sim + >$20k")
    put("cost", f"{sum(float(p.get('cost_usd') or 0) for p in papers):.2f}", a + ", sum of cost_usd")
    cl = [c for p in papers for c in p["claims"] if not own(c)]
    a = "repro/register/expected/register.json papers[*].claims without stated_in 'not a paper claim'"
    put("c_paper", str(len(cl)), a + ", len")
    cv = collections.Counter(c["verdict"] for c in cl)
    for k in ("reproduces", "fail", "not proven", "not tested"):
        put("c_" + k.replace(" ", "_"), str(cv[k]), a + f", verdict = {k}")
    assert sum(cv.values()) == len(cl) and not cv["withdrawn"]
    put("c_paper_repro", N["c_reproduces"], a + ", verdict = reproduces"); put("c_paper_fail", N["c_fail"], a + ", verdict = fail")
    put("c_open", str(cv["not proven"] + cv["not tested"]), a + ", verdict = not proven + not tested")
    allc = {c["id"]: c for p in allp for c in p["claims"]}
    by = allc
    for key, cid, field, text in (("ex_a_ours", "C-019-3", "ours", "4,751 ms"), ("ex_a_bar", "C-019-3", "bar", "298 ms"),
                                  ("ex_b_ours", "C-010-2", "ours", "0.818"), ("ex_b_len", "C-010-2", "ours", "0.938"),
                                  ("ex_c_ours", "C-001-2", "ours", "0.60"), ("ex_c_base", "C-001-2", "ours", "0.68–0.90"),
                                  ("ex_c_bar", "C-001-2", "bar", "0.8"),
                                  ("tv_swap", "C-012-1", "ours", "0.020°"), ("tv_ctl", "C-012-1", "ours", "5.5°"),
                                  ("tv_bug", "C-012-1", "bar", "≥ 5°"), ("tv_data", "C-012-1", "bar", "< 1°")):
        assert text in by[cid][field], f"{text!r} not in {cid}/{field}"
        put(key, text, f"repro/register/expected/register.json claims, id {cid}, {field}: '{by[cid][field]}'")
    # the cheapest-baseline comparisons among the paper claims, outcome read by hand from bar and ours (Table 5)
    base = {"C-001-1": "beat", "C-001-2": "lost", "C-002-1": "lost", "C-003-1": "under", "C-006-1": "lost", "C-008-1": "beat",
            "C-010-2": "lost", "C-016-2": "beat", "C-019-2": "lost", "C-020-1": "beat", "C-022-1": "under"}
    ba = "repro/register/expected/register.json claims " + ", ".join(base) + " (compared with a cheap baseline; outcome by hand)"
    for cid, o in base.items():
        assert not own(by[cid]) and by[cid]["verdict"] == {"beat": "reproduces", "lost": "fail", "under": "fail"}[o], cid
    put("b_n", str(len(base)), ba + ", len"); bc = collections.Counter(base.values())
    for k in ("beat", "lost", "under"):
        put("b_" + k, str(bc[k]), ba + f", outcome = {k}")
    # paired bootstrap on the same comparisons (repro/baseline-bootstrap, WS-212): counts and the Table 3 interval column
    bsj = json.loads((R / "baseline-bootstrap/expected/bootstrap.json").read_text()); bsa = "repro/baseline-bootstrap/expected/bootstrap.json"
    assert sorted(c["claim"] for c in bsj["claims"]) == sorted(base), "bootstrap rows must be the Table 3 rows"
    bso = collections.Counter(c["outcome"] for c in bsj["claims"])
    NOM, NAV = "rerun does not match the stored result", "rows not available"
    for key, o in (("bs_beats", "beats"), ("bs_loses", "loses"), ("bs_unclear", "unclear"), ("bs_nomatch", NOM), ("bs_navail", NAV)):
        put(key, str(bso[o]), bsa + f", claims with outcome = {o}")
    put("bs_na", str(bso[NOM] + bso[NAV]), bsa + ", claims without an interval (re-run not matching, or no rows)")
    put("bs_have", str(sum("ci95" in c for c in bsj["claims"])), bsa + ", claims with an interval")
    sg = lambda v: ("+" if v > 0 else "−" if v < 0 else "") + f"{abs(v):.2f}"
    for c in bsj["claims"]:
        if "per_d" in c:   # a range of baselines: worst and best case over the target distance d
            def one(k):
                p = c["per_d"][k]; return f"d = {k[1:]}: {sg(p['point_difference'])} [{sg(p['ci95'][0])}, {sg(p['ci95'][1])}]"
            cell = f"worst case {one(c['worst_d'])}; best case {one(c['best_d'])}, {c['outcome']}"
        elif "ci95" in c:
            lo, hi = c["ci95"]
            cell = (f"ratio {c['point_difference']:.2f} [{lo:.2f}, {hi:.2f}]" if c.get("point_is") == "ratio"
                    else f"{sg(c['point_difference'])} [{sg(lo)}, {sg(hi)}]")
            cell += f", {c['outcome']}"
        elif c["outcome"] == NOM:   # both values, as the protocol (Amendment 1) requires
            st, rr = c["stored"], c["rerun"]
            if "d30_Hd" in st:
                cell = f"{NOM} (d = 30: stored {st['d30_Hd']:.2f}, re-run {rr['d30_Hd']:.2f})"
            elif "model_mse_k30" in st:
                cell = f"{NOM} (stored {st['model_mse_k30']:.2f}, re-run {rr['model_mse_k30']:.2f})"
            else:
                cell = f"{NOM} (true actions: stored {st['true']:.3f}, re-run {rr['true']:.3f})"
        else:
            cell = "rows not available"
        put("bs_ci_" + c["claim"].lower().replace("-", ""), cell, bsa + f", claim {c['claim']}: point_difference, ci95, outcome")
    for key, cid, field, text in (("b_lewm_pred", "C-001-1", "ours", "0.31"), ("b_lewm_cl", "C-001-1", "ours", "0.89"),
                                  ("b_len_own", "C-010-3", "note", "0.521")):
        assert text in by[cid][field], (cid, text)
        put(key, text, f"repro/register/expected/register.json claims, id {cid}, {field}")
    # the failed claims and papers, split by whose method failed (by hand, from Table 4 of the paper)
    ctier = {"C-001-2": "auth", "C-002-1": "auth", "C-003-1": "auth", "C-004-1": "scope", "C-010-1": "auth", "C-010-2": "auth",
             "C-019-1": "auth", "C-019-2": "auth",
             "C-006-1": "var", "C-007-1": "var", "C-007-2": "var", "C-008-2": "var", "C-009-1": "var", "C-018-1": "var",
             "C-018-2": "var", "C-022-1": "var", "C-019-3": "eng", "C-020-2": "eng"}
    assert sorted(ctier) == sorted(c["id"] for c in cl if c["verdict"] == "fail"), "every failed claim needs a tier"
    ta = "repro/register/expected/register.json failed paper claims, tier by hand in make_paper.py (ctier)"
    tc = collections.Counter(ctier.values())
    for k in ("auth", "var", "eng", "scope"):
        put("t_c_" + k, str(tc[k]), ta + f", tier = {k}")
    ptier = {"LeWorldModel": "auth", "DINO-WM": "auth", "RoboJEPA": "auth", "H-JEPA": "scope", "Robometer": "auth",
             "Adaptive Action Chunking (AAC)": "auth", "ContactGuard": "var", "FAIL-Detect and SAFE": "var", "ReAP": "var",
             "VLA-Corrector": "var", "SURVEYOR": "var", "REMORA": "var", "PACT-VLA": "eng"}
    assert sorted(ptier) == sorted(p["paper"] for p in papers if p["verdict"] == "fail"), "every failed paper needs a tier"
    tp = collections.Counter()
    for p in papers:
        if p["paper"] in ptier: tp[ptier[p["paper"]]] += wt(p)
    for k in ("auth", "var", "eng", "scope"):
        put("t_p_" + k, str(tp[k]), ta.replace("claims", "papers").replace("ctier", "ptier") + f", tier = {k}, weighted")
    put("t_p_other", str(tp["var"] + tp["eng"] + tp["scope"]), "t_p_var + t_p_eng + t_p_scope"); put("t_c_other", str(tc["var"] + tc["eng"] + tc["scope"]), "t_c_var + t_c_eng + t_c_scope")
    # 9 of 10 trials, Wilson 95 % interval
    import math
    k_, n_, z = 9, 10, 1.96; c_ = (k_ + z * z / 2) / (n_ + z * z); h_ = z * math.sqrt(k_ * (n_ - k_) / n_ + z * z / 4) / (n_ + z * z)
    for cid in ("C-011-1", "C-013-1"):
        assert "9/10" in by[cid]["ours"] and "no numeric pass mark" in by[cid]["bar"], cid
    put("vla_ci", f"{100 * (c_ - h_):.0f}–{100 * (c_ + h_):.0f} %", "Wilson score 95 % interval for 9/10 (C-011-1, C-013-1 ours: '9/10')")
    for cid in ("C-019-3", "C-010-2", "C-001-2"):
        assert by[cid]["verdict"] == "fail" and not own(by[cid]), cid
    assert by["C-012-1"]["verdict"] == "withdrawn"
    rows = []
    for p in papers:
        cite = " ".join(f"[@{x.strip()}]" for x in p["arxiv"].split(",")) if re.fullmatch(r"[\d. ,]+", p["arxiv"]) else ""
        name = p["paper"] + ((" " + cite) if cite else "") + (" [@surveyor2026]" if p["paper"] == "SURVEYOR" else "")
        verdict = p["verdict"] + {"auth": " (authors' method)", "var": " (our variant)", "eng": " (our engine)", "scope": " (outside the paper's regime)"}.get(ptier.get(p["paper"]), "")
        if p["paper"] == "Adaptive Action Chunking (AAC)": verdict += "; the latency claim: our engine (no batched sampling)"
        if p["paper"] == "D-JEPA": verdict += " (proxy labels only)"
        bar_, ours_ = p["bar"], p["ours"]
        for a_, b_ in {"VLA-JEPA": [("; for reranking (H0): oracle / mean error ≤ ~0.7 and N = 8 ≤ 1.5× the latency", ""), ("; reranking no-go (0.76, 1.84×)", "")]}.get(p["paper"], []):
            assert a_ in bar_ + ours_, (p["paper"], a_); bar_, ours_ = bar_.replace(a_, b_), ours_.replace(a_, b_)
        cells = [name, p["their_rig_cost_class"], p["claim_tested"], bar_.replace("no numeric pass mark registered", "no numeric bar"),
                 ours_.replace("my data", "our data"), verdict]
        assert not any("|" in x for x in cells), p["paper"]
        rows.append("| " + " | ".join(cells) + " |")
    put("table1_rows", str(len(rows)), "repro/register/expected/register.json papers with a paper claim: paper (cited by its arXiv id), their_rig_cost_class, claim_tested, bar, ours, verdict (appendix table)")
    fam = {"world models": ["LeWorldModel", "DINO-WM", "RoboJEPA", "H-JEPA", "D-JEPA", "HWM (hierarchical latent world models)", "LeJEPA identifiability"],
           "failure monitors and judges": ["ContactGuard", "FAIL-Detect and SAFE", "ReAP", "VLA-Corrector", "Robometer", "SURVEYOR", "REMORA"],
           "VLA policies": ["SmolVLA", "VLA-JEPA", "REKI"],
           "chunking and edge inference": ["Real-Time Chunking", "Adaptive Action Chunking (AAC)", "PACT-VLA", "Horizon × depth (Euler steps vs execution horizon)"]}
    names = [p["paper"] for p in papers]
    flat = [n for v in fam.values() for n in v]
    assert sorted(flat) == sorted(names), (set(names) ^ set(flat))
    fa = "repro/register/expected/register.json papers, grouped by hand in make_paper.py (fam)"
    for k, key in (("world models", "f_wm"), ("failure monitors and judges", "f_mon"), ("VLA policies", "f_vla"), ("chunking and edge inference", "f_chunk")):
        put(key, str(sum(wt(p) for p in papers if p["paper"] in fam[k])), fa + f", {k}, weighted")
        vc = collections.Counter()
        for p in papers:
            if p["paper"] in fam[k]: vc[p["verdict"]] += wt(p)
        put(key + "_v", ", ".join(f"{vc[v]} {w}" for v, w in (("reproduces", "reproduce"), ("fail", "fail"), ("not proven", "not proven"), ("not tested", "not tested")) if vc[v]), fa + f", {k}: verdict counts")
    datasets()
    rig = (REG / "rig.yaml").read_text()
    eur = [int(x) for x in re.findall(r"^\s+price_eur: (\d+)\s*$", rig, re.M)]
    put("rig_eur", f"{sum(eur):,}", "repro/register/expected/rig.yaml, sum of price_eur (parts with a stated price)")
    put("rig_unpriced", str(len(re.findall(r"^\s+price_eur: null", rig, re.M))), "repro/register/expected/rig.yaml, price_eur: null")
    return "\n".join(["| paper | their rig | claim tested | bar | our result | verdict |", "|---|---|---|---|---|---|"] + rows)


def datasets():
    d = json.loads((ROOT / "data" / "datasets.json").read_text()); a = "data/datasets.json "
    for k, (g, f) in {"tel_eps": ("teleop", "episodes"), "tel_train": ("teleop", "train_episodes"), "tel_val": ("teleop", "val_episodes"),
                      "tel_fps": ("teleop", "fps"), "ro_eps": ("rollouts", "episodes"), "ro_succ": ("rollouts", "success"),
                      "ro_fail": ("rollouts", "failure"), "arm_n": ("armnetbench", "rollouts"), "arm_pol": ("armnetbench", "policies"),
                      "tim_eps": ("timing", "episodes"), "ro_p_eps": ("rollouts", "primary_episodes"), "ro_p_fail": ("rollouts", "primary_failure"), "ro_p_succ": ("rollouts", "primary_success"), "tim_b": ("timing", "boundaries")}.items():
        put(k, f"{d[g][f]:,}", a + f"{g}.{f}")
    assert d["rollouts"]["success"] % 2 == 0; put("ro_half", str(d["rollouts"]["success"] // 2), a + "rollouts.success / 2 (FAIL-Detect and SAFE calibration split)")
    t = d["teleop"]
    put("tel_frames", f"{t['frames']:,}", a + "teleop.frames"); put("tel_min", f"{t['frames'] / t['fps'] / 60:.0f}", a + "teleop.frames / fps / 60")
    put("tel_ep_s", f"{t['frames'] / t['episodes'] / t['fps']:.0f}", a + "teleop.frames / episodes / fps")


def prereg():
    allrows = json.loads((PC / "prereg_check.json").read_text())
    a = "repro/prereg-check/expected/prereg_check.json"
    # a gate with a bar and no result because it was superseded or cancelled never ran: it is named in the text, not counted in the table
    rows = [r for r in allrows if r["class"] != "not-run"]; first = [r for r in allrows[:89] if r["class"] != "not-run"]
    cancelled = [r for r in allrows if r["class"] == "not-run"]
    assert [r["gate"] for r in cancelled] == ["H3 plan", "G1b-RJ"], "the prose names the two cancelled gates"
    put("pr_cancelled", str(len(cancelled)), a + " rows, class = not-run (superseded or cancelled before a result)")
    put("pr_rows", str(len(first)), a + " rows[:89] (the log of 2026-10-31) without class = not-run"); put("pr_today", str(len(rows)), a + " rows (today) without class = not-run")
    for pre, sub in (("pr", first), ("pt", rows)):
        c = collections.Counter(r["class"] for r in sub)
        for k in ("bar-first", "same-commit", "result-first", "no-bar"):
            put(f"{pre}_{k.replace('-', '_')}", str(c[k]), a + f" {'rows[:89]' if pre == 'pr' else 'rows'} without class = not-run, class = {k}")
    put("pr_unprov", str(int(N["pr_same_commit"]) + int(N["pr_no_bar"])), a + " rows[:89], class = same-commit + class = no-bar")
    v1 = collections.Counter(r["class_v1"] for r in first)
    for k in ("bar-first", "same-commit", "no-bar", "unresolved"):
        put(f"v1_{k.replace('-', '_')}", str(v1[k]), a + f" rows[:89] without class = not-run, class_v1 = {k}")
    moved = collections.Counter(r["class"] for r in first if r["class_v1"] == "same-commit")
    put("sc_to_bf", str(moved["bar-first"]), a + " rows[:89], class_v1 = same-commit and class = bar-first")
    put("sc_to_nb", str(moved["no-bar"]), a + " rows[:89], class_v1 = same-commit and class = no-bar")
    put("sc_stay", str(moved["same-commit"]), a + " rows[:89], class_v1 = same-commit and class = same-commit")
    top = [r for r in rows if r["gate"].startswith("TOPReward")]
    assert len(top) == 1 and top[0]["class"] == "same-commit"
    lit_file("top_protocol", "prereg-check/expected/PREREG_AUDIT.md", "`TOPREWARD_PROTOCOL.md` (`6241570`)\n  predates the log commit `6868fa5`", "6241570")
    ec = json.loads((PC / "recompute_early.json").read_text())
    a = "repro/prereg-check/expected/recompute_early.json"
    put("rc_rows", str(len(ec)), a + ", len"); put("rc_flips", str(sum(r["flip_under_ci"] for r in ec)), a + ", flip_under_ci = true")
    lit_file("rc_resamples", "prereg-check/expected/RECOMPUTED.md", "2,000 resamples over episodes", "2,000")
    for key, gate in (("osc", "G14"), ("acc", "G9c-3"), ("tau", "Judge τ")):
        r = next(x for x in ec if x["gate"] == gate); b = f"{a}, gate {gate}"
        put(f"{key}_n", str(r["n_units"]), b + " n_units"); put(f"{key}_est", pct(r["estimate"]), b + " 100 estimate")
        put(f"{key}_lo", pct(r["ci95"][0]), b + " 100 ci95[0]"); put(f"{key}_hi", pct(r["ci95"][1]), b + " 100 ci95[1]")
        put(f"{key}_bar", pct(float(r["bar"].split()[-1])).replace(".0", ""), b + f" bar '{r['bar']}' x 100")
        put(f"{key}_verdict", r["point_verdict"], b + " point_verdict")
    lit_file("ps_ids", "prereg-check/expected/PAPER_SIDE_AUDIT.md", "`main:data/register.yaml`, 38 ids", "38")
    lit_file("l0", "cold-reproduction/expected/L0.md", "**29 / 29 PASS**", "29")
    t = "L1: 6 REPRO (5 exact, 1 identical but one timing at 0.2 %), 0 DIFF, 12 FAIL-ENV"
    lit_file("l1_repro", "cold-reproduction/expected/REPORT.md", t, "6"); lit_file("l1_exact", "cold-reproduction/expected/REPORT.md", t, "5")
    lit_file("l1_env", "cold-reproduction/expected/REPORT.md", t, "12")
    lit_file("l1_skip", "cold-reproduction/expected/REPORT.md", "11 SKIP (3 MAXN-only, 3 private checkpoints, 2 vast, 3 unstated)", "11")
    lit_file("kappa_bar", "classes/PROTOCOL.md", "**Bar: κ ≥ 0.6**", "0.6")
    lit_file("fail_rows", "classes/PROTOCOL.md", "All 20 claim rows of the site register whose verdict is `fail`", "20")


# read from the local PDF (~/workspace/papers/2610.40026v1-roboseed.pdf, not committed): title and first author of the first page
READ = {"2610.40026": ("RoboSeed: Multidimensional Evaluation of Vision-Language-Action and World-Action Models", "Ma, Xin and others")}


EXTRA_BIB = {"surveyor2026": "@misc{surveyor2026,\n  title = {{SURVEYOR: Certified Speculative Plan Consumption for Latent World-Model Planning}},\n"
                             "  year = {2026},\n  howpublished = {NeurIPS 2026 workshop},\n  note = {neurips.cc/virtual/2026/175857}\n}"}


def bib(md):
    """refs.bib from the [@id] citations, titles and years from the papers mirror's index.json (absent on CI: keep the
    committed refs.bib and check it covers every cited id)."""
    ids = list(dict.fromkeys(re.findall(r"\[@(\d{4}\.\d{4,5})\]", md)))
    index = Path.home() / "workspace/papers/index.json"
    if not index.exists():
        have = set(re.findall(r"eprint = \{(\d{4}\.\d{4,5})\}", (HERE / "refs.bib").read_text()))
        missing = [i for i in ids if i not in have]
        assert not missing, f"refs.bib lacks cited ids {missing}; regenerate it where the papers index exists"
        txt = (HERE / "refs.bib").read_text()
        for k, e in EXTRA_BIB.items():
            if f"[@{k}]" in md and "{" + k + "," not in txt: txt = txt.rstrip("\n") + "\n\n" + e + "\n"
        (HERE / "refs.bib").write_text(txt)
        return len(ids) + sum(f"[@{k}]" in md for k in EXTRA_BIB)
    idx = {r.get("arxiv"): r for r in json.loads(index.read_text())["papers"]}
    out = []
    for i in ids:
        r = idx.get(i, {})
        title = (r.get("title") or READ.get(i, ("",))[0] or f"arXiv {i} (not in the author's papers mirror; not read)").replace("&", "\\&")
        auth = f"  author = {{{READ[i][1]}}},\n" if i in READ else ""
        out.append(f"@misc{{arxiv{i.replace('.', '')},\n  title = {{{{{title}}}}},\n{auth}  year = {{{r.get('year') or '20' + i[:2]}}},\n"
                   f"  eprint = {{{i}}}, archivePrefix = {{arXiv}},\n  note = {{arXiv:{i}}}\n}}")
    out += [e for k, e in EXTRA_BIB.items() if f"[@{k}]" in md]
    (HERE / "refs.bib").write_text("\n\n".join(out) + "\n")
    return len(out)


def figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    FIG = HERE / "fig"; FIG.mkdir(exist_ok=True); sys.path.insert(0, str(HERE / "style")); import shisso_colors as sc; sc.use()
    GREEN, AMBER, RED = sc.CATEGORICAL[2], sc.CATEGORICAL[1], sc.CATEGORICAL[3]
    f = lambda k: int(N[k])  # noqa: E731
    tot, rep, fa_, fv = f("c_paper"), f("c_paper_repro"), f("t_c_auth"), f("t_c_other")
    other = tot - rep - fa_ - fv
    fig, ax = plt.subplots(figsize=(7.0, 0.85)); ax.set_xlim(0, 100); ax.set_ylim(13.5, 24); ax.axis("off")
    ax.text(1, 22.2, f"{tot} paper claims re-tested on a rig of about {N['rig_eur_round']} euros, by verdict", fontsize=6.6, fontweight="bold", color=sc.ACCENT)
    x = 1.0; W = 98.0
    for n, lab, c in [(rep, "reproduce", GREEN), (fa_, "fail: authors' method", RED), (fv, "fail: our variant, engine or scope", AMBER), (other, "open", "#8A90A0")]:
        wd = W * n / tot; ax.add_patch(FancyBboxPatch((x, 15.2), wd, 5.2, boxstyle="round,pad=0,rounding_size=0.8", fc=c, ec="white", lw=1.2))
        ax.text(x + wd / 2, 17.8, f"{n} {lab}", ha="center", va="center", fontsize=6.2, color="white", fontweight="bold"); x += wd
    fig.subplots_adjust(0, 0, 1, 1); fig.savefig(FIG / "verdicts.pdf"); fig.savefig(FIG / "verdicts.png", dpi=200); plt.close(fig)

    # the chain that makes every number (same in all four papers)
    fig, ax = plt.subplots(figsize=(7.0, 1.05)); ax.set_xlim(0, 100); ax.set_ylim(0, 15); ax.axis("off")
    steps = [("1  bar committed", "protocol commit\nbefore any number"), ("2  run", "rows stored in\nrepro/<exp>/expected"), ("3  result committed", "result commit\nafter the bar"),
             ("4  L0 recompute", "make l0: every number\nfrom the stored rows"), ("5  paper", "numbers.json: value\nand its anchor")]
    bw, gap = 16.2, 4.0
    for i, (a, b) in enumerate(steps):
        xx = 1 + i * (bw + gap); ax.add_patch(FancyBboxPatch((xx, 3), bw, 10, boxstyle="round,pad=0,rounding_size=1.2", fc="#EDF2FB" if i != 4 else sc.ACCENT, ec=sc.ACCENT, lw=1.0))
        ax.text(xx + bw / 2, 10.3, a, ha="center", va="center", fontsize=6.4, fontweight="bold", color="white" if i == 4 else sc.ACCENT)
        ax.text(xx + bw / 2, 6.0, b, ha="center", va="center", fontsize=5.6, color="white" if i == 4 else "black", linespacing=1.15)
        if i < 4:
            ax.add_patch(FancyArrowPatch((xx + bw, 8), (xx + bw + gap, 8), arrowstyle="-|>", mutation_scale=6, lw=1.0, color=sc.ACCENT))
    ax.text(50, 0.7, "make check regenerates the paper from the stored rows and fails on any difference", ha="center", fontsize=5.8, color=sc.DARKGREY, style="italic")
    fig.subplots_adjust(0, 0, 1, 1); fig.savefig(FIG / "number_chain.pdf"); fig.savefig(FIG / "number_chain.png", dpi=200); plt.close(fig)


def main():
    table = register()
    put("rig_eur_round", "1,500", f"repro/register/expected/rig.yaml: priced parts sum to {N['rig_eur']}; {N['rig_unpriced']} small parts unpriced; rounded up")
    put("cost_round", "50", f"cost {N['cost']} rounded up to the next 10 (written 'under $50')")
    tpl = (HERE / "DRAFT_4p.md.in").read_text()
    missing = set(re.findall(r"\{\{(\w+)\}\}", tpl)) - N.keys() - {"TABLE1"}
    assert not missing, f"placeholders without a value: {sorted(missing)}"
    md = re.sub(r"\{\{(\w+)\}\}", lambda m: table if m.group(1) == "TABLE1" else N[m.group(1)], tpl)
    nb = bib(md)
    figures()
    (HERE / "DRAFT_4p.md").write_text(re.sub(r"\[@(\d{4}\.\d{4,5})\]", r"[arXiv:\1]", md).replace("[@surveyor2026]", "[NeurIPS 2026 workshop]"))
    (HERE / "numbers.json").write_text(json.dumps({k: {"value": N[k], "anchor": A[k]} for k in sorted(N)}, indent=1, ensure_ascii=False) + "\n")
    (HERE / "main.tex").write_text(to_tex(md))
    print(f"{len(N)} numbers, {nb} references; DRAFT_4p.md, main.tex, numbers.json written")


SUB = [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
       ("≥", r"$\geq$"), ("≤", r"$\leq$"), ("≈", r"$\approx$"), ("×", r"$\times$"), ("τ", r"$\tau$"), ("κ", r"$\kappa$"),
       ("Δ", r"$\Delta$"), ("²", r"$^2$"), ("′", r"$'$"), ("→", r"$\rightarrow$"), ("−", r"$-$"), ("<", r"$<$"), (">", r"$>$"),
       ("±", r"$\pm$"), ("·", r"$\cdot$"), ("—", "---"), ("–", "--"), ("…", r"\ldots{}")]


def esc(s):
    for a, b in SUB:
        s = s.replace(a, b)
    s = re.sub(r"([\u3040-\u30ff\u4e00-\u9fff]+)", r"{\\jpfont \1}", s)  # Japanese (the lab's name)
    s = re.sub(r"\[@(\d{4})\.(\d{4,5})\]", r"\\citep{arxiv\1\2}", s).replace("[@surveyor2026]", r"\citep{surveyor2026}")
    s = re.sub(r"`([^`]*)`", r"\\texttt{\1}", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", s)
    return re.sub(r"\*([^*]+)\*", r"\\emph{\1}", s)


LINKS = r"\textbf{Code and rows:} \texttt{github.com/ravediamond/paper-register-reproducibility}\quad\textbf{Reproduce:} \texttt{make check}. Every number carries its source file and protocol commit."


def tint(v):
    v = v.strip().lower()
    c = {"reproduces": "shissopass", "fail": "shissofail", "pass": "shissopass", "not proven": "shissoamber"}.get(v)
    return "\\rowcolor{" + c + "}" if c else ""


COLS = r"p{2.2cm}p{0.95cm}p{3.95cm}p{3.7cm}p{3.7cm}p{1.15cm}"


def to_tex(md):
    out = [r"\documentclass[10pt,twocolumn]{article}", r"\usepackage[margin=0.75in]{geometry}", r"\usepackage{booktabs}",
           r"\usepackage{graphicx}", r"\usepackage[numbers]{natbib}", r"\usepackage{style/shisso}", r"\IfFontExistsTF{Noto Serif CJK JP}{\newfontfamily\jpfont{Noto Serif CJK JP}}{\newcommand\jpfont{}}", r"\usepackage{listings}\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible,keepspaces=true,frame=tb,framerule=0.3pt,aboveskip=4pt,belowskip=4pt,upquote=true}",
           r"\shissorepo{github.com/ravediamond/paper-register-reproducibility}", r"\input{shisso_commit}", r"\begin{document}"]
    lines, i, abstract, cap, appendix = md.splitlines(), 0, False, "", False
    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):  # fenced code from the repository: printed verbatim
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("\\begin{lstlisting}\n" + "\n".join(lines[i + 1:j]) + "\n\\end{lstlisting}")
            i = j + 1
            continue
        if l.startswith("# "):
            title = esc(l[2:]); out += [r"\title{" + title + "}",
                    r"\author{Ravindu Somawansa\\Shisso Robotics\\\texttt{ravindu.somawansa@shissorobotics.com}\thanks{Every number with its source file: \texttt{github.com/ravediamond/paper-register-reproducibility}.}}",
                    r"\date{}"]
        elif l.startswith("## Abstract"):
            abs_at = len(out); abstract = True
        elif l.startswith("## "):
            if abstract:
                body = " ".join(x.strip() for x in out[abs_at:] if x.strip()); del out[abs_at:]; abstract = False
                out.append(r"\twocolumn[\vspace*{0.32in}\shissopanel{" + title + "}{Ravindu Somawansa\\\\[1pt]Shisso Robotics\\\\[1pt]\\texttt{ravindu.somawansa@shissorobotics.com}}{" + body + "}{" + LINKS + r"}\vspace{4pt}]")
            if l.startswith("## References"):
                out += [r"\bibliographystyle{plainnat}", r"\bibliography{refs}"]
            elif l.startswith("## Appendix"):
                out += [r"\onecolumn", r"\appendix", r"\section*{" + esc(l[3:]) + "}"]; appendix = True
            else:
                out.append(r"\section{" + esc(re.sub(r"^\d+\.\s*", "", l[3:])) + "}")
        elif l.startswith("Table ") and i + 2 < len(lines) and lines[i + 2].startswith("|"):
            tabno, cap = l.split(": ", 1)[0][len("Table "):], l.split(": ", 1)[1]
        elif l.startswith("|"):
            t = []
            while i < len(lines) and lines[i].startswith("|"):
                if not set(lines[i]) <= set("|-: "):
                    t.append([esc(x.strip()) for x in lines[i].strip("|").split("|")])
                i += 1
            if t[0][0] != "paper" and len(t[0]) >= 4 and max(len(x) for r in t[1:] for x in r[1:]) >= 12:  # wide text table: full width
                w = ([2.2, 3.7, 2.4, 2.2, 2.6, 3.9] if len(t[0]) == 6 else [2.6, 4.2, 3.0, 2.4, 4.4]) if t[0][0] == "method" else {4: [2.8, 1.8, 5.6, 6.6], 5: [3.0, 1.1, 4.0, 5.2, 3.6]}[len(t[0])]
                out += [r"\begin{table*}[t]\centering\footnotesize", r"\caption{" + esc(cap) + "}", r"\begin{tabular}{" + "".join(f"p{{{x}cm}}" for x in w) + "}",
                        r"\toprule", r"\shissohead " + " & ".join(t[0]) + r" \\", r"\midrule"] + [" & ".join(r) + r" \\" for r in t[1:]] + \
                       [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
                continue
            if t[0][0] != "paper":  # small count tables: one column, one float
                out += [r"\begin{table}[t]\centering\footnotesize", r"\setlength{\tabcolsep}{4pt}", r"\caption{" + esc(cap) + "}",
                        (r"\resizebox{\columnwidth}{!}{" if len(t[0]) >= 5 else "") + r"\begin{tabular}{" + ("l" + "r" * (len(t[0]) - 1) if max(len(x) for r in t[1:] for x in r[1:]) < 12 else "p{1.6cm}" + "p{2.6cm}" * (len(t[0]) - 1)) + "}", r"\toprule", r"\shissohead " + " & ".join(t[0]) + r" \\", r"\midrule"] + \
                       [(tint(r[-1]) if t[0][-1] == "point verdict" else "") + " & ".join(r) + r" \\" for r in t[1:]] + [r"\bottomrule", r"\end{tabular}" + ("}" if len(t[0]) >= 5 else ""), r"\end{table}"]
                continue
            spec = COLS
            body, k = t[1:], 11  # a 22-row register does not fit one float page: two floats of 11 rows
            for j in range(0, len(body), k):
                c = esc(cap) if j == 0 else "Table " + tabno + ", continued."
                out += [(r"\begin{table}[h!]" if appendix else r"\begin{table*}[p]") + r"\centering\scriptsize", r"\setlength{\tabcolsep}{3pt}\renewcommand{\arraystretch}{1.05}",
                        r"\begin{tabular}{" + spec + "}", r"\toprule", r"\shissohead " + " & ".join(t[0]) + r" \\", r"\midrule"] + \
                       [tint(r[-1]) + " & ".join(r) + r" \\" for r in body[j:j + k]] + [r"\bottomrule", r"\end{tabular}",
                        (r"\caption{" + c + "}") if j == 0 else (r"\par\medskip " + c), r"\end{table}" if appendix else r"\end{table*}"]
            continue
        elif l.startswith("*Ravindu"):
            pass
        elif l.startswith("!["):
            cap_, img = re.match(r"!\[(.*)\]\((.*)\.png\)", l).groups()
            out.append(r"\begin{figure*}[t]\centering\includegraphics[width=\textwidth]{" + img + r".pdf}\caption{" + esc(re.sub(r"^Fig\. \d+ — ", "", cap_)) + r"}\end{figure*}")
        elif l.startswith("> "):
            q = []
            while i < len(lines) and lines[i].startswith("> "):
                q.append(lines[i][2:]); i += 1
            mm = re.match(r"\*\*(.+?)\*\*\s*(.*)", " ".join(q))
            out.append(r"\begin{shissofinding}[" + esc(mm.group(1)) + "]\n" + esc(mm.group(2)) + "\n" + r"\end{shissofinding}")
            continue
        elif re.match(r"^\s*- ", l):  # bullet lists (the skeleton): itemize, one nesting level
            out.append(r"\begin{itemize}\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}\footnotesize"); depth = 0
            while i < len(lines) and re.match(r"^\s*- ", lines[i]):
                d = 1 if lines[i].startswith("  ") else 0
                if d > depth: out.append(r"\begin{itemize}\setlength{\itemsep}{0pt}")
                if d < depth: out.append(r"\end{itemize}")
                depth = d; out.append(r"\item " + esc(lines[i].strip()[2:])); i += 1
            out += [r"\end{itemize}"] * (depth + 1)
            continue
        elif not l.strip():
            out.append("\n")  # keep paragraph breaks: an empty markdown line ends the paragraph in LaTeX too
        else:
            out.append(esc(l))
        i += 1
    if abstract:
        out.append(r"\end{abstract}")
    out.append(r"\end{document}")
    return "\n".join(x for x in out if x != "") + "\n"


if __name__ == "__main__":
    main()
