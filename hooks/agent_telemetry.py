# L0: 에이전트 위계 작업이 측정 없이 수행되는 감시 사각 제거 — 호출·완료·미완(데드엔드)이 전수 기록되어야 진화 신호가 생긴다
# L1: Stop 훅으로 트랜스크립트를 JSONL 파싱하여 Agent/Task/Skill 디스패치를 집계하고 session_id 키로 merge-write
# L2: 관측 전용 — 차단 없음, 항상 exit 0 (관측이 작업을 막으면 안 됨)
# L3: C:\Users\User\.claude\hooks\agent_telemetry.json 에 atomic write (tempfile + os.replace)

import sys
import json
import os
import tempfile
from datetime import datetime, timezone

TELEMETRY_PATH = os.path.join(os.path.dirname(__file__), "agent_telemetry.json")


def _parse_transcript(transcript_path):
    """JSONL 트랜스크립트에서 Agent/Task/Skill 디스패치와 완료 여부, 위계 에지를 수집."""
    agents = []
    skill_counts = {}
    hierarchy_edges = 0

    # tool_use id → 인덱스 매핑 (완료 여부 확인용)
    dispatched_ids = {}  # tool_use_id → agents 리스트 인덱스

    # tool_result가 존재하는 tool_use_id 집합
    completed_ids = set()

    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return agents, skill_counts, hierarchy_edges

    messages = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            messages.append(msg)
        except Exception:
            continue

    # 1패스: tool_result 완료 id 수집 + 위계 에지 수집
    for msg in messages:
        # parent_tool_use_id가 있으면 위계 에지 (최상위 또는 message 내부 확인)
        if msg.get("parent_tool_use_id"):
            hierarchy_edges += 1

        # 트랜스크립트 구조: 최상위에 role 없음, msg.message.role / msg.message.content 사용
        inner = msg.get("message") or msg
        role = inner.get("role", "")
        content = inner.get("content", [])
        if not isinstance(content, list):
            continue

        if role == "user":
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_result":
                    tid = block.get("tool_use_id", "")
                    if tid:
                        completed_ids.add(tid)

    # 2패스: agent/task/skill 디스패치 수집
    for msg in messages:
        inner = msg.get("message") or msg
        role = inner.get("role", "")
        content = inner.get("content", [])
        if not isinstance(content, list):
            continue

        if role == "assistant":
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "tool_use":
                    continue

                name = block.get("name", "")
                tool_id = block.get("id", "")
                inp = block.get("input", {}) or {}

                if name in ("Agent", "Task"):
                    desc = inp.get("description", "")
                    subagent_type = inp.get("subagent_type", "")
                    model = inp.get("model", "")
                    idx = len(agents)
                    agents.append({
                        "desc": desc,
                        "type": subagent_type,
                        "model": model,
                        "completed": False,  # 2패스 후 갱신
                        "_tool_id": tool_id,
                    })
                    if tool_id:
                        dispatched_ids[tool_id] = idx

                elif name == "Skill":
                    skill_name = inp.get("skill", "") or inp.get("name", "")
                    if skill_name:
                        skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1

    # 완료 여부 반영
    for tool_id, idx in dispatched_ids.items():
        if tool_id in completed_ids:
            agents[idx]["completed"] = True

    # 내부 키 제거
    for a in agents:
        a.pop("_tool_id", None)

    return agents, skill_counts, hierarchy_edges


def _merge_write(session_id, project, agents, skill_counts, hierarchy_edges):
    """agent_telemetry.json 에 session_id 키로 merge-write (atomic)."""
    # 기존 데이터 로드
    if os.path.exists(TELEMETRY_PATH):
        try:
            with open(TELEMETRY_PATH, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {}

    incomplete = sum(1 for a in agents if not a["completed"])

    data[session_id] = {
        "project": project,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "agents": agents,
        "agent_total": len(agents),
        "agent_incomplete": incomplete,
        "skills": skill_counts,
        "hierarchy_edges": hierarchy_edges,
    }

    # atomic write
    dir_ = os.path.dirname(TELEMETRY_PATH)
    fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, TELEMETRY_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass


def main():
    try:
        raw = sys.stdin.read().lstrip("﻿")  # BOM 방어
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    transcript_path = data.get("transcript_path", "")
    session_id = data.get("session_id", "")
    cwd = data.get("cwd", "") or os.getcwd()
    project = os.path.basename(os.path.normpath(cwd))

    if not transcript_path or not session_id:
        sys.exit(0)

    if not os.path.exists(transcript_path):
        sys.exit(0)

    try:
        agents, skill_counts, hierarchy_edges = _parse_transcript(transcript_path)
        _merge_write(session_id, project, agents, skill_counts, hierarchy_edges)
    except Exception:
        pass  # 모든 예외 무시 — 관측이 작업을 막으면 안 됨

    sys.exit(0)


if __name__ == "__main__":
    main()
