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

### 2. 자동 강제 훅 (설치 즉시 발동)

플러그인 설치 후 다음 훅이 **자동으로** 매번 강제 발동됩니다:

| 훅 | 발동 시점 | 검사 내용 |
|----|-----------|-----------|
| `pyramid_guard` | Edit/Write 저장 시 | L0-L3 위계 정합성, SSOT 중복진실 탐지 |
| `ontology_declare_enforce` | 응답 완료 시 | L0 선언 존재 여부, 의존성 체인 검증 |
| `git_push_enforce` | 응답 완료 시 | 코드 변경 후 미커밋/미푸시 차단 |

**SSOT 강제**: 동일 개념 집합이 N개 독립 위치에 중복되면 자동 차단됩니다.
**의존성 체인**: 열거형 개념 모음 수정 시 grep 증거 없으면 차단됩니다.

### 3. 코드 작성 중 — 탈존재 점검

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
