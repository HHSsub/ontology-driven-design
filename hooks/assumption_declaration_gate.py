"""
Stop 훅 — 전략 판단 시 가정 명시 강제

L0: 클로드가 전략적 판단(수익 예측, 가치 평가, 시장 분석, 아키텍처 결정)을
    채팅 응답에서 출력할 때 → 가정 선언 없이 결론만 내리는 것을 차단한다.

L1: 클로드의 마지막 응답 텍스트를 분석 →
    전략적 판단 패턴이 있으면 → 가정 선언 패턴이 있는지 확인 → 없으면 차단

L2: 파일 내용을 검사하지 않는다. 오직 Claude의 채팅 응답 텍스트만 검사한다.
    가정 명시는 응답 텍스트에 있어야 한다. 파일에 삽입하는 것 절대 금지.

L3: Stop 훅 → transcript 마지막 어시스턴트 메시지 텍스트 파싱 → 패턴 검사 → exit 2

━━ 발동 조건 ━━
클로드의 채팅 응답에 다음 중 하나 이상이 있을 때:
  - 수치 기반 사업 예측 (x건 × y원, 전환율, 예상 수익)
  - 시장/경쟁 분석 결론 ("경쟁력 있다", "시장 기회가 크다", "가능성이 높다")
  - 자산 가치 판단 ("강한 자산", "높은 가치", "매력적인 시장")
  - 전략 방향 추천 ("이 방향이 맞다", "A보다 B가 낫다")

━━ 통과 조건 ━━
응답 텍스트에 다음 중 하나라도 있으면 통과:
  [가정 명시], [가정], 가정 N:, 전제:, 미확인:, assumption:, 미검증
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# ── 전략 판단 탐지 패턴 ───────────────────────────────────────────────────
# 수치 기반 예측: "200건 × $49", "전환율 3%", "예상 매출 1000만원"
NUMERIC_PREDICT_RE = re.compile(
    r"(\d[\d,]*\s*[×x]\s*[$₩￦]?\d)"          # 수량 × 가격
    r"|전환율\s*\d"                              # 전환율 N%
    r"|(예상|추정|기대)\s*(수익|매출|판매|건수)" # 예상 수익/매출
    r"|\d+\s*(명|건|개)\s*(이상|정도)?\s*(구매|구독|결제)",
    re.IGNORECASE,
)

# 시장·가치 판단: "경쟁력 있다", "시장 기회", "강한 자산"
MARKET_JUDGE_RE = re.compile(
    r"(경쟁력\s*(있|높|강))"
    r"|(시장\s*(기회|규모|잠재))"
    r"|(강한\s*자산|높은\s*가치|매력적인\s*시장)"
    r"|(IP가\s*강|자산\s*가치)"
    r"|(팔릴\s*(것|수\s*있)|수익\s*(가능|창출))",
    re.IGNORECASE,
)

# 전략 방향 추천: "이 방향이 맞다", "A보다 B가 낫다", "권고합니다"
STRATEGY_REC_RE = re.compile(
    r"(이\s*방향이\s*(맞|옳|적합))"
    r"|(보다\s*.{1,20}\s*(낫|좋|적합))"
    r"|(권고|강력\s*추천|최적의\s*방법)"
    r"|(해야\s*합니다|해야\s*할\s*것)",
    re.IGNORECASE,
)

# 종합: 세 패턴 중 하나라도 있으면 전략 판단으로 간주
STRATEGIC_JUDGMENT_PATTERNS = [NUMERIC_PREDICT_RE, MARKET_JUDGE_RE, STRATEGY_REC_RE]

# ── 가정 선언 탐지 패턴 ───────────────────────────────────────────────────
ASSUMPTION_RE = re.compile(
    r"(\[가정\s*명시\]|\[가정\])"
    r"|가정\s*\d+\s*:"
    r"|전제\s*\d*\s*:"
    r"|미확인\s*:"
    r"|미검증"
    r"|assumption\s*\d*\s*:",
    re.IGNORECASE,
)

# ── 최소 응답 길이 (너무 짧은 응답은 건너뜀) ─────────────────────────────


def _extract_last_assistant_text(transcript_path: str) -> str:
    """transcript JSONL에서 마지막 어시스턴트 메시지의 텍스트를 추출."""
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except Exception:
        return ""

    last_text = ""
    for line in lines:
        try:
            entry = json.loads(line)
            msg = entry.get("message", {})
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            parts = [
                b.get("text", "")
                for b in content
                if isinstance(b, dict) and b.get("type") == "text"
            ]
            text = "\n".join(parts).strip()
            if text:
                last_text = text
        except Exception:
            continue
    return last_text


def _is_strategic_judgment(text: str) -> bool:
    """응답 텍스트에 전략적 판단 패턴이 있는지 확인."""
    return any(p.search(text) for p in STRATEGIC_JUDGMENT_PATTERNS)


def _has_assumption_declaration(text: str) -> bool:
    """응답 텍스트에 가정 선언이 있는지 확인."""
    return bool(ASSUMPTION_RE.search(text))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    # stop_hook_active: 이미 이 훅이 차단 중이면 무한 루프 방지
    if payload.get("stop_hook_active"):
        return 0

    transcript_path = payload.get("transcript_path", "")
    if not transcript_path or not Path(transcript_path).exists():
        return 0

    last_text = _extract_last_assistant_text(transcript_path)

    # 빈 응답은 검사 불필요
    if not last_text.strip():
        return 0

    # 전략적 판단이 없으면 통과
    if not _is_strategic_judgment(last_text):
        return 0

    # 전략적 판단이 있는데 가정 선언이 없으면 차단
    if _has_assumption_declaration(last_text):
        return 0

    err = (
        "\n══════════════════════════════════════════════\n"
        "❌ 전략 판단 — 가정 미선언 차단\n"
        "══════════════════════════════════════════════\n"
        "응답에 전략적 판단(수익 예측 / 가치 평가 / 시장 분석)이 감지됐는데\n"
        "가정 선언이 없습니다.\n\n"
        "판단 전에 채팅 응답 안에 다음 형식으로 선언하세요:\n\n"
        "  [가정 명시]\n"
        "  - 가정 1: [내용] → 검증 상태: [검증됨 / 미검증 / 가정일 뿐]\n"
        "  - 가정 2: [내용] → 검증 상태: ...\n\n"
        "⚠️  파일에 삽입하지 말 것 — 응답 텍스트에만 작성\n"
        "══════════════════════════════════════════════"
    )
    print(err, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
