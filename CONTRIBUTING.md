# Contributing to ODD

Thank you for your interest in contributing to Ontology Driven Design.

## Before You Start

ODD enforces its own philosophy on itself. Before submitting any contribution:

1. **Understand L0**: Every change must have a stated purpose. "Why does this change need to exist?"
2. **Read [CLAUDE.md](CLAUDE.md)**: The plugin's own governance rules apply to its own development.
3. **Check the [audit](docs/audit/)**: The current improvement roadmap is documented — contributions aligned with it are prioritized.

## How to Contribute

### Bug Reports

Open a GitHub issue with:
- Which hook or skill is affected
- What you expected vs. what happened
- Claude Code version and OS
- Transcript excerpt if possible (remove personal info)

### Pull Requests

1. Fork the repository
2. Create a branch: `fix/ISSUE-NNN-short-description` or `feat/description`
3. Make your changes
4. Verify all hooks with `python -m py_compile hooks/*.py`
5. Run `node verify.js` if available
6. Open a PR with a clear description of the L0 purpose this change serves

### Hook Changes

- All hook changes must include: what trigger, what it blocks, what it passes
- Exit code convention: `exit(2)` = block, `exit(0)` = pass
- No hardcoded absolute paths
- OS-agnostic (Windows + macOS + Linux)

### Skill Changes

- Follow the existing SKILL.md format with L0 declaration at top
- No hardcoded usernames, paths, or project names
- Korean + English phrasing should be consistent

## Code of Conduct

This project follows a simple rule: purpose before ego. Contributions that serve the L0 of the project (making AI coding agents more purposeful) are welcome regardless of the contributor's background.
