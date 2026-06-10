"""
Stop 훅 — 불순종(ontology-learning 미발동) 강제 차단

L0: 설계/판단 실수 후 ontology-learning을 즉시 발동하지 않는 것은 불순종이다.
L1: 비터미널 도구 실행 실패(is_error:true) 탐지 → ontology-learning 발동 여부 확인 → 없으면 차단
L2: Bash/PowerShell is_error = 터미널 오류 → 즉시 재시도 대상, ontology-learning 불필요
    Write/Edit/Agent is_error = 설계 실수 가능 → ontology-learning 필수
L3: tool_use_id → tool_name 맵 구축, TERMINAL_TOOLS 오류 제외
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LOOKBACK = 40

# 터미널 도구 오류는 ontology-learning 불필요 — 즉시 재시도로 해결
TERMINAL_TOOLS = {"Bash", "PowerShell"}

_HOOK_BLOCK_SIGNATURES = (
    "══════════════",   # ODD hook common separator — hook block = normal operation
    "hook error",       # Claude Code hook error message — hook fired = ODD working
    "PreToolUse:",      # Claude Code hook block prefix
    "PostToolUse:",     # Claude Code hook block prefix
)


def _is_hook_block_content(block: dict) -> bool:
    content = block.get("content", "")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    else:
        text = ""
    return any(sig in text for sig in _HOOK_BLOCK_SIGNATURES)


def _build_tool_name_map(messages: list) -> dict:
    """tool_use_id → tool_name 맵 구축 (assistant 메시지 기반)."""
    result = {}
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        for block in msg.get("content", []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                tid = block.get("id", "")
                name = block.get("name", "")
                if tid and name:
                    result[tid] = name
    return result


def _is_design_error(content: list, tool_name_map: dict) -> bool:
    """tool_result에 is_error:true 탐지 — ODD 훅 차단 + 터미널 도구 오류 제외."""
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_result" and block.get("is_error"):
            if _is_hook_block_content(block):
                continue  # ODD 훅 차단 = 정상 작동, 실수 아님
            # 터미널 도구 오류 제외 (Bash, PowerShell) — 명령어 수정으로 해결, ontology-learning 불필요
            tid = block.get("tool_use_id", "")
            tool_name = tool_name_map.get(tid, "")
            if tool_name in TERMINAL_TOOLS:
                continue
            return True
    return False


def _has_skill_ontology_learning(content: list) -> bool:
    """Skill(ontology-learning) 도구 호출 탐지."""
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_use" and block.get("name") == "Skill":
            skill = block.get("input", {}).get("skill", "")
            if "ontology" in skill.lower() and "learn" in skill.lower():
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

    messages = []
    for line in lines:
        try:
            entry = json.loads(line)
            msg = entry.get("message", {})
            role = msg.get("role", "")
            raw_content = msg.get("content", [])
            if isinstance(raw_content, str):
                raw_content = [{"type": "text", "text": raw_content}]
            if not isinstance(raw_content, list):
                continue
            messages.append({"role": role, "content": raw_content})
        except Exception:
            continue

    if len(messages) < 3:
        return 0

    recent = messages[-LOOKBACK:]

    # tool_use_id → tool_name 맵 구축 (최근 40개 메시지 기반)
    tool_name_map = _build_tool_name_map(recent)

    # 설계 실수 신호: 비터미널 도구 is_error:true 한정
    # Bash/PowerShell 오류 제외 — 터미널 오류는 즉시 재시도, ontology-learning 불필요
    failure_idx = -1
    for i, msg in enumerate(recent):
        if msg["role"] == "user" and _is_design_error(msg["content"], tool_name_map):
            failure_idx = i

    if failure_idx < 0:
        return 0

    # failure_idx 이후에 ontology-learning이 발동됐는지 탐색
    failure_global_idx = max(0, len(messages) - LOOKBACK) + failure_idx
    search_range = messages[failure_global_idx:]

    for msg in search_range:
        if msg["role"] == "assistant" and _has_skill_ontology_learning(msg["content"]):
            return 0  # 발동됨 → 패스

    err = (
        "\n══════════════════════════════════════════════\n"
        "❌ 불순종 차단 — ontology-learning 미발동\n"
        "══════════════════════════════════════════════\n"
        "도구 실행 실패(is_error) 후 ontology-learning 스킬이 발동되지 않았습니다.\n\n"
        "실패 감지 즉시 의무:\n"
        "  1. Skill(ontology-learning) 즉시 발동\n"
        "  2. Phase 1-6 전체 실행 (L3→L0 역추적)\n"
        "  3. 메모리 저장 + violation_registry 업데이트\n\n"
        "ontology-learning 없는 사과/수정/재시도 = 불순종 = 차단.\n"
        "══════════════════════════════════════════════"
    )
    print(err, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
