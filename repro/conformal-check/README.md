# repro/conformal-check (WS-214)

Does the stored conformal band (C-007-1, C-007-2) match FAIL-Detect's and SAFE's? `NOTES.md` (written before any new
number) lists the differences, `PROTOCOL.md` (frozen before any number) the re-run. `series.json`: the W1 surprise series
of the 69 rollouts, recomputed by `extract_series.py` with the stored run's code (latents of that run, W1 `weights_final.pt`
in the `lerobot-jetson-wm:rc` image; the stored band replays the stored per-split values exactly). `conformal_check.py`
runs both bands; `expected/conformal_check.json` is its output; `l0_check.py` recomputes and compares.
