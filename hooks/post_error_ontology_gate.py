"""
PreToolUse 훅 — is_error 후 ontology-learning 미발동 시 다음 도구 차단

L0: 실수 후 즉각 진화 없는 재시도는 반복 오류를 구조적으로 허용한다.
L1: Bash/PowerShell/Write/Edit 호출 전 — 직전 is_error가 있고
    그 후 Skill(ontology-learning)이 없으면 → 차단
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

LOOKBACK = 20


def _load_recent(transcript_path: str) -> list:
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    msgs = []
    for line in lines[-60:]:
        try:
            e = json.loads(line)
            msg = e.get("message", {})
            role = msg.get("role", "")
            content = msg.get("content", [])
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            if isinstance(content, list):
                msgs.append({"role": role, "content": content})
        except Exception:
            continue
    return msgs[-LOOKBACK:]


_ERROR_PATTERNS = (
    "Traceback (most recent call last)",
    "Error:",
    "Exception:",
    "OperationalError",
    "RuntimeError",
    "FileNotFoundError",
    "PermissionError",
    "CalledProcessError",
    "command not found",
    "No such file",
    # 훅 차단 메시지 서명 — 부분 성공으로 오분류 방지
    "══════",
    "차단",
    "hook error",
)

# ODD 훅 차단(exit 2) = 시스템이 정상 작동한 것. Claude 실수 아님.
# 훅 차단 메시지에 공통 구분선 "══════════════" 포함 → 이것으로 식별, cascade 방지
_HOOK_BLOCK_PATTERNS = (
    "══════════════",   # ODD hook common separator
    "hook error",       # Claude Code hook error message — hook fired = ODD working
    "PreToolUse:",      # Claude Code hook block prefix
    "PostToolUse:",     # Claude Code hook block prefix
)

# 인프라/네트워크 실패 패턴 — 코드 실수가 아님 (SSH 연결 불가, 네트워크 타임아웃 등)
# exit 255 = SSH 클라이언트가 원격 연결에 실패. 코드 판단 실수와 무관.
_INFRA_FAILURE_PATTERNS = (
    "Exit code 255",             # SSH client connection failure (all types)
    "Connection timed out",
    "Connection refused",
    "No route to host",
    "Network is unreachable",
    "ssh: connect to host",
    "Permission denied (publickey",  # SSH key 설정 문제 — 인프라 설정
    "Blocked:",                  # Claude Code 내부 tool guard — 코드 실수 아님
    # WebFetch SSL/TLS/인증서 오류 — 외부 서버 인증서 문제, 내 판단 실수 아님
    "unknown certificate verification error",
    "certificate verify failed",
    "SSL: CERTIFICATE_VERIFY_FAILED",
    "certificate has expired",
    "CERTIFICATE_VERIFY_FAILED",
    "ssl.SSLCertVerificationError",
    "unable to get local issuer certificate",
    "[SSL]",
)

# 유저 의지 패턴 — 오류의 발생 주체 3분류 중 "유저 의지"
# (내 판단 실수=학습 / 환경·인프라=재시도 / 유저 의지=순응·방향 전환)
# 거부·인터럽트는 실수가 아니라 라우팅 신호다. 학습 강제 대상 아님.
_USER_VOLITION_PATTERNS = (
    "The user doesn't want to proceed",
    "tool use was rejected",
    "Request interrupted by user",
    "The user doesn't want to take this action",
)

# 기계적/문법 오류 패턴 — shell quoting, bash syntax 등 판단 실수가 아님
# PowerShell→bash quoting 오류, `&;` 같은 bash 문법 오류,
# /tmp/ 임시 파일 SyntaxError (생성된 스크립트 quote strip으로 인한 오류) 포함
_MECHANICAL_ERROR_PATTERNS = (
    "syntax error near unexpected token",  # bash -c: PowerShell quoting 실패
    "bash: -c: line",                      # bash inline script 문법 오류
    "bash: syntax error",                  # bash 일반 문법 오류
    'File "/tmp/',                         # /tmp/ 임시 파일 Python SyntaxError — 전달과정 quote strip
    "File has not been read yet",          # Edit tool: Read 없이 Edit 시도 — 도구 시스템 제약, 판단 실수 아님
    "Read it first before writing",        # Edit tool: 동일 원인 대체 메시지 변형
    "CategoryInfo          : ParserError", # PowerShell 파서 오류 — PS 문법 실수, bash syntax error와 동급
    "FullyQualifiedErrorId : ExpectedValue", # PowerShell 파서 오류 변형
    "Sorry: IndentationError",  # py_compile 결과 — 편집-검증-수정 사이클 내 기계적 피드백
    "Sorry: SyntaxError",       # py_compile 결과 — 편집-검증-수정 사이클 내 기계적 피드백
    # write_existing_guard.py 차단 — 기존 파일 Write 사전방지 훅 = 설계 실수 아님
    "[BLOCKED] Write 차단",
    "기존 파일. Read tool로",
)


def _is_hook_block(block: dict) -> bool:
    """PreToolUse 훅이 차단한 is_error — 시스템 정상 작동이면 건너뜀.

    예외: ontology_violation_gate가 차단한 경우는 내 판단 실수임 → False 반환.
    post_error_ontology_gate의 cascade 차단만 skip.
    """
    content = block.get("content", "")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    else:
        text = ""
    # violation_gate가 규칙 위반으로 차단(block_message 포함, "══════" 있음) → 내 판단 실수 → False
    # violation_gate가 crash("No stderr output", "══════" 없음) → 인프라 실패 → True (skip)
    if "ontology_violation_gate" in text and "══════" in text:
        return False
    return any(pat in text for pat in _HOOK_BLOCK_PATTERNS)


def _is_mechanical_error(block: dict) -> bool:
    """bash 문법/quoting 오류 — 판단 실수가 아님, 건너뜀."""
    content = block.get("content", "")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    else:
        text = ""
    return any(pat in text for pat in _MECHANICAL_ERROR_PATTERNS)


def _is_user_volition(block: dict) -> bool:
    """유저의 거부·인터럽트 — 실수가 아니라 유저의 방향 결정. 건너뜀."""
    content = block.get("content", "")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    else:
        text = ""
    return any(pat in text for pat in _USER_VOLITION_PATTERNS)


def _is_infra_failure(block: dict) -> bool:
    """인프라/네트워크 실패 — 코드 실수가 아님, 건너뜀.

    SSH exit 255, 연결 타임아웃 등은 Claude의 판단 실수가 아니라
    외부 인프라 상태 문제다. ontology-learning 트리거 불필요.
    """
    content = block.get("content", "")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    else:
        text = ""
    return any(pat in text for pat in _INFRA_FAILURE_PATTERNS)


def _is_empty_no_match(block: dict) -> bool:
    """빈 출력 exit = grep/pgrep/pkill no-match — 코드 실수 아님.

    grep exit 1 = no match (정상)
    pgrep exit 1 = no process found (정상)
    pkill exit 1 = no process killed (정상)
    출력이 없으면 학습할 에러 메시지도 없음 → 게이트 차단 무의미.

    Bash tool은 exit code 만 있는 명령 실패에 "Exit code N" 텍스트를 추가함.
    "Exit code N" 단일 라인 = 프로그램 출력 없고 종료코드만 → 검색 결과 없음 등 정상.
    """
    content = block.get("content", "")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    else:
        text = ""
    stripped = text.strip()
    # 에러 패턴 있으면 무조건 False
    if any(pat in text for pat in _ERROR_PATTERNS):
        return False
    # 완전히 비어있음 → no-match 정상
    if not stripped:
        return True
    # "Exit code N" 단일 라인 = 실제 프로그램 출력 없음 + 종료코드 주석만 → 정상
    if re.fullmatch(r'exit\s+code\s+\d+', stripped, re.IGNORECASE):
        return True
    return False


def _is_partial_success(block: dict) -> bool:
    """출력이 있는 exit 1은 부분 성공 — 단, Python 예외/에러 패턴이 없어야 함."""
    content = block.get("content", "")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = " ".join(
            c.get("text", "") for c in content if isinstance(c, dict)
        )
    else:
        text = ""
    stripped = text.strip()
    # 오류 패턴이 포함된 출력은 부분 성공 아님 (Traceback, Error: 등)
    if any(pat in stripped for pat in _ERROR_PATTERNS):
        return False
    # 실질적 출력이 있으면 (파일 목록, 경로 등) 부분 성공으로 간주
    return len(stripped) > 80 and "\n" in text


def _last_error_idx(msgs: list) -> int:
    for i in range(len(msgs) - 1, -1, -1):
        if msgs[i]["role"] != "user":
            continue
        for block in msgs[i]["content"]:
            if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("is_error"):
                if _is_hook_block(block):
                    continue  # 훅이 차단한 것 = 실수 아님, 건너뜀
                if _is_user_volition(block):
                    continue  # 유저 거부·인터럽트 = 방향 결정, 실수 아님, 건너뜀
                if _is_infra_failure(block):
                    continue  # 인프라/네트워크 실패 = 코드 실수 아님, 건너뜀
                if _is_mechanical_error(block):
                    continue  # bash/shell 문법 오류 = 판단 실수 아님, 건너뜀
                if _is_empty_no_match(block):
                    continue  # 빈 출력 exit = grep/pgrep no-match = 정상
                if _is_partial_success(block):
                    continue  # 출력 있는 exit 1 = 부분 성공, 에러 아님
                return i
    return -1


def _has_ontology_learning_after(msgs: list, after_idx: int) -> bool:
    for msg in msgs[after_idx:]:
        if msg["role"] != "assistant":
            continue
        for block in msg["content"]:
            if (isinstance(block, dict)
                    and block.get("type") == "tool_use"
                    and block.get("name") == "Skill"):
                skill = block.get("input", {}).get("skill", "")
                if "ontology" in skill.lower() and "learn" in skill.lower():
                    return True
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    # Skill(ontology-learning) 호출 자체는 통과 — "learn"까지 확인하여 ontology-detach 오통과 방지
    tool_name = payload.get("tool_name", "")
    if tool_name == "Skill":
        inp = payload.get("tool_input", {})
        skill_name = inp.get("skill", "").lower()
        if "ontology" in skill_name and "learn" in skill_name:
            return 0

    transcript_path = payload.get("transcript_path", "")
    if not transcript_path or not Path(transcript_path).exists():
        return 0

    msgs = _load_recent(transcript_path)
    err_idx = _last_error_idx(msgs)
    if err_idx < 0:
        return 0

    if _has_ontology_learning_after(msgs, err_idx):
        return 0

    msg = (
        "\n══════════════════════════════════════════════\n"
        "❌ PreToolUse 차단 — is_error 후 ontology-learning 미발동\n"
        "══════════════════════════════════════════════\n"
        "직전 도구 실행이 is_error:true 였습니다.\n"
        "다른 도구를 호출하기 전에 반드시:\n"
        "  Skill(ontology-learning) 먼저 발동\n"
        "══════════════════════════════════════════════"
    )
    print(msg, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
