# ODD Port Specification: Continue (VS Code AI Coding Assistant)

<!-- L0: Define how ODD's governance principles can be adapted to Continue's rules and slash command system -->

**Status:** Specification only. No implementation. Requires Continue installation to validate.

**Platform:** Continue v0.9+ (VS Code extension, open-source AI coding assistant)
**Official docs:** https://docs.continue.dev

---

## 1. Continue Architecture Overview

Continue is an open-source VS Code extension that connects to any LLM (Claude, GPT-4, local models). Its extension points:

| Feature | Description | ODD Relevance |
|---------|-------------|---------------|
| `.continuerules` / `rules.md` | System prompt injected into all sessions | Primary ODD control surface |
| Slash commands | Custom commands defined in `config.json` | ODD skill equivalent |
| Context providers | Custom context injected (@-mentions) | L0 context injection |
| MCP tools | Model Context Protocol tool integration | Hook-like tool interception |
| Prompts | Saved prompt templates | ODD template equivalent |

---

## 2. Primary Integration: `.continuerules`

Continue reads `.continuerules` (or `rules.md` in `.continue/` directory) as a persistent system prompt for all sessions in the project.

**ODD Governance Rules for `.continuerules`:**

```markdown
# ODD Governance Rules

## L0 Declaration — Required Before Any Edit
State L0 before editing any file:
"L0: [why this change must exist — what fails without it?]"

Cannot state L0 → Stop. Ask user what problem we're solving.
L0 present → Proceed.

## L1-L3 Labels in Code Comments
# L0: <ultimate purpose>
# L1: <architectural goal>
# L2: <module logic / trade-offs>
# L3: <concrete implementation>

Use these labels in all significant code changes.

## Strategy Document Rule
Files ending in SPEC.md, DESIGN.md, PLAN.md, STRATEGY.md must include:
## Assumptions
- [list assumptions this document relies on]

## Search Rule
When searching the web: always include current year in the query.
Example: "Python asyncio best practices 2026"

## TDD Rule
After modifying any .py / .ts / .js / .go file:
1. State which test will verify this change
2. Run the test
3. Report test output before declaring done

## Completion Rule
"Done" = test ran + output shown + expected vs actual compared.
Not "I've made the change and it should work."
```

---

## 3. Slash Commands (Skills Equivalent)

Continue's `config.json` supports custom slash commands. ODD's 7 core skills map to Continue slash commands:

### config.json addition:

```json
{
  "slashCommands": [
    {
      "name": "pyramid-ontology",
      "description": "Declare L0-L3 hierarchy for this session",
      "prompt": "Follow this protocol:\n1. Ask: What is the ultimate purpose of this session? (L0)\n2. Derive L1: What system structure achieves this?\n3. Derive L2: What modules/components compose L1?\n4. Derive L3: What concrete code/files implement L2?\nState each level explicitly. No action without stated L0."
    },
    {
      "name": "ontology-learning",
      "description": "Learn from a mistake — reverse L3→L0 analysis",
      "prompt": "A mistake was made. Analyze it:\n1. L3: What exactly happened? (specific code/output)\n2. L2: What logic error caused it?\n3. L1: What structural gap allowed this error?\n4. L0: What purpose-level misalignment enabled this gap?\nThen: What rule would prevent this class of mistake? State the rule."
    },
    {
      "name": "ontology-review-gate",
      "description": "Ontology court — review before implementation",
      "prompt": "Before implementation, answer:\n1. L0: Why must this be built?\n2. L1: What is the minimal structure that achieves L0?\n3. L2: What are the trade-offs in this design?\n4. L3: What is the implementation plan?\n5. What would make this implementation WRONG? (exit conditions)\nOnly proceed if all 5 are answered."
    },
    {
      "name": "ontology-detach",
      "description": "Detect and remove existence-clinging patterns",
      "prompt": "Review the current code/design for:\n1. Features with no L0 connection (orphaned code)\n2. Dependencies with no exit condition\n3. Data retained past its useful life\n4. Abstractions that exist because they 'feel right' not because L0 requires them\nFor each finding: state why it should be removed or given an exit condition."
    },
    {
      "name": "health",
      "description": "System health check — L0-L3 alignment audit",
      "prompt": "Audit the current codebase:\n1. For each major module: can you trace it to L0?\n2. Are there any hooks/features that are dead code?\n3. Are there any false positive patterns in enforcement code?\n4. Is documentation consistent with implementation?\nReport findings by severity: P0 (blocking), P1 (critical), P2 (important)."
    }
  ]
}
```

---

## 4. Context Providers (L0 Context Injection)

Continue's `@`-mention context providers can inject ODD context:

### Custom Context Provider for L0 Registry:

```typescript
// .continue/config.ts
export default {
  contextProviders: [
    {
      name: "l0",
      description: "Current session L0 declaration",
      getContextItems: async (query, extras) => {
        // Read L0 from a session file if it exists
        const l0File = path.join(workspace, ".odd-session-l0.txt");
        const l0 = fs.existsSync(l0File)
          ? fs.readFileSync(l0File, "utf8")
          : "No L0 declared yet";
        return [{
          name: "Current L0",
          content: `Session L0 Declaration:\n${l0}`,
          description: "The L0 purpose governing this session"
        }];
      }
    }
  ]
};
```

Usage: Type `@l0` in Continue chat to inject the current session's L0 into context.

---

## 5. MCP Tools (Hook-Like Enforcement)

Continue supports Model Context Protocol (MCP) servers. MCP tools can implement ODD-style enforcement:

```python
# mcp_odd_server.py — MCP server implementing ODD enforcement tools

@server.call_tool()
async def check_l0_before_edit(arguments: dict) -> list[TextContent]:
    """Tool: check_l0_before_edit
    Call this before any file edit to verify L0 is declared.
    Returns PASS or BLOCK with reason.
    """
    session_context = arguments.get("session_context", "")
    l0_pattern = re.compile(r'(?:\*\*L0\*\*:|L0:|_L0_:)\s*\S')
    
    if l0_pattern.search(session_context):
        return [TextContent(type="text", text="PASS: L0 declared")]
    else:
        return [TextContent(type="text", text="BLOCK: No L0 declaration found. State L0 before editing.")]
```

**Note:** MCP tool calls are made by the model voluntarily (the model decides to call the tool), not mechanically triggered like Claude Code's PreToolUse hooks. This is a behavioral rather than mechanical enforcement mechanism.

---

## 6. Enforcement Strength Comparison

| Mechanism | Strength | Implementation |
|-----------|----------|---------------|
| `.continuerules` (system prompt) | Behavioral — model follows rules | Copy-paste, zero setup |
| Slash commands | Behavioral — explicit skill invocation | Add to config.json |
| MCP tool check | Behavioral — model must choose to call | Requires MCP server |
| Continue extension (TypeScript) | Mechanical — intercepts at API level | Requires extension development |

**Recommended starting point:** `.continuerules` + slash commands. Zero infrastructure, works immediately.

---

## 7. Key Difference from Claude Code: No Hard Block

Continue has no equivalent to Claude Code's `exit code 2` (hard block) mechanism. All enforcement is behavioral. This means:

- ODD rules will be followed consistently only if the model is instructed clearly
- There is no guarantee that an LLM will refuse to edit without L0 if the user insists
- The `tdd_enforce_stop` and `ontology_declare_enforce` stop-phase enforcement cannot be ported mechanically

**Compensation:** Continue's open-source nature allows deeper integration. A custom TypeScript extension could intercept the Continue API before tool calls and implement hard blocks. This is architecturally possible but requires significant development effort.

---

## 8. Minimum Viable ODD for Continue

Zero infrastructure, immediate value:

1. Create `.continuerules` in your project root with the governance rules from section 2
2. Add the 5 slash commands to `~/.continue/config.json`
3. Begin each session with `/pyramid-ontology`
4. End each session with review of what was built and why

---

## 9. Validation Requirements

Before publishing this port as "verified":

- [ ] Confirm `.continuerules` is read in all Continue sessions for the project
- [ ] Confirm slash commands from `config.json` are available in VS Code
- [ ] Test behavioral enforcement: does the model follow L0 rules consistently?
- [ ] Test MCP tool integration with `check_l0_before_edit`
- [ ] Test with Continue version (record exact version tested)
- [ ] Measure behavioral false positive rate across 5+ sessions
