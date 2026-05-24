# 스킬 목록

ODD는 스킬(수동 호출)과 훅(자동 발동) 두 가지 방식으로 동작합니다.

## 스킬 — 수동 호출 (`/커맨드`)

| 스킬 | 슬래시 커맨드 | 사용 시점 |
|------|------------|---------|
| [odd-onboarding](./odd-onboarding) | `/odd-onboarding` | **프로젝트/기능 시작 전** — L0 목적 확정 |
| [pyramid-ontology](./pyramid-ontology) | `/pyramid-ontology` | **모든 작업 시작 전** — L0-L3 선언 |
| [ontology-detach](./ontology-detach) | `/ontology-detach` | 코드 binding 작성/검토 시 |
| [ontology-rebuild](./ontology-rebuild) | `/ontology-rebuild` | 주요 변경 후 위상도 갱신 |
| [pyramid-label](./pyramid-label) | `/pyramid-label` | 코드 리뷰 전 라벨 일괄 적용 |
| [pyramid-topology](./pyramid-topology) | `/pyramid-topology` | 리팩토링 전 위계 점검 |
| [ontology-review-gate](./ontology-review-gate) | `/ontology-review-gate` | 구현 전 ontology court |

## 훅 — 자동 강제 발동 (사용자 명령 불필요)

| 훅 | 발동 시점 | 검사 내용 |
|----|----------|---------|
| [pyramid_guard](./hooks) | Edit/Write 저장 시마다 | L 레벨 정합성 + SSOT 위반 |
| [ontology_declare_enforce](./hooks) | 응답 완료 시마다 | L0 선언 존재 + 의존성 체인 |
| [git_push_enforce](./hooks) | 응답 완료 시마다 | 수정 파일 미커밋/미푸시 차단 |

→ [훅 상세 설명](./hooks)

## 스킬 위계

```
odd-onboarding            ← 시작 전 — 프로젝트 목적 헌법 수립
pyramid-ontology          ← 최상위 — 모든 스킬의 헌법
  ├── ontology-detach     ← L0의 구체적 적용 (binding 교체조건)
  ├── ontology-rebuild    ← 위상도 문서화
  ├── pyramid-label       ← 코드 단위 라벨링
  ├── pyramid-topology    ← 위계 정합성 검증
  └── ontology-review-gate ← 구현 전 심판
```

## 권장 사용 순서

```bash
# 0. 프로젝트/기능 시작 전
/odd-onboarding

# 1. 세션 시작
/pyramid-ontology

# 2. 코드 작성 중 (훅이 자동으로 SSOT·L0 오염 감시)
/ontology-detach

# 3. 리팩토링 전
/pyramid-topology
/ontology-review-gate

# 4. 완료 후
/pyramid-label
/ontology-rebuild
```
