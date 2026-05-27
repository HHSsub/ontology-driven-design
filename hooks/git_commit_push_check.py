"""
git_commit_push_check.py — PostToolUse Bash

L0: git commit 직후 push 누락을 즉시 경고한다.
L1: Bash 명령에 'git commit'이 포함됐고 실행 후 unpushed 커밋이 있으면 stderr 경고.
    Stop 훅(git_push_enforce_stop.py)은 세션 종료 시만 발동 → 중간 갭을 이 훅이 커버.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _git(*args, cwd=None) -> str:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=10, cwd=cwd)
        return r.stdout.strip()
    except Exception:
        return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    cmd = payload.get("tool_input", {}).get("command", "")
    if "git commit" not in cmd:
        return 0

    # 현재 작업 디렉토리에서 unpushed 커밋 확인
    cwd = payload.get("tool_input", {}).get("cwd") or str(Path.cwd())
    root = _git("rev-parse", "--show-toplevel", cwd=cwd)
    if not root:
        return 0

    upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", cwd=root)
    if not upstream:
        return 0

    unpushed = _git("log", "--oneline", "@{u}..HEAD", cwd=root)
    if not unpushed:
        return 0

    print(
        "\n──────────────────────────────────────────────\n"
        "⚠️  git commit 완료 — Push 아직 안 됨\n"
        "──────────────────────────────────────────────\n"
        f"미푸시 커밋:\n"
        + "\n".join(f"  • {l}" for l in unpushed.splitlines()[:3])
        + "\n\n  즉시 실행: git push origin main\n"
        "──────────────────────────────────────────────",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
