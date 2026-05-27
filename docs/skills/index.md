# 스킬 & 훅 & 커맨드 목록

ODD는 세 가지 발동 방식으로 동작합니다.

---

## 1. 항상 자동 발동 — superpowers 프레임워크

이 스킬들은 슬래시 커맨드 없이 **Claude가 스스로 발동**합니다.  
`description` 조건과 현재 작업이 일치하면 강제 호출됩니다.

| 스킬 | 자동 발동 조건 | 역할 |
|------|--------------|------|
| [pyramid-ontology](./pyramid-ontology) | **어떤 작업이든 시작할 때** | L0-L3 위계를 세션 헌법으로 선언 |
| [ontology-detach](./ontology-detach) | 코드 binding 작성/검토할 때마다 | 교체조건 없는 하드코딩 탐지·재설계 |
| [ontology-review-gate](./ontology-review-gate) | 구현·리팩토링·아키텍처 변경 전 | Ontology Court — PASS 없으면 구현 금지 |
| [ontology-learning](./ontology-learning) | **실수 발생·유저 교정·에러 감지 시** | L3→L0 역추적 RCA → 보편 원칙 메모리화 → 영구 진화 |

---

## 2. 수동 호출 커맨드 (`/커맨드`) — 18개

### ODD 핵심 스킬 (7개)

| 스킬 | 슬래시 커맨드 | 사용 시점 |
|------|------------|---------|
| [odd-onboarding](./odd-onboarding) | `/odd-onboarding` | 새 프로젝트/기능 시작 전 — L0 목적 확정 |
| [pyramid-ontology](./pyramid-ontology) | `/pyramid-ontology` | L0-L3 선언 강제 |
| [pyramid-label](./pyramid-label) | `/pyramid-label` | 코드 리뷰 전, 새 파일 추가 후 |
| [pyramid-topology](./pyramid-topology) | `/pyramid-topology` | 리팩토링 전 위계 정합성 점검 |
| [ontology-rebuild](./ontology-rebuild) | `/ontology-rebuild` | 주요 변경 후 위상도 갱신 |
| [ontology-detach](./ontology-detach) | `/ontology-detach` | 탈존재 원칙 — binding 교체조건 강제 |
| [ontology-learning](./ontology-learning) | `/ontology-learning` | 실수 발생 시 즉시 온톨로지 진화 |

### 워크플로우 커맨드 (11개)

| 커맨드 | 용도 |
|--------|------|
| `/brainstorming` | 구현 전 아이디어→설계 합의 (Superpowers brainstorming) |
| `/tdd` | 테스트 주도 개발 사이클 강제 |
| `/debug` | 근본 원인 체계적 디버깅 |
| `/plan` | 구현 계획 단계 분해 (Superpowers writing-plans) |
| `/investigate` | L0 기반 심층 조사 — 키워드 랜덤 검색 금지 |
| `/careful` | 비가역 행동 전 L0 연결 확인 안전 게이트 |
| `/health` | 시스템 의존성·프로세스·환경 상태 점검 |
| `/review` | 코드·문서 온톨로지 리뷰 |
| `/retro` | 세션 회고 + 온톨로지 진화 (메모리 저장) |
| `/skills` | 사용 가능한 전체 스킬/훅/커맨드 목록 표시 |
| `/frozen-exe` | Python 스크립트 → PyInstaller 단일 EXE 패키징 |

---

## 3. Claude Code 훅 — 인프라 레벨 강제 (10개)

`hooks.json`에 등록된 훅입니다.  
**Claude의 판단·superpowers 설치 여부와 무관하게** Claude Code 인프라가 발동시킵니다.

### PreToolUse

| 훅 | 발동 조건 | 검사 내용 |
|----|----------|---------|
| [pyramid_ontology_gate](./hooks) | Edit/Write **실행 전** | L0 선언 없으면 수정 자체 원천 차단 |
| [ontology_violation_gate](./hooks) | Edit/Write **실행 전** | violation_registry.json 규칙 위반 탐지 |
| [assumption_declaration_gate](./hooks) | Edit/Write **실행 전** | 전략 .md 파일에 가정 선언 없으면 차단 |
| [websearch_yearguard](./hooks) | WebSearch **실행 전** | 현재 연도 없는 쿼리 차단 |

### PostToolUse

| 훅 | 발동 조건 | 검사 내용 |
|----|----------|---------|
| [pyramid_guard](./hooks) | Edit/Write 저장 시마다 | L 레벨 정합성 + SSOT 중복 진실 |
| [git_commit_push_check](./hooks) | Bash (git commit 포함) | commit 후 미푸시 경고 |
| [pptx_validate_hook](./hooks) | Bash (build_*_ppt.py 포함) | 슬라이드 레이아웃 overflow 검증 |

### Stop

| 훅 | 검사 내용 |
|----|---------|
| [ontology_declare_enforce](./hooks) | L0 선언 존재 + 의존성 체인 검증 |
| [git_push_enforce_stop](./hooks) | 수정 파일 미커밋/미푸시 차단 |
| [tdd_enforce_stop](./hooks) | Edit/Write 후 검증 없으면 차단 |

→ [훅 상세 설명](./hooks)

---

## 발동 방식 비교

```
superpowers 자동 발동        Claude Code 훅 강제
─────────────────────        ─────────────────────────
Claude가 description 보고     hooks.json → 인프라가
"이 스킬이 필요하다" 판단      PreToolUse/PostToolUse/Stop
→ 선택적으로 거를 수 없음       시점에 무조건 실행
                              → Claude 우회 불가
```

## 권장 사용 흐름

```bash
# 새 프로젝트 시작
/odd-onboarding            ← 수동: L0 목적 헌법 수립

# 아이디어 → 설계 (구현 전)
/brainstorming             ← 수동
/plan                      ← 수동

# 작업 시작 (pyramid-ontology는 자동 발동됨)

# 코드 작성 중
# → pyramid_ontology_gate: Edit 전에 L0 확인 (자동)
# → pyramid_guard 훅: Edit/Write마다 자동 검사
# → ontology-detach: binding 작성 시 자동 발동
/tdd                       ← 수동: TDD 사이클

# 비가역 행동 전
/careful                   ← 수동: 배포·삭제·외부 API 전

# 리팩토링 전
/pyramid-topology          ← 수동
# → ontology-review-gate: 구현 전 자동 발동

# 완료 후
/pyramid-label             ← 수동
/ontology-rebuild          ← 수동
/retro                     ← 수동: 세션 회고 + 메모리 진화
# → git_push_enforce_stop 훅: 응답 완료마다 자동 검사
# → tdd_enforce_stop 훅: 검증 없으면 차단
```
