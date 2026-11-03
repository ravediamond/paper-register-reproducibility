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

## Amendment 2026-11-02 (owner)

Written before any label exists (no `labels_owner.csv`, no reader-1 or reader-2 file). It replaces Procedure step 1;
steps 2–3, the bar and the bootstrap are unchanged.

- **Reader 1 is a model, not the owner:** `gemini-3.8-flash` (the model road-to-robotics already uses for VLM labels,
  `scripts/onset_vlm_label.py`), temperature 0.
- **Input, blind and identical to the second reader's:** only the "three classes" section above and `form.csv` (no
  register text beyond the form, no owner notes, no FEASIBILITY.md examples). One call per row, the row alone (the
  form's header line and that row's line). The answer is one letter A/B/C/none plus one line of reason. The exact
  prompt is `reader1_prompt.txt` (`{ROW}` is replaced by the two lines), sha256
  `52518ad796d92b9a3cb47eadcce3643ab3f3ce76d8dc726340eb7cf42b91b2bd`, committed with this amendment.
- **Stability:** 3 independent runs per row; the label is the majority; a row with three different answers is `none`
  and flagged. Self-agreement is reported (rows where all 3 runs agree, out of 20).
- **Output:** `labels_reader1_gemini.csv` (row, claim_id, label, the 3 raw answers, reasons, flag), written by
  `label_gemini.py` and committed unchanged before anyone sees a second reader's labels.
- **Reader 2 stays a human** (not the owner and not a model; unchanged). The κ ≥ 0.6 bar and the bootstrap are
  unchanged; κ is now reader 1 (Gemini) vs the human reader.
- **Paper wording:** the class column is "labels by a model (Gemini 3.8 Flash, majority of 3), checked against a blind
  human reader"; never "the authors' labels".
- **Owner veto:** the owner may veto a Gemini label only before reader 2's file arrives, row by row, committed as an
  override with a reason; overrides are reported in the paper's appendix.

## Log

- 2026-11-02: protocol and form written (WS-136). Owner labels: pending. Second reader: pending (owner to choose).
- 2026-11-02: amendment committed (ea5e9ce) before any label; reader 1 (gemini-3.8-flash, 3 runs) written to `labels_reader1_gemini.csv` by `label_gemini.py` (log `label_gemini.log`). Owner veto window open until reader 2's file arrives.
- 2026-11-03: owner veto pass done (2026-11-03 08:10), no veto: rows 13 (C-013-2), 16 (C-019-1), 17 (C-019-2) stay `none` (Gemini majority stands, no override). Reader-1 (gemini-3.8-flash) labels in `labels_reader1_gemini.csv` are FINAL. Form ready to send to reader 2 (owner sends).
