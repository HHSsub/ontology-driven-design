# L0: violation_registry.json의 L0/L1 구조 위반 규칙을 중앙에서 적용해 실수를 사전 차단한다
# 새 실수 발생 시 이 파일을 수정하지 않고 violation_registry.json에 규칙만 추가한다

import sys
import json
import re
import os
import tempfile
from datetime import datetime, timezone

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "violation_registry.json")
STATS_PATH = os.path.join(os.path.dirname(__file__), "violation_stats.json")
ESCALATION_FLAG_PATH = os.path.join(os.path.dirname(__file__), "escalation_pending.json")


def load_registry():
    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # 레지스트리 읽기 실패 시 통과 (게이트 자체가 장애가 되면 안 됨)
        sys.stderr.buffer.write(f"[ontology_violation_gate] registry load failed: {e}\n".encode("utf-8", errors="replace"))
        sys.stderr.buffer.flush()
        return {"rules": []}


def register_rules(registry):
    """모든 활성 규칙을 violation_stats.json에 added_date와 함께 등록 (첫 발동 전에 존재 추적 시작)."""
    try:
        if os.path.exists(STATS_PATH):
            with open(STATS_PATH, encoding="utf-8") as f:
                stats = json.load(f)
        else:
            stats = {}
        today = datetime.now(timezone.utc).date().isoformat()
        changed = False
        for rule in registry.get("rules", []):
            rid = rule.get("id", "")
            if rid and rid not in stats:
                stats[rid] = {
                    "trigger_count": 0,
                    "last_triggered": None,
                    "recent_count": 0,
                    "recent_date": today,
                    "added_date": today
                }
                changed = True
        if changed:
            dir_ = os.path.dirname(STATS_PATH)
            fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                os.replace(tmp, STATS_PATH)
            except Exception:
                try:
                    os.unlink(tmp)
                except Exception:
                    pass
    except Exception as e:
        print(f"[ontology_violation_gate] stats register failed: {e}", file=sys.stderr)


def record_trigger(rule_ids, project=""):
    """규칙 발동 시 violation_stats.json에 횟수·시각·daily 카운트·프로젝트별 분포 기록 (atomic write).

    projects 필드 = scope-channel match의 기계 신호: 같은 규칙이 2개+ 프로젝트에서 발동하면
    그 원칙은 전역 범위다 → 전역 채널 승격 의무 (ontology_learning_enforce_stop이 강제).
    """
    if not rule_ids:
        return
    try:
        if os.path.exists(STATS_PATH):
            with open(STATS_PATH, encoding="utf-8") as f:
                stats = json.load(f)
        else:
            stats = {}
        now = datetime.now(timezone.utc).isoformat()
        today = datetime.now(timezone.utc).date().isoformat()
        for rid in dict.fromkeys(rule_ids):
            entry = stats.get(rid, {
                "trigger_count": 0,
                "last_triggered": None,
                "recent_count": 0,
                "recent_date": today,
                "added_date": today
            })
            entry["trigger_count"] = entry.get("trigger_count", 0) + 1
            entry["last_triggered"] = now
            if entry.get("recent_date") == today:
                entry["recent_count"] = entry.get("recent_count", 0) + 1
            else:
                entry["recent_count"] = 1
                entry["recent_date"] = today
            if project:
                projects = entry.get("projects", {})
                projects[project] = projects.get(project, 0) + 1
                entry["projects"] = projects
            stats[rid] = entry
        # atomic write: temp 파일 쓰고 rename
        dir_ = os.path.dirname(STATS_PATH)
        fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            os.replace(tmp, STATS_PATH)
        except Exception:
            try:
                os.unlink(tmp)
            except Exception:
                pass
    except Exception as e:
        try:
            os.write(2, f"[ontology_violation_gate] stats write failed: {e}\n".encode("ascii", errors="replace"))
        except Exception:
            pass


def matches_file_filter(filepath, file_filter):
    """파일이 이 규칙의 적용 대상인지 확인"""
    if not filepath:
        return False
    ext = os.path.splitext(filepath)[1].lower()
    allowed_exts = file_filter.get("extensions", [])
    if allowed_exts and ext not in allowed_exts:
        return False
    must_contain = file_filter.get("path_must_contain_any", [])
    if must_contain:
        normalized = filepath.replace("\\", "/")
        if not any(kw in normalized for kw in must_contain):
            return False
    return True


def parse_sections(content):
    """마크다운을 H2/H3 섹션 단위로 파싱. [(heading_text, body_text), ...]"""
    sections = []
    current_heading = None
    current_body = []
    for line in content.splitlines():
        m = re.match(r'^#{2,3}\s+(.+)$', line)
        if m:
            if current_heading is not None:
                sections.append((current_heading, "\n".join(current_body)))
            current_heading = m.group(1).strip()
            current_body = []
        else:
            if current_heading is not None:
                current_body.append(line)
    if current_heading is not None:
        sections.append((current_heading, "\n".join(current_body)))
    return sections


def check_heading_structure(heading, patterns):
    """헤딩이 교육 설명 구조인지 검사"""
    for pat in patterns:
        try:
            if re.search(pat, heading):
                return True
        except re.error:
            pass
    return False


def check_section_outcome_grounding(heading, body, check_cfg):
    """섹션이 사업결과나 행동 연결 없이 떠 있는지 검사"""
    exempt = check_cfg.get("exempt_headings", [])
    if any(kw in heading for kw in exempt):
        return False  # 면제 섹션
    outcome_signals = check_cfg.get("outcome_signals", [])
    action_signals = check_cfg.get("action_signals", [])
    text = (heading + " " + body[:500]).lower()
    has_outcome = any(sig in text for sig in outcome_signals)
    has_action = any(sig in text for sig in action_signals)
    return not (has_outcome or has_action)


def apply_rule(rule, filepath, content):
    """규칙 하나를 적용. 위반 발견 시 (rule_id, message) 반환, 없으면 None."""
    if not rule.get("enabled", True):
        return None
    file_filter = rule.get("file_filter", {})
    if not matches_file_filter(filepath, file_filter):
        return None

    sections = parse_sections(content)
    violations = []

    for check in rule.get("checks", []):
        check_type = check.get("type")

        if check_type == "heading_structure":
            patterns = check.get("patterns", [])
            for heading, body in sections:
                if check_heading_structure(heading, patterns):
                    violations.append({
                        "heading": heading,
                        "message": check.get("block_message", "")
                    })

        elif check_type == "section_outcome_grounding":
            for heading, body in sections:
                if check_section_outcome_grounding(heading, body, check):
                    violations.append({
                        "heading": heading,
                        "message": check.get("block_message", "")
                    })

        elif check_type == "content_pattern":
            patterns = check.get("patterns", [])
            # required_alongside: 트리거 패턴이 매칭됐을 때 이 패턴도 파일에 있어야 함
            # 없으면 차단. "확인 마커 있으면 통과" 구조를 지원
            required = check.get("required_alongside", [])
            for pat in patterns:
                try:
                    m = re.search(pat, content, re.MULTILINE | re.IGNORECASE)
                    if m:
                        # required_alongside 체크: 하나라도 있으면 통과
                        if required:
                            has_required = any(
                                re.search(r, content, re.MULTILINE | re.IGNORECASE)
                                for r in required
                            )
                            if has_required:
                                break  # 마커 있음 → 통과
                        matched = m.group(0)[:80].replace("\n", "↵")
                        violations.append({
                            "heading": f"코드 패턴: {matched}",
                            "message": check.get("block_message", "")
                        })
                        break
                except re.error:
                    pass

        elif check_type == "file_path_pattern":
            patterns = check.get("patterns", [])
            filename = os.path.basename(filepath) if filepath else ""
            if filename:
                for pat in patterns:
                    try:
                        if re.search(pat, filename, re.IGNORECASE):
                            violations.append({
                                "heading": f"파일명: {filename}",
                                "message": check.get("block_message", "")
                            })
                            break
                    except re.error:
                        pass

    if not violations:
        return None

    rule_id = rule.get("id", "unknown")
    l0 = rule.get("l0", "")
    l1 = rule.get("l1_pattern", "")

    msg = "══════════════════════════════════════════════\n"
    msg += f"❌ Ontology Violation Gate — 규칙: {rule_id}\n"
    msg += "══════════════════════════════════════════════\n\n"
    msg += f"L0 원칙: {l0}\n"
    msg += f"L1 패턴: {l1}\n\n"
    msg += f"감지된 위반 섹션 ({len(violations)}개):\n"
    for v in violations:
        msg += f"  헤딩: \"{v['heading']}\"\n"
        if v['message']:
            msg += f"  → {v['message']}\n"
        msg += "\n"
    msg += "══════════════════════════════════════════════"
    return (rule_id, msg)


def apply_ps_rule(rule, command):
    """PowerShell tool 전용 규칙 적용. ps_command_pattern check type만 처리."""
    if not rule.get("enabled", True):
        return None
    has_ps_check = any(c.get("type") == "ps_command_pattern" for c in rule.get("checks", []))
    if not has_ps_check:
        return None

    violations = []
    for check in rule.get("checks", []):
        if check.get("type") != "ps_command_pattern":
            continue
        patterns = check.get("patterns", [])
        for pat in patterns:
            try:
                m = re.search(pat, command, re.IGNORECASE)
                if m:
                    matched = m.group(0)[:80].replace("\n", "↵")
                    violations.append({
                        "heading": f"PowerShell 명령 패턴: {matched}",
                        "message": check.get("block_message", "")
                    })
                    break
            except re.error:
                pass

    if not violations:
        return None

    rule_id = rule.get("id", "unknown")
    l0 = rule.get("l0", "")
    l1 = rule.get("l1_pattern", "")

    msg = "══════════════════════════════════════════════\n"
    msg += f"❌ Ontology Violation Gate — 규칙: {rule_id}\n"
    msg += "══════════════════════════════════════════════\n\n"
    msg += f"L0 원칙: {l0}\n"
    msg += f"L1 패턴: {l1}\n\n"
    msg += f"감지된 위반 ({len(violations)}개):\n"
    for v in violations:
        msg += f"  패턴: \"{v['heading']}\"\n"
        if v['message']:
            msg += f"  → {v['message']}\n"
        msg += "\n"
    msg += "══════════════════════════════════════════════"
    return (rule_id, msg)


def apply_bash_rule(rule, command):
    """Bash tool 전용 규칙 적용. bash_command_pattern check type만 처리."""
    if not rule.get("enabled", True):
        return None
    # bash 규칙은 bash_command_pattern check를 가진 것만
    has_bash_check = any(c.get("type") == "bash_command_pattern" for c in rule.get("checks", []))
    if not has_bash_check:
        return None

    violations = []
    for check in rule.get("checks", []):
        if check.get("type") != "bash_command_pattern":
            continue
        patterns = check.get("patterns", [])
        for pat in patterns:
            try:
                m = re.search(pat, command, re.IGNORECASE)
                if m:
                    matched = m.group(0)[:80].replace("\n", "↵")
                    violations.append({
                        "heading": f"Bash 명령 패턴: {matched}",
                        "message": check.get("block_message", "")
                    })
                    break
            except re.error:
                pass

    if not violations:
        return None

    rule_id = rule.get("id", "unknown")
    l0 = rule.get("l0", "")
    l1 = rule.get("l1_pattern", "")

    msg = "══════════════════════════════════════════════\n"
    msg += f"❌ Ontology Violation Gate — 규칙: {rule_id}\n"
    msg += "══════════════════════════════════════════════\n\n"
    msg += f"L0 원칙: {l0}\n"
    msg += f"L1 패턴: {l1}\n\n"
    msg += f"감지된 위반 ({len(violations)}개):\n"
    for v in violations:
        msg += f"  패턴: \"{v['heading']}\"\n"
        if v['message']:
            msg += f"  → {v['message']}\n"
        msg += "\n"
    msg += "══════════════════════════════════════════════"
    return (rule_id, msg)


def _main():
    try:
        raw = sys.stdin.read().lstrip('﻿')  # PowerShell BOM 방어
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    project = os.path.basename(os.path.normpath(data.get("cwd", "") or os.getcwd()))
    registry = load_registry()
    register_rules(registry)  # 모든 규칙을 stats에 등록 (added_date 추적 시작)
    found_violations = []

    if tool_name in ("Write", "Edit", "NotebookEdit"):
        filepath = tool_input.get("file_path", "")
        # Write uses 'content', Edit uses 'new_string'
        content = tool_input.get("content", "") or tool_input.get("new_string", "")
        if not content or not filepath:
            sys.exit(0)
        for rule in registry.get("rules", []):
            result = apply_rule(rule, filepath, content)
            if result:
                found_violations.append(result)

    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        if not command:
            sys.exit(0)
        for rule in registry.get("rules", []):
            result = apply_bash_rule(rule, command)
            if result:
                found_violations.append(result)

    elif tool_name == "PowerShell":
        command = tool_input.get("command", "")
        if not command:
            sys.exit(0)
        for rule in registry.get("rules", []):
            result = apply_ps_rule(rule, command)
            if result:
                found_violations.append(result)

    else:
        sys.exit(0)

    if found_violations:
        triggered_ids = [rule_id for rule_id, _ in found_violations]

        # L1 에스컬레이션 감지: 오늘 이미 2회+ 발동된 규칙이 또 발동하면 경고
        today = datetime.now(timezone.utc).date().isoformat()
        escalation_parts = []
        try:
            if os.path.exists(STATS_PATH):
                with open(STATS_PATH, encoding="utf-8") as _sf:
                    current_stats = json.load(_sf)
                for rid in triggered_ids:
                    entry = current_stats.get(rid, {})
                    if entry.get("recent_date") == today and entry.get("recent_count", 0) >= 2:
                        escalation_parts.append(
                            f"  [{rid}]: 오늘 {entry['recent_count'] + 1}번째 발동"
                        )
        except Exception:
            pass

        record_trigger(triggered_ids, project)
        out_parts = []
        for rule_id, msg in found_violations:
            out_parts.append(msg)

        if escalation_parts:
            out_parts.append(
                "\n🔴 L1 에스컬레이션 경고 — 세션 종료 차단 예약됨\n"
                "동일 규칙이 반복 발동됩니다:\n" +
                "\n".join(escalation_parts) + "\n\n"
                "L2 세부 패칭을 중단하고 L1 세계관 재검토가 필요합니다.\n"
                "→ /ontology-driven-design:ontology-learning 실행 전까지 세션 종료 차단"
            )

        os.write(1, "\n".join(out_parts).encode("utf-8", errors="replace"))

        # escalation_pending.json 플래그 기록 → Stop 훅이 ontology-learning 미실행 시 차단
        if escalation_parts:
            try:
                flag = {
                    "written_at": datetime.now(timezone.utc).isoformat(),
                    "rule_ids": escalation_parts
                }
                dir_ = os.path.dirname(ESCALATION_FLAG_PATH)
                fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
                try:
                    with os.fdopen(fd, "w", encoding="utf-8") as f:
                        json.dump(flag, f, ensure_ascii=False)
                    os.replace(tmp, ESCALATION_FLAG_PATH)
                except Exception:
                    try:
                        os.unlink(tmp)
                    except Exception:
                        pass
            except Exception:
                pass

        sys.exit(2)  # exit(2) = Claude Code block signal (exit(1) treated as error, not block)

    sys.exit(0)


def main():
    try:
        _main()
    except Exception as e:
        try:
            os.write(2, f"[gate crash] {type(e).__name__}: {e}\n".encode("ascii", errors="replace"))
        except Exception:
            pass
        sys.exit(0)  # fail open — 게이트 자체 crash는 통과


if __name__ == "__main__":
    main()
