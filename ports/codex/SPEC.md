# ODD Port Specification: OpenAI Codex CLI

<!-- L0: Define how ODD's governance principles can be adapted to Codex CLI's extension system -->

**Status:** Specification only. No implementation. Requires Codex CLI access to validate.

**Last verified Codex CLI version referenced:** Codex CLI (OpenAI, 2025). Official docs at https://github.com/openai/codex

---

## 1. Codex CLI Architecture Overview

OpenAI Codex CLI is a terminal-based AI coding assistant. Its extension model differs from Claude Code in key ways:

| Feature | Claude Code | Codex CLI |
|---------|-------------|-----------|
| Hook system | `hooks.json` with PreToolUse/PostToolUse/Stop lifecycle | Skills system (as of 2025); hook lifecycle TBD |
| Plugin format | Directory with `plugin.json` + `hooks.json` | `~/.codex/instructions.md` + Skills |
| Skill invocation | Slash commands registered in `commands/` | Markdown files in `~/.codex/skills/` (miconfirmed) |
| Session transcript | Accessible via CLAUDE_DATA_DIR | Not confirmed |
| Tool names | Edit, Write, Bash, WebSearch, Agent | Apply, Shell (approximately) |

**Note:** Codex CLI's extension/hook API is not stable as of 2026-05-30. This specification is based on publicly available information and may require revision.

---

## 2. ODD Concept Mapping to Codex

### 2.1 L0 Declaration Enforcement

**Claude Code approach:** `pyramid_ontology_gate.py` intercepts `Edit|Write|NotebookEdit` tool calls via `PreToolUse` hook. Reads session transcript to find `L0:` declaration. Blocks if absent.

**Codex CLI adaptation:**

Codex uses an `instructions.md` file (`~/.codex/instructions.md`) that is injected into every session. This is the primary control surface.

```markdown
# ~/.codex/instructions.md (ODD adaptation)

## L0 Declaration Rule
Before any file edit (Apply tool), you must state:
"L0: [purpose of this edit]"

If you cannot state L0, ask the user to clarify before proceeding.
This is not optional. Do not apply changes without a stated L0.

## L1-L3 Hierarchy
L1: System/architectural goal (how L0 is achieved)
L2: Module/component logic (what trade-offs are made)
L3: Concrete code (the physical implementation)

Label code comments accordingly: # L0:, # L1:, # L2:, # L3:
```

**Limitation:** Unlike Claude Code's hook system, `instructions.md` enforcement is behavioral (Claude follows instructions) rather than mechanical (hook blocks tool call). This means:
- No hard block — only soft guidance
- Effectiveness depends on model compliance

**Workaround:** Codex CLI supports pre/post hooks via shell scripts in some versions. If `~/.codex/hooks/pre-apply.sh` is supported:

```bash
#!/bin/bash
# pre-apply.sh: Check for L0 declaration in recent output
# This is a best-effort approximation — no transcript access confirmed

if [ -z "$CODEX_SESSION_L0" ]; then
    echo "ERROR: L0 not declared. Set CODEX_SESSION_L0 before applying changes."
    exit 1
fi
```

### 2.2 Hook Lifecycle Mapping

| ODD Hook | Claude Code Lifecycle | Codex CLI Equivalent |
|----------|----------------------|---------------------|
| `pyramid_ontology_gate` | PreToolUse (Edit/Write) | `pre-apply.sh` (if supported) or instructions.md behavioral |
| `websearch_yearguard` | PreToolUse (WebSearch) | `pre-websearch.sh` (if supported) |
| `tdd_enforce_stop` | Stop | `post-session.sh` (if supported) |
| `ontology_declare_enforce` | Stop | `post-session.sh` (if supported) |
| `pyramid_guard` | PostToolUse (Edit/Write) | `post-apply.sh` (if supported) |
| `destructive_bash_gate` | PreToolUse (Bash) | `pre-shell.sh` (if supported) |

**Critical gap:** Codex CLI's `Stop`-equivalent lifecycle (session end hook) is not confirmed in public documentation. The ODD hooks that enforce L0 declaration and TDD discipline at session end cannot be ported until this lifecycle point is confirmed.

### 2.3 Skills System

**Claude Code approach:** `skills/<name>/SKILL.md` files loaded as slash commands.

**Codex CLI adaptation:**

If Codex CLI supports a `~/.codex/skills/` directory with `.md` files:

```
~/.codex/skills/
├── pyramid-ontology.md   ← copy of skills/pyramid-ontology/SKILL.md
├── ontology-learning.md  ← copy of skills/ontology-learning/SKILL.md
└── ...
```

If not, skills must be embedded in `instructions.md` as behavioral rules.

---

## 3. L0 Enforcement Priority Order

Given Codex CLI's weaker hook system, implement ODD principles in this priority order:

1. **instructions.md** — behavioral enforcement (works in all versions)
2. **pre-apply.sh** — mechanical enforcement for file edits (if supported)
3. **post-session.sh** — Stop-equivalent enforcement (if supported)
4. **Skill files** — L0-contextualized workflows (if skills directory supported)

---

## 4. Minimum Viable ODD for Codex CLI

If only `instructions.md` is available, use this minimal adaptation:

```markdown
# ODD Minimal (Codex CLI)

Before every file edit:
1. State "L0: [why this file edit exists]"
2. If you cannot state L0, ask the user.

Before every web search:
1. Include the current year in the query.

Before session end:
1. Confirm at least one test was run if code was modified.
2. If no test was run, ask the user to run tests before ending.

Label all code changes with:
  # L0: <purpose>
  # L3: <implementation detail>
```

---

## 5. Validation Requirements

Before publishing this port as "verified":

- [ ] Test `pre-apply.sh` hook trigger on file edit
- [ ] Test `post-session.sh` hook trigger on session end
- [ ] Confirm `~/.codex/skills/` directory is scanned for skill files
- [ ] Confirm `$CODEX_SESSION_*` environment variables available in hooks
- [ ] Test with Codex CLI version (record exact version tested)

---

## 6. Port Maintainer Notes

This specification was written based on:
- OpenAI Codex CLI public repository (github.com/openai/codex)
- Claude Code hook system documentation (used as reference for contrast)
- ODD architecture as implemented in `hooks/hooks.json`

Verified information is marked as confirmed. Unverified assumptions are marked as "TBD" or "if supported."
