# Outline (from road-to-robotics journal/papers/reproducibility-study/FEASIBILITY.md §10)

## 10. Skeleton

Titles: (1) *What survives when a paper leaves the lab: re-testing 22 robot-learning papers on a ≈ €1,350 arm*;
(2) *Pre-registered re-tests of robot-learning claims on commodity hardware*; (3) *The cheapest baseline first: a
reproducibility study on an SO-101 and a Jetson*.

Abstract (≤ 150 words): Robot-learning papers are shown on Franka-class arms, data-centre GPUs or in simulation. We
re-tested the central claims of 22 papers on an SO-101 arm and a Jetson Orin NX (≈ €1,350), with the pass mark
committed before each run and the cheapest baseline run first. 4 papers reproduce, 13 fail, 3 are not proven
([to run]: commit-order check). The failures fall into three classes: models that do not meet a real-time budget on
the edge GPU, zero-shot judges beaten by episode length, and latent planners beaten by the commanded joints. Every bar
is recomputable from published rows (29 / 29 posts), and every runnable gate reproduces from the public repository
(6 / 6, [to run]: W1 environment for 12 more). Total compute: $45.

Sections: 1 Introduction (the transfer gap) · 2 Method (bar first, baseline first, register schema) · 3 The 22
papers (table) · 4 Three failure classes · 5 What the method itself revealed (contradiction pairs, the audit) · 6
Reproducibility of this study (L0 / L1) · 7 Limitations · 8 Conclusion.

Figures: (1) register table — `public/data/register.json` (today); (2) their rig cost class vs verdict — register
(today); (3) per-class examples: AAC 4,751 ms vs 298 ms budget (`expected/` of adaptive-chunking), Robometer vs
episode length 0.818 vs 0.938 (robometer post), G1b 0.60 vs 0.68–0.90 (leworldmodel post) — today; (4) the L1
reproducibility table — WS-067 `L1.md` (today; 12 rows `[to run]`).
