# 자동 강제 훅 (Hooks)

ODD 플러그인은 3개의 훅을 자동으로 설치합니다. 훅은 Claude Code가 동작하는 동안 **사용자 명령 없이 매번 자동으로 발동**됩니다.

## 발동 방식 요약

| 훅 | 발동 시점 | 검사 내용 |
|----|----------|---------|
| `pyramid_guard` | Edit/Write 저장 시마다 | L 레벨 선언 정합성 + SSOT 중복 진실 탐지 |
| `ontology_declare_enforce` | Claude 응답 완료 시마다 | L0 선언 존재 여부 + 의존성 체인 검증 |
| `git_push_enforce` | Claude 응답 완료 시마다 | 이번 세션 수정 파일 미커밋/미푸시 차단 |

---

## pyramid_guard

**파일**: `hooks/pyramid_guard.py`  
**발동**: PostToolUse — `Edit` 또는 `Write` 도구 사용 시마다

### 검사 항목

**L2-A: L 레벨 선언 존재 확인**  
파일에 `L0:`, `L1:` 선언이 있는지 확인합니다.

**L2-B: L0 내용 오염 탐지**  
L0 줄에 기술 세부사항이 올라오면 차단합니다.
```
❌ 차단: L0: timeout 10초 이내 완료       (구현 제약 → L3에 있어야 함)
❌ 차단: L0: ffmpeg로 영상 인코딩           (도구 명시 → L3에 있어야 함)
✅ 통과: L0: 사용자 시간 절약 — 봇이 대신 챙긴다
```

**L2-F: 탈존재(ontology-detach) 위반**  
교체 조건 없는 하드코딩 탐지.

**L2-G: 중복 진실(Duplicate Truth) — SSOT 위반**  
동일한 개념 집합(문자열 3개 이상)이 파일 내 2개 이상 독립된 리스트에 중복 존재하면 차단합니다.
```python
# ❌ 차단: 아래 두 리스트가 60% 이상 겹침
COMMANDS = ["add", "del", "edit", "done"]
help_lines = {"add": "추가", "del": "삭제", "edit": "수정"}

# ✅ 통과: help_lines를 COMMANDS에서 파생 생성
help_lines = {cmd: descriptions[cmd] for cmd in COMMANDS}
```

이 검사는 **도메인 무관**합니다 — 어떤 프로젝트든 동일하게 적용됩니다.

---

## ontology_declare_enforce

**파일**: `hooks/ontology_declare_enforce.py`  
**발동**: Stop — Claude가 응답을 완료할 때마다

### 검사 항목

**L2-A: L0 선언 존재 확인**  
Edit/Write가 포함된 턴에서, 직전 어시스턴트 메시지에 `L0:` 선언이 없으면 차단합니다.
목적 선언 없이 코드를 수정하는 행동을 막습니다.

**L2-B: 의존성 체인 검증**  
열거형 개념 모음(리스트·딕셔너리·레지스트리)을 수정했는데 같은 턴에 Grep 증거가 없으면 차단합니다.
```
❌ 차단: COMMAND_REGISTRY에 항목 추가 → grep 없음
✅ 통과: Grep으로 파생 표현 탐색 → COMMAND_REGISTRY 수정
```

---

## git_push_enforce

**파일**: `hooks/git_push_enforce_stop.py`  
**발동**: Stop — Claude가 응답을 완료할 때마다

### 검사 항목

이번 세션에서 **실제로 수정한 파일**만 추적합니다 (pre-existing dirty 파일은 무시).

1. transcript에서 Edit/Write된 파일 경로 추출
2. `git status --porcelain` 결과와 교집합 확인
3. 세션 수정 파일이 미커밋이면 차단
4. 커밋은 됐는데 push 안 된 경우도 차단

```
❌ 차단: bot.py 수정 → git commit 안 함
❌ 차단: alarm_manager.py 수정 → commit만 하고 push 안 함
✅ 통과: 수정 파일 모두 commit + push 완료
```

---

## 설치 확인

훅이 제대로 설치됐는지 확인:

```bash
cat ~/.claude/settings.json | grep -A5 "hooks"
```

또는 `~/.claude/settings.json`에서 다음 항목이 있어야 합니다:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/pyramid_guard.py" }]
      }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/ontology_declare_enforce.py" }] },
      { "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/git_push_enforce_stop.py" }] }
    ]
  }
}
```

[설치 방법 →](/guide/installation)
