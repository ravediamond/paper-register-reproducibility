# What survives when a paper leaves the lab: re-testing {{papers}} robot-learning papers on a €{{rig_eur}} rig, and auditing our own pre-registration

*Ravindu Somawansa, Shisso Robotics. Draft, not submitted.*

## Abstract

We re-tested the main claims of new robot-learning papers on an SO-101 arm with a Jetson Orin NX. The pieces cost €{{rig_eur}} and the compute ${{cost}}. Each re-test ran the cheapest baseline first, and its pass mark was committed before the run. Of the {{c_paper}} paper claims we tested, {{c_paper_repro}} were valid on our hardware. Three proposed classes cover the failures: edge latency (a method misses the real-time budget on the edge GPU), zero-shot judges (a judge loses to a trivial signal) and latent planners (a planner loses to the commanded joints). A blind second reader still has to confirm the classes. We also verified our own pre-registration by commit history. For most gates the order of bar and result can be read from the repository, and for some it cannot.

## 1. The register

Most of the {{papers}} papers in this study were shown on setups far from ours. {{rig_sim}} were shown in simulation and {{rig_gt20k}} on rigs above $20k. {{rig_lt5k}} used a setup under $5k, which is where our rig falls. The appendix table gives the rig of each paper, including the {{rig_5to20k}} in between and the {{rig_unstated}} that does not say. Our rig is an SO-101 arm and a Jetson Orin NX 16 GB.

The register grew out of our own write-ups. Each re-test on this rig was published with its data, and there are {{l0}} so far. This paper collects them in one table and audits how the table was kept.

Here is one entry. An adaptive chunking paper claims that choosing the chunk length from the entropy of sampled chunks follows the task's phases, long in transport and short at the grasp. On our edge GPU one such decision takes {{ex_a_ours}}. The budget is {{ex_a_bar}}. The entry records a fail on this rig. It says nothing about the method on the hardware it was shown on. Next to the verdict, the entry keeps the claim in the paper's words, our pass mark, our measurement and the published rows.

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

Table 1 gives the classes for the {{pr_rows}} gates logged by 2026-10-31. Most are bar-first and {{pr_result_first}} are result-first. A same-commit gate is one where bar and result entered the repository together. It says nothing about which was written first.

Table 1: Commit-order class of each gate. The audited column is the one the paper uses; the first pass is what text search alone gave on the same gates.

| class | first text pass | audited, 2026-10-31 | audited, today |
|---|---|---|---|
| bar-first | {{v1_bar_first}} | {{pr_bar_first}} | {{pt_bar_first}} |
| same-commit | {{v1_same_commit}} | {{pr_same_commit}} | {{pt_same_commit}} |
| result-first | — | {{pr_result_first}} | {{pt_result_first}} |
| no bar | {{v1_no_bar}} | {{pr_no_bar}} | {{pt_no_bar}} |
| bar, no result yet | — | {{pr_not_run}} | {{pt_not_run}} |
| unresolved | {{v1_unresolved}} | — | — |
| gates | {{pr_rows}} | {{pr_rows}} | {{pr_today}} |

Our first pass used text search and found {{v1_same_commit}} same-commit gates. The cause was batch logging. We traced each same-commit gate back to the earlier file that holds its bar. This moved {{sc_to_bf}} gates to bar-first and {{sc_to_nb}} to no-bar, because their bar cell declares none. {{sc_stay}} stayed same-commit. The audit table in the repository gives the evidence line for every move. We did not re-audit the gates that were already bar-first. One open candidate remains, the reward-model progress test of 2026-11-01. It is same-commit by text search, although its protocol (`{{top_protocol}}`) is older than the log commit.

The early gates mixed point estimates and different intervals. We recomputed {{rc_rows}} of them from stored rows with one statistic, the episode bootstrap ({{rc_resamples}} resamples, percentile 95 % CI). For {{rc_flips}} of them the bar falls inside the interval (Table 2). The colour judge is a {{acc_verdict}} on the point estimate, and its interval does not settle it. The false-intervention threshold was fitted to meet its rate, so that interval is only descriptive. The register keeps the pre-registered point verdicts and marks these three as fragile.

Table 2: The three gates whose verdict flips somewhere inside its 95 % interval.

| gate | n | estimate | 95 % CI | bar | point verdict |
|---|---|---|---|---|---|
| colour judge (no learning), accuracy | {{acc_n}} | {{acc_est}} % | {{acc_lo}}–{{acc_hi}} % | ≥ {{acc_bar}} % | {{acc_verdict}} |
| oscillation among failed episodes | {{osc_n}} | {{osc_est}} % | {{osc_lo}}–{{osc_hi}} % | ≥ {{osc_bar}} % | {{osc_verdict}} |
| judge threshold, false interventions | {{tau_n}} | {{tau_est}} % | {{tau_lo}}–{{tau_hi}} % | ≤ {{tau_bar}} % | {{tau_verdict}} |

All {{l0}} write-ups rebuild from their published rows. The check for the cold reruns prints:

```text
$ python3 repro/cold-reproduction/l0_check.py
ok  posts: 29 (report 29)
ok  L0 PASS: 29 (report 29)
ok  L1 REPRO: 6 (report 6)
ok  L1 DIFF: 0 (report 0)
ok  L1 classes: {'REPRO': 6, '—': 3, 'SKIP': 8, 'FAIL-ENV': 12}
L0 PASS
```

The cold reruns start from a fresh clone with no credentials. {{l1_repro}} gates reran and matched, {{l1_exact}} of them exactly. {{l1_env}} more stop at the world-model environment, which is not published yet. Publishing it would unblock most of them. The remaining {{l1_skip}} need a larger GPU, a private checkpoint, the arm or a step the write-up leaves out. We checked the register's citations and paper-side fields against the papers' PDFs and corrected them. The register names {{ps_ids}} arXiv ids. The ones missing from our papers mirror all belong to scheduled tests. One tested paper has no arXiv id and was not checked against a PDF.

## 3. Results

Table 3 counts the verdicts by paper and by claim row. On claims taken from papers, {{c_paper_repro}} of {{c_paper}} reproduce and {{c_paper_fail}} fail. The other {{c_ours}} rows test our own baselines, for example that the commanded joints beat the world model. {{c_ours_repro}} of those hold.

Table 3: Verdicts by paper and by claim row (claim rows include our own baseline comparisons).

| verdict | papers | claim rows |
|---|---|---|
| reproduces | {{p_reproduces}} | {{c_reproduces}} |
| fails | {{p_fail}} | {{c_fail}} |
| not proven | {{p_not_proven}} | {{c_not_proven}} |
| not tested | {{p_not_tested}} | {{c_not_tested}} |
| withdrawn | {{p_withdrawn}} | {{c_withdrawn}} |
| total | {{papers}} | {{claims}} |

## 4. Three failure classes

The adaptive chunking entry of §1 misses the real-time budget on the edge GPU. The method may work on faster hardware. We call this kind of failure class A, the clock.

In other entries a model judged outcomes without training on this rig. A learned reward model detects failures at AUROC {{ex_b_ours}}. Episode length alone reaches {{ex_b_len}}. Judges of success, failure or progress that lose to a trivial signal like this form class B. Class C is about learned latents. A world model ranks the executed chunk first in {{ex_c_ours}} of anchors. Its pass mark was {{ex_c_bar}}, and an action-only baseline reaches {{ex_c_base}}. Class C holds latents used to plan, rank or track progress that lose to the joints, to copy-last or to an action-only baseline.

These examples illustrate the classes. They do not count them. A protocol committed before any labelling sets the rule for counting. The labels count only once a blind second reader labels the same {{fail_rows}} failed rows on the same form and agrees with the first reading at Cohen's κ ≥ {{kappa_bar}}. That reading has not happened yet.

## 5. Limitations

One operator, the author, ran the rig and labelled the outcomes. Labels were given at rest and not always blind to the arm. Observer bias is therefore the main confound. Where commit order shows it, the pass mark predates the run, so a label could not move the bar. A blind two-reader protocol for the failure classes is committed. It has not run yet, so no verdict has a second reader. For {{pr_unprov}} of the {{pr_rows}} gates the repository cannot show whether bar or result came first. {{sc_to_bf}} of the bar-first verdicts rest on matching a bar text in an earlier file. Under the bootstrap {{rc_flips}} verdicts are fragile. Cold reruns cover {{l1_repro}} gates so far, and the unpublished world-model environment blocks most of the rest. A failure here describes this rig, not the paper in its own setting. The papers were chosen for one stack, so the rate describes this register and not the field.

## 6. Related work

Two works use the same arm to evaluate policies. A standardized real-world benchmark reports a taxonomy of failures and recoveries for VLA policies [@2606.08881]. A fleet of SO-101 cells evaluates policies at scale [@2607.24481]. The vla-eval tool runs VLAs across 14 simulation benchmarks [@2603.13966]. A benchmark of demonstration quality studies one method family [@2610.18869]. We test the claims behind methods (judges, world models, latency) against thresholds fixed before the run, and we audit our own pre-registration. RoboSeed [@2610.40026] is the closest work. It scores VLA and world-action models on five dimensions, including reproduction evidence and deployment affordability. Its reproduction-evidence score counts five audit milestones (configuration mapping, task records, task coverage, training records, seeds). Its authors state that this score is not a probability that a result is correct. We give one pass or fail per claim on a €{{rig_eur}} rig.

## 7. Conclusion

We re-tested {{c_paper}} paper claims, and {{c_paper_repro}} held. The rig cost €{{rig_eur}} and the compute ${{cost}}. Every row behind the verdicts is published. Our own history cannot show the order of bar and result for {{pr_unprov}} of {{pr_rows}} gates. If you re-test a paper on a cheap rig, run its cheapest baseline on the same rows first and commit the threshold before the run. Every number here can be rebuilt from the repository (`github.com/ravediamond/paper-register-reproducibility`).

## References

## Appendix: the register

Table 4: The register, one row per paper, generated from the register file (internal model and gate names kept). The rig price of €{{rig_eur}} counts the parts with a stated price; {{rig_unpriced}} small parts are not priced yet. Read the verdict column against the rig each paper was shown on.

{{TABLE1}}
