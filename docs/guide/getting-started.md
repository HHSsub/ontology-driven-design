# 시작하기

## 설치

> **참고**: `claude plugin add` 명령어는 Claude Code 버전에 따라 동작이 다를 수 있습니다. 정상 동작하지 않으면 수동 설치 가이드를 사용하세요.

```bash
# 플러그인 설치 시도
claude plugin add HHSsub/ontology-driven-design
```

**수동 설치 (항상 작동):** [설치 가이드](installation.md) 참고

---

## 기본 흐름

### 1. 세션 시작 — 목적 선언

어떤 작업이든 시작 전에 `/pyramid-ontology`를 호출하거나, 직접 선언합니다:

```
L0: [이 작업의 비즈니스 최종 목적]
L1: [이 작업의 시스템 목표]
L2: [지금 구현할 기능 단위]
```

### 2. 자동 강제 훅 (설치 즉시 발동)

플러그인 설치 후 다음 훅이 **자동으로** 발동됩니다:

| 훅 | 발동 시점 | 검사 내용 |
|----|-----------|-----------|
| `pyramid_ontology_gate` | Edit/Write 전 | 세션에 L0 선언이 없으면 수정 차단 |
| `ontology_violation_gate` | Edit/Write 전 | violation_registry.json 규칙 위반 차단 |
| `destructive_bash_gate` | Bash 실행 전 | 위험한 명령어 차단 |
| `agent_pyramid_gate` | Agent 호출 전 | L0 미션 + 역할 선언 없는 서브에이전트 차단 |
| `pyramid_guard` | Edit/Write 후 | L0-L3 위계 정합성, SSOT 중복진실 탐지 |
| `ontology_declare_enforce` | 응답 완료 시 | L0 선언 존재 여부 검증 |
| `git_push_enforce_stop` | 응답 완료 시 | 미커밋/미푸시 코드 변경 차단 |
| `tdd_enforce_stop` | 응답 완료 시 | 코드 파일 수정 후 검증 미실행 차단 |

### 3. 코드 작성 중 — 탈존재 점검

하드코딩이 생기거나 binding을 추가할 때:

```bash
/ontology-detach
```

자가질문: **"이 binding의 교체조건은 무엇인가?"** — 답이 "없음"이면 위반.

### 4. 리팩토링 전 — 위계 점검

```bash
/pyramid-topology
```

미라벨 단위, L0 오염, 고아 파일을 탐지합니다.

### 5. 구현 전 — 심판 게이트

```bash
/ontology-review-gate
```

PASS를 받아야만 코드를 짤 수 있습니다.

### 6. 실수 후 — 온톨로지 학습

```bash
/ontology-learning
```

실수를 L3→L2→L1→L0 역추적하여 원칙을 영구 진화시킵니다.

### 7. 완료 후 — 위상도 갱신

```bash
/ontology-rebuild
```

모든 폴더에 ONTOLOGY.md를 갱신합니다.

---

## 다음 단계

- [스킬 전체 목록](/skills/) — 각 스킬의 상세 사용법
- [피라미드사고법 철학](/philosophy) — ODD의 사상적 기반
