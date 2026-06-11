# L0: 에이전트 작업의 무한루프와 예산 폭주를 알람이 아니라 실행 전 차단으로 막는 것
# L1: PreToolUse(Agent) 훅 — 동일 description 3회 반복 또는 세션 누적 12회 초과 시 exit 2
# L2: 트랜스크립트 JSONL에서 기존 Agent 디스패치를 수집, 정규화 비교 + 카운트 검사
# L3: stdin JSON 파싱 → 트랜스크립트 스캔 → 차단 or 통과

from __future__ import annotations

import json
import os
import re
import sys

LOOP_THRESHOLD = 3      # 동일 description 반복 차단 기준
BUDGET_THRESHOLD = 12   # 세션 누적 디스패치 차단 기준
UNLOCK_MARKER = "예산해제승인"


def _normalize(text: str) -> str:
    """공백 압축 + 소문자 정규화."""
    return re.sub(r"\s+", " ", text.strip()).lower()


def _collect_dispatches(transcript_path: str) -> list[str]:
    """트랜스크립트에서 assistant tool_use name=Agent/Task 의 description 목록 반환."""
    if not transcript_path or not os.path.exists(transcript_path):
        return []

    try:
        with open(transcript_path, encoding="utf-8-sig", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return []

    descs: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue

        inner = msg.get("message") or msg
        role = inner.get("role", "")
        content = inner.get("content", [])
        if role != "assistant" or not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            if block.get("name") not in ("Agent", "Task"):
                continue
            inp = block.get("input", {}) or {}
            desc = inp.get("description", "")
            descs.append(desc)

    return descs


def main() -> int:
    try:
        raw_bytes = sys.stdin.buffer.read()
        # BOM(UTF-8) 제거 후 UTF-8 디코드, 실패 시 시스템 기본값 시도
        if raw_bytes.startswith(b"\xef\xbb\xbf"):
            raw_bytes = raw_bytes[3:]
        try:
            raw = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raw = raw_bytes.decode(sys.getdefaultencoding(), errors="replace")
        data = json.loads(raw)
    except Exception:
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name != "Agent":
        return 0

    tool_input = data.get("tool_input", {}) or {}
    current_desc = tool_input.get("description", "")
    current_prompt = tool_input.get("prompt", "")
    transcript_path = data.get("transcript_path", "")

    # 해제 마커 확인 — 포함 시 모든 검사 통과
    combined_text = (current_desc or "") + (current_prompt or "")
    if UNLOCK_MARKER in combined_text:
        return 0

    past_descs = _collect_dispatches(transcript_path)
    total_count = len(past_descs)

    # ── 검사 B: 세션 누적 예산 초과 ──
    if total_count >= BUDGET_THRESHOLD:
        msg_lines = [
            "",
            "══════════════════════════════════════════════",
            "에이전트 세션 예산 소진 — 디스패치 차단",
            "══════════════════════════════════════════════",
            f"  세션 누적 디스패치: {total_count}회 (한계: {BUDGET_THRESHOLD}회)",
            "",
            "  작업 분해가 잘못됐거나 에이전트 폭주가 의심된다.",
            "  해제하려면 유저 확인 후 프롬프트에 '예산해제승인' 문자열을 포함하라.",
            "══════════════════════════════════════════════",
        ]
        os.write(2, "\n".join(msg_lines).encode("utf-8", errors="replace"))
        return 2

    # ── 검사 A: 동일 description 반복 루프 ──
    norm_current = _normalize(current_desc)
    if norm_current:
        repeat_count = sum(
            1 for d in past_descs if _normalize(d) == norm_current
        )
        if repeat_count >= LOOP_THRESHOLD:
            msg_lines = [
                "",
                "══════════════════════════════════════════════",
                "에이전트 루프 감지 — 동일 작업 반복 차단",
                "══════════════════════════════════════════════",
                f"  description '{current_desc[:80]}' 이미 {repeat_count}회 반복됨",
                "",
                "  동일 작업 재시도는 접근 자체가 틀렸다는 신호다.",
                "  세부 재시도를 금지한다.",
                "  L1 구조를 재검토하거나 ontology-learning 후 다른 접근으로 전환하라.",
                "══════════════════════════════════════════════",
            ]
            os.write(2, "\n".join(msg_lines).encode("utf-8", errors="replace"))
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
