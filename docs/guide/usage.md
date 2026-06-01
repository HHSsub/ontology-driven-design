# 기본 사용법 / Basic Usage

[시작하기](./getting-started)를 먼저 읽어주세요.

---

## 전체 스킬 목록 / Complete Skill Reference

ODD는 8개 스킬을 제공합니다 / ODD provides 8 skills:

### `/pyramid-ontology` — 세션 목적 선언 / Declare session purpose

모든 작업의 시작점. 어떤 작업이든 이 선언 없이 파일 수정 불가.

The starting point for any task. File edits are blocked without this declaration.

```
/pyramid-ontology
```

또는 직접 선언 / Or declare directly:

```
L0: [이 작업의 비즈니스 최종 목적]
L1: [이 작업의 시스템 목표]
L2: [지금 구현할 기능 단위]
```

---

### `/odd-onboarding` — 프로젝트 목적 확정 / Establish project purpose

구현 전에 프로젝트 또는 기능의 존재 목적을 확정합니다.

Establishes the purpose of a project or feature before any implementation begins.

**사용 시점 / When to use:**
- 새 프로젝트를 시작하기 전 / Before starting a new project
- 새 기능을 추가하기 전 / Before adding a new feature
- 방향이 불명확한 상태에서 구현을 시작하려 할 때 / When direction is unclear

5개 영역의 자연어 질문을 통해 L0-L3 온톨로지를 확정하고 `ONBOARDING.md`를 생성합니다.

Asks 5 areas of plain-language questions and outputs `ONBOARDING.md` — the project's constitution.

```
/odd-onboarding
```

자세한 내용: [odd-onboarding 스킬](../skills/odd-onboarding.md)

---

### `/ontology-detach` — 탈존재 점검 / Detach check

하드코딩이 생기거나 binding을 추가할 때 사용. "이 binding의 교체조건은 무엇인가?"

Use when adding hardcoded values or bindings. Asks: "What is the replacement condition for this binding?"

```
/ontology-detach
```

답이 "없음"이면 위반입니다 / If the answer is "none," it's a violation.

---

### `/ontology-review-gate` — 구현 전 심판 게이트 / Pre-implementation court

구현 전에 반드시 통과해야 하는 온톨로지 법원.

The ontology court that must be passed before writing implementation code.

```
/ontology-review-gate
```

PASS를 받아야만 코드를 짤 수 있습니다 / PASS required before writing any code.

---

### `/pyramid-topology` — 위계 정합성 스캔 / Hierarchy integrity scan

리팩토링 전 전체 위계 정합성을 점검합니다.

Scans the entire codebase hierarchy before refactoring.

```
/pyramid-topology
```

미라벨 단위, L0 오염, 고아 파일을 탐지합니다 / Detects unlabeled units, L0 contamination, orphan files.

---

### `/pyramid-label` — 코드 단위 라벨링 / Label code units

모든 코드 단위에 L0-L3 라벨을 적용합니다.

Applies L0-L3 labels to all code units in a file or directory.

```
/pyramid-label
```

코드 리뷰 전에 사용 / Use before code review.

---

### `/ontology-learning` — 실수에서 온톨로지 진화 / Evolve ontology from mistakes

실수가 발생했을 때 단순 수정이 아닌 사고 레이어를 역추적해 L0~L3 전체를 재설계합니다.

When a mistake occurs, traces back through reasoning layers instead of patching the symptom.

**사용 시점 / When to use:**
- 유저가 Claude의 출력을 수정할 때 / When the user corrects Claude's output
- Claude가 잘못된 방향으로 진행했을 때 / When Claude went in the wrong direction
- 실수가 반복되는 패턴이 보일 때 / When a mistake pattern repeats

실행 순서 / Execution sequence:
```
Phase 1: 현상 포착 (capture the phenomenon)
Phase 2: 판단 역추적 (trace the judgment failure)
Phase 3: 구조 부재 진단 (diagnose structural absence)
Phase 4: 세계관 추출 (extract worldview principle)
Phase 5: 메모리 저장 (write to memory) ← 생략 시 실패 / skip = failure
Phase 6: 훅 평가 (evaluate hooks)
```

```
/ontology-learning
```

자세한 내용: [ontology-learning 스킬](../skills/ontology-learning.md)

---

### `/ontology-rebuild` — 위상도 갱신 / Rebuild topology

작업 완료 후 모든 폴더의 ONTOLOGY.md를 갱신합니다.

Updates ONTOLOGY.md in all folders after a major change.

```
/ontology-rebuild
```

---

## 일반적인 워크플로우 / Common Workflow

```
1. /pyramid-ontology  (또는 직접 L0 선언)
2. /ontology-review-gate  (중요 기능의 경우)
3. 코드 작성
4. /ontology-detach  (하드코딩 발생 시)
5. 검증 실행 (pytest / npm test / py_compile)
6. git commit + push
7. /ontology-rebuild  (주요 변경 완료 시)
```

---

## 훅 자동 발동 / Automatic Hook Triggers

스킬 외에도 10개의 훅이 자동으로 발동됩니다.

In addition to skills, 10 hooks fire automatically:

| 훅 / Hook | 발동 시점 / Trigger | 효과 / Effect |
|-----------|-------------------|--------------|
| `pyramid_ontology_gate` | Edit/Write 전 | L0 없으면 수정 차단 |
| `ontology_violation_gate` | Edit/Write 전 | violation_registry 규칙 위반 차단 |
| `websearch_yearguard` | WebSearch 전 | 연도 없는 검색 차단 |
| `pyramid_guard` | Edit/Write 후 | L 레벨 정합성 + SSOT 검증 |
| `ontology_declare_enforce` | 세션 종료 | L0 선언 여부 검증 |
| `tdd_enforce_stop` | 세션 종료 | 코드 수정 후 검증 실행 여부 |
| `git_push_enforce_stop` | 세션 종료 | 미커밋/미푸시 차단 |

전체 훅 설명: [훅 레퍼런스](../skills/hooks.md)

---

## 다음 단계 / Next Steps

- [5분 퀵스타트](../quickstart.md) — 훅 차단을 직접 경험
- [솔로 개발자 워크플로우](../examples/solo-developer.md) — 하루 작업 사이클
- [레거시 코드에 ODD 적용](../examples/legacy-refactor.md) — 점진적 도입
- [스킬 전체 목록](../skills/) — 각 스킬 상세 설명
- [피라미드사고법 철학](../philosophy.md) — ODD의 사상적 기반
