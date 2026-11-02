# WS-136 · Pre-registration audit, closed (Part 1 step 1)

Method: `prereg_audit.py` (docstring); row-by-row table with both commits and the line each adds:
`PREREG_AUDIT_TABLE.md`; data `prereg_audit.json`; `prereg_check.py` now reads it and writes the audited class into
`prereg_check.json` (the WS-078 pickaxe class kept as `class_v1`). A class is derived only from commit order
(`git merge-base --is-ancestor`), never from a note, a memory or a folder timestamp.

## Counts (`prereg_check.json`, regenerated 2026-11-02)

| | bar-first | same-commit | result-first | no-bar | not-run | unresolved | rows |
|---|---|---|---|---|---|---|---|
| WS-078 (2026-10-31) | 36 | 31 | 0 | 19 | — | 3 | 89 |
| **audited, the same 89 rows** | **58** | **6** | **0** | **23** | **2** | **0** | 89 |
| audited, the log today (4 rows added 2026-11-01) | 61 | 7 | 0 | 23 | 2 | 0 | 93 |

Where the 31 same-commit rows went: **21 bar-first** (the bar was committed earlier in the gate's own protocol, plan,
scorer or spec: G0, G1 probes, G2, RoboJEPA A/B, G6a, G9a-AB ×2, G9a-own, G9c, G9c-3, G10, G14, G13b ×2, G15,
judge τ, AW-0 ×2, §30 at `35f4600`, REKI at the `$18` line); **4 no-bar** (the bar cell itself declares none:
"none (diagnostic)" ×2, "dev only", "fit only"); **6 stay same-commit** (H0, LeWM env, G6b, G11, G12, vla.cpp
parity: bar and result first appear in one commit). The 3 unresolved: RoboJEPA Gate B′ → bar-first (pre-registration
`90d3c68` on `origin/exp/robojepa-gate`); H3 plan and G1b-RJ → **not-run** (a bar, never a result; a fifth label,
since none of the four fits a gate with no result). The 19 no-bar rows stay no-bar.

## Caveats for the paper

- 21 upgrades rest on a bar text found by pickaxe in an earlier commit of a file tied to the gate; the evidence line
  is in the table for each, so a reader can check it. G0's rule (`bdd1dc1`) was written in the same commit as the
  5-epoch diagnostic, before the W1 run it gated; REKI's bar is a budget line set by the owner in the queue log.
- Row 89 (TOPReward, added 2026-11-01) is same-commit by the WS-078 pickaxe, but `TOPREWARD_PROTOCOL.md` (`6241570`)
  predates the log commit `6868fa5`; its result commit was not audited (outside the 31 + 19; turn cap). Candidate.
- The 36 WS-078 bar-first rows were not re-audited for an earlier result elsewhere in the repo.
- `paper-vs-hardware` starts 2026-10-26 and holds no earlier bar for these rows.
