# L0: violation_registry.json의 L0/L1 구조 위반 규칙을 중앙에서 적용해 실수를 사전 차단한다
# 새 실수 발생 시 이 파일을 수정하지 않고 violation_registry.json에 규칙만 추가한다

import sys
import json
import re
import os

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "violation_registry.json")


def load_registry():
    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # 레지스트리 읽기 실패 시 통과 (게이트 자체가 장애가 되면 안 됨)
        print(f"[ontology_violation_gate] registry load failed: {e}", file=sys.stderr)
        return {"rules": []}


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
            for pat in patterns:
                try:
                    m = re.search(pat, content, re.MULTILINE)
                    if m:
                        matched = m.group(0)[:80].replace("\n", "↵")
                        violations.append({
                            "heading": f"코드 패턴: {matched}",
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


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "NotebookEdit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    filepath = tool_input.get("file_path", "")
    # Write uses 'content', Edit uses 'new_string'
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    if not content or not filepath:
        sys.exit(0)

    registry = load_registry()
    found_violations = []

    for rule in registry.get("rules", []):
        result = apply_rule(rule, filepath, content)
        if result:
            found_violations.append(result)

    if found_violations:
        for rule_id, msg in found_violations:
            print(msg)
        sys.exit(2)  # exit(2) = Claude Code block signal (exit(1) treated as error, not block)

    sys.exit(0)


if __name__ == "__main__":
    main()
