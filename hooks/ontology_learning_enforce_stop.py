"""
Stop 훅 — 불순종(ontology-learning 미발동) 강제 차단

L0: 실수/불이행 후 ontology-learning을 즉시 발동하지 않는 것은 불순종이다.
L1: 구조적 실패 신호 탐지(tool error, 유저 재요청) → ontology-learning 발동 여부 확인 → 없으면 차단
L2: transcript에서 실패 구조 탐지 → 이후 Skill(ontology-learning) 미발동 → exit 2
    실패 구조 = tool_result is_error:true | exception/traceback/오류 텍스트 | 동일 요청 반복
L3: JSONL transcript 파싱, 구조 기반 탐지 (키워드 하드코딩 금지)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LOOKBACK = 40


def _extract_text_from_content(content: list) -> str:
    parts = []
    for block in content:
        if isinstance(block, dict):
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif block.get("type") == "tool_result":
                for sub in block.get("content", []):
                    if isinstance(sub, dict) and sub.get("type") == "text":
                        parts.append(sub.get("text", ""))
    return "\n".join(parts)


def _is_tool_error(content: list) -> bool:
    """tool_result에 is_error:true 또는 오류 텍스트 구조 탐지."""
    for block in content:
        if not isinstance(block, dict):
            continue
        # tool_result 오류
        if block.get("type") == "tool_result" and block.get("is_error"):
            return True
        # tool_result 내부 텍스트에 예외 구조 탐지 (traceback/Exception 등)
        if block.get("type") == "tool_result":
            for sub in block.get("content", []):
                if isinstance(sub, dict) and sub.get("type") == "text":
                    t = sub.get("text", "")
                    # 예외 구조: 언어 무관한 패턴 (Traceback, Error:, Exception, exit code 1)
                    if re.search(r"Traceback|Exception|Error:|exit.?code.?[1-9]|\berror\b", t, re.IGNORECASE):
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

    # 1. 구조적 실패 신호 탐지
    #    - tool_result is_error:true
    #    - user 메시지가 3회 이상 (교정 반복 구조)
    failure_idx = -1
    user_count = 0

    for i, msg in enumerate(recent):
        if msg["role"] == "user":
            user_count += 1
            # tool_result 오류 (user 역할로 전달됨)
            if _is_tool_error(msg["content"]):
                failure_idx = i
        elif msg["role"] == "assistant":
            # 어시스턴트 텍스트에서 예외/실패 구조 탐지
            text = _extract_text_from_content(msg["content"])
            if re.search(r"Traceback|Exception|Error:|exit.?code.?[1-9]|\berror\b", text, re.IGNORECASE):
                failure_idx = i

    # 유저 교정 반복 구조: 동일 세션에서 유저 메시지 3회 이상 + 어시스턴트 응답 2회 이상
    assistant_count = sum(1 for m in recent if m["role"] == "assistant")
    if user_count >= 3 and assistant_count >= 2 and failure_idx < 0:
        failure_idx = 0  # 반복 교정 구조 자체를 실패 신호로 취급

    if failure_idx < 0:
        return 0

    # 2. ontology-learning 발동 여부 탐색
    # - 하드 실패(tool error): recent의 failure_idx 이후 탐색
    # - 반복교정 구조(failure_idx==0 synthetic): 세션 전체 탐색
    if failure_idx == 0 and not any(
        msg["role"] == "user" and _is_tool_error(msg["content"])
        for msg in recent[:5]
    ):
        # 반복교정 구조 → 세션 전체에서 ontology-learning 탐색
        search_range = messages
    else:
        failure_global_idx = max(0, len(messages) - LOOKBACK) + failure_idx
        search_range = messages[failure_global_idx:]

    for msg in search_range:
        if msg["role"] == "assistant" and _has_skill_ontology_learning(msg["content"]):
            return 0  # 발동됨 → 패스

    err = (
        "\n══════════════════════════════════════════════\n"
        "❌ 불순종 차단 — ontology-learning 미발동\n"
        "══════════════════════════════════════════════\n"
        "실패/교정 구조가 감지됐으나 ontology-learning 스킬이 발동되지 않았습니다.\n\n"
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
