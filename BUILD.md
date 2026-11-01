# Build (WS-093, 2026-11-01)

Assembled by road-to-robotics `scripts/paper_repo_build.py` from road-to-robotics and paper-vs-hardware at the commits in PROVENANCE.md, by copying only (11 files). Experiments: cold-reproduction prereg-check .

- L0: every `repro/*/l0_check.py` passes from a fresh copy (`make l0`); nothing failed to reproduce.
- `make check` regenerates the paper from `repro/` and fails on any difference; two consecutive builds are byte-identical (`SOURCE_DATE_EPOCH` pinned).
- Skeleton only: `repro/prereg-check` (WS-078) and `repro/cold-reproduction` (WS-067), `paper/OUTLINE.md` from the feasibility memo §10. No draft.
- Note for the draft: `prereg_check.json` holds 89 gates — 36 bar-first, 31 same-commit, 19 no-bar, and **3 unresolved** that the paper wording (36 / 0 / 31 / 19) does not mention.
- Not copied: reviews, feasibility memos, strategy notes, keys, raw data.
