# Pre-registration check of the register (WS-078)

For every gate of the experiment log: the commit that first contains its bar and the commit that first contains its result, from git history; classified bar-first, result-first, same-commit or no-bar. Paper wording: `expected/PAPER_WORDING.md`.

**Audited (WS-136, 2026-11-02).** The 31 same-commit and 19 no-bar rows of WS-078 resolved by commit order
(`git merge-base --is-ancestor`), method in `scripts/prereg_audit.py`, row-by-row evidence in
`expected/PREREG_AUDIT_TABLE.md`, summary `expected/PREREG_AUDIT.md`: of the same 89 rows, 58 bar-first, 6 same-commit,
0 result-first, 23 no-bar, 2 not-run (93 rows today: 61 / 7 / 0 / 23 / 2). `expected/prereg_check.json` carries the
audited `class` and the WS-078 class as `class_v1`; `expected/PAPER_WORDING.md` is the WS-078 wording, superseded.
Early gates recomputed on the episode bootstrap: `expected/RECOMPUTED.md`, `expected/recompute_early.json`
(`scripts/recompute_early.py`, reads the gate data of the source repository). Paper-side audit: `expected/PAPER_SIDE_AUDIT.md`.
