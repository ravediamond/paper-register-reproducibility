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


def register():
    papers = json.loads((REG / "register.json").read_text())["papers"]
    a = "repro/register/expected/register.json papers"
    put("papers", str(len(papers)), a + ", len")
    v = collections.Counter(p["verdict"] for p in papers)
    for k in ("reproduces", "fail", "not proven", "not tested", "withdrawn"):
        put("p_" + k.replace(" ", "_"), str(v[k]), a + f", verdict = {k}")
    rc = collections.Counter(p["their_rig_cost_class"] for p in papers)
    for k, name in (("sim", "sim"), ("gt20k", ">$20k"), ("5to20k", "$5–20k"), ("lt5k", "<$5k"), ("unstated", "unstated")):
        put("rig_" + k, str(rc[name]), a + f", their_rig_cost_class = {name}")
    put("cost", f"{sum(float(p.get('cost_usd') or 0) for p in papers):.2f}", a + ", sum of cost_usd")
    cl = [c for p in papers for c in p["claims"]]
    a = "repro/register/expected/register.json papers[*].claims"
    put("claims", str(len(cl)), a + ", len"); put("claims_tested", str(sum(c["tested"] for c in cl)), a + ", tested = true")
    cv = collections.Counter(c["verdict"] for c in cl)
    for k in ("reproduces", "fail", "not proven", "not tested", "withdrawn"):
        put("c_" + k.replace(" ", "_"), str(cv[k]), a + f", verdict = {k}")
    ours = [c for c in cl if "not a paper claim" in (c.get("stated_in") or "")]
    put("c_ours", str(len(ours)), a + ", stated_in contains 'not a paper claim'")
    put("c_ours_repro", str(sum(c["verdict"] == "reproduces" for c in ours)), a + ", ours and verdict = reproduces")
    paper = [c for c in cl if c not in ours]
    put("c_paper", str(len(paper)), a + ", stated_in without 'not a paper claim'")
    put("c_paper_repro", str(sum(c["verdict"] == "reproduces" for c in paper)), a + ", paper claims, verdict = reproduces")
    put("c_paper_fail", str(sum(c["verdict"] == "fail" for c in paper)), a + ", paper claims, verdict = fail")
    by = {c["id"]: c for c in cl}
    for key, cid, field, text in (("ex_a_ours", "C-019-3", "ours", "4,751 ms"), ("ex_a_bar", "C-019-3", "bar", "298 ms"),
                                  ("ex_b_ours", "C-010-2", "ours", "0.818"), ("ex_b_len", "C-010-2", "ours", "0.938"),
                                  ("ex_c_ours", "C-001-2", "ours", "0.60"), ("ex_c_base", "C-001-2", "ours", "0.68–0.90"),
                                  ("ex_c_bar", "C-001-2", "bar", "0.8")):
        assert text in by[cid][field], f"{text!r} not in {cid}/{field}"
        put(key, text, f"{a}, id {cid}, {field}: '{by[cid][field]}'")
    for cid in ("C-019-3", "C-010-2", "C-001-2"):
        assert by[cid]["verdict"] == "fail", cid
    rows = []
    for p in papers:
        cite = " ".join(f"[@{x.strip()}]" for x in p["arxiv"].split(",")) if re.fullmatch(r"[\d. ,]+", p["arxiv"]) else ""
        name = p["paper"] + ((" " + cite) if cite else "")
        cells = [name, p["their_rig_cost_class"], p["claim_tested"], p["bar"], p["ours"], p["verdict"]]
        assert not any("|" in x for x in cells), p["paper"]
        rows.append("| " + " | ".join(cells) + " |")
    put("table1_rows", str(len(rows)), "repro/register/expected/register.json papers: paper (cited by its arXiv id), their_rig_cost_class, claim_tested, bar, ours, verdict (Table 1)")
    rig = (REG / "rig.yaml").read_text()
    eur = [int(x) for x in re.findall(r"^\s+price_eur: (\d+)\s*$", rig, re.M)]
    put("rig_eur", f"{sum(eur):,}", "repro/register/expected/rig.yaml, sum of price_eur (parts with a stated price)")
    put("rig_unpriced", str(len(re.findall(r"^\s+price_eur: null", rig, re.M))), "repro/register/expected/rig.yaml, price_eur: null")
    return "\n".join(["| paper | their rig | claim tested | bar | our result | verdict |", "|---|---|---|---|---|---|"] + rows)


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


def bib(md):
    """refs.bib from the [@id] citations, titles and years from the papers mirror's index.json (absent on CI: keep the
    committed refs.bib and check it covers every cited id)."""
    ids = list(dict.fromkeys(re.findall(r"\[@(\d{4}\.\d{4,5})\]", md)))
    index = Path.home() / "workspace/papers/index.json"
    if not index.exists():
        have = set(re.findall(r"eprint = \{(\d{4}\.\d{4,5})\}", (HERE / "refs.bib").read_text()))
        missing = [i for i in ids if i not in have]
        assert not missing, f"refs.bib lacks cited ids {missing}; regenerate it where the papers index exists"
        return len(ids)
    idx = {r.get("arxiv"): r for r in json.loads(index.read_text())["papers"]}
    out = []
    for i in ids:
        r = idx.get(i, {})
        title = (r.get("title") or READ.get(i, ("",))[0] or f"arXiv {i} (not in the author's papers mirror; not read)").replace("&", "\\&")
        auth = f"  author = {{{READ[i][1]}}},\n" if i in READ else ""
        out.append(f"@misc{{arxiv{i.replace('.', '')},\n  title = {{{{{title}}}}},\n{auth}  year = {{{r.get('year') or '20' + i[:2]}}},\n"
                   f"  eprint = {{{i}}}, archivePrefix = {{arXiv}},\n  note = {{arXiv:{i}}}\n}}")
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
    tot, rep, fail = f("c_paper"), f("c_paper_repro"), f("c_paper_fail")
    other = tot - rep - fail
    fig, ax = plt.subplots(figsize=(7.0, 1.95)); ax.set_xlim(0, 100); ax.set_ylim(0, 24); ax.axis("off")
    ax.text(1, 22.2, f"{tot} paper claims re-tested on the {N['rig_eur']} euro rig, by verdict", fontsize=6.6, fontweight="bold", color=sc.ACCENT)
    x = 1.0; W = 98.0
    for n, lab, c in [(rep, "reproduce", GREEN), (fail, "fail", RED), (other, "not proven or not tested", "#8A90A0")]:
        wd = W * n / tot; ax.add_patch(FancyBboxPatch((x, 15.2), wd, 5.2, boxstyle="round,pad=0,rounding_size=0.8", fc=c, ec="white", lw=1.2))
        ax.text(x + wd / 2, 17.8, f"{n} {lab}", ha="center", va="center", fontsize=6.2, color="white", fontweight="bold"); x += wd
    cls = [("A  the clock", "adaptive chunking: one decision\n{} on the edge GPU, budget {}".format(N["ex_a_ours"], N["ex_a_bar"]), RED),
           ("B  zero-shot judges", "a learned reward model: AUROC {}\nepisode length alone: {}".format(N["ex_b_ours"], N["ex_b_len"]), RED),
           ("C  learned latents", "world model ranks the executed chunk\nfirst in {} of anchors, bar {}".format(N["ex_c_ours"], N["ex_c_bar"]), RED),
           ("our own gates", "bar committed before the result: {} of {};\nresult first: {}".format(N["pr_bar_first"], N["pr_rows"], N["pr_result_first"]), GREEN)]
    ax.text(1, 12.2, "the failures fall into three classes; our own history is audited", fontsize=6.6, fontweight="bold", color=sc.ACCENT)
    bw, gap = 23.0, 2.0
    for i, (h, b, c) in enumerate(cls):
        xx = 1 + i * (bw + gap); ax.add_patch(FancyBboxPatch((xx, 1.0), bw, 9.4, boxstyle="round,pad=0,rounding_size=1.0", fc="white", ec=c, lw=1.7))
        ax.text(xx + bw / 2, 8.0, h, ha="center", va="center", fontsize=6.3, fontweight="bold", color=c)
        ax.text(xx + bw / 2, 4.1, b, ha="center", va="center", fontsize=5.5, linespacing=1.2)
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
    prereg()
    tpl = (HERE / "DRAFT_4p.md.in").read_text()
    missing = set(re.findall(r"\{\{(\w+)\}\}", tpl)) - N.keys() - {"TABLE1"}
    assert not missing, f"placeholders without a value: {sorted(missing)}"
    md = re.sub(r"\{\{(\w+)\}\}", lambda m: table if m.group(1) == "TABLE1" else N[m.group(1)], tpl)
    nb = bib(md)
    figures()
    (HERE / "DRAFT_4p.md").write_text(re.sub(r"\[@(\d{4}\.\d{4,5})\]", r"[arXiv:\1]", md))
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
    s = re.sub(r"\[@(\d{4})\.(\d{4,5})\]", r"\\citep{arxiv\1\2}", s)
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
           r"\usepackage{graphicx}", r"\usepackage[numbers]{natbib}", r"\usepackage{style/shisso}", r"\usepackage{listings}\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible,keepspaces=true,frame=tb,framerule=0.3pt,aboveskip=4pt,belowskip=4pt,upquote=true}",
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
            if t[0][0] != "paper":  # small count tables: one column, one float
                out += [r"\begin{table}[t]\centering\footnotesize", r"\setlength{\tabcolsep}{4pt}", r"\caption{" + esc(cap) + "}",
                        (r"\resizebox{\columnwidth}{!}{" if len(t[0]) >= 5 else "") + r"\begin{tabular}{l" + "r" * (len(t[0]) - 1) + "}", r"\toprule", r"\shissohead " + " & ".join(t[0]) + r" \\", r"\midrule"] + \
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
