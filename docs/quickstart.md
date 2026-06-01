# Quickstart — 5-Minute ODD Onboarding

> L0: A first-time developer understands ODD's core value and experiences the first hook block within 10 minutes.

This guide walks you through installing ODD, declaring your first L0, triggering a hook block, and passing it correctly — in under 5 minutes.

---

## Step 1 — Install (30 seconds)

```bash
claude plugin add HHSsub/ontology-driven-design
```

If the plugin command is unavailable in your Claude Code version, use manual install:

```bash
git clone https://github.com/HHSsub/ontology-driven-design.git
cp -r ontology-driven-design/skills/* ~/.claude/skills/
cp ontology-driven-design/commands/* ~/.claude/commands/
cp ontology-driven-design/hooks/* ~/.claude/hooks/
```

See [installation guide](./guide/installation.md) for dependencies and hook wiring details.

---

## Step 2 — Your First L0 Declaration (1 minute)

Start a new Claude Code session. Before doing anything else, declare your purpose:

```
L0: Users can submit bug reports without needing a GitHub account
L1: Add an anonymous issue form that posts to the project's issue tracker via API
L2: Form validation, API key storage, error handling
```

That's it. You have declared the pyramid. Claude now has permission to edit files in this session.

**Why L0 first?**

Without a stated purpose, any code change is directionless. The `pyramid_ontology_gate` hook enforces this structurally — no L0 means no file edits, full stop.

---

## Step 3 — Experience a Hook Block (2 minutes)

Open a fresh Claude Code session (without making an L0 declaration). Ask Claude to edit any file:

```
Edit app.py — add a print statement at the top
```

You will see this block message in the terminal:

```
══════════════════════════════════════════════
❌ L0 선언 없음 — Edit/Write 차단
══════════════════════════════════════════════
이번 세션에서 L0 선언을 한 적이 없습니다.
수정 전 반드시 목적을 선언하세요:

  L0: [이 수정이 달성하는 비즈니스 최종 목적]
  L1: [이 수정이 기여하는 시스템 목표]

선언 없이 코드 수정 = 방향 없는 행동
superpowers 설치 여부와 무관하게 적용됩니다.
══════════════════════════════════════════════
```

The file is **not modified**. The hook fires before the edit tool runs — not after.

This is the fundamental difference between ODD hooks and linting: linting catches problems after the fact. ODD blocks causally wrong actions at the source.

---

## Step 4 — Pass with a Correct L0 Declaration (1 minute)

In the same session, declare your L0 first, then repeat the request:

```
L0: Developers can trace execution flow without adding temporary debug code
L1: Add structured logging at key entry points

Now edit app.py — add a print statement at the top
```

The hook reads the session transcript, finds the `L0:` declaration, and allows the edit to proceed.

**The rule is simple:** One valid `L0:` declaration in the session is enough to unlock all subsequent file edits in that session.

---

## What Happens at Session End

When you finish working and Claude produces its final response, two more hooks fire:

- `ontology_declare_enforce` — verifies L0 was declared before any code was changed
- `tdd_enforce_stop` — verifies that code edits were followed by a verification command (e.g. `python -m py_compile`, `pytest`, `npm test`)

If you edited a file but never ran a test or compile check, the session-end hook blocks Claude's final response and demands verification.

---

## Next Steps

- [Getting Started](./guide/getting-started.md) — full workflow with all 7 skills
- [Hook reference](./skills/hooks.md) — all 10 hooks explained with block/pass examples
- [Solo developer workflow](./examples/solo-developer.md) — full day cycle with ODD
- [Legacy refactor guide](./examples/legacy-refactor.md) — gradual ODD adoption on existing codebases
- [Philosophy](./philosophy.md) — the Pyramid Thinking framework behind ODD
