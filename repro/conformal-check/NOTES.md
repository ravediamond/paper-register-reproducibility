# WS-214 notes: our conformal band against FAIL-Detect and SAFE (written 2026-11-10, before any new number)

Read: the stored run `ravediamond/paper-vs-hardware`, `posts/2026-10-23-paper-vs-hardware-contactguard`, block `c2` of
`expected/w1c_summary.json` and `scripts/run_w1c_offline.py` (`fit_band`, `band_norm_max`, `flagged`, `band_splits`);
FAIL-Detect arXiv 2503.08558 sec. IV-B and appendix B ("CP band construction"); SAFE arXiv 2506.09937 sec. 4.3 and
appendix B.4 (which defers to FAIL-Detect appendix B).

## Our band (stored run)
- score: per anchor (every 25 frames) the maximum W1 surprise over k in {15, 20, 25}; one series per rollout.
- 22 calibration successes of a seeded permutation of the 44 successes (20 seeds); the other 22 and the 25 failures are tested.
- mu_t and sigma_t (sample sd) are computed on the same 22 series that then provide the calibration statistic.
- R_i = max_t (s_it - mu_t) / sigma_t over those same 22 series; q = the ceil((n+1)(1-alpha))-th smallest R, rank 22 of 22 (the maximum).
- band_t = mu_t + q sigma_t; t beyond the last index with at least 2 calibration series carries the last value forward.
- flag: any s_t > band_t.

## Their band (FAIL-Detect appendix B, used by SAFE)
- The calibration successes are split into two disjoint parts, Dcal_A (N1) and Dcal_B (N2).
- mu_t = mean over Dcal_A only. Modulation scal_A(t) from Dcal_A only: Eq. (2) = max over k in H of |s_kt - mu_t|
  (H = all of Dcal_A when (N1+1)(1-alpha) > N1), or Eq. (1) = constant 1/T. Both papers' experiments use Eq. (2) (SAFE B.4; FAIL-Detect Table III).
- For each rollout j of Dcal_B: D_j = max_t (s_jt - mu_t) / scal_A(t) (the paper prints mu_t - s_jt; the upper band needs s - mu).
- h = the (1-alpha)-quantile of {D_j}; upper_t = mu_t + h scal_A(t). Flag: any step above upper_t (FAIL-Detect IV-B; SAFE 4.3).
- Common length T for all rollouts (SAFE trims to the shortest rollout of the task).

## Differences
| # | ours | theirs | effect |
|---|---|---|---|
| 1 | mu, sigma and R from the same 22 series (in-sample) | mu and modulation from Dcal_A, R from the disjoint Dcal_B | in-sample R are too small, test R are not: calibration and test scores are no longer exchangeable, so the 1-alpha guarantee does not apply. The likely cause of the excess |
| 2 | modulation = sample sd | max abs deviation (Eq. 2), constant (Eq. 1) | different band shape |
| 3 | q = rank ceil((n+1)(1-alpha)) of n | (1-alpha)-quantile of S | ours is the more conservative of the two |
| 4 | ragged series, tail from 2 series, carried forward | common length T | the tail of our band rests on 2 to 3 rollouts |
| 5 | flag: any step above the band | same | none |
| 6 | one-sided upper band | one-sided upper band | none |

Verdict of the reading: our band did not match. Difference 1 is not a variant of the method, it removes the property the
papers rely on. Protocol: `PROTOCOL.md` (frozen before any number). Limit that no protocol removes: with 22 calibration
successes, a split in two leaves N2 = 11, so the 95 % quantile of S is set by the top one or two of 11 values.
