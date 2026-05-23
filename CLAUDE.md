# ODD — Ontology Driven Design

A Claude Code plugin by **Hwang Hoe Sun** (황회선) — creator of Pyramid Thinking (피라미드사고법).

## Plugin Skills

This plugin provides 6 skills for purpose-driven AI workflows:

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `pyramid-ontology` | Any task start | Declares L0-L3 hierarchy as governing law |
| `ontology-detach` | Writing/reviewing code with bindings | Detects existence-clinging, enforces exit conditions |
| `ontology-rebuild` | After major changes | Rebuilds ONTOLOGY.md topology for all folders |
| `pyramid-label` | Before code review | Applies L0-L3 labels to all code units |
| `pyramid-topology` | Before refactors | Full hierarchy integrity scan |
| `ontology-review-gate` | Before any implementation | Ontology Court — PASS required before coding |

## The L0-L3 Hierarchy

Every action must connect to a purpose. No exceptions.

```
L0  Business purpose      WHY this exists
L1  System/doc goal       HOW it achieves L0
L2  Feature unit          WHAT gets built
L3  Implementation        WITH WHAT tools
```

**Rule:** If you cannot state L0, stop. Ask first.

## Slash Commands

All skills are also available as slash commands:
- `/pyramid-ontology` — declare L0-L3 for this session
- `/ontology-detach` — run de-existence check
- `/ontology-rebuild` — rebuild topology docs
- `/pyramid-label` — label all code units
- `/pyramid-topology` — scan hierarchy integrity
- `/ontology-review-gate` — run ontology court

## Philosophy

ODD is built on **Pyramid Thinking** (피라미드사고법) — a 4-layer ontology framework that organizes fragmented horizontal knowledge into a vertical hierarchy of purpose.

> "Purpose-less code is garbage. Code that works but has no purpose is failure."

Learn more: [ontology-driven-design docs](https://HHSsub.github.io/ontology-driven-design)
