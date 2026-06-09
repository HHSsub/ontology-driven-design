# Getting Started

## Installation

**Step 1 — Add the marketplace** (in a Claude Code session):

```
/plugin marketplace add HHSsub/ontology-driven-design
```

**Step 2 — Install the plugin**:

```
/plugin install ontology-driven-design@HHSsub/ontology-driven-design
```

**Step 3 — Reload plugins**:

```
/reload-plugins
```

> **Local test without installing:** `claude --plugin-dir ./ontology-driven-design`

## Basic Workflow

### 1. Session Start — Declare Purpose

Before any task, invoke `/ontology-driven-design:pyramid-ontology` or declare directly:

```
L0: [the business purpose this task must achieve]
L1: [the system goal — path to achieving L0]
L2: [the feature unit being implemented now]
```

### 2. While Coding — De-Existence Check

When adding hardcoded values or bindings:

```bash
/ontology-driven-design:ontology-detach
```

Ask yourself: **"What is the exit condition for this binding?"** — If the answer is "none", it's a violation.

### 3. Before Refactoring — Hierarchy Check

```bash
/ontology-driven-design:pyramid-topology
```

Detects unlabeled units, L0 pollution, and orphan files.

### 4. Before Implementation — Review Gate

```bash
/ontology-driven-design:ontology-review-gate
```

PASS required before writing any code.

### 5. After Completion — Update Topology

```bash
/ontology-driven-design:ontology-rebuild
```

Updates ONTOLOGY.md for all folders.

## Next Steps

- [All Skills](/en/skills/) — Detailed usage for each skill
- [Philosophy](/en/philosophy) — The Pyramid Thinking foundation of ODD
