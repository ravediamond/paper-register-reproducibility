# Paired bootstrap on the 11 baseline comparisons (Table 3)

Work-stack item WS-212, 2026-11-10. Frozen before any number: this file is committed before any interval is computed.
No register verdict changes: this adds intervals and does not re-judge any claim.

## 1. Question

For each of the 11 rows of Table 3, does the interval of (method minus baseline) exclude zero?

## 2. Data

Only rows that are already stored: per episode, per anchor, per rollout or per split. Where the per-unit rows of a
comparison are not stored, the row reads `rows not available` and names the file that would be needed. No number is
rebuilt or estimated, nothing is retrained and nothing is scored again. Offline, $0, no arm, no GPU.

## 3. Statistic and interval

- Unit of resampling: the episode. Anchors, boundaries and chunks are grouped by their episode; for ArmnetBench the unit
  is the rollout (one rollout per episode index); for ContactGuard it would be the calibration split if per-rollout scores
  were missing.
- Paired: the method and its baseline are evaluated on the same resampled units. The statistic is method minus
  baseline in the claim's metric, with the sign set so that positive means the method is better (for a lower-is-better
  metric the statistic is baseline minus method).
- 2,000 resamples, units drawn with replacement, percentile 95 % interval (2.5th and 97.5th percentile), seed 0
  (`numpy.random.default_rng(0)`).
- A resample in which an AUROC is undefined (one class only) is redrawn.
- Outcome per row: `beats` (interval entirely above 0), `loses` (interval entirely below 0), `unclear` (interval
  contains 0).

## 4. The 11 rows and what is stored

| claim | comparison | statistic | stored rows |
|---|---|---|---|
| C-001-1 | LeWorldModel vs copy-last, latent error at K = 30 | mean over anchors, grouped by episode | per-anchor errors are not stored (`g1_suite.py` would have to write them): rows not available |
| C-001-2 | LeWorldModel ranking vs action-only, top-1 | top-1 accuracy, at each target distance d; worst and best case | per-anchor top-1 of the model and of the action-only baseline are not stored (only accuracy per cell in `g1b_range_w1.json`): rows not available |
| C-002-1 | DINO-WM ranking vs action-only, top-1 | as C-001-2 | per-anchor top-1 not stored (`g1_w2prime_best_g1b.json` has cell accuracies only): rows not available |
| C-003-1 | RoboJEPA 300M vs copy-last, 9-step latent L1 | mean over clips | per-clip errors not stored (`gateA_summary.json` has per-horizon means): rows not available |
| C-006-1 | ContactGuard imagined-latent vs current-latent probe | AUROC difference | per-rollout out-of-fold scores not stored (`w1c_summary.json` has per-fold AUROC means only, and its 20 splits are conformal splits with no AUROC): rows not available |
| C-008-1 | ReAP risk head vs shuffled actions | AUROC difference | per-rollout risk scores not stored (`monitors_v2.json` has aggregates): rows not available |
| C-010-2 | Robometer-4B zero-shot vs episode length | AUROC difference on the binary rollouts (successful vs failure), unit = rollout | `ab_top.jsonl` and `ab_top_rescore.jsonl` (per-rollout `p_succ`, label and length), 2,099 rollouts |
| C-016-2 | HWM learned macro-actions vs net joint displacement | mean cosine over anchors | per-anchor cosines not stored (`lowlevel.npz` holds latents, not the trained model's outputs; `hwm_train.py` would have to write them): rows not available |
| C-019-2 | AAC + prefix overwrite vs fixed chunk + overwrite, delay 8 | median boundary jump over all boundaries of the resampled episodes; fixed minus AAC | `rows.jsonl` of the gate (254 boundaries in 20 episodes; keys `jump["aac+overwrite|8"]`, `jump["fixed+overwrite|8"]`) |
| C-020-1 | PACT selection vs random pick, k = 8 | mean executed-window error; random minus PACT | stored CI reused: `gate_b.json`, `k8.pact_minus_random.ci95` (sign flipped) |
| C-022-1 | REMORA nearest-peak vs per-frame readout | ratio of flips (R3 over R1) | stored CI reused: `summary.json`, `paired.flips_ratio_ci95` |

For C-001-2 and C-002-1 the action-only baseline is a range (0.68 to 0.90 over target distances); with rows the
bootstrap would be run at each target distance and the worst and best case given. As no rows are stored, none is given.

## 5. Rules for the two reused intervals

- PACT: the stored interval is for PACT minus random on an error (lower is better); it is read as `beats` when it lies
  entirely below 0, `loses` when entirely above, `unclear` when it contains 0.
- REMORA: the stored interval is for a ratio (flips of the method over flips of the per-frame readout, lower is better),
  so the null value is 1, not 0: `beats` when the interval lies entirely below 1, `loses` when entirely above 1,
  `unclear` when it contains 1. This is the one place where the rule "contains 0" is replaced, because a ratio has no
  zero.
- These two are not resampled again; the same unit as in the stored result (episodes of the 20-episode PACT set, the 34
  rollouts of REMORA) applies.

## 6. Checks before numbers

1. The point values recomputed from the rows must match the registered values within the register tolerance: Robometer
   AUROC 0.8184 (tol 0.0005) and episode-length AUROC 0.9383 (`g9a_ab_complete.json`), AAC medians 0.9728 and 0.9395
   (`gate0.json`).
2. The counts must match the register: 2,099 rollouts and 2,047 binary for Robometer; 254 boundaries in 20 episodes for
   AAC.
3. If a check fails the row reads `rows not available` for that comparison and the reason is written; nothing is adjusted.

## 7. Deviations

(none yet; any change after this commit is numbered, dated and gives its reason)

## 8. Exploratory

Nothing. All choices above are fixed before any number.

## Amendment 1 (WS-213), 2026-11-10, before any number of this amendment

Reason: section 4 lists seven rows as `rows not available` because the per-unit rows were never written. This amendment
allows one thing: re-running a stored evaluation, with the same checkpoint, data split, seed and code revision as the
stored result, only to write the per-unit rows (episode id, anchor or clip id, and the per-unit values of the method and
of its baseline). Nothing is retrained and no setting is changed.

- Match gate, per comparison: the aggregate recomputed from the new rows must equal the stored aggregate to its stored
  precision (for example accuracy per cell to 4 decimals). If it does not, that comparison reads `rerun does not match the
  stored result` with both values and is not bootstrapped. Nothing is adjusted to make it match.
- Statistic, resamples (2,000), seed 0, percentile 95 % interval, paired episode unit and the outcome rule stay those of
  sections 3 and 5. For C-001-2 and C-002-1 the paired difference (model top-1 minus action-only top-1) is bootstrapped at
  each target distance d the paper reports; the worst case (lowest upper bound, then lowest point) and the best case are given.
- A comparison whose re-run would take more than about an hour on the Orin, or whose checkpoint is not on this machine,
  stays `rows not available` and the reason is written.
- Offline, $0, no arm, no vast. Only small per-unit CSVs are written to data/.

Amendment 1, details fixed before any interval of this amendment is computed (the match-gate numbers exist, no
bootstrap has been run):

- Worst and best case over d (C-001-2, C-002-1): the worst case is the d whose interval has the lowest upper bound (ties:
  lowest point difference), the best case the d whose interval has the highest lower bound (ties: highest point
  difference). The outcome of the row is `loses` when the interval is below 0 at every d, `beats` when above 0 at every
  d, `unclear` otherwise. The cell is the one with H = d (the ranking the paper reports); each d is bootstrapped with its
  own `default_rng(0)`.
- Statistics, sign positive = the method is better: C-016-2 mean cosine over the 700 anchors, learned minus displacement,
  unit = episode; C-006-1 AUROC of the imagined-latent probe minus that of the current-latent probe, per seed on the
  pooled out-of-fold scores of the resampled rollouts, mean over the 5 seeds (the stored aggregate), unit = rollout;
  C-008-1 AUROC of the risk head with true actions minus with shuffled actions, per seed on the maximum risk score of
  the resampled rollouts, median over the 5 seeds (the stored aggregate), unit = rollout; C-001-1, if its rows are
  written: mean over windows of copy-last error minus model error (lower error is better), unit = episode.
- Match gate precision: the stored value as printed in the stored file (4 decimals for accuracies, AUROCs and cosines;
  5 decimals for the mean squared errors of C-001-1).
