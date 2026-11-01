# WS-078 · Pre-registration check: bar commit vs result commit, every gate (2026-10-31)

Source: `journal/EXPERIMENTS.md`, every dated row of §1 (arm gates, 8) and §2 (gates, 81) = **89 rows** (the site's
count of 85 uses the site's gate rule on its own copy of the log). Built by `prereg_check.py` (git history of this
repo, 732 commits) and `prereg_table.py`. **No verdict is edited; this table is the finding.**

**Bar commit** = the earliest of: the pre-registration hash cited in the row; the first commit adding a protocol file
the row names (or the row's project `PROTOCOL.md`); the first commit adding the gate to §3 "Pending gates"; the
first commit containing the bar text. **Result commit** = the first commit containing the result text.

| class | rows | meaning |
|---|---|---|
| bar-first | 36 | the bar's commit is an ancestor of the result's commit |
| same-commit | 31 | bar and result first appear in the same commit — 11 of them in `5fc1779` (2026-10-16), the commit that created this log from earlier notes; the bar may predate it elsewhere (research notes, the old Mac), unverifiable from this repo |
| result-first | 0 | the result was committed before the bar |
| no-bar | 19 | §1 arm rows (10-trial operator-judged runs, no bar column) and rows with no bar (`—`, measured only) |
| unresolved | 3 | the text was not found by git (H3 plan and G1b-RJ never ran; RoboJEPA Gate B′ bar not found) |

**No row is result-first.**

## Per register paper

| # | paper | gates | classes | flag |
|---|---|---|---|---|
| 1 | LeWorldModel | 3 | bar-first 2, same-commit 1 | early (2026-10-23): **not shown bar-first** |
| 2 | DINO-WM | 3 | bar-first 2, same-commit 1 | early (2026-10-23): **not shown bar-first** |
| 3 | RoboJEPA | 3 | same-commit 2, unresolved 1 | early (2026-10-23): **not shown bar-first** |
| 4 | H-JEPA | 2 | same-commit 2 | early (2026-10-23): **not shown bar-first** |
| 5 | D-JEPA | 1 | bar-first 1 | early (2026-10-23): all bars before results |
| 6 | ContactGuard | 1 | bar-first 1 | early (2026-10-23): all bars before results |
| 7 | FAIL-Detect and SAFE | 1 | bar-first 1 | early (2026-10-23): all bars before results |
| 8 | ReAP | 2 | bar-first 2 | early (2026-10-23): all bars before results |
| 9 | VLA-Corrector | 2 | bar-first 2 | early (2026-10-23): all bars before results |
| 10 | Robometer | 4 | bar-first 1, same-commit 3 | early (2026-10-23): **not shown bar-first** |
| 11 | SmolVLA | 5 | no-bar 4, same-commit 1 | early (2026-10-23): **not shown bar-first** |
| 12 | TurboVLA | 2 | bar-first 2 | early (2026-10-23): all bars before results |
| 13 | VLA-JEPA | 2 | no-bar 1, same-commit 1 | early (2026-10-23): **not shown bar-first** |
| 14 | REKI | 1 | same-commit 1 | early (2026-10-23): **not shown bar-first** |
| 15 | Real-Time Chunking | 2 | same-commit 2 | early (2026-10-23): **not shown bar-first** |
| 16 | HWM | 1 | bar-first 1 |  |
| 17 | LeJEPA identifiability | 2 | bar-first 2 |  |
| 18 | SURVEYOR | 2 | bar-first 2 |  |
| 19 | AAC | 2 | bar-first 2 |  |
| 20 | PACT-VLA | 2 | bar-first 2 |  |
| 21 | Horizon × depth | 2 | bar-first 2 |  |
| 22 | REMORA | 1 | bar-first 1 |  |

## All rows

| § | date | gate | bar commit (how) | result commit | class | verdict |
|---|---|---|---|---|---|---|
| 1 | 2026-09-29 | ACT | —  (no bar) | —  | no-bar | works |
| 1 | 2026-09-29 | SmolVLA (PyTorch) | —  (no bar) | —  | no-bar | works |
| 1 | 2026-09-29 | ACT | —  (no bar) | —  | no-bar | works |
| 1 | 2026-09-29 | SmolVLA (PyTorch) | —  (no bar) | —  | no-bar | works, slow |
| 1 | 2026-10-01 | SmolVLA via vla.cpp | —  (no bar) | —  | no-bar | works |
| 1 | 2026-10-01 | SmolVLA via vla.cpp _fa | —  (no bar) | —  | no-bar | works |
| 1 | 2026-09-29 to 10-08 | TurboVLA (several variants) | —  (no bar) | 5fc1779 2026-10-16T09:34 | no-bar | closed: ignores the instruction on the t |
| 1 | 2026-10-08 | VLA-JEPA (Qwen3-VL-2B + DiT-B, world model off at inference) | —  (no bar) | —  | no-bar | works |
| 2 | 2026-10-08 | H0 | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | no-go |
| 2 | 2026-10-08 | H3 plan | 5fc1779 2026-10-16T09:34 (pickaxe) | —  | unresolved | superseded 2026-10-11 by C1 |
| 2 | 2026-10-08 | LeWM env | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | pass |
| 2 | 2026-10-09 | MV 5-epoch | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | weak (too short) |
| 2 | 2026-10-10 | Action corruption | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | weak at 5 epochs |
| 2 | 2026-10-11 | G0 | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | pass |
| 2 | 2026-10-11 | C1 probe | 500e37a 2026-10-10T08:53 (protocol file PROBE_PROTOCOL.md) | 5fc1779 2026-10-16T09:34 | bar-first | not proven (data confounded with policy) |
| 2 | 2026-10-12 | G1b W1 | 572fa06 2026-10-12T10:20 (protocol file G1_PROTOCOL.md) | 5fc1779 2026-10-16T09:34 | bar-first | fail |
| 2 | 2026-10-12 | G1 probes | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | W2 pass on this item |
| 2 | 2026-10-12 | G2 (Mac) | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | W1 ok, W2 too slow |
| 2 | 2026-10-12 | G1 W2 dynamics | 572fa06 2026-10-12T10:20 (protocol file G1_PROTOCOL.md) | 5fc1779 2026-10-16T09:34 | bar-first | fail, so W3 not run |
| 2 | 2026-10-12/13 | G1 diagnosis | 572fa06 2026-10-12T10:20 (protocol file G1_PROTOCOL.md) | 5fc1779 2026-10-16T09:34 | bar-first | G1b measured kinematics, not world-model |
| 2 | 2026-10-12 | BotFails | 44fe22f 2026-10-12T12:14 (protocol file BOTFAILS_PROTOCOL.md) | 5fc1779 2026-10-16T09:34 | bar-first | parked until G1 picks a winner |
| 2 | 2026-10-13 | RoboJEPA Gate B | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | no-go on device; world model goes off-bo |
| 2 | 2026-10-13 | RoboJEPA Gate B' | —  (pickaxe) | 5fc1779 2026-10-16T09:34 | unresolved | no-go; off-board host must be CUDA |
| 2 | 2026-10-13 | RoboJEPA Gate A | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | no-go for the primary; 1B borderline on  |
| 2 | 2026-10-14 | G1b-RJ | 96043cd 2026-10-14T16:32 (protocol file G1B_RJ_PROTOCOL.md) | —  | unresolved | cancelled as a gate 2026-10-15 (neither  |
| 2 | 2026-10-14 | G6a | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | done detector: unadopted sanity pass; st |
| 2 | 2026-10-15/16 | G9a-AB | 5fc1779 2026-10-16T09:34 (pickaxe) | 5fc1779 2026-10-16T09:34 | same-commit | qualified pass (top camera, calibrated t |
| 2 | 2026-10-16 | G9a-AB complete (re-score of the 462 OOM episodes, top view, A6000 48  | f8b6120 2026-10-16T12:29 (pickaxe) | f8b6120 2026-10-16T12:29 | same-commit | fail: not a zero-shot judge |
| 2 | 2026-10-16 | G9a-own (zero-shot baseline) | 873af0c 2026-10-16T15:30 (pickaxe) | 873af0c 2026-10-16T15:30 | same-commit | fail (baseline for a LoRA on own data).  |
| 2 | 2026-10-16 | G9c | 6395c2c 2026-10-16T16:10 (§3 pending entry) | 6395c2c 2026-10-16T16:10 | same-commit | fail (pre-registered); exploratory pass  |
| 2 | 2026-10-16 | G9c-2 | 6395c2c 2026-10-16T16:10 (§3 pending entry) | 229ffd3 2026-10-17T21:41 | bar-first | fail (too many invalid) |
| 2 | 2026-10-16 | G9c-3 | 229ffd3 2026-10-17T21:41 (pickaxe) | 229ffd3 2026-10-17T21:41 | same-commit | narrow fail / operational pass |
| 2 | 2026-10-17 | G10 | 229ffd3 2026-10-17T21:41 (pickaxe) | 229ffd3 2026-10-17T21:41 | same-commit | PASS; world model acts as pre-execution  |
| 2 | 2026-10-18 | G6b | 77a562e 2026-10-18T08:47 (pickaxe) | 77a562e 2026-10-18T08:47 | same-commit | FAIL |
| 2 | 2026-10-18 | G11 (Phase A) | 77a562e 2026-10-18T08:47 (pickaxe) | 77a562e 2026-10-18T08:47 | same-commit | PASS (Phase A); Phase B (live perturbati |
| 2 | 2026-10-18 | G11-A re-check | —  (no bar) | 3823989 2026-10-18T18:48 | no-bar | timing valid, latents void |
| 2 | 2026-10-18 | G12 | 77a562e 2026-10-18T08:47 (pickaxe) | 77a562e 2026-10-18T08:47 | same-commit | FAIL |
| 2 | 2026-10-18 | G12 re-check | —  (no bar) | 8f965a6 2026-10-18T17:22 | no-bar | G12 void: REKI on the Orin is unmeasured |
| 2 | 2026-10-18 | G14 | dd76bf1 2026-10-18T18:41 (pickaxe) | dd76bf1 2026-10-18T18:41 | same-commit | pass: registers stay (gated tier) |
| 2 | 2026-10-18 | W1 still-scene noise floor (no arm) | —  (no bar) | dd76bf1 2026-10-18T18:41 | no-bar | measured (load only) |
| 2 | 2026-10-18 | W1 timing next to vla.cpp (no arm) | —  (no bar) | dd76bf1 2026-10-18T18:41 | no-bar | not run |
| 2 | 2026-10-18 | G13a timing part (no arm) | —  (no bar) | dd76bf1 2026-10-18T18:41 | no-bar | not run |
| 2 | 2026-10-19 | G13b (offline + timing) | 38daaf7 2026-10-19T12:20 (pickaxe) | 38daaf7 2026-10-19T12:20 | same-commit | propose 1+2 (gradient-free); exact not w |
| 2 | 2026-10-19 | G15 | 38daaf7 2026-10-19T12:20 (pickaxe) | 38daaf7 2026-10-19T12:20 | same-commit | fail → stage changes on the judge at res |
| 2 | 2026-10-19 | Judge τ (for G16) | 38daaf7 2026-10-19T12:20 (pickaxe) | 38daaf7 2026-10-19T12:20 | same-commit | fitted, judge not usable for G16 as is |
| 2 | 2026-10-19 | G16-B | aeb99e5 2026-10-19T12:39 (cited hash) | 1da325a 2026-10-19T12:57 | bar-first | fail → drop the VLM judge from v1.0; G16 |
| 2 | 2026-10-19 | G13b part 1+2 in vla.cpp | 8559829 2026-10-19T13:20 (pickaxe) | 8559829 2026-10-19T13:20 | same-commit | pass (feasible at vla.cpp speed); robot  |
| 2 | 2026-10-19 | G15-v2 dev fit | 75f81bf 2026-10-19T13:49 (pickaxe) | 75f81bf 2026-10-19T13:49 | same-commit | design unusable on this gripper/object;  |
| 2 | 2026-10-19 | W1-A (screening) | 37497f0 2026-10-19T13:26 (cited hash) | 75f81bf 2026-10-19T13:49 | bar-first | fail → W1 stays a reflex; G11-B's 2.2 /  |
| 2 | 2026-10-19 | W1-B (screening) | 37497f0 2026-10-19T13:26 (cited hash) | 75f81bf 2026-10-19T13:49 | bar-first | fail (better than G15's 48.5 / 46.7) |
| 2 | 2026-10-19 | G11-B-cal (offline) | 1ae071d 2026-10-19T13:54 (cited hash) | 156eb30 2026-10-19T14:07 | bar-first | fail → W1 reflex in shadow mode on robot |
| 2 | 2026-10-19 | G15-v3 fit (S, D) | e522896 2026-10-19T18:16 (pickaxe) | e522896 2026-10-19T18:16 | same-commit | params committed, θ_c pending |
| 2 | 2026-10-19 | W1-C1 (offline) | 2bcd2ff 2026-10-19T18:35 (cited hash) | 83ca81a 2026-10-19T18:49 | bar-first | fail → W1 stays a logged signal |
| 2 | 2026-10-19 | W1-C2 (offline) | 2bcd2ff 2026-10-19T18:35 (cited hash) | 83ca81a 2026-10-19T18:49 | bar-first | fail → shadow mode stays; registered ban |
| 2 | 2026-10-20 | G-flora (offline, Vast.ai) | 1c50a5d 2026-10-20T21:09 (cited hash) | d7c981e 2026-10-20T21:52 | bar-first | pass → write-up and a proposal (new gate |
| 2 | 2026-10-20 | G-flora-abl (offline, Vast.ai + API) | 80c0fe8 2026-10-20T22:06 (cited hash) | c92ab01 2026-10-20T23:40 | bar-first | A pass, B fail, C fail → §10: "Flora's f |
| 2 | 2026-10-16 (written 10-22) | G9b (vast 56253837) | 694a331 2026-10-16T12:50 (protocol file G9B_PROTOCOL.md) | a55f070 2026-10-22T19:31 | bar-first | not run: no verdict (zero-shot baseline  |
| 2 | 2026-10-22 | W1-R (NEXT_ANGLES §1, D-JEPA operator on frozen W1) | 902e8b1 2026-10-22T19:36 (protocol file D_JEPA_PROTOCOL.md) | 5676474 2026-10-22T20:28 | bar-first | fail; does not test D-JEPA's claim (no e |
| 2 | 2026-10-22 | TurboVLA faithful, step 1: LIBERO-Goal control (NEXT_ANGLES §15) | 27e27c6 2026-10-22T20:14 (cited hash) | 7c4ff32 2026-10-22T20:35 | bar-first | control ≥ line (small margin); four port |
| 2 | 2026-10-22 | 21-task SmolVLA via vla.cpp: parity (for §6) | c0f1b0d 2026-10-22T21:17 (pickaxe) | c0f1b0d 2026-10-22T21:17 | same-commit | pass (outlier reported); served with --m |
| 2 | 2026-10-22 | REAP step 4: monitor latency (NEXT_ANGLES §2) | —  (no bar) | c0f1b0d 2026-10-22T21:17 | no-bar | measured; the monitor comparison waits f |
| 2 | 2026-10-23 | Failure onsets, 25 failed published rollouts (VLM, deviation) | —  (no bar) | 6100e80 2026-10-23T09:22 | no-bar | labels in use, bias disclosed |
| 2 | 2026-10-23 | REAP monitors (NEXT_ANGLES §2) | 75f81bf 2026-10-19T13:49 (pickaxe) | 6100e80 2026-10-23T09:22 | bar-first | not proven pending the onset check (ep 1 |
| 2 | 2026-10-23 | W2′ (W2 re-trained, weights lost) | 6100e80 2026-10-23T09:22 (§3 pending entry) | 65ef27a 2026-10-23T13:01 | bar-first | reproduced; replaces W2 in G7 (deviation |
| 2 | 2026-10-23 | TurboVLA faithful, path A (NEXT_ANGLES §15) | 27e27c6 2026-10-22T20:14 (cited hash) | 2d54055 2026-10-23T18:01 | bar-first | fact 7 is the full story: the paper's re |
| 2 | 2026-10-23 | TurboVLA correction (NEXT_ANGLES §15 amendment; no new run) | —  (no bar) | fdda187 2026-10-23T18:49 | no-bar | corrected: data claim stands, port claim |
| 2 | 2026-10-23 | Verifier cards (NEXT_ANGLES §22; rule, no run) | —  (no bar) | bdac79f 2026-10-23T18:52 | no-bar | cards filled |
| 2 | 2026-10-23 | REAP v2 (NEXT_ANGLES §2 amendment) | c0f1b0d 2026-10-22T21:17 (§3 pending entry) | accd99d 2026-10-23T19:35 | bar-first | fail (no monitor at the bar); both W1 he |
| 2 | 2026-10-23 | vla.cpp determinism (NEXT_ANGLES §20, offline level) | —  (no bar) | b3f7b3a 2026-10-23T20:20 | no-bar | deterministic: the engine adds no noise; |
| 2 | 2026-10-23 | Wrist blank, proxies (NEXT_ANGLES §18 step 1) | —  (no bar) | b3f7b3a 2026-10-23T20:20 | no-bar | measured: offline the wrist helps match  |
| 2 | 2026-10-27 | LeJEPA identifiability, gate 0 (WS-047, arXiv 2605.26379) | ad40675 2026-10-27T22:14 (cited hash) | a057f59 2026-10-27T22:52 | bar-first | B1–B3 met: anisotropic recovery as predi |
| 2 | 2026-10-27 | SURVEYOR τ, gate 0 (WS-050, NeurIPS 2026 workshop) | 02928b7 2026-10-27T22:53 (cited hash) | d1d83ac 2026-10-27T23:14 | bar-first | fail (S1, S2): no operating point; the s |
| 2 | 2026-10-27 | SURVEYOR accept rule, gate 1 (WS-050) | 02928b7 2026-10-27T22:53 (cited hash) | d1d83ac 2026-10-27T23:14 | bar-first | fail (S3 both S; S4 met at S = 30 only): |
| 2 | 2026-10-28 | LeJEPA identifiability, gate 0 — correction (WS-047) | ad40675 2026-10-27T22:14 (cited hash) | db5460d 2026-10-28T01:17 | bar-first | B1–B3 still met (verdict unchanged, numb |
| 2 | 2026-10-28 | HWM crossover, gate 0 (WS-051, CoRL 2026, arXiv 2604.03208) | 4643775 2026-10-27T22:24 (cited hash) | bb9f71c 2026-10-28T02:02 | bar-first | bars: H1 fail, H2 fail (ratio 1.35), H3  |
| 2 | 2026-10-29 | PRIME (2610.23769) | 1e5f028 2026-10-23T08:32 (protocol file PRIME_PROTOCOL.md) | e02e755 2026-10-29T10:16 | bar-first | void (the graph check failed; no rollout |
| 2 | 2026-10-25 | AW-0 Phase 1 (annotation, §31) | 071a01a 2026-10-26T01:48 (pickaxe) | 071a01a 2026-10-26T01:48 | same-commit | pass (gate 1) |
| 2 | 2026-10-26 | AW-0 Phase 2 (slice planner, §31) | 071a01a 2026-10-26T01:48 (pickaxe) | 071a01a 2026-10-26T01:48 | same-commit | fail (accuracy, latency); gate 2 → owner |
| 2 | 2026-10-26 | §30 inverse dynamics (pre-registered 35f4600) | c1eff06 2026-10-26T12:18 (pickaxe) | c1eff06 2026-10-26T12:18 | same-commit | NOT PROVEN (random-init control blocks;  |
| 2 | 2026-10-26 | REKI SO-101 frozen-VLM training (WS-025) | 265ae3c 2026-10-27T07:28 (pickaxe) | 265ae3c 2026-10-27T07:28 | same-commit | trained (no on-robot number yet) |
| 2 | 2026-10-29 | AAC, gate 0 (WS-049, CVPR 2026, arXiv 2604.04161) | 581a955 2026-10-27T23:16 (protocol file PROTOCOL.md) | 9a93340 2026-10-30T00:48 | bar-first | A1 fail, A3 fail |
| 2 | 2026-10-30 | AAC, gate 1 (WS-049) | 581a955 2026-10-27T23:16 (protocol file PROTOCOL.md) | 9a93340 2026-10-30T00:48 | bar-first | fail; WS-049 verdict fail |
| 2 | 2026-10-29 | PACT-VLA, gate B (WS-059, arXiv 2610.28019) | 0a79846 2026-10-29T08:26 (protocol file PROTOCOL.md) | 9a93340 2026-10-30T00:48 | bar-first | B-P1 pass, B-P2 pass |
| 2 | 2026-10-30 | PACT-VLA, gate A (WS-059) | 0a79846 2026-10-29T08:26 (protocol file PROTOCOL.md) | 9a93340 2026-10-30T00:48 | bar-first | fail; WS-059: replicates offline, does n |
| 2 | 2026-10-29 | Horizon × depth, A1 (WS-057, arXiv 2610.32102) | 0a79846 2026-10-29T08:26 (protocol file PROTOCOL.md) | 9a93340 2026-10-30T00:48 | bar-first | not proven |
| 2 | 2026-10-30 | Horizon × depth, A2 (WS-057) | 0a79846 2026-10-29T08:26 (protocol file PROTOCOL.md) | 9a93340 2026-10-30T00:48 | bar-first | pass |
| 2 | 2026-10-31 | REMORA readout (WS-065, arXiv 2610.39125) | 70de84a 2026-10-31T09:03 (protocol file PROTOCOL.md) | 1e50aa8 2026-10-31T12:42 | bar-first | P1 pass, P2 fail, P3 fail: not adopted |
| 2 | 2026-10-31 | Smooth MP chunking A1 (WS-064, arXiv 2610.39451) | 6f58d7b 2026-10-31T09:03 (protocol file PROTOCOL.md) | b23c364 2026-10-31T12:45 | bar-first | pass |
| 2 | 2026-10-31 | Smooth MP chunking A2 (WS-064) | 6f58d7b 2026-10-31T09:03 (protocol file PROTOCOL.md) | b23c364 2026-10-31T12:45 | bar-first | pass; gate B (arm, raw vs S3) next |
