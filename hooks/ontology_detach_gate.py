"""
PreToolUse hook — L2 구조 변경 전 ontology-detach 강제

L0: L2 구조(타입/인터페이스/열거형/스키마/모델) 변경 시 의존성 체인이 항상 추적된다
L1: Edit/Write 전에 파일이 L2 구조 파일인지 탐지 → ontology-detach 미발동이면 차단
L2: 파일명 패턴 + 내용 패턴으로 L2 구조 파일 식별. transcript에서 detach 발동 여부 확인
L3: CLAUDE_FILE_PATHS, CLAUDE_TRANSCRIPT_PATH 환경변수로 탐지
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# L2 구조 파일로 판단하는 파일명 패턴 (대소문자 무관)
STRUCTURAL_NAME_PATTERNS = re.compile(
    r"(type|interface|model|schema|enum|constant|config|struct|entity|domain)"
    r"s?(\.|_|-|$)",
    re.IGNORECASE,
)

# L2 구조 파일로 판단하는 내용 패턴
STRUCTURAL_CONTENT_PATTERNS = [
    # TypeScript/JavaScript
    r"^(?:export\s+)?(?:interface|type)\s+\w+",
    r"^(?:export\s+)?enum\s+\w+",
    r"^(?:export\s+)?(?:abstract\s+)?class\s+\w+",
    # Python
    r"^class\s+\w+.*(?:BaseModel|Enum|TypedDict|NamedTuple|dataclass)",
    r"^@dataclass",
    r"^class\s+\w+\(.*Enum\)",
    # Go
    r"^type\s+\w+\s+(?:struct|interface)\s*\{",
    # General schema patterns
    r'"type":\s*"object"',
    r"\$schema",
]
STRUCTURAL_CONTENT_RE = re.compile(
    "|".join(STRUCTURAL_CONTENT_PATTERNS), re.MULTILINE
)

# ontology-detach 발동으로 인정하는 패턴 (transcript에서 탐지)
DETACH_TOOL_USE = re.compile(r'"name"\s*:\s*"Skill"', re.IGNORECASE)
DETACH_SKILL_INPUT = re.compile(r'"skill"\s*:\s*"ontology-detach"', re.IGNORECASE)
# grep 기반 의존성 탐색도 인정 (넓은 기준)
GREP_EVIDENCE = re.compile(
    r'"command"\s*:\s*"(?:grep|rg|Get-ChildItem|findstr|Grep)[^"]*"',
    re.IGNORECASE,
)

# 면제 경로
EXEMPT_PATHS = re.compile(
    r"(test|spec|__pycache__|\.git|node_modules|dist|build|\.odd|hooks/)",
    re.IGNORECASE,
)


def _is_structural_file(file_path: str) -> bool:
    p = Path(file_path)
    name = p.name.lower()

    # 파일명 패턴 체크
    if STRUCTURAL_NAME_PATTERNS.search(name):
        return True

    # 면제 경로
    if EXEMPT_PATHS.search(file_path.replace("\\", "/")):
        return False

    # 내용 패턴 체크 (파일이 존재할 때만)
    if p.exists() and p.suffix in (".ts", ".tsx", ".py", ".go", ".java", ".json", ".yaml", ".yml"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            if STRUCTURAL_CONTENT_RE.search(text[:3000]):  # 첫 3KB만 스캔
                return True
        except Exception:
            pass

    return False


def _has_detach_in_session(transcript_path: str) -> bool:
    """transcript에서 ontology-detach 발동 또는 grep 의존성 탐색 증거를 찾는다."""
    if not transcript_path or not Path(transcript_path).exists():
        return False

    try:
        text = Path(transcript_path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False

    # Skill(ontology-detach) 명시적 발동
    if DETACH_TOOL_USE.search(text) and DETACH_SKILL_INPUT.search(text):
        return True

    # grep 기반 의존성 탐색 (3회 이상이면 의식적으로 추적 중으로 간주)
    grep_count = len(GREP_EVIDENCE.findall(text))
    if grep_count >= 3:
        return True

    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "NotebookEdit"):
        return 0

    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return 0

    if not _is_structural_file(file_path):
        return 0

    transcript_path = payload.get("transcript_path", "") or os.environ.get("CLAUDE_TRANSCRIPT_PATH", "")

    if _has_detach_in_session(transcript_path):
        return 0  # 이미 탐색함 → 통과

    msg = (
        "\n╔══════════════════════════════════════════════════════╗\n"
        "║  ⛔ L2 구조 변경 — ontology-detach 先 발동 필수      ║\n"
        "╚══════════════════════════════════════════════════════╝\n\n"
        f"  파일: {file_path}\n\n"
        "  이 파일은 L2 구조 정의 파일입니다.\n"
        "  변경 전 의존성 체인을 반드시 추적해야 합니다.\n\n"
        "  1. /ontology-detach 실행\n"
        "     → 이 타입/인터페이스를 참조하는 모든 L3 구현 grep\n"
        "     → 교체조건 명시\n\n"
        "  2. 의존성 목록 확인 후 이 파일 수정\n\n"
        "  3. 파생 L3 구현도 같은 세션에서 함께 수정\n\n"
        "  ontology-detach 없이 L2 구조 변경 = 의존성 체인 단절 위험\n"
    )
    print(msg, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
