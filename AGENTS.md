# ODD — Ontology Driven Design (AGENTS.md)

This file is for AI agents operating in this repository.

## Plugin Skills Available

Before taking any action, invoke the appropriate skill:

- `pyramid-ontology` — declare L0-L3 hierarchy BEFORE any task
- `ontology-detach` — check bindings for exit conditions
- `ontology-rebuild` — rebuild topology docs after changes
- `pyramid-label` — label code units with L0-L3
- `pyramid-topology` — verify hierarchy integrity
- `ontology-review-gate` — gate before any implementation

## Mandatory Rule

**State L0 before any action.** If you cannot answer "what business purpose does this serve?", stop and ask.

```
L0: [business purpose]
L1: [system goal]
L2: [feature unit being built]
```

See CLAUDE.md for full plugin documentation.
