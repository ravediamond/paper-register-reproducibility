# What survives when a paper leaves the lab: re-testing 22 robot-learning papers on a €1,350 rig, and auditing our own pre-registration

*Ravindu Somawansa, Shisso Robotics. Draft, not submitted.*

## Abstract

We re-tested the main claims of new robot-learning papers on an SO-101 arm with a Jetson Orin NX. The pieces cost €1,350 and the compute $45.10. Each re-test ran the cheapest baseline first, and its pass mark was committed before the run. Of the 37 paper claims we tested, 12 were valid on our hardware. Three proposed classes cover the failures: edge latency (a method misses the real-time budget on the edge GPU), zero-shot judges (a judge loses to a trivial signal) and latent planners (a planner loses to the commanded joints). A blind second reader still has to confirm the classes. We also verified our own pre-registration by commit history. For most gates the order of bar and result can be read from the repository, and for some it cannot.

## 1. The register

Most of the 22 papers in this study were shown on setups far from ours. 9 were shown in simulation and 7 on rigs above $20k. 2 used a setup under $5k, which is where our rig falls. The appendix table gives the rig of each paper, including the 3 in between and the 1 that does not say. Our rig is an SO-101 arm and a Jetson Orin NX 16 GB.

The register grew out of our own write-ups. Each re-test on this rig was published with its data, and there are 29 so far. This paper collects them in one table and audits how the table was kept.

Here is one entry. An adaptive chunking paper claims that choosing the chunk length from the entropy of sampled chunks follows the task's phases, long in transport and short at the grasp. On our edge GPU one such decision takes 4,751 ms. The budget is 298 ms. The entry records a fail on this rig. It says nothing about the method on the hardware it was shown on. Next to the verdict, the entry keeps the claim in the paper's words, our pass mark, our measurement and the published rows.

For each claim we first run the cheapest signal the learned model has to beat, on the same rows. For a predictor this is copy-last. For a latent it is the commanded joints. For a judge it is episode length.

We chose the papers for the stack this rig runs (world models, VLA policies, failure monitors, chunking, edge latency). Each one went into the register before its test. The register file lists the papers scheduled next.

## 2. Auditing our own pre-registration

A gate's pass mark had to be in version control before its result. Notes and commit dates can be edited by hand. Commit ancestry cannot be changed without rewriting history that others have already cloned. For each gate we find the first commit that contains its bar and the first that contains its result, and compare them (`repro/prereg-check/scripts/prereg_audit.py`, abridged):

```python
def ancestor(a, b):
    return subprocess.run(["git", "-C", str(RR), "merge-base", "--is-ancestor", a, b]).returncode == 0
...
            elif b[0] == res[0]:
                cls = "same-commit"
            elif ancestor(b[0], res[0]):
                cls = "bar-first"
            elif ancestor(res[0], b[0]):
                cls = "result-first"
```

Table 1 gives the classes for the 89 gates logged by 2026-10-31. Most are bar-first and 0 are result-first. A same-commit gate is one where bar and result entered the repository together. It says nothing about which was written first.

Table 1: Commit-order class of each gate. The audited column is the one the paper uses; the first pass is what text search alone gave on the same gates.

| class | first text pass | audited, 2026-10-31 | audited, today |
|---|---|---|---|
| bar-first | 36 | 58 | 61 |
| same-commit | 31 | 6 | 7 |
| result-first | — | 0 | 0 |
| no bar | 19 | 23 | 23 |
| bar, no result yet | — | 2 | 2 |
| unresolved | 3 | — | — |
| gates | 89 | 89 | 93 |

Our first pass used text search and found 31 same-commit gates. The cause was batch logging. We traced each same-commit gate back to the earlier file that holds its bar. This moved 21 gates to bar-first and 4 to no-bar, because their bar cell declares none. 6 stayed same-commit. The audit table in the repository gives the evidence line for every move. We did not re-audit the gates that were already bar-first. One open candidate remains, the reward-model progress test of 2026-11-01. It is same-commit by text search, although its protocol (`6241570`) is older than the log commit.

The early gates mixed point estimates and different intervals. We recomputed 10 of them from stored rows with one statistic, the episode bootstrap (2,000 resamples, percentile 95 % CI). For 3 of them the bar falls inside the interval (Table 2). The colour judge is a fail on the point estimate, and its interval does not settle it. The false-intervention threshold was fitted to meet its rate, so that interval is only descriptive. The register keeps the pre-registered point verdicts and marks these three as fragile.

Table 2: The three gates whose verdict flips somewhere inside its 95 % interval.

| gate | n | estimate | 95 % CI | bar | point verdict |
|---|---|---|---|---|---|
| colour judge (no learning), accuracy | 87 | 94.2 % | 89.6–98.9 % | ≥ 95 % | fail |
| oscillation among failed episodes | 25 | 24.0 % | 8.0–40.0 % | ≥ 10 % | pass |
| judge threshold, false interventions | 42 | 2.4 % | 0.0–7.1 % | ≤ 5 % | pass |

All 29 write-ups rebuild from their published rows. The check for the cold reruns prints:

```text
$ python3 repro/cold-reproduction/l0_check.py
ok  posts: 29 (report 29)
ok  L0 PASS: 29 (report 29)
ok  L1 REPRO: 6 (report 6)
ok  L1 DIFF: 0 (report 0)
ok  L1 classes: {'REPRO': 6, '—': 3, 'SKIP': 8, 'FAIL-ENV': 12}
L0 PASS
```

The cold reruns start from a fresh clone with no credentials. 6 gates reran and matched, 5 of them exactly. 12 more stop at the world-model environment, which is not published yet. Publishing it would unblock most of them. The remaining 11 need a larger GPU, a private checkpoint, the arm or a step the write-up leaves out. We checked the register's citations and paper-side fields against the papers' PDFs and corrected them. The register names 38 arXiv ids. The ones missing from our papers mirror all belong to scheduled tests. One tested paper has no arXiv id and was not checked against a PDF.

## 3. Results

Table 3 counts the verdicts by paper and by claim row. On claims taken from papers, 12 of 37 reproduce and 18 fail. The other 8 rows test our own baselines, for example that the commanded joints beat the world model. 5 of those hold.

Table 3: Verdicts by paper and by claim row (claim rows include our own baseline comparisons).

| verdict | papers | claim rows |
|---|---|---|
| reproduces | 4 | 17 |
| fails | 13 | 20 |
| not proven | 3 | 3 |
| not tested | 1 | 4 |
| withdrawn | 1 | 1 |
| total | 22 | 45 |

## 4. Three failure classes

The adaptive chunking entry of §1 misses the real-time budget on the edge GPU. The method may work on faster hardware. We call this kind of failure class A, the clock.

In other entries a model judged outcomes without training on this rig. A learned reward model detects failures at AUROC 0.818. Episode length alone reaches 0.938. Judges of success, failure or progress that lose to a trivial signal like this form class B. Class C is about learned latents. A world model ranks the executed chunk first in 0.60 of anchors. Its pass mark was 0.8, and an action-only baseline reaches 0.68–0.90. Class C holds latents used to plan, rank or track progress that lose to the joints, to copy-last or to an action-only baseline.

These examples illustrate the classes. They do not count them. A protocol committed before any labelling sets the rule for counting. The labels count only once a blind second reader labels the same 20 failed rows on the same form and agrees with the first reading at Cohen's κ ≥ 0.6. That reading has not happened yet.

## 5. Limitations

One operator, the author, ran the rig and labelled the outcomes. Labels were given at rest and not always blind to the arm. Observer bias is therefore the main confound. Where commit order shows it, the pass mark predates the run, so a label could not move the bar. A blind two-reader protocol for the failure classes is committed. It has not run yet, so no verdict has a second reader. For 29 of the 89 gates the repository cannot show whether bar or result came first. 21 of the bar-first verdicts rest on matching a bar text in an earlier file. Under the bootstrap 3 verdicts are fragile. Cold reruns cover 6 gates so far, and the unpublished world-model environment blocks most of the rest. A failure here describes this rig, not the paper in its own setting. The papers were chosen for one stack, so the rate describes this register and not the field.

## 6. Related work

Two works use the same arm to evaluate policies. A standardized real-world benchmark reports a taxonomy of failures and recoveries for VLA policies [arXiv:2606.08881]. A fleet of SO-101 cells evaluates policies at scale [arXiv:2607.24481]. The vla-eval tool runs VLAs across 14 simulation benchmarks [arXiv:2603.13966]. A benchmark of demonstration quality studies one method family [arXiv:2610.18869]. We test the claims behind methods (judges, world models, latency) against thresholds fixed before the run, and we audit our own pre-registration. RoboSeed [arXiv:2610.40026] is the closest work. It scores VLA and world-action models on five dimensions, including reproduction evidence and deployment affordability. Its reproduction-evidence score counts five audit milestones (configuration mapping, task records, task coverage, training records, seeds). Its authors state that this score is not a probability that a result is correct. We give one pass or fail per claim on a €1,350 rig.

## 7. Conclusion

We re-tested 37 paper claims, and 12 held. The rig cost €1,350 and the compute $45.10. Every row behind the verdicts is published. Our own history cannot show the order of bar and result for 29 of 89 gates. If you re-test a paper on a cheap rig, run its cheapest baseline on the same rows first and commit the threshold before the run. Every number here can be rebuilt from the repository (`github.com/ravediamond/paper-register-reproducibility`).

## References

## Appendix: the register

Table 4: The register, one row per paper, generated from the register file (internal model and gate names kept). The rig price of €1,350 counts the parts with a stated price; 2 small parts are not priced yet. Read the verdict column against the rig each paper was shown on.

| paper | their rig | claim tested | bar | our result | verdict |
|---|---|---|---|---|---|
| LeWorldModel [arXiv:2603.19312] | sim | A small JEPA world model learns the arm's dynamics well enough to plan with it. | Dynamics: beat copy-last, every corruption ≥ 1.3 at K = 30. Planning: rank the executed chunk first among 8 in ≥ 0.8 of anchors. | dynamics 0.31 vs 0.89 copy-last (reproduces); planning top-1 0.60 vs 0.68–0.90 for an action-only baseline (fail) | fail |
| DINO-WM [arXiv:2411.04983] | sim | A predictor on frozen DINOv2 patches plans better than one on a learned latent. | G1b top-1 ≥ 0.8 at some target distance. | arm-pose R² 0.92 (vs 0.57 for W1); G1b top-1 0.55–0.61; no-model baseline 0.68–0.90 | fail |
| RoboJEPA [arXiv:2610.10515] | >$20k | Pretrained RoboJEPA predicts our latents, uses the actions, and runs on the robot's computer. | 9-step L1 ≥ 15 % below copy-last (300M) and ≥ 5 % below shuffled actions; 2-view encoder ≤ 200 ms on the Orin. | 11.8 % below copy-last (300M; 1B 15.8 % on 30 clips); 9–10 % below shuffled; encoder 526 ms on the Orin NX | fail |
| H-JEPA [arXiv:2610.06805] | sim | A slow second level makes latent distance track task progress. | Progress monotonicity Spearman ρ ≤ −0.80; false stalls ≤ 10 %. | level-2 ρ −0.73; false stalls 52 % | fail |
| D-JEPA [arXiv:2609.24749] | <$5k | A decision-aligned ranking operator on a frozen world model picks better action chunks. | G1b regret ≤ 0.10 and ≤ the action-only baseline + 0.05. | regret 0.263 (W1 alone 0.263; action-only −0.007) | not tested |
| ContactGuard [arXiv:2608.13438] | $5–20k | An event-anchored probe on imagined latents predicts grasp failure better than the current latent. | AUROC ≥ 0.85 and ≥ 0.05 above the current latent. | 0.70 imagined vs 0.82 current | fail |
| FAIL-Detect and SAFE [arXiv:2503.08558] [arXiv:2506.09937] | >$20k | A conformal band on a learned failure score keeps false alarms at α while catching failures. | Successes flagged ≤ 1/20; failures flagged ≥ 50 %. | 22.7 % of successes flagged at α = 5 %; 46 % of failures caught | fail |
| ReAP [arXiv:2610.16309] | $5–20k | A risk head on an action-conditioned latent warns before failures. | ≥ 5/8 failures caught at ≤ 1/20 false interventions; action-conditioned iff true ≥ shuffled + 0.05. | v1 AUROC 0.93 came from time and length; v2 0.789 vs 0.708 shuffled, 3/8 at 5/42 | fail |
| VLA-Corrector [arXiv:2609.06508] | sim | A verifier on observable history flags a failing rollout early enough to correct it. | ≥ 5/8 failures at ≤ 1/20 false interventions. | the paper's verifier family on our rollouts (a GRU on pooled RGB statistics and actions): 2/8 caught at 3/42 false interventions, AUROC 0.59; cosine drift of the W1 latent 0/8, AUROC 0.30 | fail |
| Robometer [arXiv:2603.02115] | >$20k | A 4B reward model judges SO-101 rollouts zero-shot. | Pooled AUROC ≥ 0.85 and within-policy ≥ 0.8 on ≥ 5 of 7 policies. | pooled AUROC 0.818 on 2099 ArmnetBench rollouts; episode length alone 0.938 | fail |
| SmolVLA [arXiv:2506.01844] | <$5k | A 450M VLA succeeds on an SO-101 task and can run on low-cost hardware. | 10-trial operator-judged gate (no numeric pass mark registered); chunk inference within the async budget (667 ms). | 9/10 on bowls; 974 ms in PyTorch, 238 ms with vla.cpp on the Orin NX | reproduces |
| TurboVLA [arXiv:2607.27205] | sim | Our claim that the architecture made the policy ignore its instruction. | Task swap ≥ 5° and per-layout ≥ 75 % → our port was the bug; < 1° with the control ≥ 0.095 → the data. | upstream's own trainer on our data: task swap 0.020°, per-layout 38.9 %; control, their released LIBERO checkpoint run here: 0.105 (≈ 5.5° of pan) | withdrawn |
| VLA-JEPA [arXiv:2602.10098] | sim | VLA-JEPA trains cheaply on SO-101 data and runs on the robot. | 10-trial operator-judged gate (no numeric pass mark registered); for reranking (H0): oracle / mean error ≤ ~0.7 and N = 8 ≤ 1.5× the latency. | 9/10 for ~$9.7; 355 ms per chunk on the Orin NX; reranking no-go (0.76, 1.84×) | reproduces |
| REKI [arXiv:2610.22178] | sim | Policies without memory oscillate between poses at a measurable rate. | ≥ 10 % of failed episodes oscillate (their criterion). | 20.3 % of all episodes, 24.0 % of failures; REKI trained on my data: 19/20 + 19/20 on the arm, oscillates in 1/40 | reproduces |
| Real-Time Chunking [arXiv:2506.07339] | unstated | Conditioning a new chunk on the executing one removes the jump at chunk boundaries. | Best gradient-free method cuts the median jump ≥ 50 % against naive async, drift ≤ +10 %, within 667 ms. | prefix overwrite cuts the jump 71–73 % against naive async at +0.4 ms; tuned LeRobot identity mode is close | not proven |
| HWM (hierarchical latent world models) [arXiv:2604.03208] | >$20k | A high-level world model over learned macro-actions beats the low-level model beyond about 1 s (their Fig. 6 crossover). | Crossover in [1.0, 2.0] s; at 2 s high-level error ≤ 0.95 × low-level; learned macro-actions ≥ net joint displacement on cosine. | no crossover: W1 0.382 ± 0.005 → 0.563 ± 0.007, high level 0.769 ± 0.009 → 0.759 ± 0.009 (0.73–2 s); cosine 0.608 ± 0.007 vs 0.551 ± 0.006 | not proven |
| LeJEPA identifiability [arXiv:2605.26379] | sim | A SIGReg JEPA trained on goal-directed data recovers the true latent state only partially and unevenly. | W1's mean R² from latent to joints < 0.80; anisotropy (max − min per-joint R²) ≥ 0.20; the higher-R² model has the higher G1b top-1. | W1 mean R² 0.565, anisotropy 0.639 (shoulder lift 0.91, wrist flex 0.27); frozen DINOv2-S 0.867 / 0.301 | reproduces |
| SURVEYOR | sim | A threshold on the imagined-vs-reached latent distance accepts good plans and rejects bad ones (τ = 0.20). | τ below the 10th percentile of non-equivalent pairs and ≤ 0.40; as a monitor ≥ 5/8 failures at ≤ 2/42; ≥ 0.05 AUROC over a shuffled drafter. | τ = 1.249 on W1 latents of 69 real rollouts; as a monitor 3/8 at 6/42 (S = 30), AUROC 0.756 vs shuffled 0.560 | fail |
| Adaptive Action Chunking (AAC) [arXiv:2604.04161] | >$20k | Chunk length chosen from the entropy of N sampled chunks follows the task's phases (long in transport, short at the grasp), lowers the boundary jump, and costs little with batched sampling. | median h* in transport ≥ grasp window + 2; jump with AAC + overwrite ≤ fixed + overwrite at d = 8; an N = 20 decision ≤ 298 ms on the Orin. | h* 2 in transport and 2 at the grasp (86 % of decisions at the floor); jump 0.973 vs 0.940; N = 20 decision 4,751 ms (sequential) on the Orin | fail |
| PACT-VLA [arXiv:2610.28019] | $5–20k | Picking among N sampled chunks by their flow residual under the pre-commit observation fits what happens next better than a random or stale pick, with no added control-step delay. | PACT beats a random pick and the stale-observation residual at d = 8 (CIs < 0); its delay on the Orin ≤ the naive delay; at that delay it still beats a single sample. | offline −0.27° vs random and vs the stale residual (both CIs < 0); on the Orin 1,200 ms per cycle, 37 control ticks vs 8 | fail |
| Horizon × depth (Euler steps vs execution horizon) [arXiv:2610.32102] | >$20k | With long open-loop commitment, cutting a flow-matching VLA's Euler steps from 10 to 2 contracts the action cloud around an unchanged centroid, saves most of the inference time and avoids edge-GPU thermal throttling. | median R(2)/R(10) ≤ 0.70 with the centroid within 0.05 relative and 3°; N = 2 latency ≤ 0.85 × N = 10 on the Orin, N = 10 within 5 % of 238 ms. | R(2)/R(10) 0.78 (CI 0.73–0.81), centroid 0.018 and 2.35°; 196.1 vs 237.5 ms per chunk (0.83, vision 151 ms); no throttling at N = 10 on the Orin, at MAXN_SUPER or 25 W | not proven |
| REMORA [arXiv:2610.39125] | >$20k | Reading a progress distribution out at the supported peak nearest the previous estimate steadies the estimate and lets it fall during real setbacks, with no worse detection of the stages. | Against per-frame argmax: premature not higher and missed ≤ +2 points (P1); flips halved, CI upper ≤ 0.7 (P2); a decrease inside ≥ 50 % of the reversal windows with ≤ 20 % false regressions (P3). | premature 0.22 vs 0.25, missed equal (P1 pass); flips 0.70 × argmax, CI 0.48–0.94 (P2 fail); setback recall 2/7, false 0.52 (P3 fail); MAE 0.184 vs median 0.218 | fail |
