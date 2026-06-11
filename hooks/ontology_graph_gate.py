"""
PreToolUse 훅 — 의미 기반 온톨로지 그래프 게이트

L0: raw 파일 파싱 없이 semantic 지식 그래프를 쿼리해 L0 판단
L1: ontology_graph.json에서 파일 의미 컨텍스트 조회 → semantic rule 적용
L2: fnmatch로 파일 패턴 매칭 → 의미 노드 찾기 → rule 평가
L3: Python fnmatch + json 로드 → exit 2 (차단)

━━ 핵심 설계 원칙 ━━
이 훅은 파일 내용을 직접 파싱해 키워드를 찾지 않는다.
ontology_graph.json의 semantic context를 쿼리해 판단한다.
새 케이스 → graph 업데이트. 이 코드 수정 최소화.
"""
from __future__ import annotations

import json
import os
import re
import sys
from fnmatch import fnmatch
from pathlib import Path

GRAPH_PATH = Path(__file__).parent / "ontology_graph.json"


def load_graph() -> dict:
    try:
        return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def match_file_node(graph: dict, file_path: str) -> dict | None:
    """파일 경로에 맞는 첫 번째 semantic 노드 반환."""
    norm_path = file_path.replace("\\", "/")
    patterns = graph.get("file_semantics", {}).get("patterns", [])
    for node in patterns:
        pattern = node.get("path_pattern", "")
        # Simple name match or full path match
        filename = Path(norm_path).name
        if fnmatch(norm_path, f"*{pattern}*") or fnmatch(filename, pattern) or fnmatch(norm_path, pattern):
            return node
        # Handle ** glob manually
        if "**" in pattern:
            parts = pattern.split("**/")
            if len(parts) == 2:
                prefix, suffix = parts[0], parts[1]
                if (not prefix or norm_path.startswith(prefix)) and fnmatch(filename, suffix):
                    return node
    return None


def check_internal_terminology(content: str, graph: dict) -> list[str]:
    """내부 기호 목록과 콘텐츠 대조. 발견된 기호 목록 반환."""
    terms = graph.get("domain_knowledge", {}).get("internal_terminology", {}).get("terms", [])
    found = []
    for term in terms:
        if re.search(term, content):
            clean = re.sub(r"\\[sb]|\\b", "", term).strip()
            found.append(clean)
    return found


def _find_index_root(file_path: str) -> Path | None:
    """파일에서 상위로 올라가며 .odd/ontology_index.json 보유 프로젝트 루트 탐색 (최대 8단계)."""
    try:
        p = Path(file_path).resolve().parent
    except Exception:
        return None
    for _ in range(8):
        if (p / ".odd" / "ontology_index.json").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return None


def _closure_check(file_path: str, transcript_path: str):
    """L0 폐쇄 강제: 다중 파일 목적 그룹의 일원을 수정하기 전,
    이 세션에서 ontology_grep으로 그 그룹을 한 번은 나열했어야 한다.

    L0: 목적 그룹의 일원만 수정되고 나머지가 방치되면 시스템이 모순 상태로 남는다
        — 전수 확인 없는 부분 수정이 구조 오염의 직접 원인.
    인덱스 없는 프로젝트는 통과 — 라벨 생산은 pyramid_guard가, 인덱스는 ontology_grep이 만든다.
    """
    root = _find_index_root(file_path)
    if root is None:
        return None
    try:
        idx = json.loads((root / ".odd" / "ontology_index.json").read_text(encoding="utf-8"))
    except Exception:
        return None
    try:
        rel = os.path.relpath(str(Path(file_path).resolve()), str(root)).replace("\\", "/")
    except Exception:
        return None
    info = idx.get("files", {}).get(rel)
    if not info:
        return None
    purposes = [n.get("purpose", "") for n in info.get("nodes", []) if n.get("level", "").startswith("L0")]
    shared = None
    for purpose in purposes:
        count = sum(
            1
            for other in idx.get("files", {}).values()
            for n in other.get("nodes", [])
            if n.get("purpose") == purpose
        )
        if count >= 2:
            shared = (purpose, count)
            break
    if not shared:
        return None
    # 세션 내 폐쇄 질의 실행 증거 (transcript에 ontology_grep 호출 흔적)
    if transcript_path and Path(transcript_path).exists():
        try:
            if "ontology_grep" in Path(transcript_path).read_text(encoding="utf-8", errors="ignore"):
                return None
        except Exception:
            return None
    return (shared[0], shared[1], str(root))


def main() -> int:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Edit", "Write", "NotebookEdit"):
        return 0

    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    if not file_path:
        return 0

    issues = []

    # ━━ L0 폐쇄 미확인 수정 차단 ━━
    cv = _closure_check(file_path, data.get("transcript_path", ""))
    if cv:
        purpose, count, idx_root = cv
        safe_kw = purpose.replace('"', "")[:30]
        issues.append({
            "seed": "ssot_single_truth",
            "message": (
                f"목적 그룹 폐쇄 미확인 수정\n\n"
                f"파일: {Path(file_path).name}\n"
                f"이 파일의 L0 '{purpose[:60]}'를 공유하는 파일이 {count}개입니다.\n"
                f"이 세션에서 종속 폐쇄를 나열한 적이 없습니다.\n\n"
                f"변경 범위는 지시문이 아니라 의존 그래프가 결정합니다. 먼저 실행:\n"
                f"  python C:/Users/User/.claude/hooks/ontology_grep.py \"{safe_kw}\" --root \"{idx_root}\"\n\n"
                f"→ 폐쇄 목록 전체를 확인·재판정한 후 수정을 재시도하면 이 게이트는 통과됩니다."
            )
        })

    graph = load_graph()
    node = match_file_node(graph, file_path)

    if not node and not issues:
        return 0  # 의미 컨텍스트 없음 → 다른 훅에 위임
    if not node:
        node = {}

    seed = node.get("seeds", [])
    write_check = node.get("write_check", "")
    modifiable = node.get("modifiable", True)

    # ━━ 불변 파일 쓰기 차단 ━━
    if modifiable is False:
        issues.append({
            "seed": "judge_independence",
            "message": (
                f"사용자 확정 기준 파일 수정 시도\n\n"
                f"파일: {Path(file_path).name}\n"
                f"이 파일은 사용자가 고정한 불변 기준입니다.\n\n"
                f"✅ 허용: Read (기준 확인·준수)\n"
                f"❌ 금지: Write, Edit\n\n"
                f"변경 필요 시: 유저에게 요청 → 명시 승인 후에만 가능"
            )
        })

    # ━━ 외부 파일 내부 기호 탐지 ━━
    elif write_check in ("no_internal_terminology", "no_internal_terminology_in_display_strings"):
        if content:
            found = check_internal_terminology(content, graph)
            if found:
                terms_str = ", ".join(f"'{t}'" for t in found[:3])
                issues.append({
                    "seed": "reader_context",
                    "message": (
                        f"외부 파일에 내부 기호 발견\n\n"
                        f"파일: {Path(file_path).name} (audience: external)\n"
                        f"발견된 내부 기호: {terms_str}\n\n"
                        f"외부 방문자는 이 기호체계를 알지 못합니다.\n\n"
                        f"번역 기준 (ontology_graph.json domain_knowledge 참조):\n"
                        f"  L0~L3 → '목적 기반 설계'\n"
                        f"  피라미드 위계 → '목적 기반 설계 방법론'\n"
                        f"  SSOT → '단일 원본 소스'"
                    )
                })

    if not issues:
        return 0

    lines = [
        "",
        "══════════════════════════════════════════════",
        "❌ 온톨로지 그래프 게이트 — 차단",
        "══════════════════════════════════════════════",
    ]
    for issue in issues:
        lines.append(f"[씨앗: {issue['seed']}]")
        lines.extend(f"  {line}" for line in issue["message"].splitlines())
        lines.append("")
    lines.append("══════════════════════════════════════════════")

    print("\n".join(lines), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
