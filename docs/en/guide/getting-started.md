# Getting Started

## Installation

```bash
# Full name
claude plugin add HHSsub/ontology-driven-design

# Short alias (identical)
claude plugin add HHSsub/odd
```

## Basic Workflow

### 1. Session Start — Declare Purpose

Before any task, invoke `/pyramid-ontology` or declare directly:

```
L0: [the business purpose this task must achieve]
L1: [the system goal — path to achieving L0]
L2: [the feature unit being implemented now]
```

### 2. While Coding — De-Existence Check

When adding hardcoded values or bindings:

```bash
/ontology-detach
```

Ask yourself: **"What is the exit condition for this binding?"** — If the answer is "none", it's a violation.

### 3. Before Refactoring — Hierarchy Check

```bash
/pyramid-topology
```

Detects unlabeled units, L0 pollution, and orphan files.

### 4. Before Implementation — Review Gate

```bash
/ontology-review-gate
```

PASS required before writing any code.

### 5. After Completion — Update Topology

```bash
/ontology-rebuild
```

Updates ONTOLOGY.md for all folders.

## Next Steps

- [All Skills](/en/skills/) — Detailed usage for each skill
- [Philosophy](/en/philosophy) — The Pyramid Thinking foundation of ODD
