# ODD — Ontology Driven Design

> **A purpose-governed engineering layer for AI coding agents.**  
> ODD prevents vibe-code drift by enforcing conceptual hierarchy, dependency traceability, and source-of-truth discipline before code changes happen.

A Claude Code plugin built on **Pyramid Thinking** (피라미드사고법) — created by [Hwang Hoe Sun](https://knowgram.vercel.app).

If you want Premium Update version, contact -> hhoesun@gmail.com


[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin-blue)](https://claude.ai/code)
[![Docs](https://img.shields.io/badge/Docs-HHSsub.github.io-orange)](https://HHSsub.github.io/ontology-driven-design)

---

## What ODD Is (and Is Not)

**ODD IS:** A governance layer that forces AI coding agents to connect every action to a stated purpose. It operates through hooks (automatic enforcement) and skills (manual invocation).

**ODD IS NOT:** A formal ontology tool (no OWL/RDF/SPARQL). It does not build knowledge graphs or semantic web artifacts. The word "ontology" refers to *purpose hierarchy* — the question "why does this exist?" — not to formal ontology engineering.

If you want formal ontology tooling, see [Protégé](https://protege.stanford.edu/) or [LinkML](https://linkml.io/). If you want AI coding agents that don't lose track of *why they're doing what they're doing*, ODD is for you.

---

## The L0-L3 Framework

Every action, file, and decision must connect to a purpose.

| Level | Layer | Question |
|-------|-------|---------|
| **L0** | Purpose / Ontology | *Why does this exist at all?* — the existence-level reason |
| **L1** | Structure / Architecture | *What is the invariant design?* — bridges L0 to reality |
| **L2** | Logic / Trade-off | *What did we choose and what did we sacrifice?* — decision record |
| **L3** | Execution / Instance | *What is the concrete act?* — code, config, physical steps |

**Core rule:** If you cannot state L0, stop. Action without L0 is purposeless.

---

## Installation

> **Note:** The `claude plugin add` installation path is being verified against current Claude Code CLI versions. If the command below does not work, use the manual installation path in [docs/guide/installation.md](docs/guide/installation.md).

```bash
# Plugin install (verify this works on your Claude Code version)
claude plugin add HHSsub/ontology-driven-design
```

**Manual install (always works):**
```bash
git clone https://github.com/HHSsub/ontology-driven-design.git
# Follow docs/guide/installation.md for full setup including hooks
```

---

## Skills (8)

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `/pyramid-ontology` | Any task start | Declares L0-L3 hierarchy as governing law |
| `/ontology-detach` | Writing/reviewing bindings | Detects existence-clinging, enforces exit conditions |
| `/ontology-rebuild` | After major changes | Rebuilds ONTOLOGY.md topology for all folders |
| `/pyramid-label` | Before code review | Applies L0-L3 labels to all code units |
| `/pyramid-topology` | Before refactors | Full hierarchy integrity scan |
| `/ontology-review-gate` | Before implementation | Ontology Court — PASS required before coding |
| `/ontology-learning` | After any mistake | L3→L2→L1→L0 reverse analysis + memory evolution |
| `/odd-onboarding` | New project setup | Interactive project ontology initialization |

> **ODD is fully standalone** — all 8 skills and 13 hooks work without any other plugin. Optional: integrates with [superpowers](https://github.com/greptile/superpowers) for additional TDD, debugging, and planning skills.

---

## Active Hooks (13 registered)

Hooks enforce ODD governance automatically — no manual invocation needed.

### PreToolUse
| Hook | Trigger | Effect |
|------|---------|--------|
| `websearch_yearguard` | WebSearch | Blocks queries without current year |
| `destructive_bash_gate` | Bash | Blocks dangerous commands (force-delete, DROP TABLE, etc.) |
| `agent_pyramid_gate` | Agent | Requires L0 declaration + role spec for all Agent calls |
| `pyramid_ontology_gate` | Edit/Write/NotebookEdit | Blocks if no L0 declaration in session |
| `ontology_violation_gate` | Edit/Write/NotebookEdit | Enforces violation_registry.json rules |

### PostToolUse
| Hook | Trigger | Effect |
|------|---------|--------|
| `pptx_validate_hook` | Bash | Validates PPTX layout after build_*_ppt.py |
| `pyramid_guard` | Edit/Write | Verifies L0 connection after write |

### Stop
| Hook | Trigger | Effect |
|------|---------|--------|
| `tdd_enforce_stop` | Session end | Blocks if code edited without verification (docs exempt) |
| `ontology_declare_enforce` | Session end | Blocks if L0 declaration incomplete |
| `assumption_declaration_gate` | Session end | Blocks if strategy docs missing [가정 명시] |
| `git_push_enforce_stop` | Session end | Blocks if unpushed commits exist |
| `ontology_learning_enforce_stop` | Session end | Blocks if tool error occurred without /ontology-learning |

---

## Quick Start

```
# 1. Declare purpose before any task
/pyramid-ontology

# 2. Check bindings before writing code
/ontology-detach

# 3. Gate before implementation
/ontology-review-gate

# 4. Learn from every mistake
/ontology-learning
```

---

## Why ODD?

AI coding agents execute L3 (implementation) brilliantly while losing track of L0 (purpose). ODD solves this by:

1. **Forcing purpose declaration** before every action — no L0, no edit
2. **Detecting existence-clinging** — assumptions that become lies as environments change
3. **Gating implementation** — nothing gets built without hierarchy review
4. **Enforcing learning** — every mistake traces back to the principle that failed

---

## Docs

Full documentation: **[HHSsub.github.io/ontology-driven-design](https://HHSsub.github.io/ontology-driven-design)**

---

## License

MIT © 2025 [Hwang Hoe Sun (황회선)](https://knowgram.vercel.app)

Creator of Pyramid Thinking (피라미드사고법)
