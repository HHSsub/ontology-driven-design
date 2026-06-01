# ODD Port Specification: GitHub Copilot Agent

<!-- L0: Define how ODD's governance principles can be adapted to GitHub Copilot's extension system -->

**Status:** Specification only. No implementation. Requires Copilot Agent access to validate.

**Platform:** GitHub Copilot (VS Code extension + GitHub Copilot Agent mode, 2025-2026)

---

## 1. Copilot Architecture Overview

GitHub Copilot operates in two distinct modes relevant to ODD:

| Mode | Description | ODD Relevance |
|------|-------------|---------------|
| Inline completion | Autocomplete in editor | Low — no conversation context |
| Copilot Chat / Agent | Conversation + multi-file edit | High — where ODD applies |
| Copilot Extensions | Custom agents via GitHub Marketplace | Potential ODD host |
| Copilot Workspace | Experimental; GitHub-native | Future consideration |

ODD's governance principles apply to **Copilot Chat Agent mode** — where Copilot makes decisions about what files to edit and how.

---

## 2. Key Differences from Claude Code

| Dimension | Claude Code | GitHub Copilot Agent |
|-----------|-------------|---------------------|
| Hook system | Python scripts triggered at tool lifecycle | No equivalent hook system (2026-05-30) |
| Session transcript | Accessible file | Not exposed to extensions |
| Custom skills | `skills/<name>/SKILL.md` slash commands | `.github/copilot-instructions.md` |
| Tool interception | PreToolUse/PostToolUse hooks | Not available |
| Extension API | Plugin directory + hooks.json | Copilot Extensions API (GitHub App) |

**Critical implication:** Copilot Agent has **no mechanical hook equivalent** to Claude Code's PreToolUse/Stop system. ODD's hard-block enforcement (exit code 2) cannot be ported directly. All Copilot ODD adaptation must use behavioral/instructional mechanisms.

---

## 3. Primary Integration Point: `.github/copilot-instructions.md`

GitHub Copilot reads `.github/copilot-instructions.md` from the repository root and injects it as a system prompt for all Copilot interactions in that repository.

This is ODD's main control surface for Copilot.

### 3.1 ODD Governance via copilot-instructions.md

```markdown
# ODD Governance Rules (Pyramid Thinking)

## L0 Requirement — MANDATORY
Before editing any file, state your L0:
"L0: [the ultimate purpose of this change — what fails if this change doesn't happen?]"

If you cannot state L0, stop and ask the user what problem we're solving.

## L1-L3 Hierarchy
L1: Structural/architectural goal (how L0 is achieved)
L2: Module logic and trade-offs
L3: Concrete implementation

## Documentation Rule
Strategy documents (.md files) must include:
[가정 명시] or [Assumptions]:
- List all assumptions this strategy relies on

## Search Rule
Web searches must include the current year.

## TDD Rule
If you modify a .py, .ts, .js file:
- State what test you will run to verify the change
- Run the test before declaring the task complete

## Completion Rule
"Done" means: test passed, log shown, output verified.
Not: "I've made the change."
```

### 3.2 Repository-Level vs User-Level

| Scope | File | Who controls |
|-------|------|-------------|
| Repository | `.github/copilot-instructions.md` | Project maintainer |
| User (VS Code) | VS Code settings: `github.copilot.chat.codeGeneration.instructions` | Individual user |
| Organization | GitHub org Copilot policy | Org admin |

ODD recommends placing governance instructions at the repository level so all team members using Copilot share the same L0 discipline.

---

## 4. Copilot Extensions API Approach

For harder enforcement, a Copilot Extension (GitHub App) could implement ODD as a server-side agent.

### 4.1 Extension Architecture

```
User message → Copilot routes to ODD Extension → ODD agent processes
                                                  ↓
                                     Check: Does message contain L0?
                                          No → Return "Please state L0 first"
                                          Yes → Forward to code generation
```

**Extension implementation would require:**
- GitHub App registration
- Server implementing [Copilot Extensions API](https://docs.github.com/en/copilot/building-copilot-extensions)
- L0 declaration check in request handler
- Skill invocation routing

**This is the only way to achieve mechanical enforcement on Copilot.** However, it requires maintaining a server and GitHub App registration — significantly higher complexity than ODD's Claude Code approach.

---

## 5. L0 Enforcement Mapping

| ODD Hook | Claude Code | Copilot Equivalent |
|----------|------------|-------------------|
| `pyramid_ontology_gate` | PreToolUse block | copilot-instructions.md behavioral rule |
| `tdd_enforce_stop` | Stop block | copilot-instructions.md TDD rule |
| `ontology_declare_enforce` | Stop block | copilot-instructions.md L0 rule |
| `websearch_yearguard` | PreToolUse block | copilot-instructions.md search rule |
| `assumption_declaration_gate` | Stop block | copilot-instructions.md doc rule |
| `destructive_bash_gate` | PreToolUse block | No equivalent (Copilot doesn't run bash) |
| `pyramid_guard` | PostToolUse check | No equivalent (no PostToolUse) |

**Net assessment:** Copilot can implement ODD at the behavioral layer (instructions, rules) but cannot implement mechanical blocking without a Copilot Extension server.

---

## 6. Minimum Viable ODD for Copilot

Recommended starting point — zero infrastructure required:

1. Add `.github/copilot-instructions.md` with ODD rules (section 3.1 above)
2. Enable Copilot Chat in VS Code
3. Begin sessions with `/pyramid-ontology` (if skill system allows custom commands, otherwise type L0 declaration manually)

---

## 7. VS Code Sidebar: ODD as Custom Chat Participant

VS Code's Copilot Chat API supports custom chat participants (`@odd` style). This is a lighter-weight extension mechanism than a full GitHub App:

```typescript
// Extension entry point
vscode.chat.createChatParticipant('odd', handler);

async function handler(request, context, stream, token) {
    // Check for L0 declaration in request.prompt
    if (!hasL0Declaration(request.prompt)) {
        stream.markdown('Please state L0 before proceeding.');
        return;
    }
    // Forward to Copilot with ODD context injected
    // ...
}
```

This approach requires a VS Code extension but no server. It enables:
- L0 check on each message
- ODD skill invocation via `@odd /pyramid-ontology`
- Session logging for metrics

---

## 8. Validation Requirements

Before publishing this port as "verified":

- [ ] Confirm `.github/copilot-instructions.md` is read in Copilot Chat Agent mode
- [ ] Confirm custom chat participant API supports L0 checking
- [ ] Test behavioral enforcement: does Copilot follow L0 rules consistently?
- [ ] Measure behavioral false positive rate (does Copilot ask for L0 when it should?)
- [ ] Test with Copilot version (record exact VS Code Copilot extension version)
