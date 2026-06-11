"""
PostToolUse 훅 — 피라미드 위계 온톨로지 가드

L0: 모든 산출물이 존재 목적에 연결되도록 구조적으로 강제
L1: 파일 저장마다 L 레벨 선언의 존재성·의미·위계 정합성 검증
L2-A: 헤더 L 선언 존재 확인
L2-B: L0 내용 → 비즈니스 목적인가 / 기술 세부사항인가 / 도구에 종속됐는가
L2-C: L1 내용 → 흐름 목표인가 / L3 구현세부가 올라왔는가 / 도구에 종속됐는가
L2-D: L2 헤더 내용 → 기능단위 이름인가 / 구현세부가 올라왔는가
L2-E: 파일 본문(헤더 이후)에서 L0 오용 탐지 — 언어·형식 무관 위치 기반
L2-F: 탈존재(ontology-detach) 위반 — 교체조건 없는 하드코딩 탐지
L2-G: 중복 진실(Duplicate Truth) — SSOT 위반 탐지 (의미론적, 도메인 무관)
L3: CLAUDE_FILE_PATHS env → 파일 읽기 → 검사 → exit 2

━━ 탈도구 원칙 ━━
L0/L1은 특정 파일형식·도구·언어에 종속되지 않는다.
상위 레벨은 하위 레벨에 종속되지 않는다.
이 훅의 L3 구현이 Python이어도 무방 — 그것이 L3(구현 세부)이기 때문.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# ─── 공통 L 레벨 패턴 ────────────────────────────────────────────────────────
L_ANY_RE = re.compile(r"\[?L([0-3])\]?\s*:", re.IGNORECASE)
L0_RE    = re.compile(r"\[?L0\]?\s*:",       re.IGNORECASE)
L1_RE    = re.compile(r"\[?L1\]?\s*:",       re.IGNORECASE)
L2_RE    = re.compile(r"\[?L2\]?\s*:",       re.IGNORECASE)

# ─── L2-B: L0 내용 위반 패턴 ─────────────────────────────────────────────────
# L0는 "왜 이 시스템이 존재하는가" — 비즈니스 최종 목적.
# 아래 내용이 L0 줄에 있으면 → L3 세부사항이 L0에 올라온 것.
#
# ✅ 통과:  L0: SNS(YouTube) 업로드 자동화 — 유저 개입 없이 콘텐츠 발행
# ✅ 통과:  L0: 비용 투명성 — FAL API 실사용량을 admin이 언제든 확인 가능
# ✅ 통과:  L0: 사용자 다운로드 권리 보장 — 완료 후 파일 즉시 삭제 금지
# ❌ 차단:  L0: 타임아웃 10초 이내 완료          (구현 제약 → L3)
# ❌ 차단:  L0: RT 비율 ≤ 2.0                   (성능 수치 → L3)
# ❌ 차단:  L0: 비트레이트 8Mbps 이상 유지        (기술 파라미터 → L3)
# ❌ 차단:  L0: ffmpeg로 영상 인코딩              (도구 명시 → L3)
# ❌ 차단:  L0: .py 파일에서 py_compile 실행      (파일형식+도구 명시 → L3)
# ❌ 차단:  L0: 필터당 video_duration * 10       (계산식 → L3)
# ❌ 차단:  L0: 단일코어 안전 마진 확보            (하드웨어 제약 → L3)
_L0_VIOLATION = re.compile(
    r"\b("
    # 시간/성능 수치
    r"timeout|time[-_]?out|타임아웃"
    r"|RT\s*비율|실시간\s*비율|RT\s*ratio|RT\s*\d"
    r"|msec|millisec|\d+\s*초\s*이내|\d+\s*sec\b|\d+\s*ms\b"
    r"|latency|레이턴시"
    # 데이터 크기/비트레이트
    r"|bitrate|bit[-_]?rate|비트레이트|\d+\s*[MKG]bps|\d+\s*[MKG]B(?:ps)?"
    r"|bandwidth|대역폭"
    # 이미지/영상 해상도
    r"|pixel|픽셀|resolution|해상도|\d+x\d+|\d+p\b"
    r"|fps|\d+\s*fps"
    # 하드웨어/런타임 제약
    r"|thread|스레드|cpu|core|코어|단일코어|멀티코어"
    r"|cache|캐시|buffer|버퍼|queue|큐|메모리\s*\d"
    # 구현 도구 / API 명칭
    r"|ffmpeg|subprocess|asyncio|httpx|fastapi|sqlalchemy"
    r"|ffprobe|libx264|aac\b|codec"
    # 반복/재시도 수치
    r"|retry\s*\d|재시도\s*\d|polling|폴링|\d+\s*[회번]\s*재시도"
    # 계산식/수학
    r"|video_duration\s*\*|\d+\s*\*\s*\d+|pts_ratio|setpts"
    # 파일 확장자 고정
    r"|\.py\b|\.ts\b|\.js\b|\.json\b|\.yaml\b|\.mp4\b|\.mp3\b"
    # 안전 마진 / 구현 여유값
    r"|안전\s*마진|마진\s*\d|여유\s*\d"
    r")\b",
    re.IGNORECASE,
)

# ─── L2-B/C: 탈도구 위반 — L0·L1에 특정 도구/언어/파일형식 고정 ─────────────
# L0·L1은 어떤 도구로 구현하든 동일해야 함.
#
# ✅ 통과 (L0):  SNS 업로드 자동화
# ✅ 통과 (L1):  음악→영상→업로드 end-to-end 파이프라인
# ✅ 통과 (L0):  Claude Code 플러그인이 더 많은 개발자에게 채택됨  (플랫폼이 목적의 문맥)
# ✅ 통과 (L0):  Claude API를 통한 LLM 파이프라인 자동화          (플랫폼이 목적 주어)
# ❌ 차단 (L0):  Python을 사용해 영상 처리            (언어 고정 — 도구를 주어/동사로)
# ❌ 차단 (L0):  ffmpeg로 인코딩                     (도구 고정 — 도구를 행위 주체로)
# ❌ 차단 (L1):  .py 파일에서 비동기 처리             (파일형식+언어 고정)
# ❌ 차단 (L1):  Edit tool로 파일 수정 감시           (도구 고정)
# ❌ 차단 (L1):  FastAPI 라우터 경유                 (프레임워크 고정)
#
# 핵심 원칙 (ISSUE-019 수정):
#   플랫폼/언어명이 "주어+동사" 구조로 쓰일 때만 차단.
#   예: "Python을 사용", "ffmpeg로 처리", "FastAPI 기반", ".py 파일에서" → 차단
#   예: "Claude Code 플러그인", "Claude API 채택됨" → 통과 (목적 문맥)
#
# 구현: 플랫폼명 + 도구종속 동사/조사 패턴으로 좁힘
_TOOL_BINDING = re.compile(
    r"(?:"
    # ── 파일형식 확장자 고정 — 항상 차단 ────────────────────────────────────────
    # 파일형식이 L0/L1 목적 문맥에 쓰일 일 없음.
    # 주의: 한국어 조사(파, 로 등)는 re에서 \w → \b가 성립 안 함. (?!\w)로 대체.
    r"\.py(?!\w)|\.ts(?!\w)|\.js(?!\w)|\.jsx(?!\w)|\.tsx(?!\w)"
    # ── 구현 도구 — 도구명 + 도구종속 조사/동사 패턴 ─────────────────────────────
    # "ffmpeg로", "ffmpeg 기반", "ffmpeg을 이용" → 차단
    # 단독 "ffmpeg" (주어/목적어로만)는 L0에 쓰일 가능성이 거의 없으나 보수적으로 포함
    r"|ffmpeg(?:\s*(?:로|으로|기반|을|을\s*사용|으로\s*실행))"
    r"|subprocess(?:\s*(?:로|으로|기반|\.run|을|으로\s*실행))"
    r"|asyncio(?:\s*(?:로|으로|기반|\.|\s+await))"
    # ── 프로그래밍 언어 + 도구종속 동사/조사 조합 ────────────────────────────────
    # 언어명이 "수단"으로 쓰일 때만 차단. 목적 문맥("Python 생태계", "Java 애플리케이션")은 통과.
    r"|Python(?:\s*(?:을|로|으로|을\s*사용|으로\s*구현|을\s*이용|기반으로|스크립트))"
    r"|JavaScript(?:\s*(?:을|로|으로|을\s*사용|으로\s*구현|기반으로))"
    r"|TypeScript(?:\s*(?:을|로|으로|을\s*사용|으로\s*구현|기반으로))"
    r"|Ruby(?:\s*(?:로|으로|기반으로|을\s*사용))"
    r"|Golang(?:\s*(?:으로|기반으로|을\s*사용))"
    r"|Rust(?:\s*(?:로|으로|기반으로|을\s*사용))"
    r"|Java(?:\s*(?:로|으로|기반으로|을\s*사용))"
    r"|C\+\+(?:\s*(?:로|으로|기반으로))"
    # ── 특정 프레임워크/ORM — 프레임워크명 + 도구종속 조사/동사 ──────────────────
    r"|FastAPI(?:\s*(?:로|으로|기반|라우터|경유|를\s*통해))"
    r"|React(?:\s*(?:로|으로|기반|컴포넌트로|를\s*이용))"
    r"|Vue(?:\s*(?:로|으로|기반))"
    r"|Next\.js(?:\s*(?:로|으로|기반))"
    r"|SQLAlchemy(?:\s*(?:로|으로|기반|을\s*통해|를\s*통해|을\s*사용|를\s*사용))"
    r"|Alembic(?:\s*(?:로|으로|기반|migration))"
    r"|pydantic(?!\w)|uvicorn(?!\w)"
    # ── Claude Code 내부 도구명 — 도구명 + tool 조합은 항상 차단 ──────────────────
    # "Edit tool로", "Write tool을" → 차단 (한국어 조사가 붙어도 차단)
    # 단독 "Edit"은 영어 일반 동사이므로 "tool" 동반 필수
    r"|Edit\s+tool|Write\s+tool|Bash\s+tool"
    r"|PostToolUse(?!\w)|PreToolUse(?!\w)|Stop\s+hook"
    r")",
    re.IGNORECASE,
)

# ─── L2-C/D: L1·L2 위계 위반 — 구현 세부가 상위로 올라온 패턴 ───────────────
# L1 = 시스템 흐름/목표 (end-to-end). L2 = 독립 기능 단위 이름.
# 아래 내용이 L1/L2 줄에 있으면 → L3 세부사항이 상위로 올라온 것.
#
# ✅ 통과 (L1):  음악→영상→확장→합성→YouTube end-to-end
# ✅ 통과 (L2):  Gemini로 temporal_type/camera_motion 추출
# ✅ 통과 (L2):  YouTube 업로드용 제목/설명/태그 생성
# ❌ 차단 (L1):  retry 3회, 10초 간격             (재시도 수치 → L3)
# ❌ 차단 (L1):  .py 파일에서 비동기 체크           (파일형식 고정 → L3)
# ❌ 차단 (L2):  retry 제한 없이 API 호출           (제한 방식 → L3)
# ❌ 차단 (L2):  subprocess.run으로 ffmpeg 실행     (구현 메서드 → L3)
# ❌ 차단 (L2):  timeout=300 이내 완료             (수치 제약 → L3)
_L1L2_IMPL_DETAIL = re.compile(
    r"\b("
    # 재시도 수치/방식
    r"retry\s*\d+\s*[회번]|재시도\s*\d+\s*[회번]|retry\s*제한\s*없이"
    r"|최대\s*\d+\s*[회번]|무제한\s*재시도|unbounded|unlimited\s*retry"
    # 타임아웃 수치
    r"|timeout\s*=\s*\d+|타임아웃\s*\d+|\d+\s*초\s*간격|\d+\s*sec\s*interval"
    r"|\d+\s*초\s*대기|\d+\s*초\s*내에"
    # 파일형식 고정
    r"|\.py\b|\.ts\b|\.js\b|\.json\b|\.yaml\b|\.mp4\b|\.mp3\b"
    # 구현 메서드 고정
    r"|subprocess\.run|asyncio\.gather|asyncio\.sleep|asyncio\.wait"
    r"|httpx\.|requests\.|urllib\."
    # Boolean 제약 표현
    r"|제한\s*없이|limit\s*없이|무제한\b"
    r")\b",
    re.IGNORECASE,
)

# ─── L2-E: 파이프라인 실행자 — 헤더 이후 L0 허용 대상 ────────────────────────
# 파이프라인 직접 실행 함수는 L0 목적을 직접 달성하므로 내부 L0 허용.
# 허용:  _run_video_music_background, _auto_youtube_upload, _pipeline_post_process
# 불허:  _make_variation_clip, _verify_duration, merge_video_with_bgm 등 일반 함수
_PIPELINE_FUNC = re.compile(
    r"\b(_run_|_auto_|_pipeline_|_bg_|_background_)\w+"
)

# ─── L2-F: 탈존재(ontology-detach) 위반 패턴 ────────────────────────────────
# ontology-detach 원칙: 모든 binding에는 교체조건이 있어야 한다.
# 교체조건 없는 고정(하드코딩)은 탈존재 위반.
#
# ✅ 통과: n_clips = math.ceil(remaining / KLING_CLIP_DURATION_SEC)  # 물리 제약 유도
# ✅ 통과: max_wait = CLIP_SEC * 150                                  # 근거 있는 상수
# ❌ 차단: max_clips: int = 8,                                        # 매직넘버
# ❌ 차단: extensions = [".py", ".ts", ".tsx", ".js"]                 # 확장자 하드코딩
# ❌ 차단: timeout = 60                                               # 근거 없는 수치

# 함수 파라미터 매직넘버 탐지: def f(param: int = 8, ...) 형태
_MAGIC_PARAM_RE = re.compile(
    r"\bdef\s+\w+\s*\([^)]*:\s*(?:int|float)\s*=\s*(\d{2,})\b"
)

# 하드코딩 확장자 리스트 탐지: [".py", ".ts", ".js", ...] 같은 패턴
_HARDCODED_EXTENSIONS_RE = re.compile(
    r'\[(?:\s*"\.(?:py|ts|tsx|js|jsx|rb|go|rs|java|cpp|c|cs|php|swift|kt)\s*",?\s*){3,}\]'
)

# ─── L2-G: 중복 진실(Duplicate Truth) 탐지 — SSOT 위반 ────────────────────────
# 원칙: 동일 "개념 집합"은 단 하나의 소스(SSOT)에서만 존재해야 한다.
# 파생 표현은 반드시 SSOT로부터 함수적으로 생성되어야 한다.
# 동일 항목 집합이 N개 독립 위치에 수동으로 중복 → SSOT 위반.
#
# ✅ 통과: SOURCE = ["a", "b", "c"]         ← 단일 소스
#           derived = _build(SOURCE)          ← 함수적 파생
# ❌ 차단: list_x = ["a", "b", "c"]         ← 독립 목록 1
#           ...20줄 후...
#           list_y = ["a", "b", "c", "d"]    ← 독립 목록 2 (60%+ 중복)
#
# 탐지 방식: 식별자형 문자열(2-40자, 공백 최소) 3개 이상 포함한 인라인
#           리스트/튜플 리터럴 쌍에서 더 작은 쪽 기준 60% 이상 겹치면 위반.
# 도메인 무관: 코드의 커맨드·라우트·피처·키, 문서의 섹션·분류 — 어떤 것이든.

_BRACKET_INNER_RE = re.compile(r'[\[\(]([^\[\]\(\)]{8,300})[\]\)]')
_IDENT_STR_RE = re.compile(r'["\']([a-zA-Z가-힣][a-zA-Z0-9가-힣_\-/\.]{1,39})["\']')


def _collect_string_sets(content: str) -> list[tuple[int, frozenset[str]]]:
    """인라인 리스트/튜플에서 3개 이상 식별자형 문자열 집합을 추출."""
    result: list[tuple[int, frozenset[str]]] = []
    for i, line in enumerate(content.split("\n")):
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", '"""', "'''")):
            continue
        for m in _BRACKET_INNER_RE.finditer(line):
            raw = frozenset(_IDENT_STR_RE.findall(m.group(1)))
            # 순수 숫자, 너무 짧은 항목 제거 후 3개 이상이어야
            items = frozenset(s for s in raw if not s.isdigit() and len(s) >= 2)
            if len(items) >= 3:
                result.append((i + 1, items))
    return result


def check_duplicate_truth(content: str, filename: str) -> list[str]:
    """L2-G: 동일 개념 집합이 독립 리스트에 중복 존재하면 SSOT 위반으로 차단."""
    string_sets = _collect_string_sets(content)
    reported: set[tuple[int, int]] = set()
    violations: list[str] = []

    for idx_a in range(len(string_sets)):
        for idx_b in range(idx_a + 1, len(string_sets)):
            la, sa = string_sets[idx_a]
            lb, sb = string_sets[idx_b]
            if abs(la - lb) <= 3:
                continue  # 인접 줄 = 동일 구조의 일부
            overlap = sa & sb
            smaller = min(len(sa), len(sb))
            if smaller < 3 or len(overlap) < 3:
                continue
            if len(overlap) / smaller < 0.6:
                continue
            key = (min(la, lb), max(la, lb))
            if key in reported:
                continue
            reported.add(key)
            sample = sorted(overlap)[:4]
            violations.append(
                f"    :{la} ↔ :{lb} — 동일 개념 {len(overlap)}개 항목 독립 중복\n"
                f"           중복 항목 예시: {sample}\n"
                f"           ✅ SSOT 등록부 하나 → 파생 표현은 함수로 자동 생성\n"
                f"           ❌ 동일 항목을 독립 리스트에 수동 N회 유지"
            )

    if not violations:
        return []

    return [
        f"  {filename} — 중복 진실(Duplicate Truth) 위반 [L2-G: SSOT 위반]\n"
        + "\n".join(violations)
        + "\n"
        "  원칙: 동일 개념 집합은 단일 소스(SSOT), 파생 표현은 함수로.\n"
        "  적용: 어떤 도메인·어떤 형식의 열거형 개념 모음이든"
    ]


EXEMPT_SUFFIXES = {
    ".lock", ".sum", ".min.js", ".min.css",
    ".ico", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".mp4", ".mp3", ".wav", ".zip", ".gz", ".tar",
    ".pdf", ".xlsx", ".docx", ".db", ".sqlite",
}
EXEMPT_NAMES = {
    "requirements.txt", "requirements-dev.txt", "requirements-test.txt",
    "package.json", "package-lock.json", "pyproject.toml",
    "setup.cfg", "setup.py", ".gitignore", ".dockerignore",
    ".gitattributes", ".editorconfig", ".env", ".env.local", ".env.example",
    "Makefile", "tsconfig.json", "jsconfig.json",
    "jest.config.js", "jest.config.ts", "vite.config.js", "vite.config.ts",
    "tailwind.config.js", "tailwind.config.ts",
    "next.config.js", "next.config.ts",
    "dockerfile", "docker-compose.yml", "docker-compose.yaml",
    # 메타 레이어: 온톨로지 시스템 자신과 고정 포맷 문서는 L 선언 대상이 아님
    "claude.md", "memory.md", "readme.md", "license", "license.md", "changelog.md",
    "settings.json", "settings.local.json",
}
# 데이터/설정 포맷: 주석 불가하거나 포맷이 외부 고정 — L 선언 강제 부적합
EXEMPT_DATA_SUFFIXES = {".json", ".yaml", ".yml", ".toml", ".csv", ".txt", ".lock"}
# 메모리 파일 규약 (frontmatter 고정 포맷)
EXEMPT_NAME_PREFIXES = ("feedback_", "reference_", "project_")
MIN_LINES_FOR_CHECK = 15
HEADER_LINES = 20


def is_exempt(path: Path) -> bool:
    name_lower = path.name.lower()
    if name_lower in EXEMPT_NAMES:
        return True
    if name_lower.startswith(EXEMPT_NAME_PREFIXES):
        return True
    if name_lower == "__init__.py":
        try:
            return path.stat().st_size < 200
        except Exception:
            return True
    if any(name_lower.endswith(s) for s in EXEMPT_DATA_SUFFIXES):
        return True
    return any(name_lower.endswith(s) for s in EXEMPT_SUFFIXES)


def _find_l_line(lines: list[str], pattern: re.Pattern) -> str | None:
    for line in lines:
        if pattern.search(line):
            return line
    return None


def check_file(file_path: str) -> list[str]:
    """위반 메시지 목록 반환. 정상이면 빈 리스트."""
    path = Path(file_path)
    if not path.exists() or not path.is_file() or is_exempt(path):
        return []
    try:
        raw = path.read_bytes()
        if b"\x00" in raw[:8192]:
            return []
        content = raw.decode("utf-8", errors="replace")
    except Exception:
        return []

    lines = content.split("\n")
    if len(lines) < MIN_LINES_FOR_CHECK:
        return []

    header = lines[:HEADER_LINES]
    header_text = "\n".join(header)
    violations: list[str] = []

    # ━━ L2-A: 헤더에 L 선언 존재 ━━
    if not L_ANY_RE.search(header_text):
        violations.append(
            f"  {path.name} — 첫 {HEADER_LINES}줄 내 L0/L1 선언 없음 ({len(lines)}줄 파일)\n"
            f"  최소: 파일 첫 줄에 '# L0: 이 시스템의 비즈니스 목적' 선언 필요"
        )
        return violations  # 이하 검사는 선언이 있어야 의미 있음

    # ━━ L2-B: L0 내용 검증 ━━
    l0_line = _find_l_line(header, L0_RE)
    if l0_line:
        m = _L0_VIOLATION.search(l0_line)
        if m:
            violations.append(
                f"  {path.name} — L0에 기술 세부사항 혼입 (위계 위반)\n"
                f"  문제 단어: '{m.group()}'\n"
                f"  현재:   {l0_line.strip()}\n"
                f"  ✅ 올바른 L0:  SNS(YouTube) 업로드 자동화 — 유저 개입 없이 콘텐츠 발행\n"
                f"  ✅ 올바른 L0:  비용 투명성 — FAL API 실사용량을 admin이 언제든 확인 가능\n"
                f"  ❌ 잘못된 L0:  타임아웃/비트레이트/RT비율/ffmpeg/retry횟수 → L3에 써야 함"
            )
        m2 = _TOOL_BINDING.search(l0_line)
        if m2:
            violations.append(
                f"  {path.name} — L0 탈도구 위반: 특정 도구/언어에 종속\n"
                f"  문제 단어: '{m2.group()}'\n"
                f"  현재:   {l0_line.strip()}\n"
                f"  ✅ 올바른 L0:  비즈니스 목적만 (도구·언어·파일형식 언급 금지)\n"
                f"  ❌ 잘못된 L0:  Python으로 / ffmpeg 기반 / .py 파일에서 / FastAPI 라우터"
            )

    # ━━ L2-C: L1 내용 검증 ━━
    l1_line = _find_l_line(header, L1_RE)
    if l1_line:
        m = _L1L2_IMPL_DETAIL.search(l1_line)
        if m:
            violations.append(
                f"  {path.name} — L1에 L3 구현세부 혼입 (위계 위반)\n"
                f"  문제 단어: '{m.group()}'\n"
                f"  현재:   {l1_line.strip()}\n"
                f"  ✅ 올바른 L1:  음악→영상→확장→합성→YouTube end-to-end 파이프라인\n"
                f"  ✅ 올바른 L1:  파일 저장마다 L 레벨 선언의 존재성·위계 정합성 검증\n"
                f"  ❌ 잘못된 L1:  retry 3회 간격 10초 / .py 파일에서 / subprocess.run으로"
            )
        m2 = _TOOL_BINDING.search(l1_line)
        if m2:
            violations.append(
                f"  {path.name} — L1 탈도구 위반: 특정 도구/언어에 종속\n"
                f"  문제 단어: '{m2.group()}'\n"
                f"  현재:   {l1_line.strip()}\n"
                f"  ✅ 올바른 L1:  end-to-end 흐름만 기술 (도구·언어 언급 금지)\n"
                f"  ❌ 잘못된 L1:  FastAPI 라우터 경유 / asyncio로 / Edit tool로"
            )

    # ━━ L2-D: L2 헤더 내용 검증 ━━
    l2_line = _find_l_line(header, L2_RE)
    if l2_line:
        m = _L1L2_IMPL_DETAIL.search(l2_line)
        if m:
            violations.append(
                f"  {path.name} — 헤더 L2에 L3 구현세부 혼입 (위계 위반)\n"
                f"  문제 단어: '{m.group()}'\n"
                f"  현재:   {l2_line.strip()}\n"
                f"  ✅ 올바른 L2:  Gemini로 temporal_type/camera_motion 추출\n"
                f"  ✅ 올바른 L2:  YouTube 업로드용 제목/설명/태그 생성\n"
                f"  ❌ 잘못된 L2:  retry 제한 없이 API 호출 / subprocess.run으로 ffmpeg"
            )

    # ━━ L2-E: 헤더 이후 L0 오용 탐지 (언어·형식 무관, 위치 기반) ━━
    # 원칙: L0는 파일 선두 또는 파이프라인 실행자(_run_*, _auto_*) 맥락에만 허용
    # 탐지: 헤더 이후(21번째 줄~)에 L0: 가 나타나면 함수 내부 오용으로 판단
    # 예외: 근접 5줄 내에 파이프라인 실행자 함수명이 있으면 허용
    #
    # 예시:
    #   ✅ 허용:  _run_video_music_background() 내부  # L0: SNS 업로드 자동화
    #   ✅ 허용:  _auto_youtube_upload() 내부         # L0: SNS 업로드 자동화
    #   ❌ 차단:  _make_variation_clip() 내부          # L0: 타임아웃 10초 이내
    #   ❌ 차단:  merge_video_with_bgm() 내부          # L0: shortest로 음악에 맞춤
    body_l0_violations: list[str] = []
    for i, line in enumerate(lines[HEADER_LINES:], start=HEADER_LINES):
        if not L0_RE.search(line):
            continue
        ctx_start = max(0, i - 5)
        ctx_end   = min(len(lines), i + 2)
        context   = "\n".join(lines[ctx_start:ctx_end])
        if not _PIPELINE_FUNC.search(context):
            body_l0_violations.append(f"    :{i+1} {line.strip()}")

    if body_l0_violations:
        violations.append(
            f"  {path.name} — 헤더 이후 L0 오용 (탈존재 위반)\n"
            + "\n".join(body_l0_violations)
            + "\n"
            f"  ✅ 허용:  _run_*/  _auto_*/ _pipeline_* 함수 맥락 내\n"
            f"  ❌ 차단:  일반 헬퍼 함수 내부 L0, 상수 블록 L0 등"
        )

    # ━━ L2-F: 탈존재(detach) 위반 — 교체조건 없는 하드코딩 탐지 ━━
    # 매직넘버: def f(param: int = 8) 형태 — 함수 파라미터 기본값이 2자리 이상 숫자
    # 인접 줄에 물리적 근거 주석(#)이 없으면 위반
    detach_violations: list[str] = []
    for i, line in enumerate(lines):
        # 매직넘버 파라미터 탐지
        m = _MAGIC_PARAM_RE.search(line)
        if m:
            num = int(m.group(1))
            # 인접 3줄(전후)에 근거 주석이 있는지 확인
            ctx_start = max(0, i - 2)
            ctx_end   = min(len(lines), i + 3)
            ctx = "\n".join(lines[ctx_start:ctx_end])
            # "⚠" 또는 "# L3:" 또는 영문/한글 근거 주석이 있으면 통과
            has_basis = bool(re.search(r"#.*(?:⚠|L3:|물리|physical|derived|계산|ceil|max\s*\(|min\s*\()", ctx))
            if not has_basis:
                detach_violations.append(
                    f"    :{i+1} 매직넘버 파라미터 = {num} — 물리적 근거 주석 없음\n"
                    f"           {line.strip()}\n"
                    f"           ✅ 올바른 방식: 상수에서 계산 (예: ceil(remaining/CLIP_SEC))\n"
                    f"           ❌ 잘못된 방식: 고정값 = {num} (환경 바뀌면 부적절)"
                )
        # 하드코딩 확장자 리스트 탐지
        if _HARDCODED_EXTENSIONS_RE.search(line):
            detach_violations.append(
                f"    :{i+1} 하드코딩 확장자 리스트 — use-case 고정\n"
                f"           {line.strip()}\n"
                f"           ✅ 올바른 방식: 바이너리 여부(\\x00)로 텍스트 파일 탐지\n"
                f"           ❌ 잘못된 방식: [\".py\", \".ts\", ...] 특정 프로젝트 가정"
            )

    if detach_violations:
        violations.append(
            f"  {path.name} — 탈존재(ontology-detach) 위반\n"
            + "\n".join(detach_violations)
            + "\n"
            f"  원칙: 모든 binding에는 교체조건이 있어야 한다.\n"
            f"  교체조건 없는 고정 = 탈존재 위반 = 미래 버그의 씨앗"
        )

    # ━━ L2-G: 중복 진실(Duplicate Truth) — SSOT 위반 탐지 ━━
    violations.extend(check_duplicate_truth(content, path.name))

    return violations


def main() -> int:
    file_paths_env = os.environ.get("CLAUDE_FILE_PATHS", "")
    if not file_paths_env:
        return 0

    all_violations: list[str] = []
    for fp in file_paths_env.split(","):
        fp = fp.strip()
        if fp:
            all_violations.extend(check_file(fp))

    if not all_violations:
        return 0

    msg = (
        "\n══════════════════════════════════════════════\n"
        "❌ 피라미드 위계 위반 — 차단\n"
        "══════════════════════════════════════════════\n"
        + "\n\n".join(all_violations)
        + "\n\n"
        "피라미드 위계 원칙:\n"
        "  L0 = 비즈니스 최종 목적 (도구·언어·파일형식 무관, 파일 최상단 전용)\n"
        "  L1 = 시스템 흐름 목표 (end-to-end, 구현 세부 금지)\n"
        "  L2 = 독립 기능 단위 (기능 이름, retry횟수·timeout·파일형식 금지)\n"
        "  L3 = 구현 세부 (timeout, retry횟수, API명, 파일형식, 수치 등 OK)\n\n"
        "위계 법칙: 상위 레벨은 하위 레벨에 종속되지 않는다.\n"
        "══════════════════════════════════════════════"
    )
    print(msg, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
