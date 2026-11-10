# WS-214 protocol: re-run C-007-1 and C-007-2 with the papers' band (frozen 2026-11-10, before any number)

## 1 Question
With the band built the way FAIL-Detect (appendix B) and SAFE (B.4) build it, on the same score, rollouts and splits as
the stored run, does W1 surprise flag at most 1/20 of the successes and at least half of the failures?

## 2 Data
- Rollouts: `ravediamond/so101-bowls-policy-rollouts` (pin bad1c8ea in the stored run), 69 rollouts, 44 successes and 25 failures (`data/FACTS.json` key `rollouts`, in the road-to-robotics repo).
- Score: the stored run's, per anchor (stride 25) the maximum W1 surprise over k in {15, 20, 25}, recomputed with the stored run's own code from the 69 W1 latents of that run (`outputs/w1_screening/latents`) and the W1 checkpoint `weights_final.pt`; shape and values are checked in 6.
- Splits: the stored run's 20: seed s = 0..19, `np.random.default_rng(s).permutation(44)` over the successes in file order; the first 22 calibrate, the last 22 test; the 25 failures are tested on every split.
- New: the 22 calibration successes of a split are divided in order into Dcal_A (first 11) and Dcal_B (last 11).

## 3 Metric and band (the papers' construction)
- mu_t = mean of Dcal_A at t, over t < T_A = the shortest series in Dcal_A (all of Dcal_A contributes at every such t); beyond T_A the last value of mu_t and of the modulation is carried forward, as the stored run carried its band.
- scal_A(t) = max over k in Dcal_A of |s_kt - mu_t| (Eq. 2; H = all of Dcal_A since (11+1)(0.95) = 11.4 > 11).
- D_j = max_t (s_jt - mu_t) / scal_A(t) for each j in Dcal_B (floor 1e-12 on scal_A, as the stored run).
- h = the 0.95-quantile of {D_j}, numpy default linear interpolation (the papers state the (1-alpha)-quantile). upper_t = mu_t + h scal_A(t).
- Flag: a rollout is flagged when any s_t > upper_t, t over all its anchors.
- Per split: successes flagged = fraction of the 22 test successes; failures flagged = fraction of the 25 failures. Reported: median, min, max, IQR over the 20 splits (as the stored run). No bootstrap: the unit is the split, as in the stored run.

## 4 Baselines
- The stored band (in-sample mu, sigma, rank-22 q) replayed on the same series: must reproduce 22.7 % and 46 % (check 6).
- Same-set comparison: both bands on the same series and splits.

## 5 Bars (copied from the stored run and the register, unchanged)
- C-007-1: median over the 20 splits of successes flagged <= 1/20 at alpha = 5 % (register: "successes flagged <= 1/20"). pass / fail.
- C-007-2: median over the 20 splits of failures flagged >= 50 % (register: "failures flagged >= 50 %"). pass / fail.
- Sources: stored run `w1c_summary.json` `c2.bar`, `repro/register/expected/register.json` papers[6]; prompt journal/prompts/2026-11-10_failsafe-conformal-check.md.

## 6 Checks before numbers
1. The recomputed series have 69 entries, 44 + 25 by outcome, and the replay of the stored band gives exactly the stored `per_split` fpr and recall lists (tolerance 1e-9); if not, stop and report.
2. Hand-computed example on two toy series for D_j and the flag.
3. Band length and N1 = N2 = 11 printed per split.

## 7 Deviations
(none)

## 8 Exploratory (labelled as such, not for the verdict)
- Eq. (1) modulation (constant) instead of Eq. (2); alpha-level sensitivity is not run.
- Outcome of 11/11 only with N2 = 11: the finite-sample rank ceil((N2+1)(1-alpha)) = 12 exceeds N2, so the exact conformal band would be infinite; the papers' plain quantile is used instead, stated here as a limitation.
- Verdict rule: if either bar's pass/fail differs from the stored run, the verdict changes; the primary result is section 3 only.
