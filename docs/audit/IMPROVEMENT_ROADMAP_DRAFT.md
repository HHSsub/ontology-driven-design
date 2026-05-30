# Improvement Roadmap Draft
<!-- Generated from main branch audit, 2026-05-30 -->
<!-- Based on: ODD_CURRENT_STATE_AUDIT.md + ISSUE_REGISTER.md + special_advice/ODD 전체개선 청사진 -->

---

## Relationship to Existing Blueprint

The existing blueprint (`special_advice/ODD 전체개선 청사진`) is **structurally sound and correctly ordered.** The Phase 1→2→3→4→5→6→7→8 sequence is valid. This roadmap does not replace it — it refines it based on audit evidence.

**Where the blueprint is right:**
- Phase 1 (Audit) → Phase 2 (Product Hygiene) → Phase 3 (Positioning) ordering is correct.
- The license/metadata/installation issues identified in Phase 2 are confirmed as P0/P1 blockers.
- Phase 3's recommended repositioning ("purpose-governed engineering layer") is exactly right.
- Phase 5's hook stability work (severity separation, allowlist, false-positive reduction) is confirmed as critical.
- Phase 4 (Formal Ontology Layer) correctly deferred until Phases 2-3 are complete.

**Where the blueprint is wrong or incomplete:**

1. **Phase 2 misses the five runtime bugs found in this audit.** The blueprint's Phase 2 focus on "라이선스·설치·메타데이터" is necessary but not sufficient. Before documentation can be trusted, the runtime is broken: `ontology_graph_gate.py` is a registered no-op, `git_commit_push_check.py` is a private project artifact, `agent_pyramid_gate.py` is dead code, `ontology_learning_enforce_stop` over-triggers, `ontology_violation_gate` uses wrong exit code. These must be fixed in Phase 2, not Phase 5.

2. **The blueprint treats Phase 5 (Hook Stability) as post-positioning.** This audit finds that hook runtime bugs are P0/P1 issues that block trust in Phase 2. Recommend merging runtime bug fixes into Phase 2 as a prerequisite batch.

3. **Phase 4 (Formal Ontology Layer) timeline is premature.** With 3 P0 bugs and 8 P1 issues unfixed, adding a formal ontology layer adds surface area without improving reliability. Phase 4 should not start until Phase 5's hook stability work confirms hook behavior is trustworthy.

4. **The blueprint has no phase for test infrastructure.** `verify.js` currently checks 6 file paths. The entire hook system has zero automated tests. A project that enforces TDD for its users but has no tests for its own hooks is philosophically incoherent. A "Test Infrastructure" phase is needed before Phase 4.

---

## Recommended Phase Order

| Phase | Name | Prerequisite | Issues Addressed |
|-------|------|-------------|-----------------|
| 2A | Runtime Bug Fixes | Phase 1 (this audit) | ISSUE-002, 004, 005, 006, 008, 009 |
| 2B | Product Hygiene | Phase 2A | ISSUE-001, 003, 007, 010, 011, 015, 016, 017, 020 |
| 3 | Positioning & Terminology | Phase 2B | ISSUE-014, 012, 013, 018 |
| 4 | Test Infrastructure | Phase 3 | Enables trust in all subsequent work |
| 5 | Hook Stability | Phase 4 | ISSUE-019, 021, (general false-positive reduction) |
| 6 | Formal Ontology Layer | Phase 5 | Blueprint Phase 4 deliverables |
| 7 | Accessibility & Onboarding | Phase 6 | Blueprint Phase 6 deliverables |
| 8 | Evidence & Benchmarks | Phase 7 | ISSUE-022 |
| 9 | Ecosystem Expansion | Phase 8 | Blueprint Phase 8 |

---

## Phase 2A: Runtime Bug Fixes

- **L0**: Users who install ODD must not encounter silent failures or personal project artifacts in their sessions.
- **Precondition**: Phase 1 audit complete (this document).
- **Deliverables**:
  1. Create `hooks/ontology_graph.json` with minimal valid schema OR remove `ontology_graph_gate.py` from hooks.json registration (removes ISSUE-002)
  2. Remove `git_commit_push_check.py` from hooks.json; move logic to author's private CLAUDE.md (removes ISSUE-004)
  3. Add "Agent" matcher to hooks.json for `agent_pyramid_gate.py` (removes ISSUE-005)
  4. Fix `ontology_learning_enforce_stop.py`: remove `user_count >= 3` trigger condition; require actual `is_error:true` signal only (removes ISSUE-006)
  5. Change `ontology_violation_gate.py` `sys.exit(1)` to `sys.exit(2)` (removes ISSUE-008)
  6. Add `.md` / documentation file exemptions to `tdd_enforce_stop.py` (removes ISSUE-009)
- **Success Criteria**: All 13 registered hooks can be exercised with a test input that produces the expected exit code (0=pass, 2=block). No hook silently fails due to missing dependencies.
- **Issues Addressed**: ISSUE-002, ISSUE-004, ISSUE-005, ISSUE-006, ISSUE-008, ISSUE-009
- **Estimated Complexity**: Low — all fixes are small, targeted code changes in existing .py files.

---

## Phase 2B: Product Hygiene

- **L0**: ODD must meet the minimum trust bar for an open-source Claude Code plugin — legal clarity, verifiable installation, consistent documentation.
- **Precondition**: Phase 2A complete.
- **Deliverables**:
  1. `LICENSE` file (MIT or Apache-2.0) in repository root (removes ISSUE-001)
  2. `"license"` field added to package.json and plugin.json
  3. Installation command verified against current Claude Code CLI; README updated with confirmed method (removes ISSUE-003)
  4. Hook count reconciled: hooks.json is SSOT; CLAUDE.md hook table updated (removes ISSUE-007)
  5. Skill count reconciled: CLAUDE.md lists all 8 skills; README updated (removes ISSUE-010)
  6. Manual installation docs updated to include hooks/ installation (removes ISSUE-011)
  7. `python-pptx` added to a new `requirements.txt` with Python version requirement (removes ISSUE-015)
  8. `marketplace.json` — clarify purpose or remove (removes ISSUE-016)
  9. `getting-started.md` step numbering fixed; hook table corrected (removes ISSUE-017)
  10. `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md` minimal versions added (removes ISSUE-020)
  11. Git tag `v1.0.0` created
- **Success Criteria**: `verify.js` passes with an expanded check list that includes LICENSE existence, consistent hook count between hooks.json and CLAUDE.md, Python requirements.txt existence. Installation can be performed by a new user following docs without errors.
- **Issues Addressed**: ISSUE-001, ISSUE-003, ISSUE-007, ISSUE-010, ISSUE-011, ISSUE-015, ISSUE-016, ISSUE-017, ISSUE-020
- **Estimated Complexity**: Low — file creation and documentation updates, no architecture changes.

---

## Phase 3: Positioning and Terminology

- **L0**: A new user reading the README must understand what ODD actually does and does not do before investing setup time. No expectation mismatch at first contact.
- **Precondition**: Phase 2B complete (documentation must be trustworthy before repositioning it).
- **Deliverables**:
  1. `docs/concepts/ONTOLOGY_POSITIONING.md` — defines "ontology" as used in ODD vs. formal ontology (removes ISSUE-014)
  2. `docs/concepts/ODD_GLOSSARY.md` — practitioner-friendly definitions for L0/L1/L2/L3, existence-clinging, SSOT, pyramid thinking, ontology-detach
  3. `docs/concepts/FORMAL_ONTOLOGY_BOUNDARY.md` — explicit "ODD is NOT" list
  4. README first paragraph rewritten to blueprint's suggested positioning: "ODD is a purpose-governed engineering layer for AI coding agents"
  5. `pyramid-label/SKILL.md` updated to use binary detection instead of hardcoded extensions (removes ISSUE-012)
  6. `ontology-learning/SKILL.md` Phase 6 example code updated to remove user-specific absolute paths (removes ISSUE-013)
  7. `SKILL-MAP.md` updated to disclose superpowers dependency and explain how to use ODD without it (removes ISSUE-018)
- **Success Criteria**: README can be read by a developer unfamiliar with 피라미드사고법 and they understand (a) what problem ODD solves, (b) what ODD enforces automatically vs. requires manual invocation, (c) what ODD does NOT do (formal ontology).
- **Issues Addressed**: ISSUE-012, ISSUE-013, ISSUE-014, ISSUE-018
- **Estimated Complexity**: Medium — requires careful writing that accurately represents the product.

---

## Phase 4: Test Infrastructure

- **L0**: A plugin that enforces TDD on its users must have its own hook behavior validated automatically. Every future change must have a regression test.
- **Precondition**: Phase 3 complete. Runtime is stable (Phase 2A). Documentation is accurate (Phase 2B-3).
- **Deliverables**:
  1. `tests/` directory with per-hook test scripts
  2. Each hook tested with: (a) input that should pass (exit 0 expected), (b) input that should block (exit 2 expected), (c) edge cases (empty transcript, missing files, short files)
  3. `verify.js` expanded to run hook tests and validate exit codes
  4. GitHub Actions CI workflow runs tests on every push
  5. Test coverage for `violation_registry.json` rules
- **Success Criteria**: `node verify.js` reports test pass/fail for all 13 registered hooks. CI workflow is green on main branch. Adding a new hook without a test fails CI.
- **Issues Addressed**: Enables trust in all future hook changes. Prevents regression of Phase 2A fixes.
- **Estimated Complexity**: Medium — test framework setup is straightforward; writing comprehensive test cases requires understanding each hook's intent.

---

## Phase 5: Hook Stability and Policy Engine

- **L0**: Hook enforcement must be proportional, configurable, and honest about what it can and cannot detect. A false-positive that blocks legitimate work destroys adoption faster than any bug.
- **Precondition**: Phase 4 (test infrastructure) complete. Hooks are tested and their current behavior is known.
- **Deliverables** (mirrors Blueprint Phase 5 with refinements):
  1. Severity model: `block` (exit 2), `warn` (exit 0 + message), `info` (exit 0 + silent log)
  2. `.odd/config.yaml` — per-project configuration: which hooks are active, which are warn-only
  3. `.odd/allowlist.yaml` — per-project exemptions (e.g., "skip tdd_enforce for *.md files" globally)
  4. False-positive reporting: hook outputs include a "report false positive" instruction
  5. Hook result logging: violations logged to `.odd/violation_log.jsonl` for trend analysis
  6. CI mode vs. Claude Code hook mode: different severity defaults for automated vs. interactive use
  7. `pyramid_guard.py` regex narrowing (removes ISSUE-019)
  8. `violation_registry.json` personal-use branches moved to per-project config (removes ISSUE-021)
- **Success Criteria**: A test project can configure ODD in `warn-only` mode. A CI run in block mode with a known violation produces exit 2. Per-project allowlist suppresses known false positives. Zero regression on Phase 2A fixes.
- **Issues Addressed**: ISSUE-019, ISSUE-021, general false-positive reduction
- **Estimated Complexity**: High — policy engine architecture requires careful design to avoid over-engineering. Blueprint's suggestion (policy_engine.py, severity.py, config_loader.py, evidence_checker.py, report_writer.py) is a good starting structure.

---

## Phase 6: Formal Ontology Layer

- **L0**: ODD's conceptual framework must be expressible as machine-readable artifacts that other tools and agents can consume — without requiring Protégé or OWL expertise from users.
- **Precondition**: Phase 5 complete. Hooks are stable and reliable. Ontology enforcement is trustworthy enough to build formal layer on top.
- **Deliverables** (mirrors Blueprint Phase 4):
  1. `ontology/concept-registry.yaml` — L0/L1/L2/L3 and related concepts defined
  2. `ontology/relationships.yaml` — how concepts relate (L0 governs L1, L1 constrains L2, etc.)
  3. `ontology/constraints.yaml` — what violations break the ontology
  4. `schemas/odd.schema.json` — JSON Schema for ODD artifacts (ONBOARDING.md structure, L-level declarations)
  5. `schemas/odd.linkml.yaml` — LinkML model (enables JSON Schema + OWL export)
  6. `docs/formal-layer/CONCEPT_REGISTRY.md` — human-readable concept registry
  7. `docs/formal-layer/COMPETENCY_QUESTIONS.md` — what questions the ODD ontology can answer
  8. `docs/formal-layer/LINKML_EXPORT.md` — how to use the LinkML schema
  9. RDF/OWL export: interface design only (not implementation) — deferred per blueprint's recommendation
- **Success Criteria**: `odd.schema.json` validates a generated ONBOARDING.md. LinkML schema can be rendered as OWL by external tools. At least 3 competency questions are answerable from the concept registry.
- **Issues Addressed**: All ONTOLOGY dimension gaps from Section 6 of the audit.
- **Estimated Complexity**: High — requires ontology modeling expertise. LinkML is the recommended tool bridge. This phase fundamentally changes ODD's category from "governance plugin" to "purpose-governed engineering layer with machine-readable ontology."

---

## Phase 7: Accessibility and Onboarding

- **L0**: Any developer using Claude Code must be able to understand and adopt ODD's core discipline within 10 minutes of first contact.
- **Precondition**: Phase 6 (formal layer) complete OR Phase 5 complete (can be parallelized with Phase 6).
- **Deliverables** (mirrors Blueprint Phase 6):
  1. `docs/quickstart.md` — 5-minute onboarding with single working example
  2. `docs/examples/solo-developer.md` — complete workflow for solo developer
  3. `docs/examples/small-team.md` — workflow for 2-5 person team
  4. `docs/examples/legacy-refactor.md` — applying ODD to existing codebase
  5. `docs/examples/enum-registry-change.md` — SSOT dependency chain example
  6. `templates/minimal/` — minimal ODD config (only pyramid_ontology_gate + pyramid_guard)
  7. `templates/strict/` — full ODD config (all hooks active in block mode)
  8. `templates/team/` — team config with allowlist and warn-only for selected hooks
  9. `odd-onboarding` skill improvement: generate output files, not just ask questions
  10. Before/After examples for each major hook's enforcement
- **Success Criteria**: A developer new to ODD can complete the quickstart in under 10 minutes. The `odd-onboarding` skill produces a validated ONBOARDING.md on first run.
- **Issues Addressed**: Accessibility gap (general)
- **Estimated Complexity**: Medium — content creation work, no new engineering.

---

## Phase 8: Evidence and Benchmarks

- **L0**: ODD's value claims must be supported by measurable, reproducible evidence that potential adopters can evaluate.
- **Precondition**: Phase 7 complete. Several real-world projects using ODD.
- **Deliverables** (mirrors Blueprint Phase 7):
  1. `benchmarks/cases/` — 3-5 documented project cases
  2. `benchmarks/results/` — measured outcomes per case
  3. `docs/case-studies/case-001-vibe-drift.md` — example: AI coding without ODD vs. with ODD
  4. `docs/case-studies/case-002-enum-regression.md` — SSOT enforcement preventing bug
  5. `docs/case-studies/case-003-architecture-drift.md` — L0-L3 labels preventing scope creep
  6. Published metrics: false-positive rate, block rate, hook disable rate, onboarding completion rate
- **Success Criteria**: At least one case study with quantitative comparison (before/after). False-positive rate documented and below 5% for key hooks.
- **Issues Addressed**: ISSUE-022
- **Estimated Complexity**: Low (documentation) but requires real usage data — time-dependent.

---

## Phase 9: Ecosystem Expansion

- **L0**: ODD's purpose-governance discipline must be accessible to developers using Claude Code, Codex, GitHub Copilot, Cursor, and Continue — not just Claude Code users.
- **Precondition**: Phase 8 complete. ODD has validated evidence of effectiveness. Formal ontology layer (Phase 6) provides machine-readable export for other tools.
- **Deliverables** (mirrors Blueprint Phase 8):
  1. `ports/claude-code/` — current implementation, packaged correctly
  2. `ports/codex/` — Codex Skills adaptation
  3. `ports/copilot/` — GitHub Copilot Agent Skills adaptation
  4. `ports/continue/` — Continue plugin adaptation
  5. `docs/integrations/` — per-tool integration guide
- **Issues Addressed**: Ecosystem reach
- **Estimated Complexity**: High — requires familiarity with each target platform's extension model.

---

## Intentionally Deferred

**RDF/OWL implementation** (Phase 6 only designs the interface): Full OWL/RDF/SPARQL is deferred until there is demonstrated demand. LinkML provides the bridge if needed.

**Multi-language hook support (non-Python)**: All hooks are Python. Cross-platform hook execution in other languages is deferred until Python dependency issues are resolved first.

**GUI/IDE integration**: All ODD enforcement is CLI/hook-based. Browser extension, VS Code extension, etc. are deferred indefinitely — they are not Claude Code plugins.

**Marketplace publishing**: Deferred until Phases 2A-2B are complete and installation command is verified. Publishing a broken plugin to a marketplace is worse than not publishing.

---

## Open Questions

These require the repo owner's (황회선) decision before execution can proceed:

1. **License choice**: MIT (most permissive, maximum adoption) vs. Apache-2.0 (patent protection) vs. Creative Commons (if non-commercial only)? The answer affects how teams can use ODD.

2. **`ontology_graph.json` direction**: Should Phase 2A create a minimal `ontology_graph.json` to make `ontology_graph_gate` functional? Or remove the hook from registration and design the graph properly in Phase 6? The Phase 6 formal ontology layer would provide a better foundation for this hook.

3. **Superpowers dependency**: Should ODD remain dependent on the `superpowers` plugin ecosystem, or should Phase 7 build ODD-native equivalents for the most critical skills? The `superpowers:*` dependency is invisible to users and undisclosed.

4. **Korean/English language strategy**: Is ODD's primary audience Korean-speaking developers? If yes, English docs are secondary. If ODD aims for international adoption, English must be primary with Korean as secondary. This affects Phase 3 positioning work significantly.

5. **`git_commit_push_check.py` preservation**: The portfolio Vercel deployment logic in this hook is presumably useful for the author's personal workflow. Does it belong in a separate private plugin, or should a generalized "post-push deployment trigger" be designed for Phase 5?

6. **Hook configurability scope**: Should Phase 5's `.odd/config.yaml` allow users to completely disable any hook, or only downgrade from block to warn? Full disable allows ODD to degrade to zero enforcement (undermining its purpose). Warn-only downgrade preserves philosophical intent while reducing friction.
