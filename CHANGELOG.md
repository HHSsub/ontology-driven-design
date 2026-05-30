# Changelog

All notable changes to ODD are documented here.

---

## [1.1.0] — 2026-05-30

### Added
- `destructive_bash_gate.py` — blocks dangerous Bash commands (PreToolUse)
- `ontology_graph_gate.py` — ontology graph consistency gate (PreToolUse, requires ontology_graph.json)
- `ontology_learning_enforce_stop.py` — enforces /ontology-learning after tool errors (Stop)
- `agent_pyramid_gate.py` — requires L0 + role spec for Agent tool calls (PreToolUse)
- `skills/pyramid-ontology/SKILL-MAP.md` — full skill ontology dependency map
- `LICENSE` — MIT license
- `requirements.txt` — Python dependencies (python-pptx)
- `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`

### Fixed
- `ontology_learning_enforce_stop.py`: removed `user_count >= 3` false-positive trigger — normal multi-turn conversations no longer cause false blocks
- `ontology_learning_enforce_stop.py`: removed assistant text scanning — analysis text containing pattern strings no longer triggers self-referencing loop
- `ontology_violation_gate.py`: changed `sys.exit(1)` to `sys.exit(2)` — now correctly signals block to Claude Code hook system
- `pyramid_ontology_gate.py`: extended L0 regex to recognize `**L0**:` (markdown bold) and `*L0*:` (italic) in addition to plain `L0:`
- `tdd_enforce_stop.py`: documentation files (.md, .yaml, .json, etc.) are now exempt — no longer requires test verification after doc edits

### Changed
- `hooks.json`: removed `ontology_graph_gate` from registration (missing data file), removed `git_commit_push_check` (personal project artifact), added Agent matcher for `agent_pyramid_gate`
- `plugin.json`: updated description to "purpose-governed engineering layer for AI coding agents"
- `CLAUDE.md`: hook table updated to match hooks.json (13 registered hooks, SSOT)
- `README.md`: rewritten — added "What ODD Is/Is Not" section, corrected skill count (8), corrected hook count (13), added installation caveat

---

## [1.0.0] — 2026-05-27

Initial public release.

### Features
- 7 skills: pyramid-ontology, ontology-detach, ontology-rebuild, pyramid-label, pyramid-topology, ontology-review-gate, ontology-learning
- 10 hooks across PreToolUse, PostToolUse, Stop lifecycles
- violation_registry.json governance rule engine
- GitHub Pages documentation site
