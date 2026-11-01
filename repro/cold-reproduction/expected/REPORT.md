# WS-067 · Reproducing every published post cold — report (2026-10-31)

A stranger's setup: a fresh clone of the public `ravediamond/paper-vs-hardware` (@ `a83fcc9`, 29 folders), the public
Hub with no token, the published container `ghcr.io/ravediamond/lerobot-jetson:public`, one Orin NX 16 GB at 25 W.
Details: `INVENTORY.md`, `L0.md`, `L1.md`. Fixes: branch `repro-2026-10-31` of `paper-vs-hardware` (8 commits, not
merged).

| # | post | L0 | L1 | fixed on the branch | content finding | not reproducible on the rig, why |
|---|---|---|---|---|---|---|
| 1 | 09-09 lerobot-jetson-container | PASS (nothing numeric) | REPRO | — | — | — |
| 2 | 09-29 three-policies-so101 | PASS | — | — | — | arm (L2) |
| 3 | 10-06 twelve-vlas-orin | PASS | SKIP | — | — | MAXN (owner); GGUFs unpinned |
| 4 | 10-12 act-vlacpp-port | PASS | SKIP | — | — | ACT checkpoint private |
| 5 | 10-14 g6-progress-latents | PASS | FAIL-ENV | — | — | W1 env unpublished; `--help` only |
| 6 | 10-17 g10-outcome-readout | PASS | FAIL-ENV | — | — | W1 env; `--help` only |
| 7 | 10-19 six-monitors-w1 | PASS | FAIL-ENV | — | — | W1 env; G15 / G16-B / tau need an API key |
| 8 | 10-20 flora-rewarder | PASS | SKIP | — | — | ≥ 80 GB GPU (vast) |
| 9 | 10-22 voided-gates | PASS | FAIL-ENV + FAIL-SCRIPT | — | — | W1 env; weights path hard-coded as a placeholder |
| 10 | 10-23 contactguard | PASS | FAIL-ENV | — | — | W1 env |
| 11 | 10-23 dino-wm | PASS | FAIL-ENV | — | — | W1 env; `--help` only |
| 12 | 10-23 d-jepa | PASS | FAIL-ENV | — | — | W1 env; `--help` only |
| 13 | 10-23 leworldmodel | PASS | FAIL-ENV | — | — | W1 env; `--help` only |
| 14 | 10-23 reap | PASS | FAIL-ENV | — | — | W1 env; `--help` only |
| 15 | 10-23 reki | PASS | REPRO | full L1 command | — | — |
| 16 | 10-23 robojepa | PASS | SKIP | — | — | gate A on an A100; gate B time unstated |
| 17 | 10-23 robometer | PASS | REPRO (judge) | — | — | Robometer scoring ≥ 48 GB |
| 18 | 10-23 smolvla | PASS | — | — | — | arm (L2) |
| 19 | 10-23 turbovla | PASS | SKIP | — | — | unstated; upstream code + unnamed val cache |
| 20 | 10-23 vla-jepa | PASS | SKIP | — | — | checkpoint private |
| 21 | 10-25 vla-chunk-boundary-jumps | PASS | SKIP | — | — | unstated; vla.cpp fork build; imports `so101_harness` |
| 22 | 10-26 vla-jepa-rope-compat | PASS | SKIP | — | — | checkpoint private |
| 23 | 10-28 hwm | PASS | FAIL-ENV + FAIL-FILE | — | — | W1 env; H.264 224 data copy unpublished |
| 24 | 10-29 lejepa | PASS | FAIL-ENV | — | — | W1 env |
| 25 | 10-29 surveyor | PASS | FAIL-ENV | — | — | W1 env |
| 26 | 10-29 vla-jepa-surprise-robot-day | PASS | — | — | — | arm (L2) |
| 27 | 10-30 adaptive-chunking | PASS | REPRO (gate 0) | `so101_harness.episodes` + G13b list; time | — | gate 1 MAXN |
| 28 | 10-30 horizon-depth | PASS | REPRO (A1, byte-identical) | same; A1 time ~40 → ~80 min | — | A2, A4 MAXN |
| 29 | 10-30 pact | PASS | REPRO (gate B, identical) | same; the gate B scorer (`pact_score.py`); checks at k = 8 | — | gate A MAXN |

**Counts.** L0: 29 PASS / 0 FAIL. L1: 6 REPRO (5 exact, 1 identical but one timing at 0.2 %), 0 DIFF, 12 FAIL-ENV
(one cause), 11 SKIP (3 MAXN-only, 3 private checkpoints, 2 vast, 3 unstated) — 3 of the 29 have no L1 (arm only)
and are counted in SKIP. GPU: ≈ 5.5 h of the 36 h budget. **Content findings: none** (no FAIL-NUMBER, no DIFF).

## Generic fixes proposed (one commit each, not made: they need the owner)

1. **Publish the W1 environment** (unblocks 12 posts): a `rig/w1/Dockerfile` `FROM ghcr.io/ravediamond/lerobot-jetson:public`
   adding `stable-worldmodel @ 21446f1`, `stable-pretraining==0.1.8`, `transformers==5.19.0` (the layer the local
   `lerobot-jetson-wm` image adds), plus a standalone `rig/w1/w1_load.py` (`W1LiveMonitor.from_checkpoint`'s 20 lines:
   hydra-instantiate from the checkpoint config, strict load), and the W1 scripts importing it instead of
   `so101_harness` / `agent.*`. Publishing the image to ghcr is the owner's call (28 GB).
2. **One shared `rig/so101_harness/episodes.py`** instead of a copy per folder (four folders import it: the three
   SmolVLA posts fixed here, and chunk-boundary).
3. **Name the image tag in every REPRODUCE:** the SmolVLA numbers were produced in local `lerobot-jetson:rc`, which is
   not on ghcr (`:latest` and `:public` share a digest); `:public` reproduces them exactly, so name `:public`.
4. **Replace the six `--help`-only L1 lines with full commands** and a stated wall-clock, measured.
5. **voided-gates:** take the weights path from `argv` instead of the placeholder string.

## Not reproducible on this rig, by cause

MAXN (owner's sudo): twelve-vlas, the latency halves of horizon-depth, adaptive-chunking, pact. vast-class GPU:
flora-rewarder, robojepa gate A, robometer scoring. Private checkpoints: act-vlacpp-port, vla-jepa, rope-compat. Arm:
three-policies, smolvla, robot day.
