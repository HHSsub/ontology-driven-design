"""
# L0: 프로젝트별 ODD 정책을 로드하여 훅 동작을 조정 — false-positive로 인한 사용자 이탈 방지
# L1: .odd/config.yaml 탐색 → severity 반환 → 훅 행동 분기
# L2: CLAUDE_PROJECT_DIR 우선 탐색, 없으면 hook 파일 상위 상위 디렉토리에서 .odd/ 탐색
# L3: PyYAML 없으면 기본값(block) 반환 (의존성 최소화)

Per-project ODD configuration loader.

사용법:
    from config_loader import load_project_config

    cfg = load_project_config("tdd_enforce_stop")
    severity = cfg["severity"]   # "block" | "warn" | "off"
    allowlist_paths = cfg["allowlist_paths"]  # list[str]

설정 파일 위치: <project_root>/.odd/config.yaml
탐색 순서:
  1. CLAUDE_PROJECT_DIR 환경변수 → {CLAUDE_PROJECT_DIR}/.odd/config.yaml
  2. 이 파일(config_loader.py)의 상위 상위 디렉토리 → .odd/config.yaml
  3. 현재 작업 디렉토리(cwd) → .odd/config.yaml

config.yaml 스키마:
    version: 1
    hooks:
      <hook_name>: block | warn | off
    allowlist:
      paths:
        - "tests/**"
        - ".odd/**"

기본값: severity = "block", allowlist_paths = []
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any


# ─── 기본값 ──────────────────────────────────────────────────────────────────
DEFAULT_SEVERITY = "block"
VALID_SEVERITIES = {"block", "warn", "off"}


def _find_config_file() -> Path | None:
    """
    .odd/config.yaml 파일을 탐색 순서에 따라 찾는다.
    탐색 순서:
      1. CLAUDE_PROJECT_DIR 환경변수
      2. config_loader.py 파일의 상위 상위 디렉토리 (hooks/ → 프로젝트 루트)
      3. 현재 작업 디렉토리(cwd)
    """
    candidates: list[Path] = []

    # 1. CLAUDE_PROJECT_DIR
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        candidates.append(Path(project_dir) / ".odd" / "config.yaml")

    # 2. config_loader.py 위치 기준 (hooks/ → 프로젝트 루트)
    this_file = Path(__file__).resolve()
    # hooks/config_loader.py → hooks/ → project_root/
    hooks_dir = this_file.parent
    project_root = hooks_dir.parent
    candidates.append(project_root / ".odd" / "config.yaml")

    # 3. cwd
    cwd_config = Path.cwd() / ".odd" / "config.yaml"
    if cwd_config not in candidates:
        candidates.append(cwd_config)

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return None


def _parse_yaml_simple(text: str) -> dict[str, Any]:
    """
    PyYAML 없을 때 사용하는 최소 YAML 파서.
    지원 형식:
      - 최상위 key: value (문자열)
      - 들여쓰기 2칸 key: value (문자열)
      - 들여쓰기 4칸 - item (리스트 항목)
    """
    result: dict[str, Any] = {}
    current_top: str | None = None
    current_sub: str | None = None

    for raw_line in text.splitlines():
        # 주석·빈 줄 스킵
        stripped = raw_line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if stripped.startswith("- "):
            # 리스트 항목
            item = stripped[2:].strip().strip('"').strip("'")
            if current_top and current_sub:
                lst = result.setdefault(current_top, {}).setdefault(current_sub, [])
                lst.append(item)
            continue

        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")

            if indent == 0:
                current_top = key
                current_sub = None
                if val:
                    result[key] = val
                else:
                    result.setdefault(key, {})
            elif indent == 2:
                current_sub = key
                if val and current_top:
                    result.setdefault(current_top, {})[key] = val
                elif current_top:
                    result.setdefault(current_top, {}).setdefault(key, [])
            # indent >= 4 는 리스트 항목으로 처리하지 않음(위에서 처리)

    return result


def _load_yaml(config_path: Path) -> dict[str, Any]:
    """config.yaml을 읽어 dict 반환. 실패 시 빈 dict."""
    try:
        text = config_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    # PyYAML 우선 사용
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except ImportError:
        pass
    except Exception:
        return {}

    # fallback: 단순 파서
    try:
        return _parse_yaml_simple(text)
    except Exception:
        return {}


def load_project_config(hook_name: str) -> dict[str, Any]:
    """
    훅 이름을 받아 severity("block"|"warn"|"off")와 allowlist_paths(list[str])를 반환한다.

    반환 형식:
        {
            "severity": "block" | "warn" | "off",
            "allowlist_paths": ["tests/**", ...],
            "config_found": True | False,   # config.yaml 발견 여부
        }

    config.yaml이 없거나 해당 hook 설정이 없으면 기본값(block) 반환.
    """
    config_path = _find_config_file()

    if config_path is None:
        return {
            "severity": DEFAULT_SEVERITY,
            "allowlist_paths": [],
            "config_found": False,
        }

    data = _load_yaml(config_path)

    # hooks 섹션에서 severity 추출
    # 주의: YAML 1.1에서 'off'/'on'/'yes'/'no'는 boolean으로 파싱됨.
    # False → "off", True → "on" 으로 문자열 변환 후 처리.
    hooks_section = data.get("hooks", {})
    raw_severity = DEFAULT_SEVERITY
    if isinstance(hooks_section, dict):
        raw_val = hooks_section.get(hook_name, DEFAULT_SEVERITY)
        # YAML boolean → 문자열 정규화
        if raw_val is False:
            raw_severity = "off"
        elif raw_val is True:
            raw_severity = "block"
        else:
            raw_severity = str(raw_val) if raw_val is not None else DEFAULT_SEVERITY
    if raw_severity not in VALID_SEVERITIES:
        raw_severity = DEFAULT_SEVERITY

    # allowlist.paths 추출
    allowlist_section = data.get("allowlist", {})
    allowlist_paths: list[str] = []
    if isinstance(allowlist_section, dict):
        paths = allowlist_section.get("paths", [])
        if isinstance(paths, list):
            allowlist_paths = [str(p) for p in paths]

    return {
        "severity": raw_severity,
        "allowlist_paths": allowlist_paths,
        "config_found": True,
    }


def get_exit_code(hook_name: str, default_exit: int = 2) -> int:
    """
    severity에 따라 exit code를 반환한다.
      - "block" → default_exit (보통 2)
      - "warn"  → 0 (경고 출력, 차단하지 않음)
      - "off"   → 0 (완전 비활성화)

    훅에서 위반 감지 후 이 함수를 호출해 exit code를 결정한다.
    """
    cfg = load_project_config(hook_name)
    severity = cfg["severity"]
    if severity == "block":
        return default_exit
    # warn 또는 off → 차단하지 않음
    return 0


def is_path_allowlisted(file_path: str, hook_name: str) -> bool:
    """
    파일 경로가 allowlist.paths 패턴에 매칭되면 True 반환.
    패턴은 fnmatch 스타일 (** 지원).
    """
    cfg = load_project_config(hook_name)
    allowlist = cfg["allowlist_paths"]
    if not allowlist:
        return False

    import fnmatch
    normalized = file_path.replace("\\", "/")
    for pattern in allowlist:
        pattern = pattern.replace("\\", "/")
        if fnmatch.fnmatch(normalized, pattern):
            return True
        # ** 패턴: 경로 중간 매칭도 시도
        if "**" in pattern:
            # tests/** → 경로에 tests/ 포함되면 통과
            prefix = pattern.split("**")[0].rstrip("/")
            if prefix and f"/{prefix}/" in f"/{normalized}/":
                return True
    return False
