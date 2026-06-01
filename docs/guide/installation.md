# 설치 / Installation

## 요구사항 / Requirements

- [Claude Code](https://claude.ai/code) CLI
- Python 3.8 이상 (훅 실행에 필요 / required for hooks)
- `python-pptx` — 선택사항, PPTX 검증 훅에만 필요 (optional, only for PPTX validation hook)

```bash
pip install python-pptx   # optional
```

---

## 플러그인 설치 (권장) / Plugin Install (Recommended)

```bash
# 풀네임 (권장)
claude plugin add HHSsub/ontology-driven-design

# 단축 alias (동일하게 작동)
claude plugin add HHSsub/odd
```

플러그인 설치 시 스킬, 커맨드, 훅이 모두 자동으로 Claude Code에 등록됩니다.

When installed via plugin, skills, commands, and hooks are all automatically registered with Claude Code.

---

## 수동 설치 / Manual Install

플러그인 명령어가 없는 Claude Code 버전에서는 수동 설치를 사용하세요.

If `claude plugin add` is unavailable in your Claude Code version, use manual installation.

### 1. 레포 클론 / Clone the repo

```bash
git clone https://github.com/HHSsub/ontology-driven-design.git
cd ontology-driven-design
```

### 2. 스킬과 커맨드 복사 / Copy skills and commands

```bash
cp -r skills/* ~/.claude/skills/
cp commands/* ~/.claude/commands/
```

### 3. 훅 파일 복사 / Copy hook files

```bash
cp hooks/*.py ~/.claude/hooks/
cp hooks/violation_registry.json ~/.claude/hooks/
```

### 4. 훅을 settings.json에 등록 / Register hooks in settings.json

Claude Code의 `~/.claude/settings.json`에 다음 훅 설정을 추가합니다.

Add the following hook configuration to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "WebSearch",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/websearch_yearguard.py"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/destructive_bash_gate.py"
          }
        ]
      },
      {
        "matcher": "Agent",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/agent_pyramid_gate.py"
          }
        ]
      },
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/pyramid_ontology_gate.py"
          },
          {
            "type": "command",
            "command": "python ~/.claude/hooks/ontology_violation_gate.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/pptx_validate_hook.py"
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/pyramid_guard.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/tdd_enforce_stop.py"
          },
          {
            "type": "command",
            "command": "python ~/.claude/hooks/ontology_declare_enforce.py"
          },
          {
            "type": "command",
            "command": "python ~/.claude/hooks/git_push_enforce_stop.py"
          }
        ]
      }
    ]
  }
}
```

> **Windows 사용자 (Windows users):** 경로에 백슬래시 또는 절대 경로를 사용하세요.
> Use backslashes or absolute paths: `python C:/Users/YourName/.claude/hooks/pyramid_ontology_gate.py`

---

## 설치 확인 / Verify Installation

### 스킬 확인 / Verify skills

Claude Code 세션에서 실행 / Run in a Claude Code session:

```
/pyramid-ontology
```

스킬이 로드되면 설치 완료입니다 / If the skill loads, installation is complete.

### 훅 확인 / Verify hooks

```bash
# settings.json에 훅이 등록됐는지 확인
cat ~/.claude/settings.json | python -m json.tool | grep -A 3 "hooks"
```

훅이 작동하는지 직접 확인하려면: 새 Claude Code 세션에서 L0 선언 없이 파일 수정을 요청하세요.

To verify hooks are active: in a new Claude Code session, ask Claude to edit any file without declaring L0 first. The `pyramid_ontology_gate` hook should block the edit.

Expected block message:
```
❌ L0 선언 없음 — Edit/Write 차단
```

---

## 제거 / Uninstall

### 플러그인 제거

```bash
claude plugin remove HHSsub/ontology-driven-design
```

### 수동 제거

```bash
rm ~/.claude/skills/pyramid-ontology/SKILL.md
rm ~/.claude/skills/ontology-detach/SKILL.md
rm ~/.claude/skills/ontology-rebuild/SKILL.md
rm ~/.claude/skills/pyramid-label/SKILL.md
rm ~/.claude/skills/pyramid-topology/SKILL.md
rm ~/.claude/skills/ontology-review-gate/SKILL.md
rm ~/.claude/skills/ontology-learning/SKILL.md
rm ~/.claude/skills/odd-onboarding/SKILL.md
rm ~/.claude/hooks/pyramid_ontology_gate.py
rm ~/.claude/hooks/pyramid_guard.py
rm ~/.claude/hooks/ontology_declare_enforce.py
rm ~/.claude/hooks/git_push_enforce_stop.py
rm ~/.claude/hooks/tdd_enforce_stop.py
rm ~/.claude/hooks/websearch_yearguard.py
rm ~/.claude/hooks/ontology_violation_gate.py
rm ~/.claude/hooks/violation_registry.json
```

Then remove the hook entries from `~/.claude/settings.json`.

---

## 다음 단계 / Next Steps

- [5분 퀵스타트 (5-minute quickstart)](../quickstart.md) — 첫 L0 선언과 훅 차단 경험
- [사용법 (Usage)](./usage.md) — 전체 스킬 워크플로우
- [훅 레퍼런스 (Hook reference)](../skills/hooks.md) — 10개 훅 상세 설명
