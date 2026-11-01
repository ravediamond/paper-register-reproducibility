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
