"""
PreToolUse hook — WebSearch 현재 연도 강제 가드

L0: 외부 정보 검색 시 항상 currentDate 기준 최신 정보 확보
L1: WebSearch 호출 시 쿼리에 현재 연도가 없으면 차단 (exit 2)
L2: stdin JSON 파싱 → query 추출 → 연도/최신 키워드 존재 확인 → 없으면 차단
"""
from __future__ import annotations

import json
import sys
import datetime

CURRENT_YEAR = datetime.datetime.now().year


def main() -> int:
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return 0

    tool_name = (
        data.get("tool_name", "")
        or data.get("tool_use", {}).get("name", "")
        or ""
    )

    if "WebSearch" not in tool_name:
        return 0

    tool_input = data.get("tool_input", {}) or data.get("tool_use", {}).get("input", {}) or {}
    query = str(tool_input.get("query", ""))

    year_str = str(CURRENT_YEAR)
    has_year = (
        year_str in query
        or "최신" in query
        or "current" in query.lower()
        or "latest" in query.lower()
        or "today" in query.lower()
        or "2026" in query
    )

    if has_year:
        return 0

    print(
        "\n══════════════════════════════════════════════\n"
        "❌ WebSearch 차단 — 현재 연도 미포함\n"
        "══════════════════════════════════════════════\n"
        f"쿼리: {query}\n\n"
        f"외부 서비스·API·요금·정책·스펙 등 어떤 외부 정보든\n"
        f"반드시 현재 연도({CURRENT_YEAR})를 쿼리에 포함해야 합니다.\n\n"
        f"✅ 수정 예시: \"{query} {CURRENT_YEAR}\"\n"
        "══════════════════════════════════════════════",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
