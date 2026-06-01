#!/usr/bin/env python3
# L0: 복잡한 작업(독립 도메인 3개 이상)에서 병렬 서브에이전트 사용 강제
# L1: TodoWrite에 task 3개 이상 pending 등록 시 Agent 디스패치 의무 경고
# L3: PreToolUse(TodoWrite) 이벤트에서 task 수 체크 → 3개 이상이면 Agent 사용 촉구
#
# 기준 출처: superpowers:dispatching-parallel-agents 스킬
#   "Multiple independent tasks? → Parallel dispatch"
#   판단 기준: 독립 도메인 3개 이상
#   ≈ TodoWrite pending task 3개 이상 = 독립 도메인 복수 가능성 높음
import json
import os
import sys
import tempfile

SESSION_DISPATCH_FILE = os.path.join(tempfile.gettempdir(), "claude_agent_dispatched.json")

def _session_id() -> str:
    return os.environ.get("CLAUDE_SESSION_ID", "")

def _was_agent_dispatched() -> bool:
    try:
        with open(SESSION_DISPATCH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("session_id") == _session_id() and data.get("dispatched", False)
    except Exception:
        return False

def _mark_agent_dispatched() -> None:
    try:
        with open(SESSION_DISPATCH_FILE, "w", encoding="utf-8") as f:
            json.dump({"session_id": _session_id(), "dispatched": True}, f)
    except Exception:
        pass

def main():
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool_name = event.get("tool_name", "")

    # Agent 호출 감지 → dispatched 기록
    if tool_name == "Agent":
        _mark_agent_dispatched()
        sys.exit(0)

    # TodoWrite 이벤트만 처리
    if tool_name != "TodoWrite":
        sys.exit(0)

    # Agent 이미 디스패치됨 → 경고 불필요
    if _was_agent_dispatched():
        sys.exit(0)

    tool_input = event.get("tool_input", {}) or {}
    todos = tool_input.get("todos", []) or []

    # pending 상태 task 수 계산
    pending_count = sum(
        1 for t in todos
        if isinstance(t, dict) and t.get("status") in ("pending", "in_progress")
    )

    if pending_count >= 3:
        print(
            f"\n"
            f"══════════════════════════════════════════════════════\n"
            f"⚠️  독립 도메인 {pending_count}개 감지 — 병렬 서브에이전트 필수\n"
            f"══════════════════════════════════════════════════════\n"
            f"TodoWrite에 {pending_count}개 tasks가 등록됐습니다.\n"
            f"이 경우 Agent()를 병렬 호출로 처리해야 합니다.\n\n"
            f"기준: superpowers:dispatching-parallel-agents\n"
            f"  '독립 도메인 3개 이상 → 병렬 에이전트 디스패치'\n\n"
            f"각 독립 task를 Agent() 호출로 위임한 후\n"
            f"이 세션을 조율(coordination)에만 사용하세요.\n"
            f"══════════════════════════════════════════════════════",
            file=sys.stderr,
        )
        # exit(0) = 경고만, 차단 안 함 (강제 차단은 과도함)
        sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
