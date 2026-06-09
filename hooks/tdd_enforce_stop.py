"""
~/.claude/hooks/tdd_enforce_stop.py

L0: 코드 변경의 "성공"은 파일 작성이 아니라 동작 검증이다.
L1: transcript에서 Edit/Write 위치와 검증 명령 위치를 시간순으로 추적.
L2: 마지막 Edit/Write 이후 검증 흔적이 없으면 차단.
L3: Bash + PowerShell 양쪽 도구, 경로 포함 명령 모두 인식.

검증으로 인정하는 패턴 (Bash 또는 PowerShell 도구):
- pytest / unittest
- python / python3 / python.exe -m py_compile|pytest|unittest
- python / python3 / python.exe <file>.py
- 전체 경로 python (예: C:/conda/python.exe -m py_compile ...)
- npm/pnpm/yarn test
- npm/pnpm/yarn run *build* (docs:build, build, build:prod 등 — 빌드 성공 = 구조 검증)
- npx/pnpm tsc / tsc --noEmit
- vitepress build / next build / nuxt build 등 프레임워크 빌드
- tsc.cmd --noEmit (Windows 전체경로)
- curl http://localhost 또는 127.0.0.1
- node <file>.js
- go test / cargo test / mvn test / gradle test / dotnet test / rspec / jest
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# L3: 검증 명령 패턴 — 경로 포함, 다양한 언어/런타임 지원
VERIFICATION_PATTERNS = [
    # Python — 경로 포함, py_compile / pytest / unittest / 직접실행
    r"python[\d.]*(?:\.exe)?\s+-m\s+py_compile",
    r"python[\d.]*(?:\.exe)?\s+-m\s+pytest",
    r"python[\d.]*(?:\.exe)?\s+-m\s+unittest",
    r"python[\d.]*(?:\.exe)?\s+-c\s+",
    r"python[\d.]*(?:\.exe)?\s+\S+\.py\b",
    r"[\"']?[A-Za-z]:[/\\][^\"'\s]+python[\d.]*(?:\.exe)?[\"']?\s+-m\s+py_compile",
    r"[\"']?[A-Za-z]:[/\\][^\"'\s]+python[\d.]*(?:\.exe)?[\"']?\s+-m\s+pytest",
    r"[\"']?[A-Za-z]:[/\\][^\"'\s]+python[\d.]*(?:\.exe)?[\"']?\s+\S+\.py\b",
    r"\bpytest\b",
    r"\bpy\.test\b",
    r"\bunittest\b",
    # JS/TS — npm/pnpm/yarn/npx + tsc.cmd 전체경로
    r"npm\s+(run\s+)?test\b",
    r"pnpm\s+test\b",
    r"yarn\s+test\b",
    r"npm\s+run\s+\S*build\S*",
    r"pnpm\s+run\s+\S*build\S*",
    r"yarn\s+\S*build\S*",
    r"npx\s+(?:jest|vitest|tsc|vitepress|next|nuxt)\b",
    r"pnpm\s+(?:jest|vitest|tsc)\b",
    r"\bvitepress\s+build\b",
    r"\bnext\s+build\b",
    r"\bnuxt\s+build\b",
    r"\btsc\b.*--noEmit",
    r"tsc\.cmd\b",
    r"\bnode\s+\S+\.js\b",
    # Web smoke test — localhost 또는 배포 URL (https://) 모두 인정
    r"curl\s+.*(?:localhost|127\.0\.0\.1|https?://)",
    # 기타 언어
    r"\bgo\s+test\b",
    r"\bcargo\s+test\b",
    r"\bmvn\s+test\b",
    r"\bgradle\s+test\b",
    r"gradlew(?:\.bat)?\s+\S*(?:test|assemble|build)\S*",
    r"\bdotnet\s+test\b",
    r"\brspec\b",
    r"\bjest\b",
]
VERIFY_RE = re.compile("|".join(VERIFICATION_PATTERNS), re.IGNORECASE)

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}

# 문서/설정 파일은 TDD 검증 대상 아님 — 테스트 명령으로 "맞게 썼는지" 검증 불가
DOC_EXTENSIONS = {".md", ".txt", ".rst", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ""}


def _extract_cmd(tool_name: str, inp: dict) -> str:
    if tool_name == "Bash":
        return inp.get("command", "")
    if tool_name == "PowerShell":
        return inp.get("command", "")
    return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    transcript_path = payload.get("transcript_path")
    if not transcript_path or not Path(transcript_path).exists():
        return 0

    last_edit_idx = -1
    last_verify_idx = -1

    try:
        with open(transcript_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return 0

    for idx, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except Exception:
            continue

        msg = entry.get("message", {})
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            name = block.get("name", "")
            if name in EDIT_TOOLS:
                file_path = block.get("input", {}).get("file_path", "")
                if Path(file_path).suffix.lower() not in DOC_EXTENSIONS:
                    last_edit_idx = idx
            elif name in SHELL_TOOLS:
                cmd = _extract_cmd(name, block.get("input", {}))
                if cmd and VERIFY_RE.search(cmd):
                    last_verify_idx = idx

    if last_edit_idx < 0:
        return 0

    if last_verify_idx > last_edit_idx:
        return 0

    err = (
        "\n──────────────────────────────────────────────\n"
        "❌ TDD 강제 hook 차단\n"
        "──────────────────────────────────────────────\n"
        "Edit/Write 후 검증 명령 실행 흔적이 없습니다.\n\n"
        "수정한 코드를 실제로 동작 검증한 후 응답을 종료하세요:\n"
        "  • Python:  python -m py_compile <file>  OR  pytest\n"
        "  • JS/TS:   npx tsc --noEmit  OR  npm test\n"
        "  • Web:     curl http://localhost:<port>/health\n"
        "  • 기타:    go test / cargo test / dotnet test 등\n\n"
        "Bash 또는 PowerShell 도구로 직접 실행해야 합니다.\n"
        "──────────────────────────────────────────────"
    )
    print(err, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
