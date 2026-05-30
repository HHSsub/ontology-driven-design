# ODD for the Solo Developer

> L0: A developer working alone uses ODD to prevent purposeless code accumulation and enforce personal discipline through automated structure.

Solo development is where ODD pays back the fastest. There is no team to push back on bad decisions, no code reviewer to catch directionless commits. The hooks become your external accountability layer.

---

## Scenario A — Starting a New Project

### Without ODD

```
1. Have idea
2. Open editor, start typing
3. Three weeks later: "why does this function exist?"
4. Refactor costs more than original build
```

### With ODD

Before touching any file, run:

```
/odd-onboarding
```

ODD asks five plain-language questions:

| Question area | What it extracts |
|--------------|-----------------|
| "What pain does this solve?" | L0 — the business purpose |
| "When would this tool make things worse?" | Never-Do constraints |
| "What should be automatic vs manual?" | L1 structural design |
| "Simple vs accurate — which do you prefer?" | L2 trade-off decisions |
| "What can Claude decide alone?" | AI autonomy boundaries |

Output: `ONBOARDING.md` — the project's constitution. Every future decision references this file.

**Example ONBOARDING.md excerpt:**

```markdown
# ONBOARDING — invoice-cli

## L0: Purpose
Small business owners can generate and send invoices without opening spreadsheet software.

## Never-Do
- Never store client payment data locally
- Never auto-send without explicit user confirmation

## L1: Overall flow
Input client info → generate PDF → preview → user confirms → send via email API

## L2: Key trade-off
Accuracy over speed. A slow correct invoice is better than a fast wrong one.
```

Once `ONBOARDING.md` exists, the `pyramid_ontology_gate` hook accepts any `L0:` declaration that references this document's purpose.

---

## Scenario B — Adding ODD to an Existing Project

You have a project that already has code. You don't want to rewrite everything — you want to add purpose tracking going forward.

### Step 1: Declare retroactive L0

Create `ONBOARDING.md` in the project root:

```markdown
# ONBOARDING — [project-name]

## L0: Purpose
[One sentence: what is the ultimate reason this codebase exists?]

## L1: Architecture intent
[What structural decisions support L0?]

## Never-Do
[What must this system never do, even if technically possible?]
```

### Step 2: Label new files only

When you create a new file, add L-level comments at the top:

```python
# L0: Users get instant order status without calling support
# L1: Polling endpoint that returns current order state
# L2: Cache-first, fall back to DB query
# L3: FastAPI GET /orders/{id}/status

def get_order_status(order_id: str) -> dict:
    ...
```

Old files stay unlabeled. New files get labeled. Over time, the codebase gains ontology coverage incrementally.

### Step 3: Run pyramid-topology to find gaps

```
/pyramid-topology
```

This scans the codebase and reports:
- Files with L-level labels
- Files without any L-level labels (candidates for future labeling)
- L0 contamination (technical details in L0 lines)

---

## A Full Day Work Cycle with ODD

### Morning — Session Start

```
L0: Users can export their data to CSV without requesting support
L1: Add export button to dashboard that streams CSV download
L2: Auth check, rate limit, streaming response
```

Declare this at the start of the Claude session. The `pyramid_ontology_gate` hook reads this from the transcript and allows all file edits that follow.

### During Coding

When you encounter a hardcoded value or a binding with no clear removal path:

```
/ontology-detach
```

Self-question: **"What is the replacement condition for this binding?"**

If the answer is "I don't know" or "never," that's a violation. The binding must either:
- Have an explicit exit condition documented in a comment
- Be replaced with a configurable value

**Example:**

```python
# VIOLATION — no exit condition
EXPORT_LIMIT = 10000

# CORRECT — exit condition declared
EXPORT_LIMIT = int(os.getenv("EXPORT_LIMIT", "10000"))
# Exit condition: when rate limiting moves to API gateway, remove this env var
```

Before implementing a major feature:

```
/ontology-review-gate
```

This runs the Ontology Court: Claude acts as judge, defense, and prosecution. PASS required before writing a line of implementation code.

### End of Day — Session Close

When Claude finishes the last response of the day, three Stop hooks fire automatically:

1. **`ontology_declare_enforce`** — was L0 declared before any edit?
2. **`tdd_enforce_stop`** — was every code edit followed by a verification command?
3. **`git_push_enforce_stop`** — are all modified files committed and pushed?

If any check fails, Claude's response is blocked with a specific error and required action.

**Common end-of-day block and fix:**

```
❌ BLOCK: tdd_enforce_stop
Last Edit: src/export.py (modified 14:32)
Last verification: none found after 14:32

Fix: Run python -m py_compile src/export.py
```

After running the verification:

```
python -m py_compile src/export.py
git add src/export.py
git commit -m "feat: add CSV export endpoint"
git push origin main
```

The next session can start clean.

---

## Before/After Summary

| Situation | Without ODD | With ODD |
|-----------|-------------|----------|
| Starting a feature | Open editor immediately | `/odd-onboarding` → L0 confirmed → code |
| Hardcoded value | Added, forgotten | `/ontology-detach` → exit condition required |
| End of day | Files modified, maybe committed | Hooks verify commit + push + test |
| Three months later | "Why does this exist?" | ONBOARDING.md answers in 30 seconds |
| Refactor | Guess at intent, break things | `/pyramid-topology` → intent map available |

---

## Related guides

- [Quickstart](../quickstart.md) — 5-minute first experience
- [Legacy refactor guide](./legacy-refactor.md) — gradual adoption on old codebases
- [Hook reference](../skills/hooks.md) — all 10 hooks with block/pass examples
