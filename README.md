# ODD — Ontology Driven Design

> **Purpose-less code is garbage. Code that works but has no purpose is failure.**

A Claude Code plugin that enforces purpose-driven AI workflows through the **Pyramid Thinking** (피라미드사고법) framework — created by [Hwang Hoe Sun](https://knowgram.vercel.app).

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin-blue)](https://claude.ai/code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/Docs-HHSsub.github.io-orange)](https://HHSsub.github.io/ontology-driven-design)

---

## 설치 (Installation)

```bash
# Full name
claude plugin add HHSsub/ontology-driven-design

# Short alias
claude plugin add HHSsub/odd
```

---

## The L0-L3 Framework

ODD enforces a 4-layer purpose hierarchy across every task — code, reports, emails, architecture decisions:

| Level | Meaning | Example |
|-------|---------|---------|
| **L0** | Business purpose — WHY | "Automate SNS upload without user intervention" |
| **L1** | System goal — HOW | "Music → Video → Upload end-to-end pipeline" |
| **L2** | Feature unit — WHAT | "Clip synthesis", "Metadata generation" |
| **L3** | Implementation — WITH WHAT | "Kling API polling", "ffmpeg concat" |

**Core rule:** Every action must trace back to L0. If you cannot state L0, stop.

---

## Skills (6)

| Skill | When to use |
|-------|-------------|
| `/pyramid-ontology` | Start of any task — declares L0-L3 as session law |
| `/ontology-detach` | Writing/reviewing bindings — detects existence-clinging |
| `/ontology-rebuild` | After major changes — rebuilds ONTOLOGY.md topology |
| `/pyramid-label` | Before code review — labels all code units L0-L3 |
| `/pyramid-topology` | Before refactors — full hierarchy integrity scan |
| `/ontology-review-gate` | Before implementation — Ontology Court (PASS required) |

---

## Quick Start

```
# 1. Start any session with purpose declaration
/pyramid-ontology

# 2. Before coding — check for existence-clinging
/ontology-detach

# 3. Before a major refactor — verify the whole hierarchy
/pyramid-topology

# 4. Gate before implementation
/ontology-review-gate
```

---

## Why ODD?

AI coding agents are powerful but directionless by default. They execute L3 (implementation) brilliantly while losing track of L0 (purpose). ODD solves this by:

1. **Forcing purpose declaration** before every action
2. **Detecting existence-clinging** — hardcoded assumptions that become lies as environments change
3. **Auditing hierarchy integrity** — every function traces back to a business goal
4. **Gating implementation** — nothing gets built without ontology review

---

## Docs

Full documentation: **[HHSsub.github.io/ontology-driven-design](https://HHSsub.github.io/ontology-driven-design)**

---

## Author

**황회선 (Hwang Hoe Sun)**  
Creator of Pyramid Thinking (피라미드사고법)  
[knowgram.vercel.app](https://knowgram.vercel.app)

---

## License

MIT
