# ODD Measurement Framework

<!-- L0: Enable reproducible, comparable evidence of ODD's governance effectiveness across projects -->

## Purpose

This framework defines how to measure ODD's impact in any project where it is applied. Without consistent measurement methodology, case studies cannot be compared. With it, a body of evidence accumulates.

---

## 1. The 7 Core Metrics

### M1: Hook Accuracy Rate

**Definition:** Percentage of hook invocations that produce the intended outcome (block or pass) without false positives or false negatives.

**Formula:** `(correct_outcomes / total_invocations) × 100`

**How to measure:**
1. Enable hook logging: set `ODD_DEBUG=1` in environment
2. Run a representative session (mix of edit, write, bash, websearch)
3. Review hook output logs
4. Count: (a) correct blocks, (b) correct passes, (c) false positives (blocked when should pass), (d) false negatives (passed when should block)
5. `Hook Accuracy = (a + b) / (a + b + c + d)`

**Baseline target:** ≥ 95%
**Case 001 result:** Before 62%, After 100%

---

### M2: False Positive Rate per Hook

**Definition:** For each hook, the percentage of invocations where the hook blocked/warned when it should have passed.

**Formula:** `false_positives / total_invocations_of_hook × 100`

**How to measure:**
- Run 10 representative sessions with a human who understands ODD
- For each session, ask the human to flag any hook trigger they believe was incorrect
- Aggregate across sessions

**Baseline target:** ≤ 5% per hook
**Case 001 critical findings:**
- `tdd_enforce_stop` on .md edits: 100% → 0%
- `ontology_learning_enforce_stop` on normal conversations: ~95% → 0%

---

### M3: Vibe-Drift Incidents Prevented

**Definition:** Count of sessions where a hook block caused the developer to reconsider and clarify their L0 before proceeding, vs sessions where the developer bypassed the hook.

**How to measure:**
- After each session, interview the developer or review session transcript
- Count: (a) hook triggered AND developer clarified L0 before continuing, (b) hook triggered AND developer bypassed/disabled
- `Prevention Rate = a / (a + b)`

**Baseline target:** ≥ 70% (prevention is the goal, not 100% compliance)

**Note:** This metric cannot be measured from logs alone. Requires session retrospective.

---

### M4: L0 Declaration Rate

**Definition:** Percentage of sessions where the developer explicitly declared L0 before making the first Edit/Write/significant action.

**How to measure:**
- Review session transcripts
- Count sessions with explicit L0 declaration at or before first code edit
- `L0 Rate = sessions_with_L0 / total_sessions`

**Baseline target:** ≥ 90%
**Measurement method:** Automated — `pyramid_ontology_gate.py` log output indicates whether L0 was present at each Edit/Write.

---

### M5: Hook Disable Rate

**Definition:** Percentage of ODD-enabled sessions where the developer explicitly commented out, removed, or bypassed a hook.

**How to measure:**
- Review git history for changes to `hooks/hooks.json`
- Review session transcripts for "disable", "comment out", "skip hook" language
- Count: hook disables / total sessions

**Baseline target:** ≤ 10%

**Interpretation:** High disable rate indicates hooks are generating friction without value (too many false positives, or blocks on legitimate actions).

---

### M6: Formal Concept Coverage

**Definition:** Percentage of domain concepts explicitly defined in `ontology/concept-registry.yaml` relative to concepts implicitly referenced in code and documentation.

**How to measure:**
1. Extract all L0-L3 terms used across skills, hooks, and docs
2. Count those with formal definitions in concept-registry.yaml
3. `Coverage = defined / total_referenced`

**Baseline target:** ≥ 80% for core concepts
**Case 001 result:** Before 0%, After: 9 concepts defined (bootstrap)

---

### M7: Test Coverage for Hooks

**Definition:** Percentage of hook behaviors covered by automated tests in `tests/test_hooks.py`.

**How to measure:**
- Run: `python tests/test_hooks.py -v 2>&1 | grep "ok\|FAIL\|ERROR" | wc -l`
- Count: tests passing / total behaviors tested

**Baseline target:** ≥ 80% of hook behaviors (block + pass cases per hook)
**Case 001 result:** Before 0 tests, After 77 tests

---

## 2. Case Study Collection Protocol

### Step 1: Pre-Session Baseline

Before applying ODD to a new project, record:
```json
{
  "project": "<name>",
  "date_start": "YYYY-MM-DD",
  "hook_accuracy": <measure or "unmeasured">,
  "test_coverage": <count or 0>,
  "formal_concepts": <count or 0>,
  "l0_declaration_rate": "unmeasured"
}
```

### Step 2: Apply ODD

- Install ODD (see `ports/claude-code/README.md`)
- Run at least one full work session with ODD active
- Do NOT disable hooks unless absolutely necessary (log any disables)

### Step 3: Post-Session Measurement

Measure all 7 metrics. Record in `benchmarks/cases/case-NNN.json` following the schema in `case-001-odd-on-odd.json`.

### Step 4: Retrospective

- What did ODD catch that you would have missed?
- What did ODD block that it should not have?
- Did L0 declaration change how you approached the work?
- Net time cost/benefit estimate

### Step 5: Submit

Open a GitHub issue with the label `case-study` and attach your `case-NNN.json`. The project will aggregate results.

---

## 3. Statistical Validity Requirements

A single case study (case-001) is not statistically significant. Guidelines for when claims become defensible:

| Claim | Minimum Evidence Required |
|-------|--------------------------|
| "ODD reduces false positives" | N ≥ 5 cases, same hook, measured before/after |
| "ODD improves L0 declaration rate" | N ≥ 10 sessions, controlled comparison |
| "ODD hooks work correctly" | 77+ unit tests passing (already met) |
| "ODD is domain-agnostic" | N ≥ 3 distinct project types (web app, CLI, data pipeline, etc.) |
| "ODD reduces vibe-drift" | N ≥ 5 cases with developer retrospective |

---

## 4. Comparison: ODD vs No-ODD Sessions

The strongest evidence for ODD's value is a controlled comparison. Recommended design:

**Condition A (ODD):** Developer uses ODD with all hooks active.
**Condition B (No-ODD):** Same developer, comparable project, no ODD.

Measure in both conditions:
- L0 declaration rate
- Number of "pivot" moments (direction change after implementation started)
- Number of commits that were reverted within 24 hours
- Time spent on retrospective/refactor vs forward progress

**Confound to control:** Project complexity. Compare projects of similar scope.

**Minimum sample:** 3 ODD / 3 No-ODD sessions per developer, 2+ developers.

---

## 5. Metric Registry (Machine-Readable)

Each case study JSON should include these metric keys:

```
hook_accuracy_before / hook_accuracy_after
false_positive_rate_before / false_positive_rate_after (per hook)
test_coverage_before / test_coverage_after
formal_concept_definitions_before / formal_concept_definitions_after
l0_declaration_rate (if measured)
vibe_drift_prevented (count, if measured)
hook_disable_count (count)
duration_hours
issues_found / issues_resolved
```

Aggregate queries across all `benchmarks/cases/*.json` files to produce trend analysis.
