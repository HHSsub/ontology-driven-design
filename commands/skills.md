# /skills — 사용 가능한 스킬 목록

L0: 어떤 스킬이 있는지 알아야 쓸 수 있다

이 커맨드는 ODD 플러그인 및 연동 스킬의 전체 목록을 보여준다.

---

## ODD 핵심 스킬 (이 플러그인 내장)

| 스킬 이름 | 발동 커맨드 | 용도 |
|-----------|------------|------|
| `pyramid-ontology` | `/pyramid-ontology` | 모든 작업의 L0-L3 목적 위계 선언 |
| `ontology-detach` | `/ontology-detach` | 탈존재 — binding 교체조건 강제 |
| `ontology-rebuild` | `/ontology-rebuild` | ONTOLOGY.md 위계 재구성 |
| `pyramid-label` | `/pyramid-label` | 코드/파일 L0-L3 라벨 일괄 적용 |
| `pyramid-topology` | `/pyramid-topology` | 전체 시스템 위계 무결성 스캔 |
| `ontology-review-gate` | `/ontology-review-gate` | 구현 전 온톨로지 법정 (blocking) |
| `ontology-learning` | `/ontology-learning` | 실수→L0~L3 역추적→메모리 진화 |

---

## Superpowers 연동 스킬 (별도 설치)

설치: `claude plugin add superpowers` (또는 개별 스킬 등록)

| 스킬 이름 | 발동 커맨드 | 용도 |
|-----------|------------|------|
| `superpowers:brainstorming` | `/brainstorming` | 아이디어→설계 합의 |
| `superpowers:test-driven-development` | `/tdd` | TDD 사이클 강제 |
| `superpowers:systematic-debugging` | `/debug` | 근본 원인 디버깅 |
| `superpowers:writing-plans` | `/plan` | 구현 계획 분해 |

---

## 기타 스킬 (사용자 등록)

| 스킬 이름 | 발동 커맨드 | 용도 |
|-----------|------------|------|
| `investigate` | `/investigate` | L0 기반 심층 조사 |
| `careful` | `/careful` | 비가역 행동 안전 게이트 |
| `health` | `/health` | 시스템 상태 점검 |
| `review` | `/review` | 코드·문서 온톨로지 리뷰 |
| `retro` | `/retro` | 세션 회고 + 온톨로지 진화 |

---

## 훅 (자동 발동)

수동 호출 불필요 — 해당 도구 사용 시 자동 실행:

| 훅 | 이벤트 | 조건 |
|----|--------|------|
| `pyramid_ontology_gate` | PreToolUse Edit/Write | L0 선언 없으면 차단 |
| `ontology_violation_gate` | PreToolUse Edit/Write | violation_registry.json 규칙 위반 차단 |
| `assumption_declaration_gate` | PreToolUse Edit/Write | 전략 문서에 가정 없으면 차단 |
| `websearch_yearguard` | PreToolUse WebSearch | 연도 없는 쿼리 차단 |
| `pyramid_guard` | PostToolUse Edit/Write | 작성 후 L0 연결 검증 |
| `git_commit_push_check` | PostToolUse Bash | commit 후 push 미완료 경고 |
| `pptx_validate_hook` | PostToolUse Bash | PPT 빌드 후 overflow 검증 |
| `ontology_declare_enforce` | Stop | 세션 종료 시 L0 선언 미완료 차단 |
| `git_push_enforce_stop` | Stop | 미push 커밋 있으면 차단 |
| `tdd_enforce_stop` | Stop | Edit/Write 후 검증 없으면 차단 |
