"""
C:\\Users\\User\\.claude\\hooks\\semantic_judge_gate.py

# L0: 껍데기 L0 선언이 의미 판정 없이 거버넌스를 통과하는 구조적 구멍을 제거한다
# L1: Stop 훅에서 이 세션 Edit/Write에 기록된 L0 선언 줄을 추출해 독립 판정자(claude CLI)에게 의미 평가를 위임한다
# L2: 트랜스크립트 JSONL 파싱 → L0 줄 추출 → claude -p 호출 → JSON 응답 파싱 → FAIL 시 exit 2
# L3: judge_rubric.md가 판정 기준 SSOT; judge_state.json이 세션별 차단 횟수 기록 (데드루프 방지)

Stop 훅 동작 요약:
1. stdin에서 transcript_path, session_id 읽기
2. 트랜스크립트에서 Edit/Write tool_use의 content/new_string 안 "L0:" 포함 줄 추출 (최대 15줄, 중복 제거)
3. L0 줄 없으면 exit 0 (판정 비용 0)
4. judge_state.json 에서 이 세션 차단 횟수 확인; 2회 이상이면 exit 0 (데드루프 방지)
5. judge_rubric.md 전문 + L0 줄 목록을 프롬프트로 구성해 claude CLI 호출 (timeout 60초)
6. 응답 JSON 파싱 → FAIL 있으면 차단 횟수 기록 + exit 2 + stderr FAIL 사유 출력
7. 전부 PASS → exit 0
8. 어떤 예외든 최외각 try에서 exit 0 (fail-open)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ── 상수 ──────────────────────────────────────────────────────────────────────
HOOKS_DIR = Path(__file__).parent
RUBRIC_PATH = HOOKS_DIR / "judge_rubric.md"
STATE_PATH = HOOKS_DIR / "judge_state.json"

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
MAX_L0_LINES = 15
MAX_BLOCK_COUNT = 2          # 이 세션에서 이미 2회 차단했으면 루프 방지로 통과
JUDGE_TIMEOUT = 60           # claude CLI 호출 최대 대기 시간(초)
JUDGE_MODEL = "claude-haiku-4-5-20251001"

# "L0:" 또는 "# L0:" 로 시작하는 줄 탐지 (대소문자 구분 없음)
_L0_LINE_RE = re.compile(r"(?m)^[^\S\n]*(?:#\s*)?L0\s*:.*$", re.IGNORECASE)


# ── 상태 관리 ─────────────────────────────────────────────────────────────────

def _load_state() -> dict:
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(state: dict) -> None:
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _get_block_count(session_id: str) -> int:
    return _load_state().get(session_id, 0)


def _increment_block_count(session_id: str) -> int:
    state = _load_state()
    state[session_id] = state.get(session_id, 0) + 1
    _save_state(state)
    return state[session_id]


# ── 트랜스크립트 파싱 ─────────────────────────────────────────────────────────

def _still_in_file(line: str, file_path: str) -> bool:
    """판정 대상은 역사가 아니라 현재 상태 — 이미 재작성·삭제된 줄은 판정에서 제외.
    파일 확인 불가(삭제·이동·권한)면 보수적으로 False (존재하지 않는 진실은 채점하지 않는다)."""
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            return line in f.read()
    except Exception:
        return False


def _extract_l0_lines(transcript_path: str) -> list[str]:
    """Edit/Write/NotebookEdit tool_use의 content/new_string에서 L0 줄 추출.

    트랜스크립트는 역사다 — 같은 줄이 이후 재작성됐으면 과거 버전은 판정 대상이 아니다.
    각 줄을 그 파일의 현재 내용과 대조하여 '지금도 존재하는' 줄만 반환 (중복 제거, 최대 MAX_L0_LINES).
    """
    try:
        # utf-8-sig: BOM이 있는 파일(일부 Windows 툴 생성)도 처리
        with open(transcript_path, encoding="utf-8-sig") as f:
            raw_lines = f.readlines()
    except Exception:
        return []

    seen: set[str] = set()
    candidates: list[tuple[str, str]] = []  # (줄, 파일경로)

    for raw in raw_lines:
        try:
            entry = json.loads(raw)
        except Exception:
            continue

        msg = entry.get("message", {})
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            if block.get("name") not in EDIT_TOOLS:
                continue

            inp = block.get("input", {})
            fpath = inp.get("file_path", "") or inp.get("path", "")
            text = inp.get("content", "") + "\n" + inp.get("new_string", "")

            for match in _L0_LINE_RE.findall(text):
                normalized = match.strip()
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    candidates.append((normalized, fpath))

    results: list[str] = []
    for line, fpath in candidates:
        if fpath and _still_in_file(line, fpath):
            results.append(line)
            if len(results) >= MAX_L0_LINES:
                break
    return results


# ── 판정자 호출 ───────────────────────────────────────────────────────────────

def _build_prompt(rubric_text: str, l0_lines: list[str]) -> str:
    lines_block = "\n".join(f"  {i+1}. {line}" for i, line in enumerate(l0_lines))
    return (
        f"{rubric_text}\n\n"
        "---\n\n"
        "## 판정 대상 L0 선언 줄 목록\n\n"
        f"{lines_block}\n\n"
        "위 각 줄을 위의 판정 기준(조건 A, B, C 및 불합격 즉시 판정)에 따라 PASS 또는 FAIL로 판정하라.\n"
        "반드시 JSON 배열만 응답. 앞뒤 설명 텍스트 금지.\n"
        '형식: [{"line": "...", "verdict": "PASS" or "FAIL", "reason": "..."}]'
    )


def _find_claude_exe() -> str:
    """
    Windows에서 claude CLI 실행 파일 경로를 탐색한다.
    1. npm 전역 설치 경로의 claude.exe (Python subprocess는 .ps1을 실행 불가)
    2. PATH에서 claude.exe / claude
    3. 없으면 "claude" 반환 (FileNotFoundError → fail-open)
    """
    # npm 전역 설치 경로 탐색 (Windows 표준 위치)
    candidates = [
        Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "npm" / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    # fallback: PATH에서 claude.exe
    import shutil
    found = shutil.which("claude.exe") or shutil.which("claude")
    return found or "claude"


def _open_stdin_handle():
    """
    Windows 파이프 환경에서 claude.exe가 대화형 모드로 동작하도록
    CONIN$ (실제 콘솔 입력 핸들)을 stdin으로 반환.
    CONIN$ 열기 실패 시 subprocess.DEVNULL fallback.
    """
    try:
        return open("CONIN$", "rb")   # Windows 전용 콘솔 입력 핸들
    except OSError:
        return subprocess.DEVNULL


def _call_judge(prompt: str) -> list[dict] | None:
    """
    claude -p "<prompt>" --model <model> 호출.
    Windows 파이프 환경에서 claude.exe는 stdin이 실제 콘솔 핸들(CONIN$)이어야 응답한다.
    stdin=DEVNULL/PIPE+close 방식은 파이프 환경에서 60초 타임아웃 발생.
    성공 시 판정 결과 list[dict] 반환.
    실패(timeout, 부재, 파싱 오류) 시 None 반환.
    """
    claude_cmd = _find_claude_exe()
    stdin_handle = _open_stdin_handle()
    proc = None
    try:
        proc = subprocess.Popen(
            [claude_cmd, "-p", prompt, "--model", JUDGE_MODEL],
            stdin=stdin_handle,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # CONIN$ 핸들은 자식에게 상속 후 부모에서 닫음 (EOF 신호)
        if stdin_handle is not subprocess.DEVNULL:
            try:
                stdin_handle.close()
            except Exception:
                pass
        try:
            stdout_bytes, _ = proc.communicate(timeout=JUDGE_TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            return None
    except FileNotFoundError:
        return None
    except OSError:
        return None
    except Exception:
        return None

    try:
        raw_output = stdout_bytes.decode("utf-8", errors="replace").strip()
    except Exception:
        return None

    if not raw_output:
        return None

    # 코드펜스 제거
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_output)
    cleaned = cleaned.replace("```", "").strip()

    # JSON 배열 추출 시도
    array_match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if not array_match:
        return None

    try:
        parsed = json.loads(array_match.group(0))
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    return None


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> int:
    try:
        # sys.stdin은 텍스트 모드 — PowerShell 파이프가 BOM을 붙일 수 있으므로
        # 바이트로 읽어 BOM 제거 후 디코딩
        raw_bytes = sys.stdin.buffer.read()
        raw_str = raw_bytes.lstrip(b"\xef\xbb\xbf").decode("utf-8", errors="replace")
        payload = json.loads(raw_str)
    except Exception:
        return 0

    # stdin 파이프(fd 0)를 닫아 자식 프로세스(claude.exe)가 상속하지 않도록 함.
    # sys.stdin.close()는 Python 파일 객체만 닫고 기저 fd는 남을 수 있으므로
    # os.close(0)으로 실제 디스크립터를 닫는다.
    # claude.exe는 상속된 stdin 파이프가 남아 있으면 데이터를 기다려 타임아웃 발생.
    try:
        sys.stdin.close()
    except Exception:
        pass
    try:
        os.close(0)
    except Exception:
        pass

    transcript_path = payload.get("transcript_path", "")
    session_id = payload.get("session_id", "unknown")
    stop_hook_active = payload.get("stop_hook_active", False)

    # transcript 없으면 통과
    if not transcript_path or not Path(transcript_path).exists():
        return 0

    # L0 줄 추출
    l0_lines = _extract_l0_lines(transcript_path)
    if not l0_lines:
        # 판정 대상 없음 — 비용 0, 통과
        return 0

    # 루프 방지: 같은 세션에서 이미 2회 차단했으면 통과
    current_blocks = _get_block_count(session_id)
    if current_blocks >= MAX_BLOCK_COUNT:
        print(
            f"[semantic_judge_gate] 세션 {session_id[:16]}... 이미 {current_blocks}회 차단 — 루프 방지 통과",
            file=sys.stderr,
        )
        return 0

    # rubric 파일 읽기
    try:
        rubric_text = RUBRIC_PATH.read_text(encoding="utf-8")
    except Exception:
        print("[semantic_judge_gate] judge_rubric.md 읽기 실패 — 판정자 불가용 — 통과(fail-open)", file=sys.stderr)
        return 0

    # 판정자 호출
    prompt = _build_prompt(rubric_text, l0_lines)
    verdicts = _call_judge(prompt)

    if verdicts is None:
        print("[semantic_judge_gate] 판정자 불가용 — 통과(fail-open)", file=sys.stderr)
        return 0

    # FAIL 항목 수집
    fails = [v for v in verdicts if isinstance(v, dict) and v.get("verdict", "").upper() == "FAIL"]

    if not fails:
        return 0

    # 차단 횟수 기록
    new_count = _increment_block_count(session_id)

    # stderr에 FAIL 사유 출력
    lines_out = [
        "",
        "══════════════════════════════════════════════",
        "L0 의미 판정 게이트 — 차단",
        "══════════════════════════════════════════════",
        "다음 L0 선언이 의미 기준을 통과하지 못했습니다.",
        "",
    ]
    for item in fails:
        line_text = item.get("line", "(알 수 없음)")
        reason = item.get("reason", "(사유 없음)")
        lines_out.append(f"  FAIL: {line_text}")
        lines_out.append(f"  사유: {reason}")
        lines_out.append("")

    lines_out += [
        "재작성 지침:",
        "  L0는 '이것이 없으면 무엇이 실패하는가'에 답해야 합니다.",
        "  기술 수단·수치·도구명은 L0에 오면 안 됩니다.",
        "  구체적 예: 나쁜 → '타임아웃 10초 이내 완료'",
        "             좋은 → '고객이 견적을 사람 도움 없이 스스로 완성'",
        f"(이 세션 누적 차단: {new_count}회 / 최대 {MAX_BLOCK_COUNT}회 후 루프 방지 자동 통과)",
        "══════════════════════════════════════════════",
    ]

    print("\n".join(lines_out), file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
