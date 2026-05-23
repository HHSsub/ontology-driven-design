# 스킬 목록

ODD는 6개의 스킬로 구성됩니다. 각 스킬은 피라미드사고법의 특정 원칙을 적용합니다.

## 핵심 스킬

| 스킬 | 슬래시 커맨드 | 사용 시점 |
|------|------------|---------|
| [pyramid-ontology](./pyramid-ontology) | `/pyramid-ontology` | **모든 작업 시작 전** — L0-L3 선언 |
| [ontology-detach](./ontology-detach) | `/ontology-detach` | 코드 binding 작성/검토 시 |
| [ontology-rebuild](./ontology-rebuild) | `/ontology-rebuild` | 주요 변경 후 위상도 갱신 |
| [pyramid-label](./pyramid-label) | `/pyramid-label` | 코드 리뷰 전 라벨 일괄 적용 |
| [pyramid-topology](./pyramid-topology) | `/pyramid-topology` | 리팩토링 전 위계 점검 |
| [ontology-review-gate](./ontology-review-gate) | `/ontology-review-gate` | 구현 전 ontology court |

## 스킬 위계

```
pyramid-ontology          ← 최상위 — 모든 스킬의 헌법
  ├── ontology-detach     ← L0의 구체적 적용 (binding 교체조건)
  ├── ontology-rebuild    ← 위상도 문서화
  ├── pyramid-label       ← 코드 단위 라벨링
  ├── pyramid-topology    ← 위계 정합성 검증
  └── ontology-review-gate ← 구현 전 심판
```

## 권장 사용 순서

```bash
# 1. 세션 시작
/pyramid-ontology

# 2. 코드 작성 중
/ontology-detach

# 3. 리팩토링 전
/pyramid-topology
/ontology-review-gate

# 4. 완료 후
/pyramid-label
/ontology-rebuild
```
