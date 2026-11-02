# WS-078 step 2 · Early gates on the episode bootstrap (2,000 resamples, seed 0)

Which gates report an interval, which statistic produced it, whether the per-episode rows are stored in this repo, and
the recomputation where they are and the statistic differs. **No verdict is edited**; a would-change row is listed for
the owner. Search: every §1 / §2 row of `journal/EXPERIMENTS.md` whose result cell carries an interval (`[a, b]`, "CI",
"±"); the statistic read from the gate's scorer code or README.

| gate | reported interval | statistic used (source) | per-episode rows stored? | recomputed (episode bootstrap, 2,000, seed 0) | verdict would change? |
|---|---|---|---|---|---|
| G9a-AB (partial, superseded) | AUROC 0.861 [0.833, 0.885] | episode bootstrap, B = 2000, `default_rng(0)` (`robometer/analyze_g9a_ab.py`) — one row per rollout | no: `ab_top.jsonl` is on the old Mac | not needed (same statistic) | — |
| G9a-AB complete | 0.818 [0.790, 0.843] | same | no (same files) | not needed | — |
| G9a-own | 0.577 [0.444, 0.704] | episode bootstrap, `default_rng(0)` (`analyze_g9a_own.py`) | summary only (`g9a_own.json`) | not needed | — |
| G9c | accuracy 86.4 % [78.4, 93.2], AUROC 0.919 [0.869, 0.961] | episode bootstrap, B = 2000, `default_rng(0)` (`judge/g9c_test.py`) | errors only (12 of 88) | not needed | — |
| **G14** | failed episodes oscillating 6 / 25 = 24.0 %, **Wilson** 11.5–43.4 % | Wilson score interval (README) | **yes**, `shared/gate/data/2026-10-18_g14/g14_episodes.csv` | **24.0 %, bootstrap 8.0–40.0 %** (all 69: 14 / 69 = 20.3 %, bootstrap 10.1–29.0 %) | **no**: the bar is "≥ 10 % of failed episodes oscillate" on the point estimate (24.0 %); a CI-based reading would put the lower bound (8.0 %) under 10 % |
| §30 inverse dynamics | CIs on paired differences | episode bootstrap, 2,000, seed 0 (README) | yes | not needed | — |
| RoboJEPA Gate A | [14.6, 17.0] | not stated in the row; no source folder linked | no | cannot recompute | — |
| W1-C1 | IQR over 20 seeds (not a CI) | seed spread | summary only | not applicable | — |
| AAC, PACT, horizon × depth, REMORA, smooth chunking, REAP v2, W1-A, G-flora | — | episode bootstrap, 2,000, seed 0, written into their frozen protocols | yes | already the statistic | — |

Note: the all-69 G14 line is descriptive (the row reports it without a CI); its bootstrap interval is 10.1–29.0 % (seed 0).

**Result:** one early gate (G14) used a different interval; recomputed, its point estimate and verdict stand, and its
lower bound moves under the bar's threshold if the bar were read on the interval (it is not). The early Robometer and
judge gates already used the episode bootstrap; their per-episode rows are partly on the old Mac (G9a-AB), which is
also WS-077's recovery item.

## WS-136 · Early gates (2026-10-08 to 10-19), episode bootstrap from the stored rows

`recompute_early.py` → `recompute_early.json` (2,000 resamples over episodes, `default_rng(0)`, percentile 95 % CI). "Rows rebuilt from counts": binary per-episode outcomes stored only as totals; for a proportion the bootstrap needs nothing else. **flip-under-CI** = the verdict on the point estimate differs from the verdict read on the CI (pass whose conservative bound crosses the bar, or fail whose CI includes it). **No verdict is changed**; flagged rows go to the owner.

| gate | metric | units | estimate | 95 % CI | bar | point verdict | flip-under-CI | source | note |
|---|---|---|---|---|---|---|---|---|---|
| G14 | failed episodes oscillating | 25 | 0.24 | [0.08, 0.4] | >= 0.1 | pass | **yes** | `shared/gate/data/2026-10-18_g14/g14_episodes.csv` |  |
| G15 | premature rate (test) | 34 | 0.4853 | [0.4559, 0.5] | <= 0.02 | fail | no | `shared/gate/data/2026-10-19_g15/g15_summary.json` |  |
| G15 | missed rate (test) | 34 | 0.4667 | [0.42, 0.5] | <= 0.1 | fail | no | `shared/gate/data/2026-10-19_g15/g15_summary.json` |  |
| W1-B | premature rate (test) | 34 | 0.2206 | [0.1471, 0.3088] | <= 0.02 | fail | no | `shared/gate/data/2026-10-19_w1_screening/w1b_summary.json` |  |
| W1-B | missed rate (test) | 34 | 0.3111 | [0.1666, 0.4474] | <= 0.1 | fail | no | `shared/gate/data/2026-10-19_w1_screening/w1b_summary.json` |  |
| G16-B | successes flagged | 42 | 0.9762 | [0.9286, 1.0] | <= 0.0476 | fail | no | `shared/gate/data/2026-10-19_g16b/g16b_episodes.csv` |  |
| G16-B | failures flagged | 8 | 1.0 | [1.0, 1.0] | >= 0.75 | pass | no | `shared/gate/data/2026-10-19_g16b/g16b_episodes.csv` |  |
| G9c | accuracy | 88 | 0.8636 | [0.7841, 0.9318] | >= 0.95 | fail | no | `projects/vla-jepa-world-model/judge/results/g9c/g9c_results.json` | rows rebuilt from counts |
| G9c-3 | accuracy on judged | 87 | 0.9425 | [0.8963, 0.9885] | >= 0.95 | fail | **yes** | `projects/vla-jepa-world-model/judge/results/g9c3/g9c3_test_results.json` | rows rebuilt from counts |
| Judge τ | false interventions on successes | 42 | 0.0238 | [0.0, 0.0714] | <= 0.05 | pass | **yes** | `shared/gate/data/2026-10-19_judge_tau/judge_tau.json` | τ is fitted to meet this; the CI is descriptive |

Point estimate only, rows not stored (or not a per-episode rate) — early gates with a bar:

| gate | why no CI here |
|---|---|
| H0, LeWM env, G0, G1 probes, G1b W1, G1 W2 dynamics, G2 (Mac), RoboJEPA Gate A / B / B′, G6a, G6b, G10, G11, G12 | summaries only in the results JSON / report (no per-episode rows), or a latency / smoke check with no episode sample |
| G9a-AB, G9a-AB complete | per-rollout scores on the old Mac (`ab_top.jsonl`, WS-077); reported CI is already the episode bootstrap |
| G9a-own, G9c (AUROC), G9c-3 (AUROC) | AUROC needs per-episode scores; only summaries / the error list are stored; reported CIs already the episode bootstrap |
| G9c-2 | summary only |
| W1-A | per-episode scores stored (`w1a_summary.json`), but the count needs τ refit per signal; not reimplemented in this pass |
| G11-B-cal | per-episode maxima stored (`g11b_cal_episodes.csv`); thresholds fitted in-sample on the same 69, so a bootstrap of the recall without the refit would be optimistic; not recomputed |
| W1-C1 / W1-C2 | seed spread over 20 splits (`w1c_summary.json`), not an episode CI |
| G13b, G13b in vla.cpp | 20 episodes in `g13b_summary.json` meta, the per-episode jumps not stored |
| G15-v2 / G15-v3, H3, G1b-RJ, G9b | no bar (dev / fit only) or never run |

**flip-under-CI, for the owner:** G14 (pass on 24.0 %; lower bound 8.0 % < 10 %), G9c-3 (fail on 94.3 %; upper bound 98.9 % ≥ 95 %), judge τ (1/42 = 2.4 % ≤ 5 %; upper bound 7.1 % > 5 %; τ was fitted to meet the rate, so the CI is descriptive). G9c's accuracy CI reproduces the reported [78.4, 93.2] (0.7841, 0.9318).
