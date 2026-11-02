# Second-reader protocol: the three failure classes

Written 2026-11-02 (WS-136, Part 1 step 4), before any second reading. The paper sorts the register's failed claims
into three classes; this protocol checks whether a second person, reading blind, puts the same rows in the same
classes. The reading is done by a human second reader, not by the owner and not by a model.

## The three classes (one sentence each)

- **A — edge latency.** The claimed method works or may work, but on the €1,350 rig's edge GPU (Jetson Orin NX) it
  does not meet the real-time budget the claim needs (time per call, per decision or per control step).
- **B — zero-shot judges.** A model used without training on this rig to judge success, failure or progress (reward
  model, VLM judge, verifier, failure detector) is no better than a trivial signal (episode length, a fixed threshold)
  or misses the bar for catching failures.
- **C — latent planners beaten by joints.** A learned latent (world-model state, imagined rollout, latent distance)
  used to plan, rank or track progress does worse than the commanded joint positions or a copy-last / action-only
  baseline.
- **none** — the failure fits none of the three (say why in one line).

A row gets exactly one letter. If two fit, pick the one the `ours` number measures.

## The rows

All 20 claim rows of the site register whose verdict is `fail`, in register order (site repository commit `7d48b9e`,
`data/register.yaml`; 45 claim rows: 20 fail, 17 reproduces, 4 not tested, 3 not proven, 1 withdrawn). The set is the
full list, not a sample, so nothing was chosen after reading. `form.csv` (built by `make_form.py`) carries, per row:
the paper, the claim (subject · relation · object · metric), the conditions, their number, our number and the bar.
It carries no class, no owner note and no page link.

## Procedure

1. The owner labels the 20 rows on `form.csv` first and commits the labels (`labels_owner.csv`) **before** sending the
   form. The commit hash goes in this file's log below.
2. The second reader receives `form.csv` and this file's "three classes" section only, labels each row alone, and
   returns `labels_reader2.csv`. No discussion before the return.
3. The owner commits the reader's file unchanged, then runs the agreement statistic.

## Agreement statistic and bar

- **Cohen's κ** between the two label columns over the 20 rows, four categories (A, B, C, none); 95 % CI by bootstrap
  over rows (2,000 resamples, seed 0).
- **Bar: κ ≥ 0.6** (owner, review of 2026-11-02).
- *Proposed, to be confirmed by the owner before the form is sent:* the bar is read on the point estimate; κ ≥ 0.6 →
  the paper reports the classes as reproducible by a second reader; κ < 0.6 → it reports them as the owner's reading
  only, with κ and the confusion table.
- Disagreements are listed row by row in the paper's appendix; no label is changed after the return.

## The form to send

> Hello — I am checking whether other people sort my failed robot-learning reproductions into the same three groups I
> do. Attached: a one-page definition of the three groups (A edge latency, B zero-shot judges, C latent planners
> beaten by joints, or "none") and a table of 20 claims, each with the paper's number, my number and the pass mark.
> Please put one letter in the last column of each row, on your own, without looking anything up beyond the table.
> It takes about 20 minutes. Please return the CSV; I will not change your answers.

## Log

- 2026-11-02: protocol and form written (WS-136). Owner labels: pending. Second reader: pending (owner to choose).
