"""
git_push_enforce_stop.py

L0: 수정된 코드는 반드시 git commit + push로 보존되어야 한다.
L1: transcript에서 Edit/Write 흔적 감지 → git uncommitted/unpushed 확인
L2: 미커밋 or 미푸시 상태면 차단
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}


def _git(*args, cwd=None) -> str:
    try:
        r = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, timeout=10, cwd=cwd
        )
        return r.stdout.strip()
    except Exception:
        return ""


def check_git(cwd: str | None = None) -> str | None:
    """미커밋 → 'uncommitted', 미푸시 → 'unpushed', 정상 → None"""
    # git repo인지 확인
    root = _git("rev-parse", "--show-toplevel", cwd=cwd)
    if not root:
        return None  # git 아님 → 무시

    # 미커밋 변경사항
    dirty = _git("status", "--porcelain", cwd=cwd)
    if dirty:
        return "uncommitted"

    # 미푸시 커밋 (upstream 없으면 스킵)
    upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", cwd=cwd)
    if upstream:
        unpushed = _git("log", "@{u}..HEAD", "--oneline", cwd=cwd)
        if unpushed:
            return "unpushed"

    return None


def _has_edit(transcript_path: str) -> bool:
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                content = entry.get("message", {}).get("content", [])
                if not isinstance(content, list):
                    continue
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        if block.get("name", "") in EDIT_TOOLS:
                            return True
    except Exception:
        pass
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    transcript_path = payload.get("transcript_path", "")
    if not transcript_path or not Path(transcript_path).exists():
        return 0

    if not _has_edit(transcript_path):
        return 0

    status = check_git()
    if status == "uncommitted":
        print(
            "\n──────────────────────────────────────────────\n"
            "❌ Git 커밋 안 됨 — 차단\n"
            "──────────────────────────────────────────────\n"
            "코드 수정 후 git commit을 하지 않았습니다.\n\n"
            "  git add <파일>\n"
            "  git commit -m \"fix: ...\"\n"
            "  git push\n"
            "──────────────────────────────────────────────",
            file=sys.stderr,
        )
        return 2

    if status == "unpushed":
        print(
            "\n──────────────────────────────────────────────\n"
            "❌ Git Push 안 됨 — 차단\n"
            "──────────────────────────────────────────────\n"
            "커밋은 됐는데 git push를 하지 않았습니다.\n\n"
            "  git push\n"
            "──────────────────────────────────────────────",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
