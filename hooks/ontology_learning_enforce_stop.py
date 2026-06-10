"""
Stop 훅 — 불순종(ontology-learning 미발동) 강제 차단 + L1 에스컬레이션 차단 + dead rule 경고

L0: ODD는 쓸수록 진화하는 시스템이다. 실수 후 학습 없음 = 진화 중단 = 차단.
L1: 비터미널 도구 실행 실패 탐지 + L1 에스컬레이션 플래그 탐지 → ontology-learning 강제
L2: Bash/PowerShell/Read/Glob/Grep is_error = 환경 오류 → 즉시 재시도, learning 불필요
    Write/Edit/Agent is_error = 설계 실수 가능 → learning 필수
L3: tool_use_id → tool_name 맵 구축, TERMINAL_TOOLS 오류 제외, dead rule 경고 포함
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

LOOKBACK = 40
DEAD_RULE_DAYS = 14  # 2주 이상 미발동 규칙 → dead rule 경고
ESCALATION_FLAG_TTL_HOURS = 4  # escalation 플래그 유효시간 (세션 경계 추정)

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
STATS_PATH = os.path.join(HOOKS_DIR, "violation_stats.json")
ESCALATION_FLAG_PATH = os.path.join(HOOKS_DIR, "escalation_pending.json")

# 환경 오류는 ontology-learning 불필요 — 즉시 재시도로 해결
# Read/Glob/Grep: 파일 없음/패턴 불일치는 설계 실수 아님
TERMINAL_TOOLS = {"Bash", "PowerShell", "Read", "Glob", "Grep", "WebSearch", "WebFetch"}

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
            tid = block.get("tool_use_id", "")
            tool_name = tool_name_map.get(tid, "")
            if tool_name in TERMINAL_TOOLS:
                continue  # 환경 오류 = 재시도로 해결, ontology-learning 불필요
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


def _check_escalation_pending(messages: list) -> bool:
    """escalation_pending.json 플래그 탐지: 유효 시간 내 + ontology-learning 미실행 → True."""
    if not os.path.exists(ESCALATION_FLAG_PATH):
        return False
    try:
        with open(ESCALATION_FLAG_PATH, encoding="utf-8") as f:
            flag = json.load(f)
        written_at_str = flag.get("written_at", "")
        if not written_at_str:
            return False
        written_at = datetime.fromisoformat(written_at_str)
        if written_at.tzinfo is None:
            written_at = written_at.replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - written_at).total_seconds() / 3600
        if age_hours > ESCALATION_FLAG_TTL_HOURS:
            try:
                os.unlink(ESCALATION_FLAG_PATH)
            except Exception:
                pass
            return False
        for msg in messages:
            if msg["role"] == "assistant" and _has_skill_ontology_learning(msg["content"]):
                try:
                    os.unlink(ESCALATION_FLAG_PATH)
                except Exception:
                    pass
                return False
        return True  # 유효 플래그 + ontology-learning 미실행 → 차단
    except Exception:
        return False


def _get_dead_rules() -> list:
    """violation_stats.json에서 14일 이상 미발동(trigger_count=0) 규칙 목록 반환."""
    if not os.path.exists(STATS_PATH):
        return []
    try:
        with open(STATS_PATH, encoding="utf-8") as f:
            stats = json.load(f)
        today = datetime.now(timezone.utc).date()
        dead = []
        for rid, entry in stats.items():
            if entry.get("trigger_count", 0) == 0:
                added_str = entry.get("added_date", "")
                if added_str:
                    try:
                        added_date = datetime.fromisoformat(added_str).date()
                        age = (today - added_date).days
                        if age >= DEAD_RULE_DAYS:
                            dead.append((rid, age))
                    except Exception:
                        pass
        return sorted(dead, key=lambda x: -x[1])
    except Exception:
        return []


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

    tool_name_map = _build_tool_name_map(recent)

    # L1 에스컬레이션 차단 확인 (우선 처리)
    if _check_escalation_pending(messages):
        err = (
            "\n══════════════════════════════════════════════\n"
            "❌ L1 에스컬레이션 차단 — ontology-learning 미실행\n"
            "══════════════════════════════════════════════\n"
            "이 세션에서 동일 규칙이 3회 이상 반복 발동됐습니다.\n"
            "L2 패칭이 아닌 L1 세계관 재검토가 필요합니다.\n\n"
            "의무:\n"
            "  1. /ontology-driven-design:ontology-learning 즉시 실행\n"
            "  2. 반복 발동 규칙의 L0 원인 분석 (L3→L0 역추적)\n"
            "  3. violation_registry.json L1 재설계 또는 메모리 업데이트\n\n"
            "ontology-learning 없이는 이 세션 종료 불가.\n"
            "══════════════════════════════════════════════"
        )
        print(err, file=sys.stderr)
        return 2

    # 설계 실수 신호: 비터미널 도구 is_error:true 한정
    failure_idx = -1
    for i, msg in enumerate(recent):
        if msg["role"] == "user" and _is_design_error(msg["content"], tool_name_map):
            failure_idx = i

    if failure_idx >= 0:
        failure_global_idx = max(0, len(messages) - LOOKBACK) + failure_idx
        search_range = messages[failure_global_idx:]

        learning_found = any(
            msg["role"] == "assistant" and _has_skill_ontology_learning(msg["content"])
            for msg in search_range
        )

        if not learning_found:
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

    # Dead rule 경고 (차단 아닌 WARNING — 진화 신호)
    dead_rules = _get_dead_rules()
    if dead_rules:
        lines_out = [
            "\n⚠️  Dead Rule 경고 (차단 아님 — 진화 신호)",
            f"다음 규칙이 {DEAD_RULE_DAYS}일 이상 단 한 번도 발동되지 않았습니다:",
        ]
        for rid, age in dead_rules[:5]:
            lines_out.append(f"  [{rid}]: {age}일 미발동")
        lines_out += [
            "",
            "이 규칙들은 이미 내재화됐거나, 애초에 잘못된 추상 수준의 규칙입니다.",
            "→ violation_registry.json에서 삭제하거나 L0 수준으로 재추상화 검토.",
            "(dead rule 축소 = 시스템 진화의 증거)",
        ]
        print("\n".join(lines_out), file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
