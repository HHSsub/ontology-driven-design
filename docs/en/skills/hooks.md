# Auto-Enforced Hooks

The ODD plugin installs 3 hooks automatically. Hooks fire **without any user command** — every time Claude Code performs certain actions.

## Summary

| Hook | Type | Fires When | Checks |
|------|------|-----------|--------|
| `pyramid_ontology_gate` | PreToolUse | **Before** Edit/Write executes | Blocks the edit if no L0 declared in session |
| `pyramid_guard` | PostToolUse | After every Edit/Write save | L-level integrity + SSOT duplicate truth |
| `ontology_declare_enforce` | Stop | Every response completion | L0 declaration + dependency chain (post-check) |
| `git_push_enforce` | Stop | Every response completion | Session-edited files committed + pushed |

**Works without superpowers installed.** All hooks operate via Claude Code `settings.json` — independent of the superpowers plugin.

---

---

## pyramid_ontology_gate

**File**: `hooks/pyramid_ontology_gate.py`  
**Trigger**: PreToolUse — fires **before** `Edit`, `Write`, or `NotebookEdit` executes

### Key difference from Stop hook

`ontology_declare_enforce` (Stop hook) blocks after the edit is already done.  
`pyramid_ontology_gate` blocks **before the file changes** — prevents the edit entirely.

### What it checks

Searches the entire session transcript for at least one `L0:` declaration.  
If none found, the Edit/Write is blocked.

```
❌ BLOCKED: attempt to edit files with no L0 declared in this session
✅ PASS:    any "L0: ..." declaration anywhere in the session unlocks all edits
```

**Exempt from checking** (prevents infinite loops):
- `~/.claude/hooks/*.py` — hook files themselves
- `settings.json`, `hooks.json` — configuration files
- `CLAUDE.md`, `ONBOARDING.md` — onboarding/rule documents

---

## pyramid_guard

**File**: `hooks/pyramid_guard.py`  
**Trigger**: PostToolUse — fires after every `Edit` or `Write` tool call

### What it checks

**L2-A: L-level declaration presence**  
Verifies that `L0:`, `L1:` declarations exist in the file.

**L2-B: L0 content contamination**  
Blocks if L0 contains implementation details instead of business purpose.
```
❌ BLOCKED: L0: timeout within 10 seconds     (implementation constraint → belongs in L3)
❌ BLOCKED: L0: encode video with ffmpeg       (tool reference → belongs in L3)
✅ PASS:    L0: save user time — bot handles scheduling automatically
```

**L2-F: Ontology-detach violation**  
Detects hardcoded values without replacement conditions.

**L2-G: Duplicate Truth — SSOT violation**  
Blocks when the same concept set (3+ strings) appears independently in 2+ separate lists in the same file.
```python
# ❌ BLOCKED: these two lists overlap 60%+ — independent copies
COMMANDS = ["add", "del", "edit", "done"]
help_lines = {"add": "Add", "del": "Delete", "edit": "Edit"}

# ✅ PASS: help_lines derived from COMMANDS
help_lines = {cmd: descriptions[cmd] for cmd in COMMANDS}
```

This check is **domain-agnostic** — applies to any project regardless of language or stack.

---

## ontology_declare_enforce

**File**: `hooks/ontology_declare_enforce.py`  
**Trigger**: Stop — fires every time Claude finishes a response

### What it checks

**L2-A: L0 declaration check**  
If a turn included Edit/Write, verifies that the preceding assistant message contained an `L0:` declaration. Prevents code modification without purpose declaration.

**L2-B: Dependency chain verification**  
If an enumerable concept collection (list/dict/registry) was modified, blocks if there's no Grep evidence in the same turn.
```
❌ BLOCKED: Added item to COMMAND_REGISTRY → no grep found
✅ PASS:    Grep searched for dependents → then modified COMMAND_REGISTRY
```

---

## git_push_enforce

**File**: `hooks/git_push_enforce_stop.py`  
**Trigger**: Stop — fires every time Claude finishes a response

### What it checks

Tracks **only files actually edited this session** (ignores pre-existing dirty files).

1. Extracts file paths from Edit/Write calls in transcript
2. Intersects with `git status --porcelain` output
3. Blocks if session-edited files are uncommitted
4. Also blocks if committed but not pushed

```
❌ BLOCKED: modified bot.py → no git commit
❌ BLOCKED: modified alarm_manager.py → committed but not pushed
✅ PASS:    all modified files committed + pushed
```

---

## Verify Installation

Check hooks are installed correctly:

```bash
cat ~/.claude/settings.json | grep -A5 "hooks"
```

Your `~/.claude/settings.json` should contain:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/pyramid_guard.py" }]
      }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/ontology_declare_enforce.py" }] },
      { "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/git_push_enforce_stop.py" }] }
    ]
  }
}
```

[Installation guide →](/en/guide/installation)
