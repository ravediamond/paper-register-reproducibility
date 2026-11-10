# ReAP with its Stage 1 (C-008-2): result

WS-217, 2026-11-10. Numbers are in `expected/results.json`; the protocol is `PROTOCOL.md` (deviations 2 and 3 apply).
Code: `extract.py` (features) and `reap_stage.py` (Stage 1, Stage 2, monitor).

Main set (50 rollouts, 42 successes, 8 failures), seed 0 of 5, true actions, combined monitor (either branch alarms): 2 of 8
failures caught at 1 of 42 false interventions, AUROC 0.72. Bar: at least 5 of 8 at no more than 2 of 42. Verdict: fail, as
before (earlier test with our own risk head: 3 of 8 at 5 of 42). Detector alone 3 of 8 at 4 of 42; predictor alone 2 of 8
at 2 of 42. Shuffled-action predictor AUROC 0.67 against 0.69 with true actions (difference 0.018, bootstrap 95 % interval
-0.060 to +0.102): the predictor is not shown to use the actions on this set.

ArmnetBench, held-out policy (7 policies, one seed, 2,047 rollouts: 1,532 failures, 515 successes): the combined monitor
caught 278 failures at 24 false interventions; per-policy AUROC 0.54 to 0.76, while episode length alone gives 0.91 to 0.96
on the same rollouts. The predictor with shuffled actions matches the true-action one within 0.05 AUROC for every policy.

Remaining differences from the paper: see PROTOCOL.md section 4 (DINOv2-small, one camera, 4 x 7 pooled tokens at 2 Hz,
narrower networks, 5,000 steps, one global threshold, training mostly on other tasks) and deviation 2 (one seed).
