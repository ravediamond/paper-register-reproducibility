# Wording to carry into the reproducibility-study paper (owner, 2026-10-31, WS-078 accepted)

From `PREREG_CHECK.md`, verbatim:

> Of 89 gate rows in the experiment log, **36 are bar-first, 0 result-first, 31 same-commit (not provable from this
> repo), 19 no-bar** (3 unresolved: two gates that never ran, one bar text not found).

Notes for the draft: "same-commit" means the bar and the result first appear in the same commit of this repository,
11 of them in the commit that created the log from earlier notes; it is not evidence that the result came first.
The site's gate count is read from the same log by the build (WS-078 check, deployed with WS-075): 89.
