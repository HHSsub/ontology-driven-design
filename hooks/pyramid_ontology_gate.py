"""
PreToolUse 훅 — Edit/Write 전 L0 선언 게이트

L0: superpowers 종속성 없이 — 목적 선언 없는 수정은 존재하지 않는다
L1: Edit/Write 직전에 세션 전체 transcript를 확인 → L0 선언 없으면 수정 자체를 차단
L2: Stop 훅(사후 차단)과 달리 수정이 일어나기 전에 막음 — 더 강력한 강제
L3: PreToolUse → stdin 파싱 → transcript 전체 탐색 → exit 2

━━ Stop 훅 vs PreToolUse 훅 ━━
ontology_declare_enforce.py (Stop):  수정 완료 후 차단 → 이미 파일이 바뀜
pyramid_ontology_gate.py (PreToolUse): 수정 전 차단 → 파일은 그대로
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}

# L0 선언 패턴
L0_RE = re.compile(r"\bL0\s*:", re.IGNORECASE)

# hooks 자체 파일 수정은 무한루프 방지를 위해 제외
EXEMPT_SUFFIXES = {".json"}  # hooks.json 등 설정 파일

# 훅/설정 파일 경로 — 스스로를 수정할 때는 체크 면제
_HOOK_DIR_MARKERS = {"hooks", ".claude"}


def _is_hook_file(file_path: str) -> bool:
    """훅 자체 또는 settings.json 수정은 면제 — 무한 재귀 방지."""
    p = Path(file_path)
    parts = {part.lower() for part in p.parts}
    if _HOOK_DIR_MARKERS & parts and p.suffix == ".py":
        return True  # .claude/hooks/*.py
    if p.name in {"settings.json", "hooks.json", "CLAUDE.md", "ONBOARDING.md"}:
        return True
    return False


def _load_messages(transcript_path: str) -> list[dict]:
    messages = []
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    msg = entry.get("message", {})
                    role = msg.get("role", "")
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        messages.append({"role": role, "content": content})
                except Exception:
                    continue
    except Exception:
        pass
    return messages


def _has_l0_in_session(messages: list) -> bool:
    """세션 전체에서 L0 선언이 한 번이라도 있었는지."""
    for msg in messages:
        if msg["role"] != "assistant":
            continue
        for block in msg.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                if L0_RE.search(block.get("text", "")):
                    return True
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_name = payload.get("tool_name", "") or payload.get("tool", "")
    if tool_name not in EDIT_TOOLS:
        return 0

    # 수정 대상 파일 경로
    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if file_path and _is_hook_file(file_path):
        return 0  # 훅/설정 파일 수정은 면제

    transcript_path = payload.get("transcript_path", "")
    if not transcript_path or not Path(transcript_path).exists():
        return 0  # transcript 없으면 통과 (초기 세션)

    messages = _load_messages(transcript_path)
    if not messages:
        return 0

    if _has_l0_in_session(messages):
        return 0  # L0 선언 있음 → 통과

    err = (
        "\n══════════════════════════════════════════════\n"
        "❌ L0 선언 없음 — Edit/Write 차단\n"
        "══════════════════════════════════════════════\n"
        "이번 세션에서 L0 선언을 한 적이 없습니다.\n"
        "수정 전 반드시 목적을 선언하세요:\n\n"
        "  L0: [이 수정이 달성하는 비즈니스 최종 목적]\n"
        "  L1: [이 수정이 기여하는 시스템 목표]\n\n"
        "선언 없이 코드 수정 = 방향 없는 행동\n"
        "superpowers 설치 여부와 무관하게 적용됩니다.\n"
        "══════════════════════════════════════════════"
    )
    print(err, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
