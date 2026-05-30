"""
Stop 훅 — 불순종(ontology-learning 미발동) 강제 차단

L0: 실수/불이행 후 ontology-learning을 즉시 발동하지 않는 것은 불순종이다.
L1: 실제 도구 실행 실패(is_error:true) 탐지 → ontology-learning 발동 여부 확인 → 없으면 차단
L2: transcript에서 tool_result is_error:true 탐지 → 이후 Skill(ontology-learning) 미발동 → exit 2
    실패 구조 = tool_result is_error:true 한정 (user_count 휴리스틱 제거 — 일반 대화도 차단하던 오탐 원인)
L3: JSONL transcript 파싱, is_error 필드 기반 탐지
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LOOKBACK = 40


def _is_tool_error(content: list) -> bool:
    """tool_result에 is_error:true 탐지."""
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_result" and block.get("is_error"):
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

    # 실패 신호: tool_result is_error:true 한정
    # user_count >= 3 휴리스틱 제거 — 일반 대화(질문 3회 이상)도 차단하는 false positive 원인
    failure_idx = -1
    for i, msg in enumerate(recent):
        if msg["role"] == "user" and _is_tool_error(msg["content"]):
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
