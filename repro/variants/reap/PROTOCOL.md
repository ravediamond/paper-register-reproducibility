# ReAP with its Stage 1 failure representation (C-008-2)

Work-stack item WS-217, 2026-11-10. Frozen before any number: this file is committed before any feature is extracted or
any model is trained. Claim C-008-2 and its bar are the register's and do not change: at least 5 of 8 failures caught at
no more than 1 of 20 false interventions on the main set (50 rollouts, 42 successes, 8 failures). Everything not written
here is exploratory.

## 1. Question

Does the monitor of Liu et al. (arXiv 2610.16309) with its own Stage 1 (a visual detector on DINOv2 patch tokens trained
on successful and failed rollouts, whose latent space the Stage 2 predictor forecasts) pass the register's bar on our
50 SO-101 rollouts, and does it work where failures are plentiful (ArmnetBench, held-out policies)?

## 2. What the paper does (Sections 3 to 4, Appendix C.3, Table 8)

Risk target y = 0 on successes, y = t / (T - 1) on failures. Stage 1: frozen DINOv2-Large patch tokens per camera, a
projection with camera and spatial position embeddings, a Perceiver-style extractor (M = 32 latent queries, 2 blocks,
width 1024), mean-pooled to one vector, linear map to the compact state z_t (width 256), detector head to r_det in [0, 1];
class-weighted binary cross entropy against the ramp target. Stage 2: z_t frozen detector; action tokens (step embedding)
cross-attend to projected latent tokens L_t (7 blocks, width 256), mean-pooled with the actions and z_t, residual MLP gives
z_(t+H|t); loss = MSE(z_(t+H|t), sg(z_(t+H))) / d + BCE of the frozen detector head on the prediction; H = 10 control
steps; lambda_feat = lambda_risk = 1. AdamW, lr 1e-4, weight decay 0.01, batch 64, 10k steps, cosine with 500 warm-up
steps. Thresholds from held-out successful rollouts, time-varying (six variants chosen on validation); the monitor alarms
when either branch crosses its threshold. No code is released.

## 3. Differences between our earlier test and the paper (recorded in the register as 3/8 at 5/42)

1. No Stage 1: the earlier head was a logistic regression on W1's generic latent (192-d) plus the commanded 30-action chunk.
2. Not DINOv2 patch tokens, no Perceiver, no learned failure space, no frozen detector head, no latent transition loss
   (the head predicted the ramp directly).
3. No separate detector branch and no either-branch alarm rule.
4. Trained on the 50 main-set rollouts only (about 40 per fold, 6 or 7 failures); the paper trains on thousands.
5. Horizon 30 frames (1 s at 30 Hz); the paper uses H = 10 control steps.
6. A single global threshold; the paper uses time-varying thresholds.

## 4. Differences that remain after this rebuild (fixed in advance, forced by the disk and by the data)

1. Backbone DINOv2-small (384-d), not Large. The paper's Table 11 reports Small at 0.672 bTWA against 0.671 for Large.
2. One camera (the top view: ArmnetBench `top`, ours `front_top_camera`), not all views; the Orin has about 4.5 GB of free
   disk, and one ArmnetBench camera is 22.4 GB of AV1 video, streamed file by file.
3. Patch tokens are average-pooled to a 4 x 7 grid (28 tokens) from a 224 x 392 input (16 x 28 patches, pooled 4 x 4), stored
   as int8 with a per-frame scale; frames sampled every 0.5 s (every 10th frame at 20 Hz in ArmnetBench, every 15th at 30 Hz
   in ours). The paper uses dense tokens at control rate. The aspect ratio of our frames is stretched to 224 x 392.
4. H is one feature step, 0.5 s: 10 control steps in ArmnetBench (as the paper), 15 in ours, whose 15 commanded actions are
   resampled to 10 by even sub-selection before the action projection. Joint actions of the two datasets are normalised
   by each dataset's own mean and standard deviation.
5. Widths reduced: Perceiver width 256, 2 blocks, M = 32 queries; compact state 128; predictor 3 blocks, width 128. The
   step count is 5,000 for each stage (paper: 10k), AdamW lr 1e-4 (cosine, 200 warm-up steps), weight decay 0.01, batch 64.
6. Threshold: one global threshold per branch, not time-varying. For the combined monitor each branch is set so that at most
   1/40 of the training successes alarm (so the union stays near 1/20 on training data); the branches alone use 1/20.
7. Training data. ArmnetBench has other tasks (eight tasks, blocks, cables, tools, eye drops, rings; none is bowls). The
   2,099 policy rollouts are used; the 400 teleoperation episodes are skipped (disk). The main-set evaluation therefore
   mixes a different task, a different robot calibration and another camera pose in training with our task in the training
   folds. This is the largest remaining difference from the paper, which trains on the policy and task it monitors.
8. Our `success` / `failure` labels are the operator's; ArmnetBench `success_class` `successful` is a success, `failure` a
   failure, `suboptimal` (52 rollouts) is dropped.
9. Training and calibration use full episodes (as the paper); scoring on the main set uses the common-horizon truncation of
   the earlier test (T_common 374 frames, so 24 feature steps at 15 frames each), so that episode length cannot separate
   outcomes.

## 5. Data

- Main set: `ravediamond/so101-bowls-policy-rollouts`, 69 episodes; the 50 of `in_g16_set` (42 successes, 8 failures) are
  the evaluation set. The other 19 (2 successes, 17 failures) are the non-test episodes: always in training, never scored.
- ArmnetBench: `armnet/armnetbench_v01_lerobot_so101` at revision 1db69c82b589c7172ee31a6b8f7ef58d1fc2c663, top camera
  only, 2,099 policy rollouts with `success_class` in {successful, failure}. Raw video is deleted after each file.

## 6. Runs

- **Run M (main, the register run).** Per seed s = 0..4 and fold k of `StratifiedKFold(5, shuffle=True, random_state=s)` over
  the 50 main episodes: train Stage 1 then Stage 2 on [all ArmnetBench rollouts + 19 non-test episodes + the 4 training
  folds of the main set]; calibrate the thresholds on the successes of the 4 training folds; score the held-out fold.
  Episode score = max over feature steps; an episode is intervened in at its first step above the threshold. Monitor =
  combined ReAP (either branch). Reported value: median over the 5 seeds of failures caught and false interventions
  (successes intervened) pooled over the 5 held-out folds.
- **Run T (transfer, exploratory).** As Run M but the 4 training folds of the main set are used only to calibrate the
  thresholds, not for training.
- **Run A (ArmnetBench, held-out policies).** For each of the 7 policies: train on the other 6 policies' rollouts (all 8
  tasks), calibrate on the successes of those 6, score the held-out policy's rollouts, truncated per task to the shortest
  rollout of that policy and task. One seed. Reported per policy and pooled: AUROC of the episode score, failures caught
  at <= 1/20 false interventions, the length-only AUROC of the same rollouts (untruncated) as the null.
- **Controls (all runs, at evaluation only; models trained on true chunks).** Shuffled: the action chunk at the same step
  of another episode of the same task, chosen by seed; zero: all normalised actions 0. Only the predictor branch reads the
  chunk, so the controls are applied to the predictor alone and the combined monitor is recomputed.
- Branches reported beside the combined monitor: detector alone, predictor alone (1/20 each).

## 7. Bars (each with its source)

1. C-008-2 passes when Run M, true actions, combined monitor, median over seeds, catches >= 5/8 failures with <= 2/42
   false interventions (register bar, `repro/register/expected/register.json`, claim C-008-2). Otherwise it fails.
2. The shuffled-action control is a check, not a second bar: C-008-1's bar (true AUROC >= shuffled AUROC + 0.05, register)
   is read for the predictor branch of Run M and stated; it changes no verdict by itself.
3. Run A has no bar; it is reported (the paper has none on this data).

The register's verdict is "fail" before this run. A pass moves C-008-2 to "reproduces"; a fail stays "fail".

## 8. Checks before numbers

Two episodes per dataset: frame counts against metadata, token arrays of shape (frames, 28, 384), a hand-computed ramp
target, a hand-computed threshold on a toy score list, and a one-batch overfit of Stage 1 on 64 frames.

## 9. Deviations (empty)

## 10. Exploratory

Run T, the branch-alone numbers, any choice made after a number exists, and bootstrap intervals (episode as unit, 2,000
resamples, seed 0, as `repro/baseline-bootstrap/PROTOCOL.md`) on the main-set AUROC difference between true and shuffled.
