# ODD on Legacy Code — Gradual Adoption

> L0: A developer inheriting or maintaining a legacy codebase can apply ODD incrementally without disrupting existing workflows.

The most common mistake when adopting any new discipline on legacy code: trying to apply it everywhere at once. ODD is designed against this. Start narrow. Let the structure prove itself. Expand from there.

---

## The Core Principle: Don't Boil the Ocean

Legacy code has no L-level labels. That is fine. The goal is not retroactive perfection — it is **forward discipline**. Every new file you touch gets labeled. Every old file you touch gets labeled. Files you don't touch stay as-is.

Three phases. Each phase is complete before the next begins.

---

## Phase 1 — Warn Mode (Weeks 1-2)

**Goal:** Install ODD hooks in observation mode. No blocking. Just learn what would have been caught.

### What to do

1. Install the plugin:

```bash
claude plugin add HHSsub/ontology-driven-design
```

2. Create a minimal `ONBOARDING.md` at the project root — even a rough one:

```markdown
# ONBOARDING — [project-name]

## L0: Purpose
[Best guess at the system's ultimate purpose — refine later]

## Never-Do
[Things that would break the system or its users]
```

3. For the first two weeks, run `/pyramid-topology` at the end of each day:

```
/pyramid-topology
```

Read the report. Note which files have no L-level labels. Note any L0 contamination warnings. **Do not fix anything yet.** You are building a map.

4. Keep a log of what the hooks would have blocked (they are in warn-only mode when `violation_registry.json` rules have no `block: true` flag).

### What you learn in Phase 1

- Which parts of the codebase are most ontologically "dark" (no purpose labeling)
- Which functions are doing L0-level decisions inside L3-level code
- Whether your draft `ONBOARDING.md` L0 is accurate or needs refinement

---

## Phase 2 — Label New Files, Block on New Code (Weeks 3-6)

**Goal:** All new files are fully labeled. Hooks block violations on new code only.

### Rule: New file = labeled file

Every file you create during this phase gets L-level comments:

```python
# L0: Customers can track their order without contacting support
# L1: Order status polling endpoint with cache layer
# L2: 5-minute cache, auth required, no PII in response
# L3: FastAPI GET /orders/{id}/status → OrderStatusResponse

from fastapi import FastAPI, Depends
...
```

For TypeScript:

```typescript
// L0: Customers can track their order without contacting support
// L1: Order status hook with SWR polling
// L2: Poll every 60s, show last-known state during network error
// L3: useOrderStatus(orderId) → { status, lastUpdated, error }

export function useOrderStatus(orderId: string) {
  ...
}
```

### Rule: Touched file = labeled file

If you edit an existing file (bug fix, feature addition), add L-level comments at the top of that file before you touch anything else. The `pyramid_ontology_gate` hook will accept the session-level L0 declaration; the labels in the file serve your future self.

### Enable blocking on new violations

In `violation_registry.json`, enable block mode for new-code patterns:

```json
{
  "rules": [
    {
      "id": "no-unlabeled-new-files",
      "description": "New files in src/ must have L0 comment",
      "type": "content_pattern",
      "path_must_contain_any": ["src/"],
      "pattern": "^(?!.*L0:).*",
      "block": true,
      "message": "New files in src/ require an L0 comment. Add L0: [purpose] at the top."
    }
  ]
}
```

Old files in `src/` that predate this rule are grandfathered — the rule only triggers when a file is written/edited in a session that has this rule active.

---

## Phase 3 — Full Block Mode, Retroactive Labeling (Week 7+)

**Goal:** All hooks at full strength. Legacy files labeled opportunistically during maintenance.

### Switch all hooks to block mode

At this point, your team (or you, solo) has enough context to handle hook blocks without friction. The `pyramid_ontology_gate` is already blocking session-level L0 absence. Enable the remaining strict checks.

### Retroactive labeling strategy

Do not schedule a "label everything" sprint. It will fail. Instead, use the **Boy Scout Rule**:

> Leave every file more labeled than you found it.

When you open a file to fix a bug:
1. Add L-level comments to the file header (5 minutes)
2. Fix the bug
3. Run verification

When you touch a function:
1. Add an inline L-level comment above the function if it's doing multi-level work:

```python
# L2: Trade-off — we accept stale data for 5 min to avoid DB load
def get_cached_status(order_id: str) -> dict:
    ...
```

Over 3-6 months, the codebase naturally acquires ontology coverage through maintenance work.

### Validate coverage periodically

Run monthly:

```
/pyramid-topology
```

Track the percentage of files with L0 labels. Watch it grow as a side effect of normal maintenance.

---

## Migration Plan Summary

| Phase | Duration | Hook mode | What you do |
|-------|----------|-----------|-------------|
| 1 — Observe | Weeks 1-2 | Warn only | Install, map, learn. Don't block. |
| 2 — New code only | Weeks 3-6 | Block new files | Label all new/touched files. Block on new violations. |
| 3 — Full | Week 7+ | Block everything | Retroactive labeling via maintenance. Full hook enforcement. |

---

## Common Mistakes in Legacy Adoption

**Mistake: Trying to label everything in a weekend**

Labels added without understanding are wrong labels. Wrong L0 is worse than no L0 — it misdirects future decisions. Phase 1 exists precisely to build understanding before labeling.

**Mistake: Disabling hooks when they're inconvenient**

If a hook fires and you don't know why, investigate. The hook is reporting a structural problem. Disabling it hides the problem. Read the hook reference and understand what it's detecting.

**Mistake: Using L0 for technical descriptions**

```
# L0: Uses Redis cache with 5-minute TTL   ← WRONG: this is L3
# L0: Users see current data without waiting for DB queries   ← CORRECT
```

The `pyramid_guard` hook will block the first form. This is by design.

**Mistake: Skipping `/ontology-review-gate` for "small" features**

There is no such thing as a feature too small for L0. If you cannot state the business purpose of a 5-line function in one sentence, you do not understand it well enough to write it.

---

## Related guides

- [Solo developer workflow](./solo-developer.md) — day-to-day ODD usage
- [SSOT — enum registry change](./enum-registry-change.md) — the most critical SSOT case
- [Hook reference](../skills/hooks.md) — all hooks with block/pass examples
