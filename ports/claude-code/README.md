# ODD for Claude Code — Installation & Architecture

<!-- L0: Enable any Claude Code user to install and understand ODD in under 10 minutes -->

This is the canonical port of ODD (Ontology Driven Design). Claude Code is the primary platform for which ODD was built.

---

## Requirements

- Claude Code CLI (version supporting `hooks.json` plugin hook system)
- Python 3.9+ (for hook scripts)
- Git (for `git_push_enforce_stop.py`)

---

## Installation

### Method 1: Plugin Directory (Verified)

```bash
# Clone the repository
git clone https://github.com/HHSsub/ontology-driven-design.git

# Launch Claude Code with the plugin loaded
claude --plugin-dir ./ontology-driven-design
```

### Method 2: Plugin Add (Unverified — see ISSUE-003)

```bash
claude plugin add HHSsub/ontology-driven-design
```

**Status:** This command has not been tested on a clean Claude Code installation. If it fails, use Method 1. See `docs/audit/ISSUE_REGISTER.md` ISSUE-003 for details.

### Method 3: Global User Installation

Copy the plugin to your Claude configuration directory:

```bash
# Linux/macOS
cp -r ontology-driven-design ~/.claude/plugins/

# Windows (PowerShell)
Copy-Item -Recurse ontology-driven-design "$env:APPDATA\.claude\plugins\"
```

---

## How hooks.json Connects to Claude Code

ODD's `hooks/hooks.json` is the primary integration point with Claude Code's hook system.

### Hook Lifecycle

Claude Code supports three hook lifecycle points:

```
PreToolUse  → Runs BEFORE a tool is called
              Can block the tool call (exit code 2 + JSON message)
              Can warn but allow (exit code 0 + JSON message)

PostToolUse → Runs AFTER a tool completes
              Cannot block (action already taken)
              Can warn, log, trigger side effects

Stop        → Runs when Claude is about to end the session
              Can block session end (exit code 2)
              Used for enforcement: "session cannot end until X is done"
```

### Hook Registration Format

ODD's `hooks/hooks.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [{
          "type": "command",
          "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/pyramid_ontology_gate.py\""
        }]
      }
    ]
  }
}
```

- `matcher`: Tool name regex. `Edit|Write|NotebookEdit` matches any of the three.
- `CLAUDE_PLUGIN_ROOT`: Environment variable set by Claude Code to the plugin's directory.
- `type: "command"`: Runs the command, reads stdout for JSON response, reads exit code for block decision.

### Hook Response Protocol

Each hook script communicates with Claude Code via:

**Exit codes:**
- `0` — Pass (allow the tool call to proceed)
- `2` — Block (prevent the tool call, show message to Claude)

**Stdout (JSON):**
```json
{
  "decision": "block",
  "reason": "No L0 declaration found in session context."
}
```

ODD's hooks implement this protocol. Example from `pyramid_ontology_gate.py`:
```python
import sys, json

def main():
    # ... check for L0 declaration ...
    if not l0_found:
        print(json.dumps({"decision": "block", "reason": "..."}))
        sys.exit(2)
    sys.exit(0)
```

---

## How skills/ Connects to Claude Code Skill System

ODD's `skills/` directory contains skill definitions that Claude Code loads as slash commands.

### Skill Directory Structure

```
skills/
├── pyramid-ontology/
│   ├── SKILL.md          ← The skill definition (loaded by Claude Code)
│   └── SKILL-MAP.md      ← Optional: relationship map for this skill
├── ontology-learning/
│   └── SKILL.md
└── ...
```

### Skill Registration

Skills in `skills/<name>/SKILL.md` are automatically available as `/skill-name` once the plugin is loaded.

**Global commands** (available without plugin loading) live in `commands/<name>.md`. ODD registers 18 slash commands this way.

### Skill Invocation Pattern

Claude Code reads `SKILL.md` content and injects it into Claude's context when the skill is invoked. ODD's skills follow this pattern:

```markdown
# SKILL: pyramid-ontology

## Trigger
Any task start — code, report, analysis, any output.

## Protocol
1. Declare L0: [state the ultimate purpose]
2. Derive L1: [structure that achieves L0]
3. Derive L2: [modules that compose L1]
4. Derive L3: [concrete implementation]

## Enforcement
No L2/L3 action without L0 declaration.
```

---

## Environment Variable Reference

| Variable | Set By | Purpose |
|----------|--------|---------|
| `CLAUDE_PLUGIN_ROOT` | Claude Code | Absolute path to the plugin directory |
| `CLAUDE_SESSION_ID` | Claude Code | Current session identifier |
| `ODD_DEBUG` | User | Set to `1` to enable hook debug logging |

---

## Verifying Installation

After installation, run:

```bash
python hooks/pyramid_ontology_gate.py --test
```

Or run the full test suite:

```bash
python tests/test_hooks.py
```

Expected output: `Ran 77 tests in ~10s — OK`

---

## Known Limitations (Claude Code)

1. **`CLAUDE_SESSION_ID` not always set**: Some Claude Code versions do not set this variable. Hooks that read session context fall back to transcript file scanning.

2. **Transcript access**: ODD's Stop hooks read the session transcript to detect mistakes. The transcript path is inferred from Claude Code's data directory. If Claude Code changes this path, Stop hooks may fail to find the transcript.

3. **Hook timeout**: Claude Code may impose a hook execution timeout (typically 10-30 seconds). ODD's hooks are designed to be fast (< 1 second each), but Python startup time on Windows can be 200-500ms per hook.

4. **`Agent` tool matcher**: As of the current ODD version, registering a hook for the `Agent` tool type has not been verified to work in Claude Code's hook system. See `hooks/agent_pyramid_gate.py` — the hook exists but may not fire.
