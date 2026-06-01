# ODD Current State Audit
<!-- Generated from main branch audit, 2026-05-30 -->
<!-- Auditor: Worker Agent — read-only access, no code changes -->

---

## 1. Executive Verdict

**Experimental but usable by advanced users — NOT ready for public adoption**

ODD is a coherent and philosophically consistent Claude Code plugin for purpose-governed AI development. For a single advanced user who already understands Pyramid Thinking (피라미드사고법) and is willing to tolerate setup friction, it provides meaningful enforcement of L0-L3 discipline through hooks and skills.

It is not ready for public adoption because:
- No LICENSE file exists in the repository. Using or distributing ODD carries unknown legal risk.
- Installation command (`claude plugin add HHSsub/odd`) references a `claude plugin` subcommand that is UNVERIFIED against current Claude Code CLI behavior. Users cannot install without validating this works.
- `ontology_graph_gate.py` references `hooks/ontology_graph.json` which does not exist in the repository. This hook will silently fail or produce a runtime error on every Edit/Write/NotebookEdit call.
- CLAUDE.md advertises "14 hooks" while hooks.json registers 13. README.md advertises "6 skills" while CLAUDE.md and docs list 7-8. These count mismatches are a trust signal failure.
- The hook `git_commit_push_check.py` hardcodes logic specific to a private portfolio project (`dynamic_portfolio`), yet it runs for all users via the plugin. This is a SSOT violation and a RUNTIME_RISK that contradicts ODD's own design philosophy.
- The term "ontology" creates immediate expectation mismatch: new users expect RDF/OWL/formal ontology; they get Markdown skills and Python regex hooks. This must be addressed before public adoption.

---

## 2. Repository Map

```
ontology-driven-design/
├── .claude-plugin/
│   ├── plugin.json          — Plugin metadata (version, author, homepage)
│   └── marketplace.json     — Self-referencing marketplace wrapper
├── .github/
│   └── workflows/deploy.yml — VitePress docs deployment to GitHub Pages
├── commands/                — 18 slash command .md files (global registration)
├── docs/                    — VitePress documentation site source
│   ├── .vitepress/config.ts
│   ├── guide/               — getting-started, installation, usage
│   ├── skills/              — one .md per skill (Korean docs)
│   ├── en/                  — Mirror English docs (not fully audited)
│   ├── index.md
│   └── philosophy.md
├── hooks/                   — 14 .py files + hooks.json + violation_registry.json
│   ├── hooks.json           — Hook registration (13 entries registered)
│   ├── violation_registry.json — Rule data for ontology_violation_gate
│   └── *.py                 — Individual hook implementations
├── skills/                  — 8 skill directories, each with SKILL.md
│   └── pyramid-ontology/    — Also contains SKILL-MAP.md
├── special_advice/          — 4 files: research docs + blueprint (no code)
├── AGENTS.md                — Agent-facing instructions
├── CLAUDE.md                — Plugin manifest for Claude Code
├── README.md                — Public-facing documentation
├── package.json             — npm package metadata (no main entry, only devDeps)
├── package-lock.json
└── verify.js                — Shallow file existence check only
```

**Missing (critical):** LICENSE file, SECURITY.md, CHANGELOG.md, CONTRIBUTING.md, `ontology_graph.json`

---

## 3. What ODD Currently Is

ODD is a **Claude Code plugin implementing purpose-governance discipline** for AI-assisted development, based on a 4-layer framework (L0-L3) derived from 피라미드사고법 (Pyramid Thinking).

**Concretely, ODD is:**

1. **A hook system (13 registered, 14 .py files)** that intercepts Claude Code tool calls and blocks actions lacking ontological justification:
   - Blocks Edit/Write if no `L0:` declaration exists in session transcript (`pyramid_ontology_gate.py`)
   - Validates L-level hierarchy purity in written files via complex regex (`pyramid_guard.py`)
   - Blocks session end if no L0 declaration was made (`ontology_declare_enforce.py`)
   - Blocks session end if code was edited without test verification (`tdd_enforce_stop.py`)
   - Blocks git push without prior commit, blocks session end with unpushed commits (`git_push_enforce_stop.py`)
   - Blocks WebSearch queries missing the current year (`websearch_yearguard.py`)
   - Blocks destructive Bash commands (DROP, DELETE, rm -rf *.db) without user confirmation (`destructive_bash_gate.py`)
   - Blocks session end if strategy output lacks assumption declaration (`assumption_declaration_gate.py`)
   - Warns/blocks Agent tool calls lacking L0 and role specification (`agent_pyramid_gate.py`)
   - Enforces ontology-learning skill invocation after detected failures (`ontology_learning_enforce_stop.py`)
   - Applies violation rules from `violation_registry.json` to Edit/Write content (`ontology_violation_gate.py`)
   - Validates PPTX layout overflow after pptx build scripts (`pptx_validate_hook.py`)
   - For dynamic_portfolio repo only: triggers Vercel deployment after git push (`git_commit_push_check.py`)
   - References missing `ontology_graph.json` file — will fail silently (`ontology_graph_gate.py`)

2. **A skill system (8 skills)** providing structured reasoning protocols invocable via slash commands:
   - `pyramid-ontology`: Purpose declaration protocol (L0-L3)
   - `ontology-detach`: Binding exit-condition audit
   - `ontology-rebuild`: Generate ONTOLOGY.md topology docs per folder
   - `pyramid-label`: L0-L3 label application to all code units
   - `pyramid-topology`: Full codebase hierarchy integrity scan
   - `ontology-review-gate`: Pre-implementation Ontology Court
   - `ontology-learning`: Post-mistake root-cause analysis (L3→L0 reverse trace)
   - `odd-onboarding`: Natural-language project onboarding (generates ONBOARDING.md)

3. **A documentation site** (VitePress) covering philosophy, getting-started, installation, and per-skill usage.

4. **A `violation_registry.json`** implementing a seed/branch/rule self-limiting evolution protocol with 5 L0 seeds, 11 L1 branches, and 1 active rule (`evaluator_self_judge_guard`).

---

## 4. What ODD Currently Is Not

**ODD is not formal ontology.** This is not a subjective judgment — it is a structural observation.

| Formal Ontology Capability | Present in ODD? |
|---------------------------|----------------|
| Concept registry (machine-readable) | No |
| Entity / Property definitions | No |
| Relation definitions (object properties) | No |
| Axiom / Constraint definitions | No |
| Competency questions | No |
| OWL/RDF serialization | No |
| SHACL shape validation | No |
| SPARQL query support | No |
| Description logic reasoning | No |
| LinkML schema | No |
| JSON Schema export | No |
| Ontology reuse / import | No |
| Machine-to-machine knowledge sharing | No |

What ODD uses the word "ontology" to mean is: *the philosophical sense of "grounding existence in purpose."* This is legitimate in philosophy but creates systematic expectation mismatch with developers who know formal ontology tools (Protégé, OWL, ROBOT, LinkML).

**ODD is not a test framework.** `verify.js` checks that 6 named files exist. It does not test any hook behavior, skill execution, or rule application. There are zero automated tests.

**ODD is not installation-verified.** The installation command `claude plugin add HHSsub/ontology-driven-design` is the only documented path. Whether this command works with the current Claude Code CLI version is UNVERIFIED.

**ODD is not OS-portable verified.** Hook scripts use `${CLAUDE_PLUGIN_ROOT}` in hooks.json. Whether this environment variable is set correctly on Windows vs. macOS vs. Linux in Claude Code's hook execution context is UNVERIFIED.

---

## 5. Product Hygiene Assessment

| Area | Status | Evidence | Risk | Required Fix |
|------|--------|----------|------|--------------|
| LICENSE file | MISSING | No LICENSE file in repo root or anywhere in tree | LEGAL_RISK P0 | Add MIT or Apache-2.0 LICENSE immediately |
| SECURITY.md | MISSING | No security policy file | PRODUCT_HYGIENE P2 | Add basic security disclosure policy |
| CHANGELOG.md | MISSING | No changelog file | PRODUCT_HYGIENE P2 | Add with version 1.0.0 entry |
| CONTRIBUTING.md | MISSING | No contribution guide | PRODUCT_HYGIENE P3 | Add before public adoption |
| package.json metadata | PARTIAL | Has name, version, description, scripts, devDependencies. Missing: main, keywords, license field, engines | ADOPTION_RISK P2 | Add `"license": "MIT"` or equivalent, `"engines"` field |
| plugin.json completeness | PARTIAL | Has name, version, author, description, homepage, repository, keywords. Missing: hooks key pointing to hooks.json, skills key, minimum Claude Code version | ADOPTION_RISK P1 | Add hooks/skills registration, add Claude Code version requirement |
| marketplace.json | REDUNDANT/CONFLICT | Wraps plugin.json with a separate "marketplace" concept that has no documented standard | ADOPTION_RISK P2 | Remove or clarify purpose — Claude Code plugin spec does not define marketplace.json |
| version consistency | OK | All three files (package.json, plugin.json, marketplace.json) say 1.0.0 | — | — |
| Installation command | UNVERIFIED | `claude plugin add HHSsub/odd` — Claude Code does not have a documented `plugin add` subcommand per public documentation | ADOPTION_RISK P0 | Verify or document the actual install mechanism. README says two aliases, docs/installation.md says same. Neither is verified. |
| Short alias `HHSsub/odd` | UNVERIFIED | README claims `claude plugin add HHSsub/odd` works as alias, but no alias mechanism is defined in the repo | ADOPTION_RISK P1 | Remove or verify |
| `verify.js` | SHALLOW | Only checks file existence for 6 paths. No hook/skill behavior test | PRODUCT_HYGIENE P2 | Expand to test hook exit codes and skill parsing |
| Release tags | NONE | No git tags in repository | PRODUCT_HYGIENE P2 | Tag v1.0.0 |
| Documentation site | FUNCTIONAL | VitePress + GitHub Pages deploy workflow present. Korean and English docs parallel. | — | — |
| OS portability | UNVERIFIED | `${CLAUDE_PLUGIN_ROOT}` used in hooks.json — behavior on Windows unknown | RUNTIME_RISK P1 | Test on Windows; document OS requirements |

---

## 6. Ontology Formality Assessment

| Capability | Present? | Evidence | Gap | Priority |
|------------|----------|----------|-----|----------|
| Concept registry | No | Not found anywhere | No machine-readable concept definitions | P1 (needed for Phase 4) |
| Entity definitions | No | Not found | No typed entity model | P1 |
| Relation definitions | No | Not found | No object/data property model | P1 |
| Constraint definitions | Partial (informal) | violation_registry.json encodes behavioral rules, not logical constraints | Rules are regex-based, not logic-based | P2 |
| Competency questions | No | Not found | No validation criteria for ontology correctness | P2 |
| Schema generation (JSON Schema) | No | Not found | Cannot export to other systems | P1 |
| LinkML compatibility | No | Not found | Cannot bridge to formal ontology ecosystem | P2 |
| RDF/OWL export | No | Not found | No interoperability with Protégé, SPARQL engines | P3 |
| Reasoning support | No | Not found | No inference on L0-L3 relationships | P3 |
| Ontology reuse/import | No | Not found | Each project must restate everything | P2 |

**Summary:** ODD implements zero formal ontology capabilities. This is not a defect given its stated purpose. It IS a defect in positioning — using the word "ontology" without disclosure of what it does and does not include causes adoption friction and trust erosion among technically literate users.

The `violation_registry.json` is the closest artifact to a machine-readable knowledge structure. Its seed/branch/rule design is philosophically coherent but is not formal ontology — it is a behavioral policy engine expressed in JSON.

---

## 7. Hook System Assessment

| Hook | Lifecycle | Behavior | Blocking? | False-Positive Risk | Needed Improvement |
|------|-----------|----------|-----------|--------------------|--------------------|
| `pyramid_ontology_gate` | PreToolUse (Edit/Write/NotebookEdit) | Reads full session transcript; blocks if no `L0:` pattern found in any assistant message | Yes (exit 2) | LOW — session-wide scan prevents early-L0 missed detection | Exempt list for quick edits; configurable per project |
| `ontology_graph_gate` | PreToolUse (Edit/Write/NotebookEdit) | Loads `ontology_graph.json` — FILE DOES NOT EXIST — will return empty graph, then silently pass or error | No (silent fail) | CRITICAL — hook is registered but non-functional | Create `ontology_graph.json` or remove hook from hooks.json |
| `ontology_violation_gate` | PreToolUse (Edit/Write/NotebookEdit) | Loads `violation_registry.json`; applies content/heading/pattern checks. Currently only 1 active rule (LOCKED file write) | Yes (exit 1) | LOW (only 1 rule active) | Exit code inconsistency: uses exit(1) while others use exit(2); document severity levels |
| `pyramid_guard` | PostToolUse (Edit/Write) | Complex regex: L-level header existence, L0/L1 content validation, magic number detection, duplicate truth detection (SSOT) | Yes (exit 2) | HIGH — regex patterns are broad; `.py`, `.ts` in L0 line trigger even in valid cross-level comments; SSOT check may trigger on intentionally similar lists | Add per-file opt-out; reduce regex scope; add user-visible false-positive reporting |
| `websearch_yearguard` | PreToolUse (WebSearch) | Checks query for current year or recency keywords | Yes (exit 2) | LOW — simple year check with multiple escape keywords | Add `YYYY` pattern support alongside explicit year |
| `destructive_bash_gate` | PreToolUse (Bash) | Regex match on Bash commands for DROP/DELETE/rm *.db patterns | Yes (exit 2) | MEDIUM — `rm -rf *.db` pattern but not `rm -rf /` (general rm); truncate pattern only matches `truncate *.db` not `truncate -s 0 file` | Expand pattern coverage; add general rm -rf recursive delete |
| `tdd_enforce_stop` | Stop (session end) | Checks if last Edit/Write was followed by a recognized test/verification command | Yes (exit 2) | HIGH — any documentation-only edit (SKILL.md, README) triggers this; no exemption for non-code files | Add file-type exemptions for docs, config files |
| `ontology_declare_enforce` | Stop (session end) | Session-wide L0 declaration check + optional dependency chain check (registry modification without grep) | Yes (exit 2) | LOW for L0 check; MEDIUM for dependency chain (regex for 3+ string literals may trigger on coincidental list similarity) | Configurable sensitivity; document the dependency chain detection |
| `assumption_declaration_gate` | Stop (session end) | Reads last assistant message; checks for strategy judgment patterns without assumption declarations | Yes (exit 2) | MEDIUM — pattern "해야 합니다" is very common in normal assistance and may trigger inappropriately | Tighten patterns; add minimum response length threshold |
| `git_push_enforce_stop` | Stop (session end) | Checks for uncommitted/unpushed changes after any Edit/Write in session | Yes (exit 2) | HIGH — forces git commit+push for ALL edits in ALL repos. Not appropriate for users who want to review before pushing | Make configurable; add per-repo opt-out |
| `ontology_learning_enforce_stop` | Stop (session end) | Detects failure signals (tool errors, 3+ user corrections) → requires `ontology-learning` Skill invocation | Yes (exit 2) | HIGH — `user_count >= 3` triggers on any conversation with 3+ user turns. This is nearly every productive session | Require actual `is_error:true` tool result, not conversation length |
| `pptx_validate_hook` | PostToolUse (Bash) | Checks PPTX layout overflow after `build_*_ppt.py` commands only | No (warning only, exit 0 normally) | VERY LOW — narrow trigger condition | python-pptx dependency not declared anywhere; will fail if not installed |
| `git_commit_push_check` | PostToolUse (Bash) | Triggers Vercel deploy on git push ONLY if cwd contains "dynamic_portfolio" string | No | VERY LOW (private portfolio only) | CONFLICT: This is a personal-project hook shipping in a public plugin. Non-portfolio users get a hook that runs on every Bash command, checks git, and silently exits if not in dynamic_portfolio. Wasteful and philosophically contradicts SSOT. |
| `agent_pyramid_gate` | PreToolUse (Agent) | Validates Agent tool calls for L0 declaration and role specification | Yes for L0 absence (exit 2); No for role-only hint (exit 0) | LOW — only fires on Agent tool calls with 150+ char prompts | Not registered in hooks.json — dead code. Will never fire. |

**Critical Finding:** `agent_pyramid_gate.py` exists in the hooks folder and is referenced in CLAUDE.md's hook list, but is NOT registered in hooks.json under the "Agent" matcher. It will never execute. This is dead code presenting as active enforcement.

**Critical Finding:** `ontology_graph_gate.py` is registered in hooks.json and fires on every Edit/Write/NotebookEdit, but it reads `ontology_graph.json` which does not exist. It will return an empty graph dict and immediately exit 0 (pass). Effectively a no-op that adds overhead.

---

## 8. Skill System Assessment

| Skill | Purpose | Strength | Weakness | Improvement |
|-------|---------|----------|----------|-------------|
| `pyramid-ontology` | Declare L0-L3 before any task | Clear, comprehensive. Covers all output types (code, docs, email, PPT). Red flags table is useful. | SSOT enforcement section duplicates logic that hooks also enforce; slight disconnect | Move the "강제 법칙" to be clearly tied to what hooks enforce vs. what is human-only |
| `ontology-detach` | Binding exit-condition audit (6 dimensions) | Deep, philosophically coherent. The 6-dimension taxonomy (State/Dependency/Value/Assumption/Identifier/Sequence) is the best content in the entire repo | Complex to apply without examples. No concrete code-before/after comparison | Add 2-3 real before/after code examples per dimension |
| `ontology-rebuild` | Generate per-folder ONTOLOGY.md | Clear procedure. Binary detection heuristic (first 8 bytes `\x00`) for binary files is good. | "Confirms" ONTOLOGY.md as less reliable than code (Step 4 note). No automated validation of generated docs. | Add a diff-against-previous step to flag drift |
| `pyramid-label` | Apply L0-L3 labels to files | Practical. Language-agnostic. Decision tree is clear. | Step 1 hardcodes file extensions (`.py .ts .js .jsx .tsx .go .rb .java .yaml .yml .md .sh`) — this contradicts the ontology-rebuild skill which says "확장자 하드코딩 금지" | Fix extension hardcoding; align with ontology-rebuild's binary detection approach |
| `pyramid-topology` | Full hierarchy integrity scan | Good violation catalog. Output format is clear. | This is a protocol for Claude to follow, not automated tooling. Results vary based on Claude's interpretation. | Build as actual static analysis tool with testable outputs |
| `ontology-review-gate` | Pre-implementation Ontology Court | Strong checklist (10 items). The concept of rejecting "magic number additions" and "local patches" is philosophically consistent. | REJECT criteria are strict enough that ANY static configuration would fail (`MAX_LOOP=12` → REJECT). This may cause review fatigue. | Add severity tiers to the court criteria |
| `ontology-learning` | Post-mistake root-cause analysis | The 6-phase structure (L3→L0 trace + memory + enforcement update) is the most sophisticated skill. The "케이스 A/B/C" branching in Phase 6 is clear. | Phase 5 (memory) says to save files at `~/.claude/projects/.../memory/` — this path structure is UNVERIFIED as a Claude Code convention. Phase 6 example code hardcodes `C:/Users/User/.claude/hooks/` — a specific user's path. | Remove personal paths; make file location configurable |
| `odd-onboarding` | Natural-language project onboarding | Best accessibility-first skill. Plain language questions. Non-technical framing. | Step 2 generates ONBOARDING.md but does not validate the L0 against `pyramid_guard`'s L0 content rules. Could generate L0s that pyramid_guard would then block. | Validate generated ONBOARDING.md against pyramid_guard criteria |

---

## 9. Documentation Assessment

**README.md:** States "Skills (6)" but there are 7-8 skills. Installation command is unverified. Quick Start shows `/pyramid-ontology` without explaining what it actually does for a first-time user. Tone is philosophical rather than practical. No "what problem does this solve in 30 seconds" statement.

**docs/guide/getting-started.md:** The Step 2 table shows only 3 hooks ("pyramid_guard", "ontology_declare_enforce", "git_push_enforce") but there are 13+ registered. Misleading. Step 3 and Step 3 (second occurrence) are duplicate numbering.

**docs/guide/installation.md:** Manual install path (`cp -r skills/* ~/.claude/skills/`) is provided as fallback, but does not mention hooks installation. A user following manual install would get skills without hooks — a broken half-install.

**docs/philosophy.md:** High quality philosophical framing. Correctly positions L2 as trade-off record rather than feature decomposition — this is non-obvious and important.

**docs/skills/**: One page per skill. Content mirrors SKILL.md files without substantial addition.

**CLAUDE.md vs README.md skill count conflict:** CLAUDE.md says 7 skills, README says 6. The repo contains 8 SKILL.md files (including odd-onboarding, ontology-learning, pyramid-ontology, ontology-detach, ontology-rebuild, pyramid-label, pyramid-topology, ontology-review-gate).

**Terminology consistency issue:** Korean-primary content with mixed Korean/English. CLAUDE.md is English. AGENTS.md is English. Skill files are Korean. Command files are Korean/English mixed. For non-Korean users, English documentation is incomplete.

**SKILL-MAP.md:** References `superpowers:*` skills as L1/L2 utilities. These are external skills from a separate plugin ecosystem. A new user has no way to know these exist or how to get them. This creates an undisclosed dependency on `superpowers` plugin for full functionality.

---

## 10. Adoption Risks (P0-P3)

| Priority | Risk | Evidence | Tag |
|----------|------|----------|-----|
| **P0** | No LICENSE file — legal status unknown | Root directory and all subdirectories contain no LICENSE file | LEGAL_RISK |
| **P0** | `ontology_graph_gate.py` is a registered no-op — fires on every Edit/Write, reads missing file, silently passes | `hooks/ontology_graph.json` does not exist; `ontology_graph_gate.py` line 23: `GRAPH_PATH = Path(__file__).parent / "ontology_graph.json"` | RUNTIME_RISK |
| **P0** | Installation command unverified — users may be unable to install | `claude plugin add HHSsub/odd` — Claude Code does not document a `plugin add` subcommand per available docs | ADOPTION_RISK |
| **P1** | `git_commit_push_check.py` is a personal portfolio hook in a public plugin | Line 16: `PORTFOLIO_MARKER = "dynamic_portfolio"` — this only activates for a specific private project but runs on every Bash `git push` for all users | CONFLICT, RUNTIME_RISK |
| **P1** | `agent_pyramid_gate.py` is dead code — not registered in hooks.json | No `"Agent"` matcher in hooks.json; hook will never execute despite appearing in CLAUDE.md docs | CONFLICT |
| **P1** | `ontology_learning_enforce_stop` triggers on conversations with 3+ user messages | Line 117: `if user_count >= 3 and assistant_count >= 2` — nearly every multi-turn conversation qualifies; massively over-triggers | RUNTIME_RISK |
| **P1** | `tdd_enforce_stop` blocks all sessions ending with document edits (no verification command possible for .md files) | No file-type exemption for non-code files; any README edit forces a verification command | RUNTIME_RISK |
| **P1** | SSOT violation in plugin itself: hook count stated in 3 places (README: 10, CLAUDE.md: 14, hooks.json: 13, actual .py count: 14) | README.md line 42, CLAUDE.md line 57, hooks directory | CONFLICT |
| **P2** | `ontology_violation_gate.py` exits with code 1, not 2 — inconsistent with all other blocking hooks which use exit 2 | Line 181: `sys.exit(1)` vs. all other hooks use `return 2` / `sys.exit(2)` | RUNTIME_RISK |
| **P2** | Manual install (cp skills + commands) leaves hooks uninstalled — no hooks in manual install path | docs/guide/installation.md: only skills and commands are cp'd | ADOPTION_RISK |
| **P2** | `pyramid_label` SKILL.md hardcodes file extensions — contradicts `ontology-rebuild` SKILL.md's explicit anti-hardcoding rule | `pyramid-label/SKILL.md` line 82 vs `ontology-rebuild/SKILL.md` Step 1 | CONFLICT |
| **P2** | `ontology-learning` SKILL.md references absolute path `C:/Users/User/.claude/hooks/` | Phase 6 example code: `C:/Users/User/.claude/hooks/ontology_violation_gate.py` — non-portable | RUNTIME_RISK |
| **P3** | `pptx_validate_hook.py` requires `python-pptx` which is not declared as a dependency anywhere | Line 39: `from pptx import Presentation` — no requirements.txt, no dependency declaration | RUNTIME_RISK |
| **P3** | Terminology mismatch: "ontology" means different things to different audiences | External research docs (special_advice) explicitly note this problem | ADOPTION_RISK |

---

## 11. Strategic Conclusion

**The existing blueprint (`special_advice/ODD 전체개선 청사진`) is correct in sequence and covers the right categories.** The Phase 1 → 2 → 3 → 4 → 5 order (Audit → Hygiene → Positioning → Formal Layer → Hook Stability) is the right priority order. This audit confirms and deepens Phase 1's findings.

**What the blueprint gets right:**
- Identifies license, metadata inconsistency, installation verification as Phase 2 blockers — confirmed as P0/P1 issues.
- Identifies the "ontology" naming problem as requiring Phase 3 positioning work — confirmed as significant.
- Phase 5 (hook stability: severity separation, allowlist, false-positive logging) is urgently needed — confirmed by this audit's finding that 3+ hooks have over-triggering conditions.
- Phase 6 (accessibility, quickstart, examples) is correctly identified as post-hygiene.

**What the blueprint misses or underweights:**
1. **The missing `ontology_graph.json` is not mentioned.** This is a P0 runtime defect that will cause every user to experience a broken hook on every Edit/Write call.
2. **The `git_commit_push_check.py` portfolio contamination is not mentioned.** A personal-project hook shipping in a public plugin is a direct violation of ODD's own SSOT principle and must be fixed before any public release.
3. **`agent_pyramid_gate.py` dead code is not mentioned.** A hook that appears in documentation but never executes is a documentation integrity failure.
4. **The `ontology_learning_enforce_stop` over-triggering condition (user_count >= 3) is not mentioned.** This will be the highest-friction user experience issue at first contact.
5. **Exit code inconsistency (ontology_violation_gate uses exit 1, others use exit 2)** is a protocol-level bug not mentioned.
6. **The blueprint's Phase 4 (Formal Ontology Layer) is premature** relative to the current state. Phases 2 and 5 must be completed first — formal layer work with a broken hook system is waste.

**Most important immediate direction:** Fix the 5 P0/P1 runtime bugs before any documentation or positioning work. A broken plugin cannot be improved by better docs.
