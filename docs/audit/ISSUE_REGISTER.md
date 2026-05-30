# Issue Register
<!-- Generated from main branch audit, 2026-05-30 -->
<!-- All issues are OPEN. No code was modified during this audit. -->

## How to Read This

- **ID**: ISSUE-NNN
- **Category**: PRODUCT_HYGIENE | ONTOLOGY | PHILOSOPHY | PLUGIN | HOOK | ACCESSIBILITY | MARKET
- **Severity**: P0 (blocking) | P1 (critical) | P2 (important) | P3 (nice-to-have)
- **Status**: OPEN
- **Tags**: CONFLICT | ADOPTION_RISK | LEGAL_RISK | RUNTIME_RISK | UNVERIFIED

---

## Issues

### ISSUE-001
- **ID**: ISSUE-001
- **Category**: PRODUCT_HYGIENE
- **Severity**: P0
- **Title**: No LICENSE file — legal status unknown for all users and contributors
- **Evidence**: Complete repository tree scan found no file named LICENSE, LICENSE.md, LICENSE.txt, or any equivalent. plugin.json has no `"license"` field. package.json has no `"license"` field.
- **Risk**: LEGAL_RISK
- **Impact**: Any user who installs this plugin cannot legally distribute, modify, or use it in a commercial context without explicit permission from the author. Teams or companies considering adoption cannot proceed. GitHub by default applies "all rights reserved" to repositories without a license.
- **Proposed Resolution**: Add a LICENSE file (MIT recommended for broad adoption) to the repository root. Add `"license": "MIT"` to package.json and plugin.json. This is a 10-minute fix that unblocks all downstream adoption.
- **Status**: OPEN

---

### ISSUE-002
- **ID**: ISSUE-002
- **Category**: HOOK
- **Severity**: P0
- **Title**: `ontology_graph_gate.py` references missing `ontology_graph.json` — registered hook is a runtime no-op
- **Evidence**: `hooks/ontology_graph_gate.py` line 23: `GRAPH_PATH = Path(__file__).parent / "ontology_graph.json"`. File `hooks/ontology_graph.json` does not exist anywhere in the repository (confirmed by full glob scan). The hook is registered in `hooks/hooks.json` under `PreToolUse` for `Edit|Write|NotebookEdit`. The `load_graph()` function catches the FileNotFoundError and returns `{}`. With an empty graph, `match_file_node()` returns `None` on line 33, causing `main()` to return 0 (pass) on line 87.
- **Risk**: RUNTIME_RISK, CONFLICT
- **Impact**: Every Edit/Write/NotebookEdit call in any user's session runs this hook, paying the overhead of the hook invocation + Python startup + file read attempt + silent failure. The hook is documented in CLAUDE.md as providing "ontology graph consistency" checking but provides zero enforcement. Users believe they have a guard that does not exist.
- **Proposed Resolution**: Either (a) create `hooks/ontology_graph.json` with the expected schema defining file semantics, or (b) remove `ontology_graph_gate.py` from `hooks/hooks.json` until the graph file is created. Option (b) is safer and takes 2 minutes.
- **Status**: OPEN

---

### ISSUE-003
- **ID**: ISSUE-003
- **Category**: PLUGIN
- **Severity**: P0
- **Title**: Installation command `claude plugin add HHSsub/odd` is unverified against Claude Code CLI
- **Evidence**: README.md lines 14-19 and docs/guide/installation.md lines 5-15 both document `claude plugin add HHSsub/ontology-driven-design` and `claude plugin add HHSsub/odd`. Claude Code's publicly documented installation mechanisms reference either marketplace installation or `--plugin-dir` local loading. The `plugin add <github-shorthand>` pattern is not confirmed in any file in this repository to have been tested successfully.
- **Risk**: UNVERIFIED, ADOPTION_RISK
- **Impact**: A user following the documented installation path may find the command does not exist or fails. First contact failure is the highest adoption barrier possible.
- **Proposed Resolution**: Test the installation command on a clean Claude Code installation. Document the exact Claude Code CLI version that was tested. If `claude plugin add` does not work, document the working installation method (likely `--plugin-dir` or manual copy). Update README and docs to reflect the verified method.
- **Status**: OPEN

---

### ISSUE-004
- **ID**: ISSUE-004
- **Category**: HOOK
- **Severity**: P1
- **Title**: `git_commit_push_check.py` is a private portfolio hook shipping in a public plugin
- **Evidence**: `hooks/git_commit_push_check.py` line 16: `PORTFOLIO_MARKER = "dynamic_portfolio"`. The hook only activates when the git repository root path contains the string "dynamic_portfolio". The hook is registered in `hooks/hooks.json` under PostToolUse for Bash. For all non-portfolio users, the hook runs on every Bash command, calls `git rev-parse`, checks for "dynamic_portfolio" in the path, and silently exits. The hook name and description in CLAUDE.md describes it as "Warns if unpushed commits after git commit" — which is not what the actual code does (it triggers Vercel deployment for a specific private project).
- **Risk**: CONFLICT, RUNTIME_RISK
- **Impact**: (1) Every user running any Bash command in a git repository pays overhead for a hook that does nothing for them. (2) The hook description is inaccurate — it claims to be a generic git check but is actually a portfolio-specific Vercel deploy trigger. (3) This is a direct violation of ODD's own SSOT principle: the plugin's purpose is not portfolio deployment. (4) `git_push_enforce_stop.py` already handles the generic "warn on unpushed commits" use case that the CLAUDE.md description claims this hook does.
- **Proposed Resolution**: Remove `git_commit_push_check.py` from the public plugin's hooks.json. Move it to the author's private CLAUDE.md configuration where it belongs. If a generic "warn on unpushed commits after git push" hook is desired, that logic already exists in `git_push_enforce_stop.py` and should be documented correctly.
- **Status**: OPEN

---

### ISSUE-005
- **ID**: ISSUE-005
- **Category**: HOOK
- **Severity**: P1
- **Title**: `agent_pyramid_gate.py` is dead code — not registered in hooks.json
- **Evidence**: `hooks/agent_pyramid_gate.py` exists and implements a PreToolUse hook for the "Agent" tool name. `hooks/hooks.json` has no matcher for "Agent" tool — only "WebSearch", "Bash", "Edit|Write|NotebookEdit". CLAUDE.md does not list this hook in its hook table. The hook therefore never fires.
- **Risk**: CONFLICT
- **Impact**: The hook provides valuable governance (L0 declaration + role specification enforcement for Agent tool calls, Opus recommendation for strategy work). This governance is silently absent. Any user relying on Agent tool call governance is unprotected.
- **Proposed Resolution**: Add to `hooks/hooks.json` under PreToolUse: `{"matcher": "Agent", "hooks": [{"type": "command", "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/agent_pyramid_gate.py\""}]}`. Then document it in CLAUDE.md's hook table.
- **Status**: OPEN

---

### ISSUE-006
- **ID**: ISSUE-006
- **Category**: HOOK
- **Severity**: P1
- **Title**: `ontology_learning_enforce_stop.py` triggers on any conversation with 3+ user turns
- **Evidence**: `hooks/ontology_learning_enforce_stop.py` lines 117-118: `if user_count >= 3 and assistant_count >= 2 and failure_idx < 0: failure_idx = 0  # 반복 교정 구조 자체를 실패 신호로 취급`. The `user_count` counts ALL user messages in the last 40 transcript entries, not specifically correction messages. Any productive multi-turn conversation (asking follow-up questions, clarifying scope, iterating on design) will have 3+ user turns and 2+ assistant responses — this is normal usage, not a failure signal.
- **Risk**: RUNTIME_RISK
- **Impact**: Users will experience constant false-positive blocks at session end when they have not made any mistakes but simply had a normal conversation. This is the most likely hook to cause user abandonment of ODD.
- **Proposed Resolution**: Remove the `user_count >= 3` heuristic. Keep only the `is_error:true` tool result detection as a reliable failure signal. If user correction detection is desired, require explicit correction language patterns in user messages (e.g., "틀렸어", "wrong", "incorrect", "다시", "아니야") rather than message count.
- **Status**: OPEN

---

### ISSUE-007
- **ID**: ISSUE-007
- **Category**: HOOK
- **Severity**: P1
- **Title**: Hook count inconsistency across README, CLAUDE.md, hooks.json, and actual .py files
- **Evidence**: README.md does not list a hook count. CLAUDE.md line 57: "14 hooks, auto-trigger". hooks.json has 13 entries registered. Actual .py files in hooks/: 14 files. Previous README (referenced in commit history) said "10 hooks". None of these numbers agree.
- **Risk**: CONFLICT, ADOPTION_RISK
- **Impact**: Users reading documentation cannot trust the stated hook count. If documentation is wrong about a simple factual count, users will doubt other claims. This is a symptom of documentation not being updated when hooks are added.
- **Proposed Resolution**: Establish hooks.json as SSOT for "active hooks." Update CLAUDE.md to derive its hook table from hooks.json. Establish a verification step in `verify.js` that counts hooks.json entries and compares to CLAUDE.md.
- **Status**: OPEN

---

### ISSUE-008
- **ID**: ISSUE-008
- **Category**: HOOK
- **Severity**: P2
- **Title**: `ontology_violation_gate.py` uses exit code 1 while all other blocking hooks use exit code 2
- **Evidence**: `hooks/ontology_violation_gate.py` line 181: `sys.exit(1)`. All other blocking hooks (`pyramid_guard.py`, `ontology_declare_enforce.py`, `tdd_enforce_stop.py`, `git_push_enforce_stop.py`, `websearch_yearguard.py`, `pyramid_ontology_gate.py`, `assumption_declaration_gate.py`, `ontology_learning_enforce_stop.py`, `destructive_bash_gate.py`) use `sys.exit(2)` or `return 2` for blocking behavior.
- **Risk**: RUNTIME_RISK, CONFLICT
- **Impact**: Claude Code's hook system likely treats exit codes differently. Exit code 2 is the documented "block" signal. Exit code 1 may be treated as "error" rather than "block" — the tool might proceed despite the violation gate firing. The intent of this hook (blocking LOCKED file writes) may not be enforced.
- **Proposed Resolution**: Change `sys.exit(1)` to `sys.exit(2)` in `ontology_violation_gate.py` to match all other blocking hooks.
- **Status**: OPEN

---

### ISSUE-009
- **ID**: ISSUE-009
- **Category**: HOOK
- **Severity**: P1
- **Title**: `tdd_enforce_stop.py` blocks sessions ending with documentation edits — no code file exemption
- **Evidence**: `hooks/tdd_enforce_stop.py` has no file-type exemption. Any session where the last Edit/Write was to a `.md`, `.json`, `.yaml`, `.txt`, or similar non-code file will trigger the block because no verification command (pytest, npm test, etc.) can meaningfully verify a documentation change. VERIFICATION_PATTERNS list covers Python, JS/TS, Go, Rust, Java, C#, curl — nothing covers "documentation was updated correctly."
- **Risk**: RUNTIME_RISK
- **Impact**: Users who update README.md, SKILL.md, docs, or any markdown documentation cannot close their Claude Code session without running an arbitrary test command. This creates artificial friction for the most common editing task (documentation). It contradicts the ODD philosophy that enforcement should be purposeful — there is no L0 for "verify documentation edits with a test command."
- **Proposed Resolution**: Add a file extension exemption list for documentation files (`.md`, `.txt`, `.rst`, `.json` config files). The hook should only apply when the last edited file is a code file.
- **Status**: OPEN

---

### ISSUE-010
- **ID**: ISSUE-010
- **Category**: PRODUCT_HYGIENE
- **Severity**: P2
- **Title**: Skill count inconsistency across README.md and CLAUDE.md
- **Evidence**: README.md line 42 says "Skills (6)" and lists 6. CLAUDE.md line 7-17 shows 7 skills. Repository contains 8 SKILL.md files: pyramid-ontology, ontology-detach, ontology-rebuild, pyramid-label, pyramid-topology, ontology-review-gate, ontology-learning, odd-onboarding.
- **Risk**: CONFLICT, ADOPTION_RISK
- **Impact**: Minor trust erosion. New users comparing README to docs will find inconsistencies. `odd-onboarding` is missing from README. `ontology-learning` count varies.
- **Proposed Resolution**: Update README.md to say "8 skills" and list all 8. Establish CLAUDE.md as SSOT for skill list.
- **Status**: OPEN

---

### ISSUE-011
- **ID**: ISSUE-011
- **Category**: ACCESSIBILITY
- **Severity**: P2
- **Title**: Manual installation path in docs leaves hooks uninstalled
- **Evidence**: `docs/guide/installation.md` lines 33-44 shows manual install as: `cp -r ontology-driven-design/skills/* ~/.claude/skills/` and `cp ontology-driven-design/commands/* ~/.claude/commands/`. No instruction to copy hooks directory or register hooks.json with Claude Code settings.
- **Risk**: ADOPTION_RISK
- **Impact**: A user following the manual install path gets skills and commands but no hook enforcement. They will experience none of the automatic blocking behavior. This is a severely degraded experience that may lead them to incorrectly conclude "ODD hooks don't work on my system."
- **Proposed Resolution**: Document complete manual install: copy hooks/ directory, add hooks.json configuration to Claude Code's settings.json. Or provide a setup script.
- **Status**: OPEN

---

### ISSUE-012
- **ID**: ISSUE-012
- **Category**: PHILOSOPHY
- **Severity**: P2
- **Title**: `pyramid-label` SKILL.md hardcodes file extensions — contradicts `ontology-rebuild` SKILL.md's explicit anti-hardcoding rule
- **Evidence**: `skills/pyramid-label/SKILL.md` line 82: "포함: `.py .ts .js .jsx .tsx .go .rb .java .yaml .yml .md .sh`". `skills/ontology-rebuild/SKILL.md` Step 1: "**대상 파일**: 바이너리가 아닌 모든 텍스트 파일. 확장자 하드코딩 금지. 파일 첫 8바이트에 `\x00`이 있으면 바이너리로 간주하고 스킵."
- **Risk**: CONFLICT
- **Impact**: ODD's own philosophy (ontology-detach, L2 hardcoding = use-case hardcoding) prohibits extension hardcoding. Two skills in the same plugin contradict each other on this point. A user applying `pyramid-label` gets a different file scope than a user applying `ontology-rebuild` to the same project.
- **Proposed Resolution**: Update `pyramid-label` SKILL.md to use the same binary-detection heuristic as `ontology-rebuild`: scan all files, skip those with `\x00` in first 8 bytes. Remove the hardcoded extension list.
- **Status**: OPEN

---

### ISSUE-013
- **ID**: ISSUE-013
- **Category**: ACCESSIBILITY
- **Severity**: P2
- **Title**: `ontology-learning` SKILL.md references absolute Windows path specific to one user
- **Evidence**: `skills/ontology-learning/SKILL.md` Phase 6 example code, line 151: `C:/Users/User/.claude/hooks/ontology_violation_gate.py`. This is an absolute path to a specific Windows user's home directory.
- **Risk**: RUNTIME_RISK, ADOPTION_RISK
- **Impact**: Any user following this example on macOS, Linux, or Windows with a different username will copy a path that does not exist on their system. This is a subtle bug that will cause confusion.
- **Proposed Resolution**: Replace with a path variable reference like `${HOME}/.claude/hooks/ontology_violation_gate.py` or platform-agnostic description "your Claude hooks directory."
- **Status**: OPEN

---

### ISSUE-014
- **ID**: ISSUE-014
- **Category**: MARKET
- **Severity**: P2
- **Title**: "Ontology" naming creates systematic expectation mismatch with technically literate users
- **Evidence**: The external research document `special_advice/ODD와 온톨로지적 AI 개발 보조 도구 조사.md` (an independent analysis) explicitly states: "ODD 플러그인은 '형식적 온톨로지 엔진'이라기보다 목적 중심 개발 거버넌스 플러그인에 가깝다." The same document rates ODD "아이디어 4점, 현재 제품화 2점." ODD contains zero RDF/OWL/SHACL/SPARQL/LinkML/reasoning artifacts. The term "ontology" in formal CS means something ODD does not implement.
- **Risk**: ADOPTION_RISK
- **Impact**: Developers familiar with formal ontology tools (Protégé, LinkML, ROBOT) will install ODD expecting machine-readable concept registries and get Markdown skills. Developers unfamiliar with ontology will be confused by the philosophical framing. Both audiences face an explanation gap at first contact.
- **Proposed Resolution**: Phase 3 of the blueprint addresses this. The proposed repositioning ("ODD is a purpose-governed engineering layer for AI coding agents") is correct. Add a "What ODD is NOT" section to README before the Quick Start. This is a documentation fix, not a feature change.
- **Status**: OPEN

---

### ISSUE-015
- **ID**: ISSUE-015
- **Category**: PRODUCT_HYGIENE
- **Severity**: P2
- **Title**: `pptx_validate_hook.py` depends on `python-pptx` which is not declared as a project dependency
- **Evidence**: `hooks/pptx_validate_hook.py` line 39: `from pptx import Presentation`. `package.json` devDependencies: only `typescript` and `vitepress`. No `requirements.txt`, no `pyproject.toml`, no mention of `python-pptx` in any dependency declaration file.
- **Risk**: RUNTIME_RISK
- **Impact**: On a system without `python-pptx` installed, the hook imports fail silently (the outer `try/except` on line 81 catches all exceptions and calls `sys.exit(0)`). User sees no error, assumes hook works, but PPTX validation is never happening.
- **Proposed Resolution**: Add `requirements.txt` with `python-pptx` and any other Python dependencies. Document Python version requirement. Or add an import-failure warning message before the silent exit.
- **Status**: OPEN

---

### ISSUE-016
- **ID**: ISSUE-016
- **Category**: PLUGIN
- **Severity**: P2
- **Title**: `marketplace.json` defines a non-standard schema with no documented purpose
- **Evidence**: `.claude-plugin/marketplace.json` wraps plugin data in a `"plugins"` array under an `"odd-marketplace"` name. Claude Code plugin documentation does not reference a `marketplace.json` file format. `plugin.json` already contains all the same data.
- **Risk**: ADOPTION_RISK, CONFLICT
- **Impact**: Redundant file creates confusion about which file is authoritative for plugin metadata. Adds maintenance burden (two files to update when version changes).
- **Proposed Resolution**: Determine whether Claude Code's plugin system requires or uses `marketplace.json`. If not required, remove it. If it is part of a planned multi-plugin marketplace, document its intended role.
- **Status**: OPEN

---

### ISSUE-017
- **ID**: ISSUE-017
- **Category**: PRODUCT_HYGIENE
- **Severity**: P2
- **Title**: `docs/guide/getting-started.md` has duplicate step numbering and incomplete hook table
- **Evidence**: File contains "### 3. 코드 작성 중 — 탈존재 점검" and "### 3. 리팩토링 전 — 위계 점검" — two sections numbered 3. The hook table in Step 2 lists only 3 hooks (`pyramid_guard`, `ontology_declare_enforce`, `git_push_enforce`) but there are 13 registered hooks.
- **Risk**: ADOPTION_RISK
- **Impact**: Users following the getting-started guide see incomplete information and duplicate step numbers. This undermines confidence in documentation quality.
- **Proposed Resolution**: Fix step numbering (3/4/5). Update hook table to accurately list the most important hooks with correct descriptions.
- **Status**: OPEN

---

### ISSUE-018
- **ID**: ISSUE-018
- **Category**: ACCESSIBILITY
- **Severity**: P2
- **Title**: `SKILL-MAP.md` references `superpowers:*` skills as active dependencies without disclosing the external dependency
- **Evidence**: `skills/pyramid-ontology/SKILL-MAP.md` lists `superpowers:test-driven-development`, `superpowers:verification-before-completion`, `superpowers:systematic-debugging`, `superpowers:brainstorming`, `superpowers:writing-plans`, `superpowers:executing-plans`, `superpowers:subagent-driven-development`, `superpowers:dispatching-parallel-agents`, `superpowers:using-superpowers`, `superpowers:using-git-worktrees`, `superpowers:finishing-a-development-branch`, `superpowers:requesting-code-review`, `superpowers:receiving-code-review`, `superpowers:writing-skills` as L1/L2 skill dependencies.
- **Risk**: ADOPTION_RISK
- **Impact**: A user installing ODD alone will not have the `superpowers:*` skills. Any workflow that depends on these skills will silently fail or degrade. This is an undisclosed external dependency.
- **Proposed Resolution**: Add a "Prerequisites" or "Works best with" section to README documenting that `superpowers` plugin is recommended for full functionality. Or make ODD fully self-contained by providing equivalent skills.
- **Status**: OPEN

---

### ISSUE-019
- **ID**: ISSUE-019
- **Category**: HOOK
- **Severity**: P2
- **Title**: `pyramid_guard.py` false-positive risk: broad regex patterns for L0/L1 validation
- **Evidence**: `hooks/pyramid_guard.py` `_TOOL_BINDING` regex (line 88-101) blocks `Python`, `.py`, `JavaScript`, `TypeScript`, `React`, `Vue`, `Next.js`, `Claude Code`, `Claude API` from appearing in L0/L1 lines. However, this pattern will also match valid L0/L1 content that legitimately references these names in non-binding ways (e.g., "L0: Claude Code 플러그인이 더 많은 개발자에게 채택됨"). The SSOT duplicate-truth detection (line 200-237) uses a 60% overlap threshold on string literals — this may trigger on intentionally parallel structures (e.g., navigation menus, comparison tables).
- **Risk**: RUNTIME_RISK
- **Impact**: Users writing legitimate L0/L1 declarations that mention their platform context will be blocked. The hook was designed to prevent tool-binding in L0/L1 but the regex is broader than the intent.
- **Proposed Resolution**: Narrow the `_TOOL_BINDING` pattern to only match when the tool name appears as the primary subject/verb of the L0/L1 declaration, not when mentioned as context. Or use negative lookahead patterns. For SSOT detection, increase threshold to 80% or add a minimum absolute overlap count of 5 items.
- **Status**: OPEN

---

### ISSUE-020
- **ID**: ISSUE-020
- **Category**: PRODUCT_HYGIENE
- **Severity**: P3
- **Title**: No SECURITY.md, CONTRIBUTING.md, or CHANGELOG.md
- **Evidence**: Full repository scan found none of these files.
- **Risk**: PRODUCT_HYGIENE
- **Impact**: Standard open-source community hygiene files are absent. GitHub's community standards checklist will show these as missing. Contributors have no guidance. Security researchers have no disclosure path.
- **Proposed Resolution**: Add minimal versions of each before public promotion. SECURITY.md: disclosure email. CONTRIBUTING.md: how to submit issues/PRs. CHANGELOG.md: v1.0.0 initial release entry.
- **Status**: OPEN

---

### ISSUE-021
- **ID**: ISSUE-021
- **Category**: ONTOLOGY
- **Severity**: P3
- **Title**: `violation_registry.json` `l1_branches` contains highly personal use cases as "global" rules
- **Evidence**: `hooks/violation_registry.json` `l1_branches` includes: `paid_api_parameter_validation` (references Mystic/FAL/Kling v2/v3 APIs), `research_data_code_integrity` (references GPU/model inference, research DB), `user_specified_data_integrity` (references video generation/job IDs), `ux_completion_requires_user_test` (references Duolingo as benchmark), `example_as_input_not_output` (personal creative work pattern). The comment at top of file states: "전역 파일 — 프로젝트 고유 케이스·경로·키워드 금지."
- **Risk**: CONFLICT
- **Impact**: The file's own documentation says project-specific cases are prohibited, yet the `l1_branches` contain exactly that — cases derived from specific projects (video generation APIs, research databases). These are not globally applicable governance rules; they are personal workflow patterns.
- **Proposed Resolution**: Move project-specific branches to a per-project `violation_registry.json` (or `.odd/policy.yaml` as Blueprint Phase 5 suggests). Keep global `violation_registry.json` only for truly general principles. This aligns with the file's own stated architecture.
- **Status**: OPEN

---

### ISSUE-022
- **ID**: ISSUE-022
- **Category**: MARKET
- **Severity**: P3
- **Title**: No usage metrics, benchmark data, or case studies — value claims are unvalidated
- **Evidence**: No `benchmarks/` directory. No `docs/case-studies/`. No data on false-positive rates, hook adoption rates, or measurable impact. Philosophy pages make strong claims ("Purpose-less code is garbage") without supporting evidence.
- **Risk**: ADOPTION_RISK
- **Impact**: Advanced users will ask: "Does this actually work?" Without evidence, adoption depends entirely on trust in the author's reputation. This limits reach beyond the author's existing network.
- **Proposed Resolution**: Blueprint Phase 7 addresses this correctly. Even one documented case study with before/after comparison would be more persuasive than all the philosophical framing combined.
- **Status**: OPEN

---

## Summary Table

| ID | Category | Severity | Title | Risk |
|----|----------|----------|-------|------|
| ISSUE-001 | PRODUCT_HYGIENE | P0 | No LICENSE file | LEGAL_RISK |
| ISSUE-002 | HOOK | P0 | `ontology_graph_gate.py` references missing `ontology_graph.json` | RUNTIME_RISK, CONFLICT |
| ISSUE-003 | PLUGIN | P0 | Installation command unverified | UNVERIFIED, ADOPTION_RISK |
| ISSUE-004 | HOOK | P1 | `git_commit_push_check.py` is a personal portfolio hook in public plugin | CONFLICT, RUNTIME_RISK |
| ISSUE-005 | HOOK | P1 | `agent_pyramid_gate.py` is dead code — not in hooks.json | CONFLICT |
| ISSUE-006 | HOOK | P1 | `ontology_learning_enforce_stop` over-triggers on normal conversations | RUNTIME_RISK |
| ISSUE-007 | PLUGIN | P1 | Hook count inconsistency across all documents | CONFLICT, ADOPTION_RISK |
| ISSUE-008 | HOOK | P2 | `ontology_violation_gate.py` uses exit(1) not exit(2) | RUNTIME_RISK, CONFLICT |
| ISSUE-009 | HOOK | P1 | `tdd_enforce_stop` blocks sessions with documentation edits | RUNTIME_RISK |
| ISSUE-010 | PRODUCT_HYGIENE | P2 | Skill count inconsistency: README says 6, repo has 8 | CONFLICT, ADOPTION_RISK |
| ISSUE-011 | ACCESSIBILITY | P2 | Manual install path leaves hooks uninstalled | ADOPTION_RISK |
| ISSUE-012 | PHILOSOPHY | P2 | `pyramid-label` hardcodes extensions, contradicts `ontology-rebuild` | CONFLICT |
| ISSUE-013 | ACCESSIBILITY | P2 | `ontology-learning` references absolute user-specific Windows path | RUNTIME_RISK, ADOPTION_RISK |
| ISSUE-014 | MARKET | P2 | "Ontology" naming creates expectation mismatch | ADOPTION_RISK |
| ISSUE-015 | PRODUCT_HYGIENE | P2 | `pptx_validate_hook` depends on undeclared `python-pptx` | RUNTIME_RISK |
| ISSUE-016 | PLUGIN | P2 | `marketplace.json` non-standard schema with no documented purpose | ADOPTION_RISK, CONFLICT |
| ISSUE-017 | PRODUCT_HYGIENE | P2 | `getting-started.md` has duplicate step numbering and wrong hook table | ADOPTION_RISK |
| ISSUE-018 | ACCESSIBILITY | P2 | `superpowers:*` undisclosed dependency | ADOPTION_RISK |
| ISSUE-019 | HOOK | P2 | `pyramid_guard.py` broad regex — false positive risk | RUNTIME_RISK |
| ISSUE-020 | PRODUCT_HYGIENE | P3 | Missing SECURITY.md, CONTRIBUTING.md, CHANGELOG.md | PRODUCT_HYGIENE |
| ISSUE-021 | ONTOLOGY | P3 | `violation_registry.json` l1_branches contain project-specific personal use cases | CONFLICT |
| ISSUE-022 | MARKET | P3 | No benchmark data or case studies | ADOPTION_RISK |
