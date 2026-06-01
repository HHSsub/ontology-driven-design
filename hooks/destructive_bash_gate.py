# L0: DB 데이터 파괴 명령(UPDATE NULL, DELETE, DROP, VACUUM, rm *.db)은
#     유저 확인 없이 Bash로 실행되는 것을 원천 차단한다
# 이 훅은 PreToolUse Bash 매처에 등록. 위반 시 exit 2로 차단.

import sys
import json
import re

# 비가역 파괴 패턴 (SSH 원격 포함, python -c 인라인 포함)
DESTRUCTIVE_PATTERNS = [
    (r'UPDATE\s+\w+\s+SET\s+\w+\s*=\s*(NULL|0|\'\'|\"\")', 'UPDATE SET NULL/0/빈값 — 데이터 파괴'),
    (r'DELETE\s+FROM\s+\w+', 'DELETE FROM — 행 삭제'),
    (r'DROP\s+(TABLE|DATABASE|INDEX|COLUMN)\b', 'DROP — 스키마/데이터 파괴'),
    (r'\bVACUUM\b', 'VACUUM — DB 물리적 축소 (선행 삭제 확정)'),
    (r'rm\s+-[rf]+\s+\S+\.db', 'rm -rf *.db — DB 파일 삭제'),
    (r'truncate\s+\S+\.db', 'truncate *.db — DB 파일 초기화'),
    (r'os\.remove\([^)]*\.db', 'os.remove(*.db) — DB 파일 삭제'),
    (r'shutil\.rmtree', 'shutil.rmtree — 디렉토리 재귀 삭제'),
]


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Bash",):
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    found = []
    for pattern, label in DESTRUCTIVE_PATTERNS:
        try:
            m = re.search(pattern, command, re.IGNORECASE)
            if m:
                found.append((label, m.group(0)[:80]))
        except re.error:
            pass

    if not found:
        sys.exit(0)

    print("══════════════════════════════════════════════════════")
    print("❌  Destructive Bash Gate — 비가역 행동 차단")
    print("══════════════════════════════════════════════════════")
    print()
    print("L0 원칙: DB 데이터 파괴 명령은 유저 명시적 동의 없이 실행 불가")
    print()
    print("탐지된 파괴 패턴:")
    for label, matched in found:
        print(f"  ⚠  {label}")
        print(f"     패턴: {matched}")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("실행하려면: 유저에게 먼저 보고하고 명시적 동의를 받은 후 진행하세요.")
    print("  1. 무엇을 삭제/변경하는가")
    print("  2. 왜 필요한가 (L0 연결)")
    print("  3. 복구 가능 여부")
    print("══════════════════════════════════════════════════════")
    sys.exit(2)


if __name__ == "__main__":
    main()
