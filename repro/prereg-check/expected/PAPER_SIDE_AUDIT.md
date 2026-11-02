# WS-136 step 3 · Paper-side audit (WS-068), closed

**Applied.** Every WS-068 fix is in the site register: branch `claims-audit` (last commit `f53db4f`, 2026-10-31,
"Claims audit: owner-approved content rows, VLA-Corrector re-pointed …") is fully merged into site `main`
(`git rev-list --count $(git merge-base main claims-audit)..claims-audit` = 0; `main` at `7d48b9e`). That covers both
passes recorded in `ws show WS-068`: the citation fixes (first pass 20 CITE on 12 papers, second pass 19 CITE on 9) and
the 22 content rows the owner approved with `go WS-068` ("follow your recommendation"), with
`journal/drafts/2026-10-31-claims-audit/REPORT.md` and `AUDIT.md` as the record. No new site commit is needed; none
was made here (the site checkout is on WS-120's `readers` branch and was not touched).

**Owner decisions still open:** none from WS-068's rows. One follow-up WS-068 named and left: 3 of the 5 /findings/
disagreements oppose baselines the papers never ran (page wording unchanged, "a follow-up if wanted").

**Missing from the papers mirror** (`~/workspace/papers/INDEX.md`, checked 2026-11-02 against every arXiv id in site
`main:data/register.yaml`, 38 ids):

| paper | arXiv | where in the register | to do |
|---|---|---|---|
| SURVEYOR | none (NeurIPS 2026 workshop poster) | register entry C-018 (2 fail rows) | owner: add the PDF to Drive `Projects/Robotics/Papers` when available; the only register paper not audited against its PDF |
| PEEK | 2509.18282 | `scheduled:` (§21 mask overlay for ACT) | add to Drive before that test |
| SEVO | 2605.11114 | `scheduled:` (§18 wrist blanking) | same |
| PSG-JEPA + SA/IDM | 2608.06799, 2609.03565 | `scheduled:` (§7 three-arm grounding) | same |
| Planning Limits of JEPA | 2609.39235 | `scheduled:` (§19 ranking test) | same |

The "10 papers missing" of the WS-068 first pass were added by the owner on 2026-10-31 evening (second pass, 21 of 22
audited); what remains is the table above. No PDF was fetched here.
