---
layout: home
title: ODD — Ontology Driven Design
hero:
  name: "ODD"
  text: "Ontology Driven Design"
  tagline: "Purpose-less code is garbage. Code that works but has no purpose is failure."
  actions:
    - theme: brand
      text: Get Started
      link: /en/guide/getting-started
    - theme: alt
      text: GitHub
      link: https://github.com/HHSsub/ontology-driven-design
    - theme: alt
      text: 한국어
      link: /

features:
  - icon: 🎯
    title: Purpose Enforcement (pyramid-ontology)
    details: No task starts without declaring L0 (business purpose). Applies to code, reports, emails — every output.
  - icon: 🔓
    title: De-Existence Principle (ontology-detach)
    details: Every binding must have an exit condition. Hardcoding is a lie — it will break as environments change.
  - icon: 🗺️
    title: Topology Rebuild (ontology-rebuild)
    details: Auto-generates L0-L3 topology maps for the entire project. Per-folder ONTOLOGY.md + root _WIKI.md.
  - icon: 🏷️
    title: Hierarchy Labeling (pyramid-label)
    details: Applies L0-L3 labels to all code units in any language — Python, TypeScript, Go, YAML, Markdown.
  - icon: 📐
    title: Integrity Check (pyramid-topology)
    details: Detects unlabeled units, L0 pollution, orphan files, and circular dependencies. Required before refactors.
  - icon: ⚖️
    title: Review Gate (ontology-review-gate)
    details: Ontology Court review before any implementation. PASS required before writing code.
---

## Installation

```bash
claude plugin add HHSsub/ontology-driven-design
# or short alias
claude plugin add HHSsub/odd
```

## The L0-L3 Hierarchy

```
L0  Business purpose    WHY — why does this exist
L1  System goal         HOW — how does it achieve L0
L2  Feature unit        WHAT — what gets built
L3  Implementation      WITH WHAT — which tools
```

**Rule:** If you cannot state L0, stop and ask first.

---

*Created by [Hwang Hoe Sun (황회선)](https://knowgram.vercel.app) · Based on Pyramid Thinking (피라미드사고법)*
