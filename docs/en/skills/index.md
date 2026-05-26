# Skills & Hooks

ODD operates in three invocation modes.

---

## 1. Always Auto-invoked — superpowers framework

These skills fire **without any slash command** — Claude invokes them automatically when the `description` condition matches the current task.

| Skill | Auto-trigger condition | Role |
|-------|----------------------|------|
| [pyramid-ontology](./pyramid-ontology) | **At the start of any task** | Declares L0-L3 as the governing law for all decisions |
| [ontology-detach](./ontology-detach) | Whenever writing or reviewing code bindings | Detects hardcoding without exit conditions |
| [ontology-review-gate](./ontology-review-gate) | Before any implementation or refactor | Ontology Court — PASS required before coding begins |
| [ontology-learning](./ontology-learning) | **On mistake, user correction, or error detection** | L3→L0 reverse RCA → universal principle → permanent memory |

---

## 2. Situational manual invocation (`/command`)

Invoked intentionally by the user in specific situations.

| Skill | Command | When to use |
|-------|---------|-------------|
| [odd-onboarding](./odd-onboarding) | `/odd-onboarding` | Before starting any new project or feature |
| [pyramid-label](./pyramid-label) | `/pyramid-label` | Before code review, after adding new files |
| [pyramid-topology](./pyramid-topology) | `/pyramid-topology` | Before refactors — hierarchy integrity check |
| [ontology-rebuild](./ontology-rebuild) | `/ontology-rebuild` | After major changes — update topology docs |

---

## 3. Claude Code Hooks — Infrastructure-level enforcement

Registered in `~/.claude/settings.json`.  
These fire **regardless of Claude's judgment or superpowers installation** — invoked by Claude Code infrastructure.

| Hook | Type | Fires When | Checks |
|------|------|-----------|--------|
| [pyramid_ontology_gate](./hooks) | PreToolUse | **Before** Edit/Write executes | Blocks edit if no L0 declared — no superpowers needed |
| [pyramid_guard](./hooks) | PostToolUse | Every Edit/Write save | L-level integrity + SSOT duplicate truth |
| [ontology_declare_enforce](./hooks) | Stop | Every response completion | L0 declaration + dependency chain |
| [git_push_enforce](./hooks) | Stop | Every response completion | Uncommitted/unpushed session files |

→ [Hook details](./hooks)

---

## Invocation mode comparison

```
superpowers auto-invoke         Claude Code hooks
─────────────────────────       ─────────────────────────
Claude reads description,        settings.json → infrastructure
decides "this skill applies"     fires unconditionally at
→ cannot be silently skipped     Edit/Stop events
                                 → Claude cannot bypass
```

## Recommended workflow

```bash
# New project
/odd-onboarding              ← manual: establish L0 purpose

# Start working (pyramid-ontology fires automatically)

# During coding
# → pyramid_guard hook: auto-checks every Edit/Write
# → ontology-detach: auto-fires when writing bindings

# Before refactors
/pyramid-topology             ← manual
# → ontology-review-gate: auto-fires before implementation

# After completion
/pyramid-label                ← manual
/ontology-rebuild             ← manual
# → git_push_enforce hook: auto-checks on every response
```
