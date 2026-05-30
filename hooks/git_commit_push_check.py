"""
git_commit_push_check.py — PostToolUse Bash

L0: git push 완료 시 Vercel 프로덕션 자동 배포
L1: Bash 명령에 'git push'가 포함되고 dynamic_portfolio repo이면
    → vercel deploy --prod 자동 실행
    unpushed 커밋 경고도 병행
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PORTFOLIO_MARKER = "dynamic_portfolio"
VERCEL_CWD = None  # 아래에서 동적으로 탐색


def _git(*args, cwd=None) -> str:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=10, cwd=cwd)
        return r.stdout.strip()
    except Exception:
        return ""


def _find_portfolio_app(root: str) -> str | None:
    """portfolio_app 디렉토리 경로 반환"""
    candidate = Path(root) / "portfolio_app"
    if candidate.exists():
        return str(candidate)
    return None


def _run_vercel_deploy(cwd: str) -> None:
    print(
        "\n──────────────────────────────────────────────\n"
        "🚀 Vercel 프로덕션 자동 배포 시작\n"
        "──────────────────────────────────────────────",
        file=sys.stderr,
    )
    try:
        result = subprocess.run(
            ["vercel", "deploy", "--prod"],
            cwd=cwd,
            capture_output=False,
            timeout=180,
        )
        if result.returncode == 0:
            print("✅ Vercel 배포 완료", file=sys.stderr)
        else:
            print(f"❌ Vercel 배포 실패 (exit {result.returncode})", file=sys.stderr)
    except Exception as e:
        print(f"❌ Vercel 배포 오류: {e}", file=sys.stderr)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    cmd = payload.get("tool_input", {}).get("command", "")
    if "git push" not in cmd:
        return 0

    cwd = payload.get("tool_input", {}).get("cwd") or str(Path.cwd())
    root = _git("rev-parse", "--show-toplevel", cwd=cwd)
    if not root:
        return 0

    # dynamic_portfolio 프로젝트인지 확인
    if PORTFOLIO_MARKER not in root.replace("\\", "/"):
        return 0

    # unpushed 커밋 경고 (참고용)
    upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", cwd=root)
    if upstream:
        unpushed = _git("log", "--oneline", "@{u}..HEAD", cwd=root)
        if unpushed:
            print(
                "\n──────────────────────────────────────────────\n"
                "⚠️  미푸시 커밋 있음\n"
                "──────────────────────────────────────────────",
                file=sys.stderr,
            )
            return 2

    # Vercel 자동 배포
    portfolio_app = _find_portfolio_app(root)
    if portfolio_app:
        _run_vercel_deploy(portfolio_app)

    return 0


if __name__ == "__main__":
    sys.exit(main())
