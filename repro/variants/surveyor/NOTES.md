# SURVEYOR monitor claim (C-018-2): can FF-JEPA's drafter be used? (WS-218, 2026-11-10)

Step 1 only, no number was computed. Answer: no, the drafter cannot be run as the authors' method. The row stays our variant.

## Is the code or a checkpoint released?

| Place checked | Result |
|---|---|
| Hugging Face paper page API for 2606.09311 | no GitHub repository, no project page listed |
| Hugging Face model and dataset search ("2606.09311", "ff-jepa", "ffjepa") | no hits |
| GitHub repository search ("FF-JEPA", "2606.09311") | only awesome-lists; no code from the authors (Masip, Swinnen, Hu, Detry, Tuytelaars) |
| The paper text (mirror `WorldModel/2606.09311v1-ffjepa.pdf`) | names no code link, no weights, and calls its results preliminary (Push-T only) |

What does exist is the base it builds on: LeWM (`lucas-maes/le-wm`, `galilai-group/stable-worldmodel`), which has training code for the 18 M parameter encoder and predictor, but not the latent planner.

## Could we reimplement it honestly offline?

| Item | Paper gives | Missing or mismatched |
|---|---|---|
| Diffusion planner | DiT backbone, 50.1 M parameters, epsilon-prediction loss, predicts N = 3 subgoals, context 1, horizon H = 25, 20 epochs, "similar to Xie et al." | depth, width, heads, number of denoising steps K, noise schedule, learning rate, batch size, conditioning details, optimizer |
| World model under it | frozen LeWM encoder, trained on Push-T demonstrations | no LeWM exists for the SO-101 camera; it would have to be trained by us first, with a recipe the paper does not restate |
| Data | 8318 successful Push-T episodes (200 in the ablation) | our teleop set `ravediamond/so101_bowls_all_trimmed` has 182 episodes, 61462 frames at 30 fps, 2.1 GB (too large for the 1.5 GB download cap on this disk, 4.7 GB free) |
| Compute | 157320 training iterations for the full run, RTX 5070 Ti | Orin share capped at 8 GB; feasible only for a much smaller model |

Two layers of our own choices (a LeWM trained on our images and a DiT with guessed sizes) would sit between the authors' paper and any number. A rerun would therefore measure our reimplementation, not FF-JEPA, and could not move the claim or the paper to the authors' tier under the rule of the prompt. The paper is also a Push-T result with a goal-free planner; whether its subgoal drafter transfers to SURVEYOR's plan-consumption setting is not something the authors report.

## Decision

Stop at Step 1. No PROTOCOL.md was written because no run follows. C-018-2 keeps: verdict fail (3/8 at 6/42 against the bar of at least 5/8 at no more than 2/42), tier our variant (W1's own imagination as drafter). Reason: the authors' drafter is not released and is under-specified for an honest reimplementation. The Section 7 variant paragraph already states "their drafter not released"; no fact changed, so the paper text is untouched. Revisit if the authors publish code or weights.
