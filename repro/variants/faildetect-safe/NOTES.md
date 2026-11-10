# FAIL-Detect and SAFE with the authors' code (C-007-1, C-007-2): which of our rollouts can feed it? (WS-216, 2026-11-10)

Step 1 only (feasibility); no score was computed. Answer: the authors' code can be run on the SmolVLA episodes, but there are too few of them (24 successes, 6 failures, three runtimes of one checkpoint) for the 22 + 22 split or for the failure bar, so no run follows. The row stays our variant.

## What the authors' code needs

Read from shallow clones of `CXU-TRI/FAIL-Detect` and `vla-safe/SAFE` (in `~/scratch/WS-216/`, not committed).

| | FAIL-Detect | SAFE |
|---|---|---|
| Input per step | the policy's embedded visual features plus robot state (`save_data.py` O_t) and the action A_t taken from the policy's training data | the VLA's hidden state per step (OpenVLA token features; pi0 and pi0-FAST `pre_logits`; open-pi-zero action embeddings) |
| Scores | score networks trained on training-set pairs only (logpZO, RND, CFM, NatPN, DER, PCA-kmeans); no failure data | `indep` MLP and `lstm` trained on success and failure rollouts; embedding-distance baselines |
| Band | split conformal on successes, as in WS-214's `PROTOCOL.md` | the same band on held-out successes |
| Policies in the papers | diffusion and flow policies on robomimic | OpenVLA, pi0, pi0-FAST on LIBERO, SimplerEnv, two real robots |

## Which of our policies can be re-forwarded offline

Counts from `meta/rollout_labels.csv` of `ravediamond/so101-bowls-policy-rollouts` (69 episodes; main set 50 = 42 successes, 8 failures).

| Policy (episodes) | Successes / failures | Re-forward offline? |
|---|---|---|
| `smolvla` (10) | 9 / 1 | yes: the stored checkpoint `ravediamond/smolvla_2026-09-24_14-34-40` (6.1 GB in the local cache) takes the recorded front and wrist frames, state and task text |
| `smolvla_vlacpp`, `smolvla_vlacpp_fa` (10 + 10) | 15 / 5 | same weights, but the rollouts ran through a GGUF conversion in vla.cpp; the HF model gives the same network, not the same arithmetic |
| `act` (10) | 9 / 1 | no for SAFE (not a VLA); no match for FAIL-Detect (its encoders are diffusion and flow policies) |
| `vla_jepa` (10) | 9 / 1 | no: its checkpoint is not in the local cache |
| `turbovla_*` (not in the main set, 19) | 2 / 17 | not in the main set; no run planned |

The SmolVLA family therefore gives 30 episodes: 24 successes and 6 failures (17232 frames). The checkpoint alone gives 9 successes and 1 failure.

## Why that is not enough

- The bars are medians over 20 splits of 22 calibration and 22 test successes plus all failures. 24 successes allow a split of 12 + 12; the papers' construction halves the calibration part again (Dcal_B = 6), so the 95 % quantile rests on 6 values.
- C-007-2 asks for at least 50 % of failures flagged. With 6 failures one episode moves it by 17 points; with the 1 failure of the stored checkpoint the bar is a yes or no on one rollout.
- SAFE's detector is trained on failures. Holding some of the 6 out for testing leaves a handful for training.
- The population changes (30 episodes of one task and one checkpoint instead of 69 of five policies), so a verdict would not be the same claim as C-007 as registered.
- The score networks of FAIL-Detect are meant to be trained on the policy's own training data (`so101_bowls_all`, 69897 frames) and used on a diffusion or flow policy's encoder. SmolVLA's prefix features are our choice of embedding, one more layer between the authors' code and the number.

## What fits the Orin

Compute is not what stops this. SmolVLA forward on 17232 rollout frames at stride 5 fits the 8 GB cap (`scripts/memcap.sh -m 8G`, `flock ~/scratch/gpu.lock`); the 1.5 GB policy-rollouts dataset is already local; free disk is about 4.3 GB. No vast rental is needed, so no cost estimate is written.

## Decision

Stop at Step 1. No PROTOCOL.md was written because no run follows. C-007-1 and C-007-2 keep their verdicts (fail, fail) and the tier our variant (WS-214's papers' band on W1 surprise: 9.1 % of successes flagged, 24 % of failures caught; see `repro/conformal-check/`). The Section 7 variant paragraph already says our score was used instead of theirs; no fact changed, so the paper text is untouched. Revisit when the rollout set holds at least 22 + 22 successes and a usable number of failures of one VLA checkpoint; that needs new arm runs, which this item does not ask for.
