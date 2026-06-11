# L0: 에이전트 위계가 목적 분해 없이 실행되는 것을 구조적으로 차단
# L1: Agent 호출 시 직책별(Leader/Manager/Worker) 필수 구조 요소 존재 검증 + 디스패치 기록

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone


def extract_role(prompt: str) -> str | None:
    """직책 값을 추출. '직책: Leader' 형식만 인식."""
    for line in prompt.splitlines():
        stripped = line.strip()
        if stripped.startswith("직책"):
            # '직책:' 또는 '직책 :' 이후 값 추출
            colon_idx = stripped.find(":")
            if colon_idx == -1:
                continue
            value = stripped[colon_idx + 1:].strip()
            if value:
                return value
    return None


def extract_l0_line(prompt: str) -> str:
    """프롬프트에서 'L0:' 줄 첫 120자 추출."""
    for line in prompt.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("L0:") or stripped.upper().startswith("L0："):
            return stripped[:120]
    return ""


def record_dispatch(role: str, cwd: str, prompt: str, has_subgoals: bool, has_acceptance: bool) -> None:
    """goal_registry.json에 디스패치 기록 append-merge (atomic write)."""
    registry_path = os.path.join(os.path.dirname(__file__), "goal_registry.json")
    try:
        if os.path.exists(registry_path):
            with open(registry_path, encoding="utf-8") as f:
                registry = json.load(f)
        else:
            registry = {}

        key = datetime.now(tz=timezone.utc).isoformat()
        project = os.path.basename(cwd) if cwd else ""
        registry[key] = {
            "role": role,
            "project": project,
            "l0_line": extract_l0_line(prompt),
            "has_subgoals": has_subgoals,
            "has_acceptance": has_acceptance,
        }

        # atomic write: tempfile + os.replace
        dir_name = os.path.dirname(registry_path)
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, registry_path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    except Exception:
        pass  # 기록 실패는 무시 — 게이트 본 기능 우선


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

    role = extract_role(prompt)
    if role is None:
        # 직책 표기 없음 → agent_pyramid_gate 소관, 중복 차단 금지
        return 0

    role_lower = role.lower()

    # ── Leader / Manager: 서브골 분해 요건 ──
    if role_lower in ("leader", "manager"):
        has_subgoals = ("서브골" in prompt) or ("분해" in prompt)
        has_acceptance = "수용 기준" in prompt

        if not has_subgoals or not has_acceptance:
            missing = []
            if not has_subgoals:
                missing.append('"서브골" 또는 "분해" — 하위 에이전트에게 전달할 서브골 분해 명세')
            if not has_acceptance:
                missing.append('"수용 기준" — 각 서브골의 완료 판단 기준')

            lines = [
                "",
                "══════════════════════════════════════════════",
                f"❌ 목적 분해 게이트 차단 — 직책: {role}",
                "══════════════════════════════════════════════",
                "Leader/Manager는 서브골 분해 명세가 필요합니다.",
                "",
                "누락 항목:",
            ]
            for item in missing:
                lines.append(f"  • {item}")
            lines += [
                "",
                "프롬프트에 다음 형식을 추가하세요:",
                "  서브골 분해:",
                "    - 서브골 1: [구체적 작업]",
                "    - 서브골 2: [구체적 작업]",
                "  수용 기준:",
                "    - [서브골 1 완료 조건]",
                "    - [서브골 2 완료 조건]",
                "══════════════════════════════════════════════",
            ]
            print("\n".join(lines), file=sys.stderr)
            return 2

        # 통과 → 기록
        cwd = data.get("cwd", "")
        record_dispatch(role, cwd, prompt, has_subgoals=True, has_acceptance=True)
        return 0

    # ── Worker: 수용 기준 + 예산 요건 ──
    if role_lower == "worker":
        has_acceptance = "수용 기준" in prompt
        has_budget = "예산" in prompt

        if not has_acceptance or not has_budget:
            missing = []
            if not has_acceptance:
                missing.append('"수용 기준" — 이 Worker 작업의 완료 판단 기준')
            if not has_budget:
                missing.append('"예산" — 컨텍스트/API 호출 상한 (예: "예산: 도구 호출 10회 이내")')

            lines = [
                "",
                "══════════════════════════════════════════════",
                "❌ 목적 분해 게이트 차단 — 직책: Worker",
                "══════════════════════════════════════════════",
                "Worker는 수용 기준과 예산이 필요합니다.",
                "",
                "누락 항목:",
            ]
            for item in missing:
                lines.append(f"  • {item}")
            lines += [
                "",
                "프롬프트에 다음 형식을 추가하세요:",
                "  수용 기준:",
                "    - [작업 완료를 증명하는 조건 1]",
                "    - [작업 완료를 증명하는 조건 2]",
                "  예산: 도구 호출 N회 이내",
                "══════════════════════════════════════════════",
            ]
            print("\n".join(lines), file=sys.stderr)
            return 2

        # 통과 → 기록
        cwd = data.get("cwd", "")
        record_dispatch(role, cwd, prompt, has_subgoals=False, has_acceptance=True)
        return 0

    # 알 수 없는 직책 → 통과 (gate는 알려진 케이스만 검사)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"goal_decompose_gate 크래시: {e}", file=sys.stderr)
        sys.exit(0)
