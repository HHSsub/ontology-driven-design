---
layout: home
title: ODD — Ontology Driven Design
hero:
  name: "ODD"
  text: "Ontology Driven Design"
  tagline: "A purpose-governed engineering layer for AI coding agents. Prevents vibe-code drift by enforcing conceptual hierarchy before code changes happen."
  actions:
    - theme: brand
      text: 5-min Quickstart
      link: /en/guide/getting-started
    - theme: alt
      text: GitHub
      link: https://github.com/HHSsub/ontology-driven-design
    - theme: alt
      text: 한국어
      link: /

features:
  - icon: 🎯
    title: Purpose Enforcement
    details: "pyramid-ontology: No edit starts without declaring L0 (the deepest reason this must exist). Applies to code, reports, emails — any output."
  - icon: 🔓
    title: De-Existence Principle
    details: "ontology-detach: Every binding must state its exit condition. Hardcoding is a lie — it will break as environments change."
  - icon: 🧠
    title: Permanent Learning
    details: "ontology-learning: Every mistake traces back L3→L2→L1→L0. Findings become rules. ODD evolves from its own errors — and yours."
  - icon: ⚖️
    title: Implementation Gate
    details: "ontology-review-gate: Ontology Court before any implementation. PASS required before writing code. Prevents premature L3 execution."
  - icon: 📐
    title: Hierarchy Integrity
    details: "pyramid-topology: Detects unlabeled units, L0 pollution, orphan files, circular dependencies. Required before refactors."
  - icon: 🗺️
    title: Topology Maps
    details: "ontology-rebuild: Auto-generates L0-L3 topology docs for the entire project. Every folder gets an ONTOLOGY.md."
  - icon: 🏷️
    title: Hierarchy Labeling
    details: "pyramid-label: Applies L0-L3 labels to all code units in any language or file type."
  - icon: 🔒
    title: Auto-Enforced Hooks
    details: "13 hooks enforce ODD governance automatically. Block purposeless edits, detect SSOT violations, enforce TDD — before damage is done."
---

## The L0-L3 Hierarchy

ODD enforces a 4-layer purpose hierarchy across every output.

| Level | Layer | Question | Cannot Be |
|-------|-------|---------|-----------|
| **L0** | Purpose / Ontology | *Why must this exist at all?* | Stated in terms of tools or platforms |
| **L1** | Architecture / Structure | *What is the invariant design?* | Changed without changing L0 |
| **L2** | Decision / Trade-off | *What did we choose and what did we give up?* | Undocumented |
| **L3** | Execution / Instance | *What is the concrete act?* | Orphaned from L0 |

**Core rule:** If you cannot state L0, stop. The action has no purpose.

> ODD is self-applicable: the same L0-L3 discipline that governs your code governed the development of ODD itself. [Case Study →](/en/guide/getting-started)

---

## Installation

```bash
claude plugin add HHSsub/ontology-driven-design
```

> Note: Verify this works on your Claude Code version. [Manual install →](/en/guide/installation)

---

*Created by [Hwang Hoe Sun (황회선)](https://knowgram.vercel.app) · Based on Pyramid Thinking (피라미드사고법)*
