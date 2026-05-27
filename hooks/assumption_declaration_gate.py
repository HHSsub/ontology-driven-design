"""
PreToolUse 훅 — 전략 문서 Write 시 가정 명시 강제 게이트

L0: 전략 판단을 담은 문서에 가정 목록 없이 결론만 쓰는 것을 차단한다
L1: 사업부/전략실행 경로 .md 파일 Write 시 → 파일 내용에 가정 선언 섹션 존재 확인
L2: 전략 문서에만 적용 (코드/메모리/설정 제외), 섹션 존재 여부만 확인 (내용 평가 X)
L3: PreToolUse → file_path 필터링 → 파일 content/new_string 탐색 → 없으면 exit 2

━━ 이 훅의 발동 조건 ━━
- Edit / Write / NotebookEdit
- file_path가 전략 문서 경로이고 .md 확장자
- 파일 내용에 가정 선언 패턴이 없으면 차단

━━ 통과 조건 ━━
다음 중 하나라도 포함:
  [가정 명시] 또는 [가정]
  가정 1:  가정 2: 가정:
  전제:  전제 1:
  미확인:  확인됨:
  assumption: premise:

━━ 커스터마이징 ━━
STRATEGY_PATH_PATTERNS 리스트에 자신의 전략 문서 경로 키워드를 추가하면
자신의 프로젝트 구조에 맞게 적용 가능.
기본값은 예시이며, 경로가 다르면 발동하지 않음 (안전).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}

# 전략 문서 경로 패턴 — 이 경로의 .md 파일만 체크
# 자신의 전략 문서 경로에 맞게 수정하세요
STRATEGY_PATH_PATTERNS = [
    "사업부",
    "전략실행",
    "역공학",
    "당장파이프라인",
    "strategy",
    "strategic",
]

# 가정 선언 패턴들
ASSUMPTION_RE = re.compile(
    r"(\[가정\s*명시\]|\[가정\]|가정\s*\d*\s*:|전제\s*\d*\s*:|미확인:|확인됨:|assumption\s*:|premise\s*:)",
    re.IGNORECASE,
)

# 체크 면제 파일 패턴
EXEMPT_FILE_PATTERNS = [
    r"memory[/\\]",
    r"\.claude[/\\]",
    r"hooks[/\\]",
    r"\.json$",
    r"\.py$",
    r"MEMORY\.md$",
    r"CLAUDE\.md$",
]
EXEMPT_RE = re.compile("|".join(EXEMPT_FILE_PATTERNS), re.IGNORECASE)


def _is_strategy_doc(file_path: str) -> bool:
    if not file_path.lower().endswith(".md"):
        return False
    if EXEMPT_RE.search(file_path):
        return False
    path_lower = file_path.lower().replace("\\", "/")
    return any(p.lower() in path_lower for p in STRATEGY_PATH_PATTERNS)


def _extract_content(tool_name: str, tool_input: dict) -> str:
    if tool_name == "Write":
        return tool_input.get("content", "")
    if tool_name == "Edit":
        return tool_input.get("new_string", "")
    return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_name = payload.get("tool_name", "") or payload.get("tool", "")
    if tool_name not in EDIT_TOOLS:
        return 0

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")

    if not file_path or not _is_strategy_doc(file_path):
        return 0

    content = _extract_content(tool_name, tool_input)
    if not content:
        return 0

    if ASSUMPTION_RE.search(content):
        return 0

    err = (
        "\n══════════════════════════════════════════════\n"
        "❌ 가정 명시 없음 — 전략 문서 Write 차단\n"
        "══════════════════════════════════════════════\n"
        f"파일: {file_path}\n\n"
        "전략 문서에는 반드시 가정 목록을 선언해야 합니다.\n\n"
        "다음 중 하나를 포함하세요:\n\n"
        "  [가정 명시]\n"
        "  - 가정 1: [내용] → 검증 상태: [검증됨 / 미검증 / 가정일 뿐]\n"
        "  - 가정 2: [내용] → 검증 상태: ...\n\n"
        "또는:\n"
        "  미확인: [판단 내용]\n"
        "  가정: [내용]\n"
        "  전제: [내용]\n\n"
        "검증 안 된 가정을 숨기고 결론만 쓰는 것 = 틀린 판단의 온상\n"
        "══════════════════════════════════════════════"
    )
    print(err, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
