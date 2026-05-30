# 스킬 온톨로지 맵 — 피라미드 위계 기반 전체 스킬 분류

> 이 문서의 L0: 모든 스킬이 목적을 가지고, 그 목적이 위계적으로 연결되도록 보장한다.
> 목적 없이 존재하는 스킬은 없다.

---

## L0 (최상위 법칙 스킬)

| 스킬 | 목적 | 연결 |
|------|------|------|
| `pyramid-ontology` | 모든 행동이 최종 목적(L0)에 연결되도록 강제 | 모든 스킬의 상위 원칙 |
| `ontology-detach` | 모든 binding에 교체조건 강제 — 존재교착 방지 | pyramid-ontology의 구체 적용 |

### 전역 슬래시 커맨드 (모든 폴더·모든 프로젝트에서 사용 가능)

위치: `~/.claude/commands/` (글로벌). 슬래시 메뉴에 자동 등록.

| 커맨드 | 발동 효과 | 인자 |
|--------|----------|------|
| `/pyramid-ontology` | L0-L3 위계 헌법 발동 — 행동 전 L0 선언 강제 | 작업명 (선택) |
| `/ontology-detach` | 탈존재 원칙 발동 — binding 교체조건 강제 | 파일/폴더 (선택) |
| `/pyramid-label` | 파일·코드에 L0-L3 라벨 일괄 적용 | 파일/폴더 (선택) |
| `/pyramid-topology` | 시스템 전체의 위계 토폴로지 점검 | 범위 (선택) |

**Skill 도구 호출은 모두 자동 가능**: `Skill(skill="pyramid-ontology")` 등.
**커맨드 vs 스킬**: 커맨드는 사용자가 슬래시로 직접 발동, 스킬은 Claude가 작업 중 자동 invoke.

---

## L1 (개발 프로세스 강제)

이 스킬들이 없으면 L0 달성 경로가 깨진다.

> **외부 의존성 고지:** 아래 `superpowers:*` 스킬들은 [superpowers 플러그인](https://github.com/greptile/superpowers)을 별도 설치해야 사용 가능합니다.
> ODD만 단독 설치한 경우, 이 스킬들은 없어도 핵심 훅 강제(pyramid_ontology_gate, pyramid_guard 등)는 정상 작동합니다.
> ODD 자체 스킬만으로 완전한 거버넌스를 구성하는 방법: pyramid-ontology + ontology-review-gate + ontology-learning 3개로 기본 사이클 가능.

| 스킬 | 목적 | 언제 | 필요 플러그인 |
|------|------|------|-------------|
| `superpowers:test-driven-development` | 검증 없는 구현 금지 — 테스트 먼저 | 기능 구현/버그 수정 시 | superpowers |
| `superpowers:verification-before-completion` | 완료 선언 전 실제 동작 검증 강제 | 완료 보고 전 항상 | superpowers |
| `superpowers:systematic-debugging` | 증상 픽스가 아닌 근본 원인 추적 강제 | 버그/에러 발생 시 | superpowers |
| `superpowers:brainstorming` | 구현 전 설계 확인 강제 | 신기능/변경 전 | superpowers |
| `superpowers:writing-plans` | 구현 계획 구체화 | 설계 승인 후 | superpowers |
| `superpowers:executing-plans` | 계획 단계별 실행 | 계획 작성 후 | superpowers |

---

## L1 (안전 가드)

| 스킬/훅 | 목적 | 강제 방식 |
|---------|------|----------|
| `guard` / `careful` | 파괴적 명령(rm -rf, DROP TABLE 등) 차단 | PreToolUse 훅 |
| `tdd_enforce_stop.py` | Edit/Write 후 검증 없으면 Stop 차단 | Stop 훅 exit 2 |
| `pyramid_guard.py` | 백그라운드 함수 L0 주석 없으면 PostToolUse 차단 | PostToolUse 훅 exit 2 |

---

## L2 (에이전트 관리 도구)

| 스킬 | 목적 |
|------|------|
| `superpowers:subagent-driven-development` | 서브에이전트 태스크 분배 및 리뷰 |
| `superpowers:dispatching-parallel-agents` | 병렬 서브에이전트 조율 |
| `superpowers:using-superpowers` | 스킬 시스템 진입점 — 세션 시작 시 |
| `superpowers:using-git-worktrees` | 격리된 작업 공간 생성 |
| `superpowers:finishing-a-development-branch` | 브랜치 완료 절차 |
| `superpowers:requesting-code-review` | 코드 리뷰 요청 |
| `superpowers:receiving-code-review` | 코드 리뷰 수행 |
| `superpowers:writing-skills` | 스킬 자체 작성 가이드 |

---

## L2 (코드 품질)

| 스킬 | 목적 |
|------|------|
| `qa` / `qa-only` | 웹앱 QA 및 버그 수정 |
| `review` | 코드 리뷰 |
| `health` | 시스템 상태 확인 |
| `investigate` | 원인 탐색 |

---

## L2 (UI/디자인 도구)

| 스킬 | 목적 |
|------|------|
| `design-review` | 시각적 QA |
| `design-html` | HTML 목업 생성 |
| `design-consultation` | 디자인 방향 상담 |
| `design-shotgun` | 빠른 다중 디자인 안 생성 |

---

## L3 (gstack 에코시스템 유틸리티) — 수정 금지 (auto-generated)

이 스킬들은 gstack 시스템이 자동 생성/관리. 직접 수정 시 다음 업데이트에 덮어씌워짐.

`autoplan`, `benchmark`, `benchmark-models`, `browse`, `canary`, `codex`, `connect-chrome`,
`context-restore`, `context-save`, `cso`, `devex-review`, `document-release`, `freeze`, `unfreeze`,
`gstack`, `gstack-upgrade`, `land-and-deploy`, `landing-report`, `learn`, `make-pdf`,
`office-hours`, `open-gstack-browser`, `pair-agent`, `plan-ceo-review`, `plan-design-review`,
`plan-devex-review`, `plan-eng-review`, `plan-tune`, `retro`, `scrape`, `setup-browser-cookies`,
`setup-deploy`, `setup-gbrain`, `ship`, `skillify`, `sync-gbrain`

---

## 스킬 없는 상태의 기본 원칙

어떤 스킬도 없이 zero-context 서브에이전트가 투입된 경우:
1. CLAUDE.md의 피라미드 위계 섹션 → 헌법
2. 파일/코드 상단의 L0~L3 주석 → 해당 파일의 법률
3. 둘 다 없으면 → L0를 물어보고 나서 진행
