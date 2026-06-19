# Auto-Enforced Hooks

The ODD plugin installs several hooks automatically. Hooks fire **without any user command** — every time Claude Code performs certain actions.

## Core architecture — Pattern hooks vs Agent judges

Hooks split into two layers. This distinction is the foundation of ODD enforcement.

| Layer | Catches | How | Examples |
|-------|---------|-----|----------|
| **Pattern hooks** (deterministic) | **Fixed-pattern** violations — shell syntax, filename rules, banned keywords, path filters | Regex/string matching. Instant, free, deterministic | `websearch_yearguard`, `python3_guard`, `git_push_enforce_stop` |
| **Agent judges** (semantic) | **Meaning** violations — is this L0 a real purpose, was the premise analyzed, was completion declared without external verification | Delegated to an LLM (cheap model) as a natural-language judgment | `semantic_judge_gate` |

**Invariant principle: semantic judgment is never faked with patterns — it is always done by an agent.**

Regex catches only surface patterns. Judgments like "did this L0 disguise an implementation detail as a purpose", "did it change existing code without analyzing the premise", "did it repeat a failing approach without rethinking L1" have ten-million expressions — regex won't catch ten of them. Meaning must be judged by meaning — i.e. by an **agent (LLM judge)**.

Endlessly stacking rules into a regex file (case accumulation) is an L3 patch and a sign of evolutionary failure. Use pattern hooks only for truly mechanical violations; delegate everything that requires judgment to an agent.

---

## Summary

### PreToolUse — Block Before Execution

| Hook | Fires When | Checks |
|------|-----------|--------|
| `pyramid_ontology_gate` | **Before** Edit/Write/NotebookEdit | Blocks edit if no L0 declared in session |
| `ontology_violation_gate` | **Before** Edit/Write/NotebookEdit | Checks violation_registry.json rules |
| `assumption_declaration_gate` | **Before** Edit/Write/NotebookEdit | Blocks strategy .md without [가정 명시] |
| `websearch_yearguard` | **Before** WebSearch | Blocks queries without current year |

### PostToolUse — Verify After Execution

| Hook | Fires When | Checks |
|------|-----------|--------|
| `pyramid_guard` | After every Edit/Write save | L-level integrity + SSOT duplicate truth |
| `git_commit_push_check` | After Bash commands | Warns if unpushed commits after git commit |
| `pptx_validate_hook` | After Bash commands | Validates PPTX layout overflow after build_*_ppt.py |

### Stop — Enforce at Session End

| Hook | Checks |
|------|--------|
| `ontology_declare_enforce` | L0 declaration + dependency chain verification |
| `git_push_enforce_stop` | Session-edited files committed + pushed |
| `tdd_enforce_stop` | Blocks if no verification after Edit/Write |

**Works without superpowers installed.** All hooks operate via Claude Code `settings.json` — independent of the superpowers plugin.

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

## ontology_violation_gate

**File**: `hooks/ontology_violation_gate.py`  
**Trigger**: PreToolUse — fires **before** `Edit`, `Write`, or `NotebookEdit` executes

### Architecture

Reads `violation_registry.json` and applies registered rules in sequence.  
When a new mistake is discovered, **add a rule to the registry** — do not modify the Python file.

### Supported check types

- `heading_structure` — detects educational/explanatory heading patterns in markdown
- `section_outcome_grounding` — blocks sections with no business outcome or action link
- `content_pattern` — detects code patterns (regex) in file content

### Path filtering

Each rule has a `path_must_contain_any` filter — fires **only on matching paths**.  
No interference with other projects.

---

## assumption_declaration_gate

**File**: `hooks/assumption_declaration_gate.py`  
**Trigger**: PreToolUse — fires **before** `Edit`, `Write`, or `NotebookEdit` executes

### Applies to

`.md` files whose path contains: `사업부`, `전략실행`, `역공학`, `당장파이프라인`, `strategy`, or `strategic`.

### What it checks

Requires at least one of the following in the file content:
- `[가정 명시]` / `[가정]` / `가정:` / `전제:`
- `미확인:` / `확인됨:`
- `assumption:` / `premise:`

```
❌ BLOCKED: strategy doc with conclusions but no assumption list
✅ PASS:    contains "[가정 명시] - 가정 1: ... → 검증 상태: 미검증"
```

---

## websearch_yearguard

**File**: `hooks/websearch_yearguard.py`  
**Trigger**: PreToolUse — fires **before** `WebSearch` executes

### What it checks

Blocks if query lacks the current year (`datetime.now().year`) or keywords: `최신`, `current`, `latest`, `today`.

```
❌ BLOCKED: "Vercel pricing plans"
✅ PASS:    "Vercel pricing plans 2026"
```

Any external information — services, APIs, pricing, policies — must be searched with the current year.

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
✅ PASS:    L0: save user time — bot handles scheduling automatically
```

**L2-F: Ontology-detach violation**  
Detects hardcoded values without replacement conditions.

**L2-G: Duplicate Truth — SSOT violation**  
Blocks when the same concept set (3+ strings) appears independently in 2+ separate lists in the same file.

---

## git_commit_push_check

**File**: `hooks/git_commit_push_check.py`  
**Trigger**: PostToolUse — fires after Bash commands that include `git commit`

### What it checks

Warns (stderr) if there are unpushed commits after a commit.  
Covers the gap between commits and session-end enforcement by `git_push_enforce_stop`.

```
⚠️  git commit done — not pushed yet
    run: git push origin main
```

---

## pptx_validate_hook

**File**: `hooks/pptx_validate_hook.py`  
**Trigger**: PostToolUse — fires after Bash commands matching `build_*_ppt.py`

### What it checks

Finds `.pptx` files modified in the last 120 seconds and checks for shape overflow beyond the 13.33" × 7.5" slide boundary.

**Requires**: `python-pptx` package (`pip install python-pptx`)

---

## ontology_declare_enforce

**File**: `hooks/ontology_declare_enforce.py`  
**Trigger**: Stop — fires every time Claude finishes a response

### What it checks

**L2-A: L0 declaration check**  
If a turn included Edit/Write, verifies the preceding assistant message contained an `L0:` declaration.

**L2-B: Dependency chain verification**  
If an enumerable concept collection (list/dict/registry) was modified, blocks if there's no Grep evidence in the same turn.

---

## git_push_enforce_stop

**File**: `hooks/git_push_enforce_stop.py`  
**Trigger**: Stop — fires every time Claude finishes a response

### What it checks

Tracks **only files actually edited this session** (ignores pre-existing dirty files).

```
❌ BLOCKED: modified bot.py → no git commit
❌ BLOCKED: modified alarm_manager.py → committed but not pushed
✅ PASS:    all modified files committed + pushed
```

---

## tdd_enforce_stop

**File**: `hooks/tdd_enforce_stop.py`  
**Trigger**: Stop — fires every time Claude finishes a response

### What it checks

Scans the transcript for the positions of the last Edit/Write and the last verification command.  
If no verification command found **after** the last edit, blocks the response.

**Accepted verification patterns:**
- Python: `pytest`, `python -m py_compile`, `python <file>.py`
- JS/TS: `npx tsc --noEmit`, `npm test`, `npm run build`
- Web: `curl http://localhost`
- Others: `go test`, `cargo test`, `dotnet test`, `jest`

```
❌ BLOCKED: code modified, no verification before response
✅ PASS:    python -m py_compile <file> ran after last edit
```

---

## Verify Installation

Check hooks are installed correctly:

## semantic_judge_gate (agent-based L0 meaning judgment)

**File**: `hooks/semantic_judge_gate.py`
**Fires**: Stop — every time Claude completes a response

### Why an agent, not a pattern

`ontology_violation_gate` (a pattern hook) only checks whether the string `"L0:"` **exists**. But a hollow L0 (e.g. `L0: implement JSON parsing` — an implementation act sitting in the purpose slot) passes the string check. **Whether an L0 is a real purpose is a semantic judgment, impossible for regex.**

`semantic_judge_gate` closes this structural hole. It extracts the `L0:` lines from this session's Edit/Write calls and delegates to an **independent judge (claude CLI, cheap model)**, getting PASS/FAIL against the criteria in `judge_rubric.md`.

### Behavior

1. Extract `L0:` lines from Edit/Write in the transcript (only lines still present in the current file — judging the present state, not history)
2. No L0 lines → pass (zero judging cost)
3. Build a prompt from the full `judge_rubric.md` + the L0 lines → call the agent
4. On FAIL, block (exit 2) with the reason, prompting a rewrite
5. **Dead-loop guard**: after 2 blocks in one session it passes (recorded in `judge_state.json`)
6. **fail-open**: if the judge call fails or times out, it passes — a judge outage never blocks work

### judge_rubric.md = the criteria SSOT

The criteria live as data in `judge_rubric.md`, not in code. To change the criteria, edit the markdown, not the Python. The judge decides on these criteria alone and does not soften them with its own training knowledge.

```
❌ FAIL: L0: complete within a 10-second timeout   (a numeric metric in the purpose slot)
❌ FAIL: L0: speed up responses with Redis caching  (a technical means in the purpose slot)
✅ PASS: L0: the customer completes a quote without human help
```

> This is where ODD actually implements the principle "semantic judgment must always be done by an agent." Any governance that cannot be expressed as a pattern can be extended the same way — with an agent judge.

---

```bash
cat ~/.claude/settings.json | grep -A5 "hooks"
```

When the plugin is installed, hooks defined in `hooks.json` are applied automatically.

[Installation guide →](/en/guide/installation)
