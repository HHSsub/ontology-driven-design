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

> **Note:** When installed as a plugin, all commands are namespaced: `/ontology-driven-design:command-name`

### ODD Core (18 commands)

| Command | Purpose |
|---------|---------|
| `/ontology-driven-design:pyramid-ontology` | Declare L0-L3 for this session |
| `/ontology-driven-design:ontology-detach` | Run de-existence check on bindings |
| `/ontology-driven-design:ontology-rebuild` | Rebuild topology docs |
| `/ontology-driven-design:pyramid-label` | Label all code units L0-L3 |
| `/ontology-driven-design:pyramid-topology` | Scan hierarchy integrity |
| `/ontology-driven-design:ontology-review-gate` | Ontology court before implementation |
| `/ontology-driven-design:ontology-learning` | Evolve ontology from mistakes |
| `/ontology-driven-design:brainstorming` | Design-first before implementation |
| `/ontology-driven-design:tdd` | Test-driven development cycle |
| `/ontology-driven-design:debug` | Systematic root-cause debugging |
| `/ontology-driven-design:plan` | Write implementation plan |
| `/ontology-driven-design:investigate` | L0-driven deep research |
| `/ontology-driven-design:careful` | Safety gate for irreversible actions |
| `/ontology-driven-design:health` | System health check |
| `/ontology-driven-design:review` | Ontology review of code/docs |
| `/ontology-driven-design:retro` | Session retrospective + memory evolution |
| `/ontology-driven-design:skills` | List all available skills and hooks |
| `/ontology-driven-design:frozen-exe` | Package Python script as standalone EXE |

## Active Hooks (21 hooks, auto-trigger)
<!-- Source of truth: hooks/hooks.json — update this table when hooks.json changes -->

### PreToolUse
| Hook | Trigger | Effect |
|------|---------|--------|
| `websearch_yearguard` | WebSearch | Blocks queries without current year |
| `destructive_bash_gate` | Bash | Blocks dangerous bash commands |
| `agent_pyramid_gate` | Agent | Requires L0 + role spec for Agent calls |
| `goal_decompose_gate` | Agent | Leader/Manager dispatch requires sub-goal decomposition + acceptance criteria; logs goal hierarchy to goal_registry.json |
| `agent_loop_gate` | Agent | Hard-blocks repeated identical dispatch (loop) and session dispatch budget breach — enforcement, not alerting |
| `pyramid_ontology_gate` | Edit/Write/NotebookEdit | Blocks if no L0 declaration in session |
| `ontology_detach_gate` | Edit/Write/NotebookEdit | Blocks L2 structural file edits without prior ontology-detach |
| `ontology_violation_gate` | Edit/Write/NotebookEdit/Bash/PowerShell | Checks violation_registry.json rules; records per-project trigger stats |
| `ontology_graph_gate` | Edit/Write/NotebookEdit | Blocks edits to multi-file L0 purpose groups without a prior ontology_grep closure query this session |

### PostToolUse
| Hook | Trigger | Effect |
|------|---------|--------|
| `pptx_validate_hook` | Bash | Validates PPTX layout overflow after build_*_ppt.py |
| `pyramid_guard` | Edit/Write | Enforces L0~L3 header labels on every saved file (≥15 lines; meta/data formats exempt) — labels feed the ontology_grep index |

### Stop
| Hook | Trigger | Effect |
|------|---------|--------|
| `tdd_enforce_stop` | Session end | Blocks if code edited without verification (docs exempt) |
| `ontology_declare_enforce` | Session end | Blocks if L0 declaration incomplete |
| `assumption_declaration_gate` | Session end | Blocks if strategy docs missing [가정 명시] |
| `git_push_enforce_stop` | Session end | Blocks if unpushed commits exist |
| `ontology_learning_enforce_stop` | Session end | Blocks if tool error occurred without /ontology-learning; blocks if a rule fired in 2+ projects without global-channel promotion (scope-channel match); reports dead/internalized rule evolution signals |
| `agent_telemetry` | Session end + SubagentStop | Records agent dispatches, completion, skill invocations per session (observability, never blocks) |
| `semantic_judge_gate` | Session end | Independent LLM judge (separate context, judge_rubric.md as SSOT) semantically evaluates L0 declarations written this session — meaning-based, not regex; self-loop capped |

### SessionStart
| Hook | Trigger | Effect |
|------|---------|--------|
| `principles.md injection` | Session start | Injects machine-unenforceable principles into every session context — the global-domain internalization channel |

### Supporting data files (hooks/)
`violation_registry.json` (seed→branch→rule), `violation_stats.json` (per-rule, per-project trigger telemetry), `thresholds.json` (every behavioral threshold with rationale, source, replacement_condition — no bare magic numbers), `goal_registry.json` (dispatched goal hierarchy), `agent_telemetry.json` (agent/skill usage), `judge_rubric.md` (L0 semantic criteria), `principles.md` (unenforceable principles)

## Philosophy

ODD is built on **Pyramid Thinking** (피라미드사고법) — a 4-layer ontology framework that organizes fragmented horizontal knowledge into a vertical hierarchy of purpose.

> "Purpose-less code is garbage. Code that works but has no purpose is failure."

Learn more: [ontology-driven-design docs](https://HHSsub.github.io/ontology-driven-design)
