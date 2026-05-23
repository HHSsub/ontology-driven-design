# Skills

ODD provides 6 skills implementing the Pyramid Thinking principles.

## Skill Reference

| Skill | Command | When to use |
|-------|---------|-------------|
| [pyramid-ontology](./pyramid-ontology) | `/pyramid-ontology` | **Start of every task** — declare L0-L3 |
| [ontology-detach](./ontology-detach) | `/ontology-detach` | Writing or reviewing code bindings |
| [ontology-rebuild](./ontology-rebuild) | `/ontology-rebuild` | After major changes — update topology |
| [pyramid-label](./pyramid-label) | `/pyramid-label` | Before code review — label all units |
| [pyramid-topology](./pyramid-topology) | `/pyramid-topology` | Before refactors — check integrity |
| [ontology-review-gate](./ontology-review-gate) | `/ontology-review-gate` | Before implementation — court review |

## Skill Hierarchy

```
pyramid-ontology          ← Top-level — constitution for all skills
  ├── ontology-detach     ← L0 applied to bindings
  ├── ontology-rebuild    ← Topology documentation
  ├── pyramid-label       ← Code unit labeling
  ├── pyramid-topology    ← Hierarchy integrity check
  └── ontology-review-gate ← Pre-implementation gate
```

## Recommended Order

```bash
/pyramid-ontology       # 1. Start
/ontology-detach        # 2. During coding
/pyramid-topology       # 3. Before refactor
/ontology-review-gate   # 4. Before implementation
/pyramid-label          # 5. Before review
/ontology-rebuild       # 6. After completion
```
