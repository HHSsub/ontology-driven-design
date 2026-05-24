# Skills

ODD operates in two modes: skills (manual invocation) and hooks (automatic enforcement).

## Skills — Manual invocation (`/command`)

| Skill | Command | When to use |
|-------|---------|-------------|
| [odd-onboarding](./odd-onboarding) | `/odd-onboarding` | **Before any project/feature** — lock in L0 purpose |
| [pyramid-ontology](./pyramid-ontology) | `/pyramid-ontology` | **Start of every task** — declare L0-L3 |
| [ontology-detach](./ontology-detach) | `/ontology-detach` | Writing or reviewing code bindings |
| [ontology-rebuild](./ontology-rebuild) | `/ontology-rebuild` | After major changes — update topology |
| [pyramid-label](./pyramid-label) | `/pyramid-label` | Before code review — label all units |
| [pyramid-topology](./pyramid-topology) | `/pyramid-topology` | Before refactors — check integrity |
| [ontology-review-gate](./ontology-review-gate) | `/ontology-review-gate` | Before implementation — court review |

## Hooks — Automatic enforcement (no user command needed)

| Hook | Fires When | Checks |
|------|-----------|--------|
| [pyramid_guard](./hooks) | Every Edit/Write save | L-level integrity + SSOT violations |
| [ontology_declare_enforce](./hooks) | Every response completion | L0 declaration + dependency chain |
| [git_push_enforce](./hooks) | Every response completion | Uncommitted/unpushed session files |

→ [Hook details](./hooks)

## Skill Hierarchy

```
odd-onboarding            ← Before start — establishes project constitution
pyramid-ontology          ← Top-level — constitution for all skills
  ├── ontology-detach     ← L0 applied to bindings
  ├── ontology-rebuild    ← Topology documentation
  ├── pyramid-label       ← Code unit labeling
  ├── pyramid-topology    ← Hierarchy integrity check
  └── ontology-review-gate ← Pre-implementation gate
```

## Recommended Order

```bash
# 0. Before any project or feature
/odd-onboarding

# 1. Start of session
/pyramid-ontology

# 2. During coding (hooks auto-monitor SSOT + L0 contamination)
/ontology-detach

# 3. Before refactors
/pyramid-topology
/ontology-review-gate

# 4. After completion
/pyramid-label
/ontology-rebuild
```
