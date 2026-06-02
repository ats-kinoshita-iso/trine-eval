# Sprint 12 Mini Retrospective

**Sprint:** 12
**Result:** PASS
**Timestamp:** 2026-06-02T11:50:00Z
**Mode:** mini (capture-only; no Standard-Work proposals)

## Learning Points

1. **Single-round APPROVAL after non-blocking advisories worked because both advisories pointed to specific implementation-time fixes.** Advisory 1 (B1 classification boundary) was a grading-hierarchy disposition the Evaluator could honor unilaterally at R1 by treating B1 as llm-judge in practice; Advisory 2 (eval-harness missing from Step 1 ambiguity list) was a verbatim line-23 edit captured in J10(d). Neither required contract revision; both were closed at implementation. Breaks Sprint 7–10 R1→R2 negotiation precedent for the second sprint running (cf. S11 PO3). *observed, confidence 5.*

2. **Static-artifact carve-out invocation was clean because Technical Notes spelled out the fallback ladder explicitly.** Contract documented behavioral coverage at 54% with B1 included and 40% if B1 reclassified, then named the Sprint 7 carve-out as the load-bearing justification rather than relying on B1's "simulation behavioral" label. Evaluator accepted on the first read. Compare to Sprint 11's PROC-002 trigger-band format non-conformance (S11 LP1) — Sprint 12 demonstrates the format the carve-out wants. *observed, confidence 5.*

3. **Sprint 11 P-A2 calibration signal was addressed by acknowledged-gap routing, not closure.** Contract Technical Notes (lines 246–256) named the synthetic-authoring vulnerability, documented that B5/SN7 are weak tamper-resistance not real-dispatch verification, and explicitly routed the structural fix to Sprint 13 (HK-0006). Evaluator accepted this as "honest gap acknowledgment, not evasion." Pattern: route what you cannot close to a sprint that can, in the contract itself. *observed, confidence 5.*

4. **All 7 SN gates passed with verified pre-sprint baselines on 14 separate commands.** Contract's pre-sprint baseline table (lines 227–245) was the Evaluator's verification checklist verbatim — every SN1–SN7 row matched. Pre-baselining at contract time, then re-verifying at eval time, is the cheapest way to make a 7-gate sprint single-round-approvable. *observed, confidence 5.*

5. **Phase 2 SC10 closed with a documentation-only sprint** — but only partially at first; council fan-out caught the residual surface (eval-rubric/SKILL.md missing README pointer) and closed it via DEC-0017. Documentation sprints PASS the contract while leaving spec-named surfaces uncovered if the contract criteria do not enumerate every spec-named artifact. The Architect catch is the load-bearing layer here. *observed, confidence 5.*

## Pattern Observations

1. **behavioral_pct now 54% — fifth consecutive sprint at-or-below the 60% floor (S8=66, S9=63, S10=62, S11=62, S12=54).** Strong descent toward the rule's edge across Phase 2; Sprint 12 is the first to drop below the floor, justified by the static-artifact carve-out. PO1 from Sprint 11 mini (stable-at-floor band) is now refined: declining-through-floor. Surfaced as HK-0009 actionable update (DEC-0018). *inferred, confidence 4.*

2. **Sprint 12 is the second consecutive single-round APPROVAL, breaking the Sprint 7–10 R1→R2 negotiation precedent.** Sprint 11 (LP-free contract, simple domain, possibly less-aggressive review) and Sprint 12 (advisory-only review with both advisories closed at implementation) both single-rounded. Two-of-two is a candidate process-shift signal but causes are not yet attributable. *inferred, confidence 3 — two observations.*

3. **Honest-disclosure-as-process-strength pattern continues into Sprint 12 (S9→S10→S11→S12).** Sprint 12's Technical Notes section names the unresolved synthetic-authoring vulnerability and defers it explicitly to Sprint 13 rather than asserting closure. Fourth consecutive Phase 2 sprint where Generator or Evaluator named a gap rather than concealed it. PO5 from Sprint 11 mini upgraded from "converging" toward "established." *inferred, confidence 5.*

4. **Pre-sprint prebrief AND post-sprint fan-out coverage rebuilding after Sprint 11 retroactive fan-out.** Sprint 12 has a Cynefin prebrief (complicated/0.7) at contract time; post-sprint fan-out executed in this same session. This is the first sprint after Sprint 10 with prebrief in place pre-execution and fan-out executed in-cycle. Contributes 1-of-2 toward HK-0003 resolved-promotion criterion, but only after Sprint 13 b2 (structural auto-trigger) lands. *inferred, confidence 4.*
