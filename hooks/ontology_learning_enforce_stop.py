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


def _has_structure_change_after(timestamp_epoch: float) -> bool:
    """escalation 이후 violation_registry.json이 실제로 수정됐는지 mtime으로 검증.
    스킬 호출만으로는 강제 고리가 닫히지 않음 — 실제 구조 변화(파일 mtime)를 요구한다.
    """
    try:
        registry_path = os.path.join(HOOKS_DIR, "violation_registry.json")
        if os.path.exists(registry_path) and os.path.getmtime(registry_path) > timestamp_epoch:
            return True
        # ODD repo 경로도 확인 (플러그인으로 설치된 경우)
        odd_registry = os.path.join(
            os.path.dirname(HOOKS_DIR), "Downloads", "ontology-driven-design", "hooks", "violation_registry.json"
        )
        if os.path.exists(odd_registry) and os.path.getmtime(odd_registry) > timestamp_epoch:
            return True
        return False
    except Exception:
        return False


def _check_escalation_pending(messages: list) -> bool:
    """escalation_pending.json 플래그 탐지: 유효 시간 내 + 구조 변화 없음 → True.

    강제 고리 종착점은 "스킬 호출"이 아니라 "violation_registry.json mtime 갱신"이다.
    빈 스킬 호출로 탈출하는 구멍을 닫는다.
    """
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
        # 구조 변화 검증: registry mtime이 escalation 이후인가?
        ts_epoch = written_at.timestamp()
        if _has_structure_change_after(ts_epoch):
            try:
                os.unlink(ESCALATION_FLAG_PATH)
            except Exception:
                pass
            return False
        # registry 변화 없음 — 스킬 호출 여부도 fallback으로 확인
        for msg in messages:
            if msg["role"] == "assistant" and _has_skill_ontology_learning(msg["content"]):
                # 스킬 호출됐지만 registry 미변경 → 빈 호출 의심이나 일단 통과
                # 단, 메모리/원칙 업데이트만으로도 진화로 인정 (registry 외 경로 허용)
                try:
                    os.unlink(ESCALATION_FLAG_PATH)
                except Exception:
                    pass
                return False
        return True  # 유효 플래그 + 구조 변화 없음 + 스킬 미호출 → 차단
    except Exception:
        return False


INTERNALIZED_DAYS = 30  # 마지막 발동 후 이 기간 지나면 내재화 후보

def _get_evolution_signals() -> tuple:
    """violation_stats.json에서 진화 신호 2종류 탐지.

    dead: trigger_count==0 AND added_date > 14일 → 한 번도 발동 안 됨 (과잉 명시)
    internalized: trigger_count > 0 AND last_triggered > 30일 → 발동되다 멈춤 (내재화)
    두 경로를 구분해야 한다: dead는 "잘못 만든 rule", internalized는 "임무 완수한 rule"
    """
    if not os.path.exists(STATS_PATH):
        return [], []
    try:
        with open(STATS_PATH, encoding="utf-8") as f:
            stats = json.load(f)
        today = datetime.now(timezone.utc).date()
        dead = []
        internalized = []
        for rid, entry in stats.items():
            trigger_count = entry.get("trigger_count", 0)
            if trigger_count == 0:
                added_str = entry.get("added_date", "")
                if added_str:
                    try:
                        age = (today - datetime.fromisoformat(added_str).date()).days
                        if age >= DEAD_RULE_DAYS:
                            dead.append((rid, age))
                    except Exception:
                        pass
            else:
                last_str = entry.get("last_triggered", "")
                if last_str:
                    try:
                        last_date = datetime.fromisoformat(last_str)
                        if last_date.tzinfo is None:
                            last_date = last_date.replace(tzinfo=timezone.utc)
                        dormant_days = (datetime.now(timezone.utc) - last_date).days
                        if dormant_days >= INTERNALIZED_DAYS:
                            internalized.append((rid, dormant_days, trigger_count))
                    except Exception:
                        pass
        return sorted(dead, key=lambda x: -x[1]), sorted(internalized, key=lambda x: -x[1])
    except Exception:
        return [], []


def _get_unpromoted_global_rules() -> list:
    """scope-channel match 기계 신호: 같은 규칙이 2개+ 프로젝트에서 발동 = 전역 범위 원칙.

    전역 채널(전역 CLAUDE.md/principles.md) 승격 없이는 다른 프로젝트 세션이
    그 원칙을 로드하지 못해 구조적 재발이 결정적이다.
    승격 완료 표시 = stats entry에 "globalized" 키 (값: "YYYY-MM-DD 채널설명").
    """
    if not os.path.exists(STATS_PATH):
        return []
    try:
        with open(STATS_PATH, encoding="utf-8") as f:
            stats = json.load(f)
        pending = []
        for rid, entry in stats.items():
            projects = entry.get("projects", {})
            if len(projects) >= 2 and "globalized" not in entry:
                pending.append((rid, sorted(projects.keys())))
        return pending
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

    # tool_use_id → tool_name 맵 구축 (최근 40개 메시지 기반)
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

    # scope-channel 강제: 다중 프로젝트 발동 규칙이 전역 채널 미승격이면 종료 차단
    unpromoted = _get_unpromoted_global_rules()
    if unpromoted:
        lines_out = [
            "",
            "══════════════════════════════════════════════",
            "❌ scope-channel 차단 — 전역 범위 원칙이 프로젝트 silo에 갇힘",
            "══════════════════════════════════════════════",
            "다음 규칙이 2개 이상 프로젝트에서 발동됨 = 전역 범위 원칙인데 전역 채널에 없음:",
        ]
        for rid, projs in unpromoted:
            lines_out.append(f"  [{rid}] ← 발동 프로젝트: {', '.join(projs)}")
        lines_out += [
            "",
            "의무 (순서대로):",
            "  1. 해당 원칙을 전역 채널로 승격: ~/.claude/CLAUDE.md 기존 섹션 심화",
            "     또는 ~/.claude/hooks/principles.md (SessionStart로 전 세션 주입됨)",
            "  2. 승격 후 violation_stats.json 해당 entry에 표시:",
            '     "globalized": "YYYY-MM-DD <채널>"',
            "  3. 표시 전까지 세션 종료 불가.",
            "══════════════════════════════════════════════",
        ]
        print("\n".join(lines_out), file=sys.stderr)
        return 2

    # 설계 실수 신호: 비터미널 도구 is_error:true 한정
    failure_idx = -1
    for i, msg in enumerate(recent):
        if msg["role"] == "user" and _is_design_error(msg["content"], tool_name_map):
            failure_idx = i

    if failure_idx >= 0:
        # failure_idx 이후에 ontology-learning이 발동됐는지 탐색
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

    # 진화 신호 경고 (차단 아님 — 시스템 성숙도 신호)
    dead_rules, internalized_rules = _get_evolution_signals()
    if dead_rules:
        lines_out = [
            "\n⚠️  Dead Rule 경고 (차단 아님 — 진화 신호)",
            f"다음 규칙이 {DEAD_RULE_DAYS}일 이상 단 한 번도 발동되지 않았습니다 (과잉 명시 의심):",
        ]
        for rid, age in dead_rules[:5]:
            lines_out.append(f"  [{rid}]: {age}일 미발동")
        lines_out += [
            "",
            "→ 이 규칙들은 애초에 잘못된 추상 수준(L3 과잉 명시)으로 설계됐을 가능성 높음.",
            "→ violation_registry.json에서 삭제하거나 L0 수준으로 재추상화 검토.",
        ]
        print("\n".join(lines_out), file=sys.stderr)
    if internalized_rules:
        lines_out = [
            "\n✅  내재화 신호 (차단 아님 — 시스템 성숙 증거)",
            f"다음 규칙이 {INTERNALIZED_DAYS}일 이상 발동 없음 (이전엔 발동됐음):",
        ]
        for rid, dormant, count in internalized_rules[:5]:
            lines_out.append(f"  [{rid}]: {dormant}일 침묵 (총 {count}회 발동)")
        lines_out += [
            "",
            "→ 이 패턴이 행동에 내재화된 신호. 규칙 삭제로 시스템 자기감소 실현 가능.",
        ]
        print("\n".join(lines_out), file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
