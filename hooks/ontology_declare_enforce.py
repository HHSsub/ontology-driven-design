"""
Stop 훅 — 온톨로지 선언 강제

L0: 코드 수정 전 존재 목적 선언이 없는 행동은 금지
L1: 모든 Edit/Write 턴에 L0 선언이 있었는지 검증 + 열거형 개념 모음 수정 시 의존성 체인 검증
L2-A: transcript 파싱 → Edit/Write 포함 턴 탐지 → 선행 L0 선언 확인 → 없으면 차단
L2-B: 열거형 개념 모음(리스트·레지스트리) 수정 감지 → grep 증거 없으면 차단
L3: transcript JSONL 읽기 → 역순 탐색 → 패턴 검사 → exit 2

━━ 탈도구 원칙 ━━
이 훅의 L0/L1은 특정 도구·언어에 종속되지 않는다.
Edit/Write는 L3 구현 세부 — 이 훅은 어떤 수정 도구를 써도 동일하게 적용.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}

# L0-L2 선언 패턴 — 어시스턴트 텍스트에서 탐지
L0_DECL_RE = re.compile(r"\bL0\s*:", re.IGNORECASE)
L1_DECL_RE = re.compile(r"\bL1\s*:", re.IGNORECASE)

# Edit/Write 이전 몇 개 메시지(어시스턴트 턴)까지 탐색할지
LOOKBACK_MESSAGES = 8

# 열거형 개념 모음 탐지: 3개 이상 식별자형 문자열 포함 리스트/튜플 리터럴
# 어떤 도메인이든 — 코드 컬렉션, 문서 목록, 설정 키 집합 등 모두 포함
_REGISTRY_MOD_RE = re.compile(
    r'[\[\(](?:\s*["\'][a-zA-Z가-힣][a-zA-Z0-9가-힣_\-/\.]{1,39}["\'],?\s*){3,}[\]\)]'
)

# grep/검색 도구 사용 탐지
_GREP_CMD_RE = re.compile(r'\bgrep\b|\brg\b|\bfindstr\b', re.IGNORECASE)


def _has_edit_tool(content: list) -> bool:
    return any(
        isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name", "") in EDIT_TOOLS
        for b in content
    )


def _extract_text(content: list) -> str:
    parts = []
    for b in content:
        if isinstance(b, dict) and b.get("type") == "text":
            parts.append(b.get("text", ""))
    return "\n".join(parts)


def _has_l0_declaration(text: str) -> bool:
    return bool(L0_DECL_RE.search(text))


def _detect_registry_modification(messages: list) -> bool:
    """최근 Edit/Write 호출 중 열거형 개념 모음 수정 여부 감지."""
    for m in messages[-LOOKBACK_MESSAGES:]:
        if m["role"] != "assistant":
            continue
        for block in m.get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use" or block.get("name") not in EDIT_TOOLS:
                continue
            inp = block.get("input", {})
            text = inp.get("new_string", "") + inp.get("content", "")
            if _REGISTRY_MOD_RE.search(text):
                return True
    return False


def _detect_search_activity(messages: list) -> bool:
    """최근 메시지에서 grep/검색 실행 증거 탐지."""
    for m in messages[-LOOKBACK_MESSAGES:]:
        if m["role"] != "assistant":
            continue
        for block in m.get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            tool = block.get("name", "")
            if tool == "Grep":
                return True
            if tool == "Bash":
                cmd = block.get("input", {}).get("command", "")
                if _GREP_CMD_RE.search(cmd):
                    return True
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    transcript_path = payload.get("transcript_path")
    if not transcript_path or not Path(transcript_path).exists():
        return 0

    try:
        with open(transcript_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return 0

    # 모든 메시지 파싱
    messages = []
    for line in lines:
        try:
            entry = json.loads(line)
            msg = entry.get("message", {})
            role = msg.get("role", "")
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            messages.append({"role": role, "content": content})
        except Exception:
            continue

    if not messages:
        return 0

    # 최근 메시지 중 Edit/Write가 있는 어시스턴트 턴 탐지
    # Edit/Write가 없으면 검사 불필요
    has_any_edit = any(
        m["role"] == "assistant" and _has_edit_tool(m["content"])
        for m in messages[-LOOKBACK_MESSAGES:]
    )
    if not has_any_edit:
        return 0

    # 최근 LOOKBACK_MESSAGES 개 메시지에서 L0 선언 탐색
    recent = messages[-LOOKBACK_MESSAGES:]
    declaration_found = False
    for msg in recent:
        if msg["role"] == "assistant":
            text = _extract_text(msg["content"])
            if _has_l0_declaration(text):
                declaration_found = True
                break

    if declaration_found:
        # ━━ L2-B: 의존성 체인 검증 — 열거형 개념 모음 수정 시 grep 증거 요구 ━━
        # 열거형 개념 모음(리스트·레지스트리·enum·컬렉션)이 수정됐는데
        # 파생 표현 탐색(grep) 증거가 없으면 → SSOT 위반 가능성으로 차단
        if _detect_registry_modification(messages) and not _detect_search_activity(messages):
            err = (
                "\n══════════════════════════════════════════════\n"
                "❌ 의존성 체인 미검증 — 차단\n"
                "══════════════════════════════════════════════\n"
                "열거형 개념 모음(리스트·레지스트리·컬렉션)을 수정했는데\n"
                "파생 표현 탐색(grep/검색) 증거가 없습니다.\n\n"
                "열거형 개념 모음 수정 전 반드시:\n"
                "  1. Grep/Bash(grep)으로 동일 개념에 의존하는 모든 파생 표현 탐색\n"
                "  2. 파생 표현 전부 동시 갱신 (어느 하나도 누락 금지)\n\n"
                "원칙: 어떤 도메인·어떤 형식이든\n"
                "  SSOT 등록부 변경 → 의존 파생 N개 전부 갱신\n"
                "  탐색 없는 수정 = 의존성 체인 파괴 = 미래 불일치의 씨앗\n"
                "══════════════════════════════════════════════"
            )
            print(err, file=sys.stderr)
            return 2
        return 0

    err = (
        "\n══════════════════════════════════════════════\n"
        "❌ 온톨로지 선언 강제 훅 — 차단\n"
        "══════════════════════════════════════════════\n"
        "코드를 수정(Edit/Write)하기 전에 L0-L2 목적 선언이 없습니다.\n\n"
        "수정 전 반드시 다음 형식으로 선언하세요:\n\n"
        "  L0: [이 수정이 달성하는 비즈니스 최종 목적]\n"
        "  L1: [이 수정이 기여하는 시스템 목표]\n"
        "  L2: [지금 구현하는 기능 단위]\n\n"
        "선언 없이 코드 수정은 ontology-detach 위반입니다.\n"
        "상위 목적 없는 수정은 방향 없는 행동입니다.\n"
        "══════════════════════════════════════════════"
    )
    print(err, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
