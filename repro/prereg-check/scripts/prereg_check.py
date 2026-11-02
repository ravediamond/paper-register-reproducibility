#!/usr/bin/env python3
"""WS-078 step 1: for every dated gate row of journal/EXPERIMENTS.md (§1 arm gates, §2 gates), when was its bar first
committed and when was its result first committed. Writes PREREG_CHECK.md and prereg_check.json next to this file.

Bar commit = the pre-registration hash cited in the bar cell (`abc1234`) when there is one and it exists in git, else the
earliest commit whose diff adds the bar text (git log -S, first 60 characters of the bar cell with marks stripped) in any
*.md / *.py file. Result commit = the earliest commit adding the result text (first 60 characters) to EXPERIMENTS.md, or
anywhere in *.md if EXPERIMENTS.md only imported it later. Class: bar-first (bar commit an ancestor of, and not equal to,
the result commit), same-commit, result-first, no-bar (empty bar cell, "—", "none", "(measured)" rows), unresolved (text
not found by pickaxe). No verdict is edited.
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
RR = HERE.parents[2]
EXP = RR / "journal/EXPERIMENTS.md"


def git(*a):
    return subprocess.run(["git", "-C", str(RR), *a], capture_output=True, text=True).stdout.strip()


def rows():
    out, hdr, sec = [], None, None
    for l in EXP.read_text().split("\n"):
        if l.startswith("## "):
            sec, hdr = l[3:].split(".")[0], None; continue
        if l.startswith("|") and "Verdict" in l and hdr is None:
            hdr = [c.strip() for c in l.strip("|").split("|")]; continue
        if hdr and re.match(r"\|\s*(\d{4}-)?\d{2}-\d{2}", l) and sec in ("1", "2"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", l.strip().strip("|"))]
            out.append((sec, dict(zip(hdr, cells)), l))
    return out


def clean(s):
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[*`]", "", s)
    return s.strip()


def first(text, paths):
    """Earliest commit (hash, iso date) whose diff adds `text` in `paths`."""
    if len(text) < 12:
        return None
    o = git("log", "--reverse", "--format=%h|%ad", "--date=iso-strict", f"-S{text}", "--", *paths)
    return tuple(o.split("\n")[0].split("|")) if o else None


def snippet(cell):
    # the longest run of plain text in the cell, 60 characters, so pickaxe matches the line as written
    raw = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)
    parts = sorted(re.split(r"[*`]", raw), key=len, reverse=True)
    return parts[0].strip()[:60] if parts else ""


def pending_commit(key):
    """First commit adding a §3 (pending gates) row whose bold name starts with `key`."""
    o = git("log", "--reverse", "--format=%h|%ad", "--date=iso-strict", "-G", rf"^\| \*\*{re.escape(key)}", "--", "journal/EXPERIMENTS.md")
    return tuple(o.split("\n")[0].split("|")) if o else None


def main():
    out = []
    for sec, r, line in rows():
        gate = clean(r.get("ID") or r.get("Gate") or r.get("Policy / engine") or "")
        bar = next((v for k, v in r.items() if k.startswith("Bar")), "")
        res_cell = r.get("Result") or r.get("Success") or ""
        res = first(snippet(res_cell), ["journal/EXPERIMENTS.md"]) or first(snippet(res_cell), ["*.md"])
        src = r.get("Source", "")
        cited = [h for h in re.findall(r"`([0-9a-f]{7,12})`", bar + " " + gate) if git("cat-file", "-t", h) == "commit"]
        if sec == "1" or not clean(bar) or clean(bar) in ("—", "-", "none") or re.match(r"^[—-]\s*\(", clean(bar)):
            b, how = None, "no bar"
        else:
            cands = [((h, git("show", "-s", "--format=%ad", "--date=iso-strict", h)), "cited hash") for h in cited]
            paths = set(re.findall(r"[\w./-]*(?:PROTOCOL|RUNBOOK)[\w./-]*\.md", bar + " " + src + " " + gate))
            for proj in set(re.findall(r"projects/([\w.-]+)/", bar + " " + src)):  # the row's project protocol
                if (RR / "projects" / proj / "PROTOCOL.md").exists():
                    paths.add(f"projects/{proj}/PROTOCOL.md")
            for path in paths:
                path = path.lstrip("./").replace("../", "")
                if "/" in path and (RR / path).exists():
                    hits = [path]
                elif "/" not in path and path != "PROTOCOL.md":  # a unique protocol name, e.g. PRIME_PROTOCOL.md
                    hits = [x for x in git("ls-files", f"*{path}").split("\n") if Path(x).name == path]
                else:
                    hits = [x for x in git("ls-files", f"*/{path}").split("\n") if x.endswith("/" + path) and
                            any(seg in x for seg in re.findall(r"[\w-]+", path.rsplit("/", 1)[0]))] if "/" in path else []
                for h in [x for x in hits if x]:
                    o = git("log", "--diff-filter=A", "--reverse", "--format=%h|%ad", "--date=iso-strict", "--", h)
                    if o:
                        cands.append((tuple(o.split("\n")[0].split("|")), f"protocol file {Path(h).name}"))
            key = re.split(r"[\s(]", gate)[0] if gate else ""
            if key and len(key) >= 2:
                o = pending_commit(key)
                if o:
                    cands.append((o, "§3 pending entry"))
            p = first(snippet(bar), ["*.md", "*.py"])
            if p:
                cands.append((p, "pickaxe"))
            if cands:
                b, how = min(cands, key=lambda c: c[0][1])
            else:
                b, how = None, "pickaxe"
        if b is None and how != "no bar":
            cls = "unresolved"
        elif how == "no bar":
            cls = "no-bar"
        elif res is None:
            cls = "unresolved"
        elif b[0] == res[0]:
            cls = "same-commit"
        elif subprocess.run(["git", "-C", str(RR), "merge-base", "--is-ancestor", b[0], res[0]]).returncode == 0:
            cls = "bar-first"
        elif b[1] < res[1]:
            cls = "bar-first (by date)"
        else:
            cls = "result-first"
        out.append({"section": sec, "date": r.get("Date"), "gate": gate[:70], "bar_commit": b[0] if b else None,
                    "bar_date": b[1][:16] if b else None, "bar_how": how, "result_commit": res[0] if res else None,
                    "result_date": res[1][:16] if res else None, "class": cls, "verdict": clean(r.get("Verdict", ""))[:40]})
    # WS-136: the audited class (PREREG_AUDIT.md, prereg_audit.py) replaces the pickaxe class of the rows it resolved
    audit = HERE / "prereg_audit.json"
    for x in out:
        x["class_v1"] = x["class"]
    if audit.exists():
        for a in json.loads(audit.read_text()):
            x = out[a["row"]]
            assert x["gate"] == a["gate"] and x["date"] == a["date"], (a["row"], x["gate"], a["gate"])
            x.update({"class": a["class"], "bar_commit": a["bar_commit"], "bar_date": a["bar_date"],
                      "result_commit": a["result_commit"], "result_date": a["result_date"], "bar_how": "audit (WS-136)"})
    (HERE / "prereg_check.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    import collections
    o = main()
    print(len(o), collections.Counter(x["class"] for x in o))
