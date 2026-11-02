#!/usr/bin/env python3
"""Reader 1 (PROTOCOL.md, Amendment 2026-11-02): each form.csv row alone, sent to gemini-3.8-flash at temperature 0
with reader1_prompt.txt, 3 independent runs; the label is the majority, three different answers -> `none`, flagged.
Stdlib only (Gemini's OpenAI-compatible endpoint, as road-to-robotics scripts/onset_vlm_label.py).

usage: VLM_API_KEY=$(cat ~/.config/gemini/api_key) python3 label_gemini.py > label_gemini.log
"""
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
MODEL = "gemini-3.8-flash"
RUNS = 3
LABEL = re.compile(r"^\s*label:\s*(A|B|C|none)\s*$", re.I | re.M)
REASON = re.compile(r"^\s*reason:\s*(.+)$", re.I | re.M)


def ask(key, text):
    body = json.dumps({"model": MODEL, "temperature": 0, "max_tokens": 4096,
                       "messages": [{"role": "user", "content": text}]}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
            return d["choices"][0]["message"]["content"] or "", d.get("usage") or {}
        except (urllib.error.URLError, TimeoutError, OSError, KeyError) as exc:
            print(f"  retry {attempt + 1}: {exc}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise SystemExit("API failed 4 times")


def main():
    key = os.environ["VLM_API_KEY"].strip()
    template = (HERE / "reader1_prompt.txt").read_text()
    print("prompt sha256", hashlib.sha256(template.encode()).hexdigest())
    lines = (HERE / "form.csv").read_text().splitlines()
    header, body = lines[0], lines[1:]
    rows = list(csv.reader([header] + body))[1:]
    out, tok_in, tok_out, calls = [], 0, 0, 0
    for line, r in zip(body, rows):
        prompt = template.replace("{ROW}", header + "\n" + line)
        labels, reasons = [], []
        for _ in range(RUNS):
            text, usage = ask(key, prompt)
            calls += 1
            tok_in += usage.get("prompt_tokens", 0)
            tok_out += usage.get("completion_tokens", 0)
            m, rs = LABEL.search(text), REASON.search(text)
            labels.append(({"a": "A", "b": "B", "c": "C"}.get(m.group(1).lower(), "none")) if m else "invalid")
            reasons.append(rs.group(1).strip() if rs else text.strip().replace("\n", " ")[:300])
        top, n = Counter(labels).most_common(1)[0]
        label, flag = (top, "") if n >= 2 and top != "invalid" else ("none", "three different answers" if n == 1
                                                                       else "invalid majority")
        out.append([r[0], r[1], label, *labels, *reasons, "yes" if n == RUNS else "no", flag])
        print(f"row {r[0]:>2} {r[1]:<9} {label:<4} runs {'/'.join(labels)}")
    with open(HERE / "labels_reader1_gemini.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["row", "claim_id", "label", "run1", "run2", "run3", "reason1", "reason2", "reason3",
                    "all_three_agree", "flag"])
        w.writerows(out)
    agree = sum(o[-2] == "yes" for o in out)
    print(f"self-agreement {agree}/{len(out)}; labels {dict(Counter(o[2] for o in out))}")
    print(f"cost line: {calls} calls, {tok_in} prompt tokens, {tok_out} completion tokens ({MODEL})")


if __name__ == "__main__":
    main()
