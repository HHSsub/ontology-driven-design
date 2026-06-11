# L0: L0 변경의 영향 범위는 텍스트 검색이 아니라 그래프 질의로 결정된다.
#     "지시문에 언급된 항목" ≠ 변경 범위. 변경 범위 = 그 목적에 종속된 노드의 폐쇄(closure).
# 사용법:
#   python ontology_grep.py "<목적 키워드>" [--root 프로젝트경로] [--reindex]
#   python ontology_grep.py --list [--root 프로젝트경로]   ← 목적 노드 전체 나열
# 인덱스: <root>/.odd/ontology_index.json (소스 mtime 기반 자동 재구축)
import argparse
import fnmatch
import json
import os
import re
import sys
import time

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build",
             ".next", ".odd", "coverage", ".turbo", "out"}
TEXT_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".json", ".html", ".css",
             ".yaml", ".yml", ".ps1", ".sh", ".sql", ".toml", ".vue", ".svelte"}
HEAD_LINES = 40          # 파일 상단 주석 블록만 스캔 (L 주석은 헤더 관례)
MAX_SIZE = 2 * 1024 * 1024

# 주석 접두(#, //, <!--, /*, ;, --, ## 마크다운 헤딩) 뒤 L0~L3 선언
ANNOT_RE = re.compile(
    r"^\s*(?:#{1,6}|//+|<!--|/\*+|;+|--+|\*+)?\s*"
    r"(L[0-3])(\.\d+)?\s*[:：]\s*(.+?)\s*(?:-->|\*/)?\s*$"
)


def _iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            if os.path.splitext(fn)[1].lower() in TEXT_EXTS:
                try:
                    if os.path.getsize(p) <= MAX_SIZE:
                        yield p
                except OSError:
                    pass


def _scan_file(path):
    """파일 상단에서 L0~L3 선언 추출. ONTOLOGY.md는 전체 스캔(폴더 위계 문서)."""
    nodes = []
    is_topology = os.path.basename(path).upper().startswith("ONTOLOGY")
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if not is_topology and i >= HEAD_LINES:
                    break
                m = ANNOT_RE.match(line)
                if m:
                    level, depth, purpose = m.group(1), m.group(2) or "", m.group(3)
                    if len(purpose) >= 3:
                        nodes.append({"level": level + depth, "purpose": purpose, "line": i + 1})
    except OSError:
        pass
    return nodes


def build_index(root):
    """인덱스 구조:
    files: {상대경로: {"mtime": f, "nodes": [...]}}
    folder_l0: {폴더상대경로: ONTOLOGY.md가 선언한 L0 목적}  ← 폴더 하위 파일은 이를 상속
    """
    index = {"built_at": time.time(), "root": root, "files": {}, "folder_l0": {}}
    for p in _iter_files(root):
        rel = os.path.relpath(p, root).replace("\\", "/")
        nodes = _scan_file(p)
        if nodes:
            index["files"][rel] = {"mtime": os.path.getmtime(p), "nodes": nodes}
            if os.path.basename(p).upper().startswith("ONTOLOGY"):
                folder = os.path.dirname(rel)
                l0s = [n["purpose"] for n in nodes if n["level"].startswith("L0")]
                if l0s:
                    index["folder_l0"][folder] = l0s
    return index


def load_or_build(root, reindex=False):
    idx_path = os.path.join(root, ".odd", "ontology_index.json")
    if not reindex and os.path.exists(idx_path):
        try:
            with open(idx_path, encoding="utf-8") as f:
                idx = json.load(f)
            # 인덱싱된 파일 중 하나라도 mtime이 바뀌었으면 재구축
            stale = any(
                not os.path.exists(os.path.join(root, rel))
                or os.path.getmtime(os.path.join(root, rel)) > info.get("mtime", 0)
                for rel, info in idx.get("files", {}).items()
            )
            if not stale:
                return idx
        except Exception:
            pass
    idx = build_index(root)
    try:
        os.makedirs(os.path.join(root, ".odd"), exist_ok=True)
        with open(idx_path, "w", encoding="utf-8") as f:
            json.dump(idx, f, ensure_ascii=False, indent=1)
    except OSError:
        pass
    return idx


def closure(index, query):
    """목적 키워드 → 종속 폐쇄. 반환: {파일: [매칭 근거]}"""
    q = query.lower()
    hits = {}
    matched_purposes = set()
    for rel, info in index["files"].items():
        for n in info["nodes"]:
            if q in n["purpose"].lower():
                hits.setdefault(rel, []).append(f"{n['level']} 직접선언 (line {n['line']}): {n['purpose']}")
                matched_purposes.add(n["purpose"])
    # 폴더 상속: 매칭된 L0를 선언한 ONTOLOGY.md 폴더 하위의 모든 인덱스 파일
    for folder, l0s in index.get("folder_l0", {}).items():
        if any(q in p.lower() for p in l0s):
            prefix = folder + "/" if folder else ""
            for rel in index["files"]:
                if rel.startswith(prefix) and rel not in hits:
                    hits.setdefault(rel, []).append(f"폴더 상속 ← {folder or '.'}/ONTOLOGY.md")
    return hits, matched_purposes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", help="목적 키워드 (L0/L1 텍스트 부분일치)")
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--reindex", action="store_true")
    ap.add_argument("--list", action="store_true", help="목적 노드 전체 나열")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    idx = load_or_build(root, args.reindex)

    if args.list or not args.query:
        purposes = {}
        for rel, info in idx["files"].items():
            for n in info["nodes"]:
                purposes.setdefault(n["level"].split(".")[0], set()).add(n["purpose"])
        for level in sorted(purposes):
            print(f"\n[{level}] ({len(purposes[level])}개 목적 노드)")
            for p in sorted(purposes[level]):
                print(f"  - {p}")
        print(f"\n인덱스: {len(idx['files'])}개 파일, 폴더 L0 {len(idx.get('folder_l0', {}))}개")
        return 0

    hits, purposes = closure(idx, args.query)
    print(f"질의: \"{args.query}\"  (root: {root})")
    print(f"매칭 목적 노드: {len(purposes)}개")
    for p in sorted(purposes):
        print(f"  ◆ {p}")
    print(f"\n종속 폐쇄 — 변경 범위 {len(hits)}개 파일:")
    for rel in sorted(hits):
        print(f"  {rel}")
        for reason in hits[rel]:
            print(f"      └ {reason}")
    if hits:
        print(f"\n→ 이 {len(hits)}개가 변경 범위다. 지시문에 언급된 항목만 수정하는 것 = scope 위반.")
        return 0

    # ━━ 자가 치유 폴백: 라벨 부재/키워드 불일치여도 데드엔드 금지 ━━
    # 원시 텍스트 스캔으로 후보 폐쇄를 제시하고, 정식 그래프 구축 경로를 지시한다.
    q = args.query.lower()
    labeled = len(idx["files"])
    print(f"\n→ L0 주석 매칭 없음 (인덱싱된 라벨 파일: {labeled}개) — 텍스트 폴백 스캔 시작:")
    cands = []
    for p in _iter_files(root):
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                if q in f.read().lower():
                    cands.append(os.path.relpath(p, root).replace("\\", "/"))
                    if len(cands) >= 50:
                        break
        except OSError:
            pass
    if cands:
        print(f"  키워드 본문 포함 파일 {len(cands)}개{' (50개 상한)' if len(cands) >= 50 else ''}:")
        for rel in sorted(cands):
            print(f"    {rel}")
        print("\n  ⚠ 이것은 후보일 뿐 정식 폐쇄가 아니다 — 텍스트 일치 ≠ 목적 종속.")
    else:
        print("  본문에도 키워드 없음 — 키워드를 바꾸거나 --list로 목적 노드를 먼저 확인하라.")
    if labeled == 0:
        print("\n  이 프로젝트는 L0 라벨이 0개다. 정식 그래프 구축 의무:")
        print("    1. /pyramid-label 실행 → 모든 코드 단위에 L0~L3 주석 생성")
        print("    2. 이 도구 --reindex 재실행 → 그래프 질의 활성화")
        print("  (라벨 생산은 pyramid_guard 훅이 이후 저장마다 강제한다)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
