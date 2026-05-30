"""
PreToolUse 훅 — Agent 호출 피라미드 가드

L0: 모든 에이전트 호출이 목적·역할·범위를 명시해 수직위계 구조를 강제
L1: Agent 도구 호출마다 L0 선언 + 역할명세 존재 검증. 전략 작업에 Opus 권고.
L2: stdin JSON → tool_name == Agent 시 prompt 분석 → L0 / 역할명세 확인
L3: Python stdin 파싱 → 키워드 탐지 → exit 2 (하드차단) or exit 1 (경고)

━━ 수직위계 구조 (예시, 고정 아님) ━━
Seed(Opus): L0 분석·전략·병렬가설 생성
  ├─ Branch-A (Sonnet): 도메인 A 실행
  ├─ Branch-B (Sonnet): 도메인 B 실행
  └─ Executor (Haiku): 순수 파일 수정·포맷

이 훅은 특정 구조를 강제하지 않는다.
어떤 구조든 L0 목적과 역할 명세가 있어야 한다.
"""
from __future__ import annotations

import json
import re
import sys

# L0 선언 탐지
L0_RE = re.compile(r"\bL0\s*[:：]", re.IGNORECASE)

# 역할 명세 탐지 (어떤 형태든)
ROLE_PATTERNS = [
    re.compile(r"직책\s*[:：]"),
    re.compile(r"역할\s*[:：]"),
    re.compile(r"\b(Leader|Manager|Worker|Executor|Seed|Branch)\b", re.IGNORECASE),
    re.compile(r"담당\s*범위\s*[:：]"),
    re.compile(r"L0\s*(미션|목적|목표)\s*[:：]"),
]

# 전략 작업 키워드 → Opus 권장
STRATEGY_KEYWORDS = [
    "전략", "설계", "어떤 방향", "어떤 구조", "무엇을 해야",
    "어떻게 해야", "평가", "분析", "분석", "가설", "아키텍처",
    "L0~L3", "온톨로지", "피라미드", "자가진화",
]

# 실행 작업 키워드 → Haiku 적합
EXECUTOR_KEYWORDS = [
    "파일 수정", "편집", "교체", "변경사항 적용", "텍스트 교체",
    "JSON 검증", "lint", "format",
]

MIN_PROMPT_LEN = 150  # 짧은 프롬프트는 검사 생략


def has_role_spec(prompt: str) -> bool:
    return any(p.search(prompt) for p in ROLE_PATTERNS)


def detect_work_type(prompt: str) -> str:
    """전략/실행/일반 중 분류."""
    strategy_score = sum(1 for kw in STRATEGY_KEYWORDS if kw in prompt)
    executor_score = sum(1 for kw in EXECUTOR_KEYWORDS if kw in prompt)
    if strategy_score >= 2:
        return "strategy"
    if executor_score >= 2:
        return "executor"
    return "general"


def main() -> int:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        return 0

    tool_name = data.get("tool_name", "")
    if tool_name != "Agent":
        return 0

    tool_input = data.get("tool_input", {})
    prompt = tool_input.get("prompt", "")
    model = tool_input.get("model", "")

    if len(prompt) < MIN_PROMPT_LEN:
        return 0  # 짧은 프롬프트 (simple lookup) 는 검사 생략

    issues = []
    hints = []

    # ━━ L0 선언 필수 ━━
    if not L0_RE.search(prompt):
        issues.append("L0 선언 없음 — 에이전트가 왜 존재하는지 목적이 없다")
        hints.append("  L0: [이 에이전트가 달성해야 할 비즈니스 목적]")

    # ━━ 역할 명세 권장 ━━
    if not has_role_spec(prompt):
        hints.append("  권장: 역할(Leader/Manager/Worker/Executor) 또는 담당 범위 명시")

    # ━━ 전략 작업 → Opus 권고 ━━
    work_type = detect_work_type(prompt)
    if work_type == "strategy" and model and model not in ("opus",):
        hints.append(
            f"  전략 작업에 model='{model}' — 전략·설계·분析은 model='opus' 권장\n"
            f"  (병렬 가설 탐색, 창의적 전략 생성은 Opus가 적합)"
        )

    # ━━ 실행 작업 → Haiku 권고 ━━
    if work_type == "executor" and model and model not in ("haiku", "sonnet"):
        hints.append(
            f"  순수 실행 작업에 model='{model}' — 파일 수정·포맷 작업은 model='haiku' 적합"
        )

    if not issues and not hints:
        return 0

    lines = [
        "",
        "══════════════════════════════════════════════",
    ]
    if issues:
        lines.append("❌ 에이전트 피라미드 가드 — 차단")
        lines.append("══════════════════════════════════════════════")
        for issue in issues:
            lines.append(f"  • {issue}")
    else:
        lines.append("⚠️  에이전트 피라미드 가드 — 개선 권고")
        lines.append("══════════════════════════════════════════════")

    if hints:
        lines.append("")
        lines.append("개선 방향:")
        lines.extend(hints)

    lines.extend([
        "",
        "에이전트 호출 필수 명세 (어떤 구조든 공통):",
        "  L0: [이 에이전트가 달성해야 할 최종 목적]",
        "  역할: [Leader | Manager | Worker | Executor | Seed | Branch]",
        "  범위: [접근 가능한 파일/도메인]",
        "  보고: [결과를 누구에게 압축 전달하는가]",
        "",
        "구조 예시 (고정 아님, 상황에 맞게 선택):",
        "  단순: Opus(전략) → Sonnet(실행)",
        "  트리: Opus(Seed) → Sonnet×N(Branch) → Haiku(Executor)",
        "  검토: Haiku(초안) → Sonnet(개선) → Opus(L0 검증)",
        "  병렬: Opus(가설생성) → Sonnet×3(가설검증) → Opus(종합)",
        "══════════════════════════════════════════════",
    ])

    print("\n".join(lines), file=sys.stderr)
    return 2 if issues else 0  # L0 없으면 하드차단, 권고만이면 통과


if __name__ == "__main__":
    sys.exit(main())
