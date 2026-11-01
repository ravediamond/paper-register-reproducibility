# WS-067 · Inventory (step 0, before any run)

Fresh clone of `ravediamond/paper-vs-hardware` @ `a83fcc9` in `~/workspace/pvh-repro-2026-10-31/`; 29 folders under
`posts/`. Read from each folder's `REPRODUCE.md` and `env/`. L0 = `python3 l0_check.py`; every `env/requirements.txt`
is empty except two (`numpy>=1.26`), and every `l0_check.py` imports only the standard library (+ numpy in those two).

Missing pieces: `2026-09-09-lerobot-jetson-container` has no `expected/` (its L0 checks the build guide, nothing
numeric); `2026-10-12-act-vlacpp-port` and `2026-10-20-flora-rewarder-input-format` have no `scripts/` (code lives
upstream / needs an 80 GB GPU).

| # | post | L1 promised | env / where | Hub artefacts (rev) | stated L1 time | vast / MAXN / container | L2 |
|---|---|---|---|---|---|---|---|
| 1 | 09-09 lerobot-jetson-container | build the image, `torch.cuda.is_available()` | JetPack 6.2, `ghcr.io/ravediamond/lerobot-jetson:public` | — | unstated (image build: hours) | container | robot protocol, not re-verified |
| 2 | 09-29 three-policies-so101 | none (arm trials) | numpy | — | — | — | arm |
| 3 | 10-06 twelve-vlas-orin | `bench_chain.sh` | vla.cpp `f7e0f7f` era, sm_87 | GGUFs from `vrfai` (no rev) | unstated | MAXN | — |
| 4 | 10-12 act-vlacpp-port | upstream parity check | vla.cpp `65d16f5` | `act_2026-09-24_12-19-31` **private** | unstated | — | — |
| 5 | 10-14 g6-progress-latents | `g6a.py`, `g6b_eval.py` (`--help` only) | — | `lewm-w2-so101-bowls`, `so101_bowls_all_trimmed` @ `4e5c6fda` | unstated | — | — |
| 6 | 10-17 g10-outcome-readout | `g10_eval.py` (`--help`) | — | W1 / W2′, rollouts @ `bad1c8ea` | unstated | — | — |
| 7 | 10-19 six-monitors-w1 | `run_w1_offline_screening.py`; G15 / G16-B / tau need an API key | — | W1, rollouts @ `bad1c8ea` | unstated | — | — |
| 8 | 10-20 flora-rewarder-input-format | none here (≥ 80 GB GPU + API) | — | Flora-Rewarder-27B | — | **vast** | — |
| 9 | 10-22 voided-gates | `strict_load_log.py` under transformers 5.5.4 and 5.19.0 | container | W1 | unstated | container | — |
| 10 | 10-23 contactguard | `run_w1_offline_screening.py`, `run_w1c_offline.py` | container + transformers 5.19.0 | W1, rollouts @ `bad1c8ea` | unstated | container | — |
| 11 | 10-23 dino-wm | `g1_suite.py` (`--help`) | — | W2′ (`w2prime/`), DINOv2-S | unstated | — | — |
| 12 | 10-23 d-jepa | `djepa_operator.py` (`--help`) | — | W1, data @ `4e5c6fda` | unstated | — | — |
| 13 | 10-23 leworldmodel | `eval_action_sensitivity.py`, `g1b_range.py` (`--help`) | container, transformers 5.19.0 | W1 @ `d0336db6`, data @ `4e5c6fda` | unstated | container | — |
| 14 | 10-23 reap | `run_reap_v2.py` (`--help`) | container + 5.19.0 | W1, rollouts @ `bad1c8ea` | unstated | container | — |
| 15 | 10-23 reki | `run_g14_oscillation_audit.py` (`--help`), CPU | — | rollouts @ `bad1c8ea` | "minutes" (CPU) | — | — |
| 16 | 10-23 robojepa | gate B `bench_orin.py`; gate A needs an A100 | — | RoboJEPA upstream (no rev) | unstated | gate A **vast** | — |
| 17 | 10-23 robometer | judge `g9c3_test.py` (full command, expected result stated); Robometer needs ≥ 48 GB | CPU | rollouts @ `bad1c8ea` | **~3 min** (CPU; 177.7 s on 2026-10-26) | scoring **vast** | — |
| 18 | 10-23 smolvla | none (ticks are L0; re-timing is L2) | — | — | — | — | arm |
| 19 | 10-23 turbovla | `gate_upstream.py` | upstream TurboVLA `a3365e8`, transformers 4.56.2, CUDA | `turbovla_…_patha` @ `68ecb75d`; "a validation cache" (not named) | unstated | — | — |
| 20 | 10-23 vla-jepa | `sample_diversity.py`, `latency.py` | container | `vla_jepa_so101_bowls_trimmed` @ `c65c98bb` **private**, 61.6 GB | unstated | — | — |
| 21 | 10-25 vla-chunk-boundary-jumps | `check_vlacpp_prefix_overwrite.py` (full command) | vla.cpp fork `805570d`, CUDA | SmolVLA @ `c1d76f62` → GGUF, data @ `f98902…` | unstated | — | — |
| 22 | 10-26 vla-jepa-rope-compat | `eval_rope_compat.py compare` | lerobot `d3793b7` vs `2e88044` | VLA-JEPA ckpt **private** | ~10 min | — | — |
| 23 | 10-28 hwm | `hwm_extract.py` (~20 min Orin) + `hwm_train.py` (~25 min RTX 3090) | W1 container | W1, `so101-bowls-h264-224` | **~45 min** | container | n/a |
| 24 | 10-29 lejepa | `gate0_extract.py`, `gate0_analyze.py` | W1 container | W1 @ `d0336db6`, data @ `4e5c6fda` | unstated | container | gate 1 not run |
| 25 | 10-29 surveyor | judge + `surveyor_gate0/imagine/gate1.py` (numpy) | W1 | W1 @ `d0336db6`, rollouts | unstated | — | n/a |
| 26 | 10-29 vla-jepa-surprise-robot-day | session script (arm) + frozen scorer (not run: no failures) | — | — | — | — | arm |
| 27 | 10-30 adaptive-chunking | gate 0 `aac_gate0.py` (~3 h, 25 W); gate 1 `aac_latency.py` (~5 min, MAXN) | container + vla.cpp | SmolVLA @ `c1d76f6`, `so101_bowls_all` | **~3 h 5 min** | MAXN (gate 1), container | n/a |
| 28 | 10-30 horizon-depth | A1 `hd_cloud.py` (~40 min, 25 W); A2 / A4 `hd_latency.py`, `hd_thermal.py` (MAXN) | container + vla.cpp | SmolVLA @ `c1d76f6`, `so101_bowls_all` | **~40 min + A2/A4 unstated** | MAXN (A2, A4), container | n/a |
| 29 | 10-30 pact | gate B `pact_flowres.py` ("a few hours", 25 W); gate A latency (MAXN) | container + vla.cpp | SmolVLA @ `c1d76f6`, `so101_bowls_all` | **"a few hours"** | MAXN (gate A), container | n/a |

**Stated L1 hours:** robometer 0.05 + reki ~0.1 + rope-compat 0.17 (private: skip) + hwm 0.75 + adaptive-chunking
3.1 + horizon-depth A1 0.67 + pact "a few" (~3) ≈ **7.8 h stated**, the rest unstated. Not reproducible on the
rig: flora-rewarder (80 GB GPU), robojepa gate A (A100), robometer scoring (48 GB), the four arm posts (2, 18, 26, and
the robot halves). Blocked by private artefacts: 4 (ACT checkpoint), 20 and 22 (VLA-JEPA checkpoint).
Seven posts' L1 is a `--help` pointer (5, 6, 11, 12, 13, 14, 15): a stranger has no full command for them.
