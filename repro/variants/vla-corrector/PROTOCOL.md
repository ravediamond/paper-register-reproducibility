# VLA-Corrector's Learned Verifier, built and trained as the paper describes (C-009-1)

Work-stack item WS-215, 2026-11-10. Frozen before any number: this file is committed before the verifier is trained or
scored on any episode. Claim C-009-1 and its bar are the register's and do not change: at least 5 of 8 failures caught at
no more than 1 of 20 false interventions on the main set (50 rollouts, 42 successes, 8 failures). Everything not written
here is exploratory.

## 1. Question

Does the Learned Verifier of Song et al. (arXiv 2609.06508), trained on our SO-101 rollouts with the paper's label
definition, optimiser settings and online gate, pass the register's bar on the 50 main-set rollouts, and is its score
driven by the executed actions (shuffled-action control)?

## 2. Correction of the task premise (read before the rest)

The register row and the item text say the earlier test (2 of 8 caught at 3 of 42, AUROC 0.59) used "pooled RGB
statistics and actions" and left out the proprioceptive state. The code says otherwise: `scripts/run_reap_v2.py` (class
`GRUFloor`, `Linear(12, 32)` on the 12-d state-action vector; line 126 concatenates `E[e]["s"][ix]`, the recorded
`observation.state`, with the action) fed the six joint positions to the GRU. The earlier test already had the paper's
visual featuriser (108 = 2 x 54), the 8-step window every 2 frames, GRU 64 and projections 64 / 32. What it did **not**
have is the paper's training and gate (section 3). So this item does not add an input; it replaces the training label, the
optimiser loop, the split and the gate, and corrects the register's description of the earlier input.

## 3. What the paper does (Method, "Learned Verifier"; Table 2; Experimental Setup)

- Input at time t: two RGB views (agent, wrist), an 8-d proprioceptive vector, the 7-d executed action. Window of 8 steps
  sampled every 2 environment steps; verifier images 112 x 112.
- Visual branch, parameter-free: per view a 3 x 4 x 4 adaptive-average-pooled RGB (48 values) plus the RGB mean (3) and
  standard deviation (3) = 54 per view, 108 for two views; projected to 64. The 15-d state-action vector is projected to 32.
  A GRU with hidden size 64; a sigmoid risk head and a 5-class stage head.
- Label: f_t = 1 if the distance to the nearest teacher-defined failure event is at most 10 environment steps, f_t = 0 if
  it is more than 20, and windows in between are excluded from the binary loss. Stage labels come from a privileged
  rule-based teacher.
- Training (Table 2): 120 episodes, episode-disjoint 60 / 20 / 20 train / validation / test; 30 epochs, batch 32,
  learning rate 1e-3, weight decay 1e-4, CPU.
- Gate: threshold 0.40, four consecutive positive windows, 10-sample cooldown, evaluation every two environment steps. The
  threshold, confirmation length and cooldown are selected on the validation split.
- Reported: accuracy 93.1 %, precision 61.1 %, recall 94.9 %, AUROC 0.902, AUPRC 0.7123 (LIBERO, simulator).

## 4. Our build (the inputs that have an SO-101 equivalent)

| paper | here | file |
|---|---|---|
| agent-view and wrist RGB, 112 x 112, 54 features per view | `front_top_camera` and `wrist_camera`, 640 x 480 frames resized to 112 x 112, the same 54 features per view (all 54 exist: nothing is dropped) | `outputs/reap/rgbfeat/ep###.npy` of road-to-robotics, (frames, 108) float32, concatenated-bytes sha256 `33a651f75b25ccdac249d0e93b0a81b67582740bfc56325a23eb6c67eb40d704` |
| 8-d proprioception (end-effector position, axis-angle, two-finger gripper) | 6 joint positions of the follower, `observation.state` | `data/episodes.npz` (`s<ep>`) |
| 7-d executed action (end-effector delta and gripper) | 6 commanded joint targets, `action` | `data/episodes.npz` (`a<ep>`) |
| 15-d state-action vector | 12-d | |
| 5-class stage head, teacher stage labels | **absent** (no stage labels exist for our rollouts) | |

Features that do not exist here: end-effector pose and axis-angle (the SO-101 records joints only; we do not compute
forward kinematics), the second gripper finger (one gripper joint), the stage labels. `data/episodes.npz` and
`data/episodes_meta.csv` (sha256 `7b6bec5970efd54f9cb231fe46c0769358bf11c295ac8a98a7a7adf15f577b6f` and
`d7ee2fb5051f1dcbf62d7c9f42b5a699e86d60e2ad1e78738091cd5683e39375`) are produced by `extract_episodes.py` from
`ravediamond/so101-bowls-policy-rollouts` (69 rollouts with an operator outcome, 30 fps).

## 5. Data

- Main set: the 50 episodes with `in_g16_set` (42 successes, 8 failures; 5 policies); evaluation set. All are the task
  "Put the blue bowl in the pink bowl.".
- Non-test: the other 19 (2 successes, 17 failures; they include the task "Pick up the blue bowl."). Used only in the
  secondary reading R4.
- Failure event: one per failed rollout, the frame `onset_frame` of `shared/gate/data/2026-10-23_onsets_vlm/onsets.csv`
  (Gemini reading of the video; exists for all 25 failures, none for successes). This replaces the paper's rule-based
  teacher. Successes carry no event, so all their windows have f = 0.
- Usable frames: up to `reset_start` when the rollout has a reset, else all frames (`end` in the metadata).

## 6. Procedure

1. Windows: query times t = 0, 2, 4, ... < end; window = frames t-14, t-12, ..., t (clipped at frame 0), 8 steps. Features
   per step: the 108 visual values; state and action standardised with the W1 constants (`W1_ACTION_MEAN`, `W1_ACTION_STD`
   of `src/so101_harness/w1_live.py`, six joint values each, applied to both state and action, as the earlier test did).
2. Model: visual 108 -> Linear 64 -> ReLU; state-action 12 -> Linear 32 -> ReLU; GRU(96 -> 64); risk head Linear(64 -> 1),
   sigmoid. AdamW, learning rate 1e-3, weight decay 1e-4, batch 32 shuffled each epoch, 30 epochs, binary cross-entropy on
   the windows with f defined (section 3), the model after epoch 30 (no early stopping). CPU, torch seed = the split seed.
3. Splits, seeds 0..4: `StratifiedKFold(5, shuffle=True, random_state=seed)` over the 50 main episodes gives the test fold
   (10 episodes); of the other 40, a stratified quarter (10 episodes, `train_test_split(test_size=0.25, stratify, random_state=seed)`)
   is validation and 30 are training: 60 / 20 / 20 as in Table 2. Each episode is a test episode once per seed.
4. Scoring: on a test episode, queries every 2 frames from t = 2 to the common horizon (T_common = 374, the shortest
   usable main-set episode, so that episode length cannot separate outcomes), the risk p_t at each query. Gate fires at the
   first query where the last four queries all have p >= tau. Episode score = max over t of min(p over the last four
   queries); the gate fires if and only if score >= tau. Cooldown does not matter for the first intervention.
5. Shuffled-action control: the test episode's actions are replaced by those of a partner episode (the same main-set pool,
   `numpy.random.default_rng(0)` choice over the other 49), same frame indices; visual and joint inputs unchanged. Same
   model, same threshold.

## 7. Readings

| id | what | status |
|---|---|---|
| R1 | training windows unweighted; training on the 30 training episodes of each fold; gate tau = 0.40 as printed in the paper | **primary, the register verdict** |
| R2 | R1 with binary cross-entropy weighted by N_neg / N_pos on the positives (the paper states no weighting; on the 50 main episodes 85 windows have f = 1 and 14,459 have f = 0, about 1 in 170 (counted from the metadata by the same window rule)) | secondary, does not change the verdict |
| R3 | R1's model, tau set per fold to the highest episode score among the 10 validation episodes' successes (fires on a test episode only if its score exceeds it) | secondary, does not change the verdict |
| R4 | R1 with the 19 non-test episodes added to every training set | secondary, does not change the verdict |

Per seed and reading: failures caught and successes intervened in, pooled over the five test folds (each of the 50 episodes
tested once); reported value = median over the 5 seeds. Also reported, descriptive: AUROC of the episode score (median over
seeds), window-level AUROC and AUPRC of p against f on the test windows with f defined (the paper's 0.902 and 0.7123), the
same for the shuffled control.

## 8. Bar and verdict (the register's, unchanged)

Pass if, under R1, the median caught is at least 5 of 8 and the median successes intervened in at most 2 of 42 (1/20 of 42
rounded down, as the earlier test counted). Otherwise fail. Shuffled-action control: the score is action-conditioned if the
true-action episode AUROC exceeds the shuffled one by at least 0.05 (the earlier test's rule). If R1 fails and R2, R3 or R4
passes, the register keeps "fail" and the paper says which reading passed, as exploratory.

## 9. Differences that remain after this rebuild (fixed in advance)

1. **Data.** The paper trains on 120 episodes of its simulator with scripted perturbations; we train on 30 real rollouts
   per fold (about 5 failures) and test on 10. The largest remaining difference, and the likeliest reason for a null.
2. **Embodiment.** Joint-space 6-d state and action in place of 8-d and 7-d end-effector quantities; no forward kinematics.
3. **Label source.** One failure event per failed rollout from a Gemini reading of the video, not a rule-based teacher
   with several events; the frames after an event are negative once 20 steps away, as the printed formula says.
4. **No stage head.** No stage labels; the paper's multi-task training (risk and stage through one GRU) is not reproduced.
5. **Rate.** Our rollouts are 30 fps and the paper's 20 Hz; the step counts (window stride 2, horizon 10, exclusion 20,
   four confirmations) are kept in steps, so they cover 1.5 times less wall time.
6. **Threshold.** 0.40 is the paper's value for its data; the paper's selection rule on its validation split is not
   stated, so R1 does not select (R3 selects with our own rule).
7. **Unspecified by the paper and fixed here:** optimiser (AdamW), activation after the projections (ReLU), class weights
   (none in R1), standardisation of state and action, seed handling, the 5-fold scheme, the window clip at the start.
8. **Views.** `front_top_camera` stands in for the agent view; 640 x 480 frames are squeezed to 112 x 112.
9. **Perturbations and policy.** The paper's policy is a frozen pi0.5 under LIBERO; ours are five SO-101 policies. The
   paper's closed-loop recovery effect is not tested (no arm).
10. **Test truncation** to a common horizon (the earlier test's rule), which the paper does not apply.
