# ODD Promotional Copy Assets

<!-- L0: ODD가 개발자 커뮤니티에 도달하여 실제 설치로 이어지게 하는 카피 자산 -->

All copy by Hwang Hoe Sun (황회선) — use as-is or adapt for each channel.

---

## X / Twitter (10 posts)

---

**Post 1 — Hook block experience**
```
Your AI just tried to edit a file.

ODD blocked it.

"❌ No L0 declaration found. State WHY this change needs to exist."

The AI cannot edit anything until it can answer that one question.

That's the whole product.

github.com/HHSsub/ontology-driven-design
```

---

**Post 2 — Problem framing**
```
AI coding agents are incredible at L3 (how to implement).

They are terrible at L0 (why this should exist at all).

The result: technically perfect code solving the wrong problem.

ODD is the Claude Code plugin that enforces the WHY before the WHAT.
```

---

**Post 3 — Not a prompt pack**
```
"Just add this to your system prompt: always ask about purpose"

I've seen this advice 100 times.

It doesn't work because Claude can ignore it.

ODD hooks intercept at the tool level. The edit tool is blocked before it runs.

You cannot bypass it by asking nicely.
```

---

**Post 4 — The L0-L3 framework**
```
Every piece of code exists at one of four levels:

L0 — Purpose: why does this exist?
L1 — Structure: what design achieves L0?
L2 — Logic: what did we choose and sacrifice?
L3 — Execution: the actual code

AI agents collapse everything to L3.
ODD enforces all four.

Free Claude Code plugin 👇
github.com/HHSsub/ontology-driven-design
```

---

**Post 5 — The session end hooks**
```
ODD doesn't just block edits without purpose.

It blocks you from ending the session if:
- You edited code without running tests
- An error occurred without root-cause analysis
- You have unpushed commits

The AI literally cannot say goodbye until the work is done right.
```

---

**Post 6 — Solo developer angle**
```
Solo devs: you have no code reviewer.

ODD is the reviewer that:
- Blocks edits without stated purpose
- Requires root cause analysis after every mistake
- Blocks session end with unpushed commits

13 hooks. 8 skills. Free.

github.com/HHSsub/ontology-driven-design
```

---

**Post 7 — Quick install**
```
Install ODD in 2 commands:

git clone github.com/HHSsub/ontology-driven-design
claude --plugin-dir ./ontology-driven-design

That's it. Your next edit attempt will be blocked until you state L0.

(You'll understand immediately why that's useful)
```

---

**Post 8 — The philosophy**
```
"Purpose-less code is garbage. Code that works but has no purpose is failure."

This is the principle behind ODD — a Claude Code plugin that enforces purpose hierarchy before every code change.

Built on Pyramid Thinking (피라미드사고법) by 황회선.
```

---

**Post 9 — Team angle**
```
Your team writes great code.

But six months later, nobody knows why half of it exists.

ODD forces every edit to declare L0 (the business reason). That declaration goes into the session context permanently.

The WHY is never lost.
```

---

**Post 10 — The ontology-learning skill**
```
When Claude makes a mistake, most systems: say sorry, try again.

ODD: triggers /ontology-learning

Phase 1: What happened exactly?
Phase 2: What judgment failure caused it?
Phase 3: What process was missing?
Phase 4: What worldview needs to change?
Phase 5: Write to memory. Enforce forever.

That's evolution, not patching.
```

---

## Product Hunt

**Name:** ODD — Ontology Driven Design

**Tagline:** The Claude Code plugin that blocks AI from coding without a purpose

**Description:**

ODD is a governance layer for Claude Code. It enforces a simple rule: before editing any file, state why the change needs to exist.

Not as a suggestion. As a hard block.

**How it works:**

ODD registers 13 hooks into Claude Code's tool lifecycle. When Claude tries to edit a file without a L0 (purpose) declaration in the session, the `pyramid_ontology_gate` hook fires and blocks the edit. Claude cannot proceed until it answers: "Why does this change need to exist?"

This is the L0-L3 framework:
- **L0** — Purpose: why does this exist?
- **L1** — Structure: what design achieves L0?
- **L2** — Logic: what decisions and trade-offs?
- **L3** — Execution: the actual code

**What you get:**

- 8 skills: `/pyramid-ontology`, `/ontology-learning`, `/ontology-review-gate`, and 5 more
- 13 auto-firing hooks covering PreToolUse, PostToolUse, and session-end enforcement
- The `ontology-learning` skill: when a mistake occurs, traces it back to the root principle (not just the symptom) and writes enforcement rules to memory
- Session-end enforcement: can't quit until errors are analyzed, commits are pushed, and tests pass

**Who it's for:**

- Solo developers using Claude Code daily who want their AI to stay on purpose
- Teams tired of AI-generated code that works but doesn't connect to any business goal
- Anyone who has experienced "vibe coding drift" — where the AI starts solving a different problem than the one you asked about

**Install in 2 commands:**
```
git clone https://github.com/HHSsub/ontology-driven-design
claude --plugin-dir ./ontology-driven-design
```

Free and open source (MIT). Built by Hwang Hoe Sun (황회선), creator of Pyramid Thinking (피라미드사고법).

---

## Hacker News — Show HN

**Title:** Show HN: ODD – Claude Code plugin that blocks AI from editing files without stating purpose

**Post body:**

```
I built a Claude Code plugin that enforces a single rule: before Claude edits any file, it must state L0 — the business reason the change needs to exist.

Not as a prompt suggestion. As a hard hook that blocks the Edit tool before it runs.

The plugin registers 13 Python hooks into Claude Code's hook lifecycle:
- pyramid_ontology_gate: blocks Edit/Write if no L0 declaration in session
- ontology_detach_gate: blocks structural edits without a prior "replacement condition" check
- 5 session-end hooks: block session termination until errors are analyzed, commits are pushed, tests pass

The L0-L3 framework it enforces:
- L0: Why does this exist? (existence-level purpose)
- L1: What design achieves L0? (structure)
- L2: What did we choose and sacrifice? (trade-offs)
- L3: The actual code

The "ontology-learning" skill is the part I'm most proud of: when a mistake occurs, it traces back through L3 → L2 → L1 → L0 to find the root principle that failed, writes a memory file, and adds an enforcement rule to violation_registry.json. The AI can't just apologize and move on — it has to evolve.

Built on Pyramid Thinking (피라미드사고법) — a 4-layer knowledge organization framework I've been developing.

GitHub: https://github.com/HHSsub/ontology-driven-design
Docs: https://HHSsub.github.io/ontology-driven-design

Happy to discuss the hook architecture, the L0-L3 framework design, or the ontology-learning evolution mechanism.
```

---

## LinkedIn (3 posts)

---

**LinkedIn Post 1 — Professional / governance angle**

```
Most teams have coding standards. Almost none have purpose standards.

Your linter checks syntax. Your CI checks tests. Nothing checks whether the code being written connects to a business reason.

I built ODD — a Claude Code plugin that enforces purpose at the tool level.

Before Claude edits any file, it must declare L0: the existence-level reason the change needs to happen. If it can't, the edit is blocked.

This is the L0-L3 framework:
• L0 — Purpose: why does this need to exist?
• L1 — Structure: what design achieves L0?
• L2 — Logic: what decisions and trade-offs?
• L3 — Execution: the actual code

AI agents are exceptional at L3. They drift away from L0.

ODD keeps them anchored.

Free, open source, MIT license.
→ github.com/HHSsub/ontology-driven-design

#AIcoding #ClaudeCode #SoftwareEngineering #DeveloperTools
```

---

**LinkedIn Post 2 — Thought leadership / Pyramid Thinking**

```
I've spent years developing Pyramid Thinking (피라미드사고법) — a framework for organizing knowledge vertically, not horizontally.

The insight: most knowledge systems accumulate facts at the same level. Pyramid Thinking enforces hierarchy: every fact connects upward to a purpose, and every action connects downward to an instance.

I recently applied this to AI coding agents.

The result is ODD — Ontology Driven Design. A Claude Code plugin that enforces the L0-L3 hierarchy before every code change:

L0 (Purpose) → L1 (Structure) → L2 (Logic) → L3 (Code)

The plugin's 13 hooks block any edit that can't trace back to L0.

When I look at AI-generated codebases six months after they're built, the most common failure isn't technical — it's purposive. The code works, but nobody can explain why it's built the way it is.

ODD is the enforcement layer that prevents that.

→ github.com/HHSsub/ontology-driven-design

#PyramidThinking #AIGovernance #KnowledgeManagement
```

---

**LinkedIn Post 3 — Personal / creator story**

```
I got frustrated with my own AI coding sessions.

The code was technically fine. But a week later, I'd look at a function and realize I had no memory of why it existed. Claude had answered "how to implement X" perfectly and completely forgotten "why X should exist at all."

I built ODD to solve this for myself first.

Now every session starts with a forced declaration of L0. The hooks won't let Claude edit anything until that question is answered in writing.

Six months of using it: the codebase stays coherent in a way it never did before. Not because the code is better — because the purpose is always visible.

ODD is free. Claude Code + git + Python 3.9+ is all you need.

→ github.com/HHSsub/ontology-driven-design

Built by 황회선 (Hwang Hoe Sun), creator of 피라미드사고법.
```

---

## Gumroad — Premium Pack Product Description

**Product title:** ODD Premium Pack — Advanced Hooks + Eval Skill

**Subtitle:** The enforcement layer that activates when things go wrong

**Description:**

ODD core is free (GitHub). The Premium Pack adds the protection patterns extracted from months of real daily use — the ones that catch mistakes after they happen and force the right recovery.

**5 advanced global hooks** (fire in every Claude Code session, across all your projects):

**`post_error_ontology_gate`** — Error → Forced Evolution Checkpoint
> After any tool error, all Bash/Write/Edit calls are blocked until `/ontology-learning` is invoked. Eliminates the retry loop — forces root-cause diagnosis before the next action.

**`edit_freshness_gate`** — Read-Before-Edit Enforcement
> Blocks `Edit` on config/JSON/settings files if no `Read` was done in the current session. Prevents "String to replace not found" failures and stale-state edits on critical files.

**`context_complexity_gate`** — Parallel Agent Advisory
> When 3+ independent tasks are queued in `TodoWrite` without a prior `Agent` dispatch, warns to use parallel agents. Prevents single-context overload on multi-domain work.

**`ontology_graph_gate`** — Semantic Graph File Protection
> Reads `ontology_graph.json` to determine file semantics. Blocks writes to files marked immutable, detects internal jargon in external-facing docs. Extend by editing JSON — no Python changes needed.

**`python3_guard`** *(Windows)* — Python Command Enforcement
> Blocks `python3` in Bash commands on Windows. Automatically exempts SSH remote execution.

**1 exclusive skill:**

**`/persona-driven-eval-loop`** — External Recipient Evaluation
> A 6-phase structured loop for outputs that must work for someone else. Define recipient persona → lock evaluation criteria before generating → generate → external agent scores → iterate → PASS only at ≥80%. Structurally eliminates self-grading.

**`ontology_graph.json`** — Configurable Knowledge Graph
> The data file for `ontology_graph_gate`. Add your project's locked files, audience rules, and internal terminology here. The gate adapts without touching Python.

---

**Free ODD vs Premium Pack — the real difference:**

The free ODD repo on GitHub is the creator's personal setup, built in Korean for their own daily workflow. The Premium Pack is engineered for **global developers** — all hook messages, documentation, and skill instructions are in English. Every block, warning, and error is readable by anyone using Claude Code worldwide, regardless of language background.

---

**You don't configure ODD Premium — you just work.**

The hooks run silently in the background of every Claude Code session. When they fire, they don't just block — they explain the principle being enforced. Your Claude setup becomes more structured over time, not because you spent time configuring it, but because the hooks enforce the right recovery every time something goes wrong.

---

**Who this is for:**

- Developers using Claude Code daily who want protection beyond the free plugin
- Anyone who has hit "String to replace not found" or the retry loop after errors
- Windows users running Claude Code with Python projects
- Teams where AI-generated outputs need to pass external review, not self-assessment

**Prerequisites:** ODD free plugin + Claude Code + Python 3.8+

**License:** Personal/team use. Not for redistribution.

**Questions:** hhoesun@gmail.com

---

*All copy assets — Hwang Hoe Sun (황회선), 2026*
