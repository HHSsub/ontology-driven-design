# 시작하기

## 설치

```bash
# 풀네임
claude plugin add HHSsub/ontology-driven-design

# 단축명 (동일)
claude plugin add HHSsub/odd
```

## 기본 흐름

### 1. 세션 시작 — 목적 선언

어떤 작업이든 시작 전에 `/pyramid-ontology`를 호출하거나, 직접 선언합니다:

```
L0: [이 작업의 비즈니스 최종 목적]
L1: [이 작업의 시스템 목표]
L2: [지금 구현할 기능 단위]
```

### 2. 코드 작성 중 — 탈존재 점검

하드코딩이 생기거나 binding을 추가할 때:

```bash
/ontology-detach
```

자가질문: **"이 binding의 교체조건은 무엇인가?"** — 답이 "없음"이면 위반.

### 3. 리팩토링 전 — 위계 점검

```bash
/pyramid-topology
```

미라벨 단위, L0 오염, 고아 파일을 탐지합니다.

### 4. 구현 전 — 심판 게이트

```bash
/ontology-review-gate
```

PASS를 받아야만 코드를 짤 수 있습니다.

### 5. 완료 후 — 위상도 갱신

```bash
/ontology-rebuild
```

모든 폴더에 ONTOLOGY.md를 갱신합니다.

## 다음 단계

- [스킬 전체 목록](/skills/) — 각 스킬의 상세 사용법
- [피라미드사고법 철학](/philosophy) — ODD의 사상적 기반
