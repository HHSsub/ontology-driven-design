# 스킬 & 훅 목록

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

---

## 2. 상황별 수동 호출 (`/커맨드`)

특정 상황에서 사용자가 의도적으로 호출하는 스킬입니다.

| 스킬 | 슬래시 커맨드 | 사용 시점 |
|------|------------|---------|
| [odd-onboarding](./odd-onboarding) | `/odd-onboarding` | 새 프로젝트/기능 시작 전 — L0 목적 확정 |
| [pyramid-label](./pyramid-label) | `/pyramid-label` | 코드 리뷰 전, 새 파일 추가 후 |
| [pyramid-topology](./pyramid-topology) | `/pyramid-topology` | 리팩토링 전 위계 정합성 점검 |
| [ontology-rebuild](./ontology-rebuild) | `/ontology-rebuild` | 주요 변경 후 위상도 갱신 |

---

## 3. Claude Code 훅 — 인프라 레벨 강제

`~/.claude/settings.json`에 등록된 훅입니다.  
**Claude의 판단·superpowers 설치 여부와 무관하게** Claude Code 인프라가 발동시킵니다.

| 훅 | 타입 | 발동 시점 | 검사 내용 |
|----|------|----------|---------|
| [pyramid_ontology_gate](./hooks) | PreToolUse | Edit/Write **실행 전** | L0 선언 없으면 수정 자체 원천 차단 |
| [pyramid_guard](./hooks) | PostToolUse | Edit/Write 저장 시마다 | L 레벨 정합성 + SSOT 중복 진실 |
| [ontology_declare_enforce](./hooks) | Stop | 응답 완료 시마다 | L0 선언 존재 + 의존성 체인 검증 |
| [git_push_enforce](./hooks) | Stop | 응답 완료 시마다 | 수정 파일 미커밋/미푸시 차단 |

→ [훅 상세 설명](./hooks)

---

## 발동 방식 비교

```
superpowers 자동 발동        Claude Code 훅 강제
─────────────────────        ─────────────────────────
Claude가 description 보고     settings.json → 인프라가
"이 스킬이 필요하다" 판단      Edit/Stop 시점에 무조건 실행
→ 선택적으로 거를 수 없음       → Claude 우회 불가
```

## 권장 사용 흐름

```bash
# 새 프로젝트 시작
/odd-onboarding            ← 수동: L0 목적 헌법 수립

# 작업 시작 (pyramid-ontology는 자동 발동됨)

# 코드 작성 중
# → pyramid_guard 훅: Edit/Write마다 자동 검사
# → ontology-detach: binding 작성 시 자동 발동

# 리팩토링 전
/pyramid-topology          ← 수동
# → ontology-review-gate: 구현 전 자동 발동

# 완료 후
/pyramid-label             ← 수동
/ontology-rebuild          ← 수동
# → git_push_enforce 훅: 응답 완료마다 자동 검사
```
