# Skills & Hooks & Commands

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

## 2. Manual slash commands — 18 total

### ODD Core Skills (7)

| Skill | Command | When to use |
|-------|---------|-------------|
| [odd-onboarding](./odd-onboarding) | `/odd-onboarding` | Before starting any new project or feature |
| [pyramid-ontology](./pyramid-ontology) | `/pyramid-ontology` | Declare L0-L3 for this session |
| [pyramid-label](./pyramid-label) | `/pyramid-label` | Before code review, after adding new files |
| [pyramid-topology](./pyramid-topology) | `/pyramid-topology` | Before refactors — hierarchy integrity check |
| [ontology-rebuild](./ontology-rebuild) | `/ontology-rebuild` | After major changes — update topology docs |
| [ontology-detach](./ontology-detach) | `/ontology-detach` | De-existence — enforce exit conditions on all bindings |
| [ontology-learning](./ontology-learning) | `/ontology-learning` | Immediately after any mistake — evolve ontology |

### Workflow Commands (11)

| Command | Purpose |
|---------|---------|
| `/brainstorming` | Design-first before implementation (Superpowers brainstorming) |
| `/tdd` | Test-driven development cycle enforcement |
| `/debug` | Systematic root-cause debugging |
| `/plan` | Break implementation into steps (Superpowers writing-plans) |
| `/investigate` | L0-driven research — no random keyword searches |
| `/careful` | Safety gate before irreversible actions |
| `/health` | System dependencies, processes, env check |
| `/review` | Ontology review of code/docs |
| `/retro` | Session retrospective + ontology evolution (memory save) |
| `/skills` | List all available skills, hooks, and commands |
| `/frozen-exe` | Package Python script as standalone EXE via PyInstaller |

---

## 3. Claude Code Hooks — Infrastructure-level enforcement (10 hooks)

Registered in `hooks.json`.  
These fire **regardless of Claude's judgment or superpowers installation** — invoked by Claude Code infrastructure.

### PreToolUse

| Hook | Fires When | Checks |
|------|-----------|--------|
| [pyramid_ontology_gate](./hooks) | **Before** Edit/Write executes | Blocks edit if no L0 declared — no superpowers needed |
| [ontology_violation_gate](./hooks) | **Before** Edit/Write executes | violation_registry.json rule violations |
| [assumption_declaration_gate](./hooks) | **Before** Edit/Write executes | Strategy .md files without assumption declaration |
| [websearch_yearguard](./hooks) | **Before** WebSearch executes | Blocks queries without current year |

### PostToolUse

| Hook | Fires When | Checks |
|------|-----------|--------|
| [pyramid_guard](./hooks) | Every Edit/Write save | L-level integrity + SSOT duplicate truth |
| [git_commit_push_check](./hooks) | After Bash (git commit) | Warns if unpushed commits |
| [pptx_validate_hook](./hooks) | After Bash (build_*_ppt.py) | PPTX slide layout overflow |

### Stop

| Hook | Checks |
|------|--------|
| [ontology_declare_enforce](./hooks) | L0 declaration + dependency chain |
| [git_push_enforce_stop](./hooks) | Uncommitted/unpushed session files |
| [tdd_enforce_stop](./hooks) | Blocks if no verification after Edit/Write |

→ [Hook details](./hooks)

---

## Invocation mode comparison

```
superpowers auto-invoke         Claude Code hooks
─────────────────────────       ─────────────────────────
Claude reads description,        hooks.json → infrastructure
decides "this skill applies"     fires unconditionally at
→ cannot be silently skipped     PreToolUse/PostToolUse/Stop
                                 → Claude cannot bypass
```

## Recommended workflow

```bash
# New project
/odd-onboarding              ← manual: establish L0 purpose

# Idea → design (before implementation)
/brainstorming               ← manual
/plan                        ← manual

# Start working (pyramid-ontology fires automatically)

# During coding
# → pyramid_ontology_gate: checks L0 before every edit (auto)
# → pyramid_guard hook: auto-checks every Edit/Write
# → ontology-detach: auto-fires when writing bindings
/tdd                         ← manual: TDD cycle

# Before irreversible actions
/careful                     ← manual: deploy, delete, external API

# Before refactors
/pyramid-topology             ← manual
# → ontology-review-gate: auto-fires before implementation

# After completion
/pyramid-label                ← manual
/ontology-rebuild             ← manual
/retro                        ← manual: session retrospective + memory
# → git_push_enforce_stop hook: auto-checks on every response
# → tdd_enforce_stop hook: blocks if no verification
```
