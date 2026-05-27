# ODD — Ontology Driven Design

A Claude Code plugin by **Hwang Hoe Sun** (황회선) — creator of Pyramid Thinking (피라미드사고법).

## Plugin Skills

This plugin provides 7 skills for purpose-driven AI workflows:

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `pyramid-ontology` | Any task start | Declares L0-L3 hierarchy as governing law |
| `ontology-detach` | Writing/reviewing code with bindings | Detects existence-clinging, enforces exit conditions |
| `ontology-rebuild` | After major changes | Rebuilds ONTOLOGY.md topology for all folders |
| `pyramid-label` | Before code review | Applies L0-L3 labels to all code units |
| `pyramid-topology` | Before refactors | Full hierarchy integrity scan |
| `ontology-review-gate` | Before any implementation | Ontology Court — PASS required before coding |
| `ontology-learning` | After any mistake | L3→L2→L1→L0 reverse analysis + memory evolution |

## The L0-L3 Hierarchy

Every action must connect to a purpose. No exceptions.

```
L0  Ontology / Purpose       궁극적 융합과 내재화 — the deepest reason this exists
L1  Abstract / Structure     질서의 아키텍처 — design that bridges L0 to reality
L2  Logic / Trade-off        현실과의 타협과 선택 — decisions, constraints, cost of choice
L3  Execution / Instance     물리적 닻 — concrete code, tools, physical acts
```

**Rule:** If you cannot state L0, stop. Ask first.

## Slash Commands

### ODD Core (18 commands)

| Command | Purpose |
|---------|---------|
| `/pyramid-ontology` | Declare L0-L3 for this session |
| `/ontology-detach` | Run de-existence check on bindings |
| `/ontology-rebuild` | Rebuild topology docs |
| `/pyramid-label` | Label all code units L0-L3 |
| `/pyramid-topology` | Scan hierarchy integrity |
| `/ontology-review-gate` | Ontology court before implementation |
| `/ontology-learning` | Evolve ontology from mistakes |
| `/brainstorming` | Design-first before implementation |
| `/tdd` | Test-driven development cycle |
| `/debug` | Systematic root-cause debugging |
| `/plan` | Write implementation plan |
| `/investigate` | L0-driven deep research |
| `/careful` | Safety gate for irreversible actions |
| `/health` | System health check |
| `/review` | Ontology review of code/docs |
| `/retro` | Session retrospective + memory evolution |
| `/skills` | List all available skills and hooks |
| `/frozen-exe` | Package Python script as standalone EXE |

## Active Hooks (10 hooks, auto-trigger)

### PreToolUse
| Hook | Trigger | Effect |
|------|---------|--------|
| `pyramid_ontology_gate` | Edit/Write/NotebookEdit | Blocks if no L0 declaration in content |
| `ontology_violation_gate` | Edit/Write/NotebookEdit | Checks violation_registry.json rules |
| `assumption_declaration_gate` | Edit/Write/NotebookEdit | Blocks strategy .md files without [가정 명시] |
| `websearch_yearguard` | WebSearch | Blocks queries without current year |

### PostToolUse
| Hook | Trigger | Effect |
|------|---------|--------|
| `pyramid_guard` | Edit/Write | Verifies L0 connection after write |
| `git_commit_push_check` | Bash | Warns if unpushed commits after git commit |
| `pptx_validate_hook` | Bash | Validates PPTX layout overflow after build_*_ppt.py |

### Stop
| Hook | Trigger | Effect |
|------|---------|--------|
| `ontology_declare_enforce` | Session end | Blocks if L0 declaration incomplete |
| `git_push_enforce_stop` | Session end | Blocks if unpushed commits exist |
| `tdd_enforce_stop` | Session end | Blocks if Edit/Write without verification |

## Philosophy

ODD is built on **Pyramid Thinking** (피라미드사고법) — a 4-layer ontology framework that organizes fragmented horizontal knowledge into a vertical hierarchy of purpose.

> "Purpose-less code is garbage. Code that works but has no purpose is failure."

Learn more: [ontology-driven-design docs](https://HHSsub.github.io/ontology-driven-design)
