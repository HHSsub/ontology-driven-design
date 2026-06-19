# 자동 강제 훅 (Hooks)

ODD 플러그인은 여러 훅을 자동으로 설치합니다. 훅은 Claude Code가 동작하는 동안 **사용자 명령 없이 매번 자동으로 발동**됩니다.

## 핵심 아키텍처 — 패턴 훅 vs 에이전트 판정자

훅은 두 계층으로 나뉩니다. 이 구분이 ODD 강제의 근본 설계입니다.

| 계층 | 무엇을 잡나 | 어떻게 | 예 |
|------|------------|--------|-----|
| **패턴 훅** (결정론) | **고정 패턴** 위반 — 쉘 문법, 파일명 규칙, 금지 키워드, 경로 필터 | 정규식/문자열 매칭. 즉시·무료·결정론적 | `websearch_yearguard`, `python3_guard`, `git_push_enforce_stop` |
| **에이전트 판정자** (의미) | **의미 위반** — L0가 진짜 목적인가, 전제를 분석했는가, 외부 검증 없이 완료 선언했는가 | LLM(저비용 모델)에게 자연어로 판정 위임 | `semantic_judge_gate` |

**불변 원칙: 의미 기반 판정은 절대 패턴으로 흉내내지 않는다 — 반드시 에이전트가 한다.**

정규식은 표면 패턴만 잡는다. "이 L0가 구현 수단을 목적으로 위장했나", "기존 코드의 전제를 분석하지 않고 바꿨나", "같은 접근을 반복 실패하면서 L1 재검토를 안 했나" 같은 **의미 판단**은 1000만 가지 표현형을 가지므로 정규식으로는 그중 10개도 못 잡는다. 의미는 의미로 — 즉 **에이전트(LLM 판정자)로** 잡아야 한다.

규칙을 정규식 파일에 끝없이 쌓는 것(케이스 누적)은 L3 패치이며 진화 실패의 신호다. 패턴 훅은 진짜 기계적 위반에만 쓰고, 판단이 필요한 모든 것은 에이전트에게 위임하라.

---


## 발동 방식 요약

### PreToolUse — 실행 전 차단

| 훅 | 발동 조건 | 검사 내용 |
|----|----------|---------|
| `pyramid_ontology_gate` | Edit/Write/NotebookEdit **실행 전** | L0 선언 없으면 수정 자체를 원천 차단 |
| `ontology_violation_gate` | Edit/Write/NotebookEdit **실행 전** | violation_registry.json 규칙 위반 차단 |
| `assumption_declaration_gate` | Edit/Write/NotebookEdit **실행 전** | 전략 문서에 [가정 명시] 없으면 차단 |
| `websearch_yearguard` | WebSearch **실행 전** | 연도 없는 검색 쿼리 차단 |

### PostToolUse — 실행 후 검증

| 훅 | 발동 조건 | 검사 내용 |
|----|----------|---------|
| `pyramid_guard` | Edit/Write 저장 시마다 | L 레벨 정합성 + SSOT 중복 진실 탐지 |
| `git_commit_push_check` | Bash 명령 실행 후 | `git commit` 명령 후 미푸시 커밋 경고 |
| `pptx_validate_hook` | Bash 명령 실행 후 | `build_*_ppt.py` 후 슬라이드 overflow 검증 |

### Stop — 세션 종료 시 강제

| 훅 | 검사 내용 |
|----|---------|
| `ontology_declare_enforce` | L0 선언 존재 + 의존성 체인 검증 |
| `git_push_enforce_stop` | 세션 수정 파일 미커밋/미푸시 차단 |
| `tdd_enforce_stop` | Edit/Write 후 검증 명령 실행 흔적 없으면 차단 |

**superpowers 미설치 환경에서도 모두 작동합니다.** Claude Code `settings.json` 훅으로 동작하며 superpowers 플러그인과 무관합니다.

---

## pyramid_ontology_gate

**파일**: `hooks/pyramid_ontology_gate.py`  
**발동**: PreToolUse — `Edit`, `Write`, `NotebookEdit` **실행 전에** 발동

### 핵심 차이

`ontology_declare_enforce`(Stop 훅)은 수정이 완료된 후에 차단합니다.  
`pyramid_ontology_gate`는 **파일이 바뀌기 전에** 차단합니다 — 수정 자체를 막습니다.

### 검사 항목

세션 전체 transcript를 탐색해 `L0:` 선언이 한 번이라도 있었는지 확인합니다.  
없으면 Edit/Write를 차단합니다.

```
❌ 차단: 세션 시작 후 L0 선언 없이 파일 수정 시도
✅ 통과: 세션 어디서든 "L0: ..." 선언이 있으면 이후 모든 수정 허용
```

**면제 대상** (무한루프 방지):
- `~/.claude/hooks/*.py` — 훅 파일 자체
- `settings.json`, `hooks.json` — 설정 파일
- `CLAUDE.md`, `ONBOARDING.md` — 온보딩/규칙 문서

---

## ontology_violation_gate

**파일**: `hooks/ontology_violation_gate.py`  
**발동**: PreToolUse — `Edit`, `Write`, `NotebookEdit` **실행 전에** 발동

### 구조

`violation_registry.json`을 읽어 등록된 규칙을 순서대로 적용합니다.  
새 실수가 생기면 이 파이썬 파일을 수정하지 않고 **레지스트리에 규칙만 추가**합니다.

### 지원 검사 유형

- `heading_structure` — 마크다운 H2/H3 헤딩 패턴 검사 (예: 교육 설명형 헤딩 차단)
- `section_outcome_grounding` — 섹션에 사업결과/행동 연결 없으면 차단
- `content_pattern` — 파일 내 코드 패턴(정규식) 탐지

### 경로 필터

각 규칙에 `path_must_contain_any` 필터가 있어 **해당 경로의 파일에만 발동**합니다.  
다른 프로젝트에 간섭 없음.

---

## assumption_declaration_gate

**파일**: `hooks/assumption_declaration_gate.py`  
**발동**: PreToolUse — `Edit`, `Write`, `NotebookEdit` **실행 전에** 발동

### 적용 대상

경로에 `사업부`, `전략실행`, `역공학`, `당장파이프라인`, `strategy`, `strategic` 중 하나가 포함된 `.md` 파일.

### 검사 항목

파일 내용에 다음 중 하나가 있는지 확인합니다:
- `[가정 명시]` / `[가정]`
- `가정 1:` / `가정:` / `전제:`
- `미확인:` / `확인됨:`
- `assumption:` / `premise:`

```
❌ 차단: 전략 문서에 가정 목록 없이 결론만 있는 경우
✅ 통과: "[가정 명시] - 가정 1: ... → 검증 상태: 미검증" 포함 시
```

---

## websearch_yearguard

**파일**: `hooks/websearch_yearguard.py`  
**발동**: PreToolUse — `WebSearch` **실행 전에** 발동

### 검사 항목

쿼리에 현재 연도(`datetime.now().year`)나 `최신`, `current`, `latest`, `today` 키워드 없으면 차단합니다.

```
❌ 차단: "Vercel pricing plans"
✅ 통과: "Vercel pricing plans 2026"
```

외부 서비스·API·요금·정책 등 어떤 외부 정보든 최신 연도 기준이어야 합니다.

---

## pyramid_guard

**파일**: `hooks/pyramid_guard.py`  
**발동**: PostToolUse — `Edit` 또는 `Write` 도구 사용 시마다

### 검사 항목

**L2-A: L 레벨 선언 존재 확인** — 파일에 `L0:`, `L1:` 선언이 있는지 확인합니다.

**L2-B: L0 내용 오염 탐지** — L0 줄에 기술 세부사항이 올라오면 차단합니다.
```
❌ 차단: L0: timeout 10초 이내 완료       (구현 제약 → L3에 있어야 함)
✅ 통과: L0: 사용자 시간 절약 — 봇이 대신 챙긴다
```

**L2-F: 탈존재(ontology-detach) 위반** — 교체 조건 없는 하드코딩 탐지.

**L2-G: 중복 진실(Duplicate Truth) — SSOT 위반**  
동일한 개념 집합(문자열 3개 이상)이 파일 내 2개 이상 독립된 리스트에 중복 존재하면 차단합니다.

---

## git_commit_push_check

**파일**: `hooks/git_commit_push_check.py`  
**발동**: PostToolUse — Bash 명령 실행 후 (`git commit` 포함된 경우만)

### 검사 항목

commit 후 upstream 대비 미푸시 커밋이 있으면 stderr로 경고합니다.  
`git_push_enforce_stop`(Stop 훅)이 세션 종료 시에만 발동하는 갭을 이 훅이 커버합니다.

```
⚠️  git commit 완료 — Push 아직 안 됨
  즉시 실행: git push origin main
```

---

## pptx_validate_hook

**파일**: `hooks/pptx_validate_hook.py`  
**발동**: PostToolUse — Bash 명령 실행 후 (`build_*_ppt.py` 포함된 경우만)

### 검사 항목

최근 120초 내 생성된 `.pptx` 파일을 찾아 슬라이드 레이아웃 overflow를 검사합니다.  
13.33" × 7.5" 슬라이드 경계를 벗어난 shape가 있으면 차단합니다.

**의존성**: `python-pptx` 패키지 필요 (`pip install python-pptx`)

---

## ontology_declare_enforce

**파일**: `hooks/ontology_declare_enforce.py`  
**발동**: Stop — Claude가 응답을 완료할 때마다

### 검사 항목

**L2-A: L0 선언 존재 확인** — Edit/Write가 포함된 턴에서 직전 어시스턴트 메시지에 `L0:` 선언이 없으면 차단합니다.

**L2-B: 의존성 체인 검증** — 열거형 개념 모음 수정 시 같은 턴에 Grep 증거 없으면 차단합니다.

---

## git_push_enforce_stop

**파일**: `hooks/git_push_enforce_stop.py`  
**발동**: Stop — Claude가 응답을 완료할 때마다

### 검사 항목

이번 세션에서 **실제로 수정한 파일**만 추적합니다 (pre-existing dirty 파일은 무시).

```
❌ 차단: bot.py 수정 → git commit 안 함
❌ 차단: alarm_manager.py 수정 → commit만 하고 push 안 함
✅ 통과: 수정 파일 모두 commit + push 완료
```

---

## tdd_enforce_stop

**파일**: `hooks/tdd_enforce_stop.py`  
**발동**: Stop — Claude가 응답을 완료할 때마다

### 검사 항목

transcript에서 마지막 Edit/Write 위치와 검증 명령 위치를 시간순으로 추적합니다.  
마지막 Edit/Write **이후** 검증 흔적이 없으면 차단합니다.

**검증으로 인정하는 패턴:**
- Python: `pytest`, `python -m py_compile`, `python <file>.py`
- JS/TS: `npx tsc --noEmit`, `npm test`, `npm run build`
- Web: `curl http://localhost`
- 기타: `go test`, `cargo test`, `dotnet test`, `jest`

```
❌ 차단: 코드 수정 후 검증 없이 응답 완료
✅ 통과: python -m py_compile <file> 실행 후 응답 완료
```

---

## semantic_judge_gate (에이전트 기반 L0 의미 판정)

**파일**: `hooks/semantic_judge_gate.py`
**발동**: Stop — Claude가 응답을 완료할 때마다

### 왜 패턴이 아니라 에이전트인가

`ontology_violation_gate`(패턴 훅)는 "L0:"라는 **문자열이 존재하는가"**만 본다. 하지만 껍데기 L0(예: `L0: JSON 파싱 기능 구현` — 구현 행위가 목적 자리를 차지)는 문자열로는 통과한다. **L0가 진짜 목적인지 아닌지는 의미 판단이라 정규식으로 불가능하다.**

`semantic_judge_gate`는 이 구조적 구멍을 메운다. 이 세션의 Edit/Write에서 `L0:` 선언 줄을 추출해 **독립 판정자(claude CLI, 저비용 모델)에게** 위임하고, `judge_rubric.md`의 기준으로 PASS/FAIL을 받는다.

### 동작

1. 트랜스크립트에서 Edit/Write의 `L0:` 줄 추출 (현재 파일에 실제로 남아있는 줄만 — 역사가 아니라 현재 상태를 판정)
2. L0 줄 없으면 통과 (판정 비용 0)
3. `judge_rubric.md` 전문 + L0 줄을 프롬프트로 구성 → 에이전트 호출
4. FAIL 있으면 사유와 함께 차단(exit 2), 재작성 유도
5. **데드루프 방지**: 한 세션에서 2회 차단하면 이후 통과 (`judge_state.json` 기록)
6. **fail-open**: 판정자 호출 실패/타임아웃 시 통과 — 판정자 장애가 작업을 막지 않는다

### judge_rubric.md = 판정 기준 SSOT

판정 기준은 코드가 아니라 `judge_rubric.md`에 데이터로 존재한다. 기준을 바꾸려면 파이썬이 아니라 이 마크다운만 수정한다. 판정자는 이 기준만으로 판정하며 자체 학습 지식으로 완화하지 않는다.

```
❌ FAIL: L0: 타임아웃 10초 이내 완료        (기술 수치가 목적 자리)
❌ FAIL: L0: Redis 캐싱으로 응답속도 향상    (기술 수단이 목적 자리)
✅ PASS: L0: 고객이 견적을 사람 도움 없이 스스로 완성
```

> 이것이 ODD가 "의미 기반 판정은 반드시 에이전트로"라는 원칙을 실제로 구현한 지점이다. 같은 방식으로, 패턴으로 표현 불가능한 어떤 거버넌스든 에이전트 판정자로 확장할 수 있다.

---

## 설치 확인

훅이 제대로 설치됐는지 확인:

```bash
cat ~/.claude/settings.json | grep -A5 "hooks"
```

플러그인 설치 시 `hooks.json`에 정의된 훅이 자동으로 적용됩니다.

[설치 방법 →](/guide/installation)
