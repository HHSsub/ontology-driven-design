# ODD 용어집

ODD에서 사용하는 용어들의 실무적 정의. 철학적 원어와 개발자 친화적 번역을 병기한다.

---

## L0 / L1 / L2 / L3

**핵심 4계층.** 모든 코드 단위, 결정, 산출물은 이 계층 중 하나에 속한다.

| 레벨 | 용어 | 실무 의미 | 질문 |
|------|------|----------|------|
| L0 | Purpose / 존재 이유 | 이것이 없으면 무엇이 실패하는가 | "Why does this exist?" |
| L1 | Architecture / 구조 | L0를 달성하는 불변 설계 | "What is the invariant design?" |
| L2 | Decision / 판단 | 구조를 현실에 적용할 때 선택한 것 | "What did we choose and why?" |
| L3 | Execution / 실행 | 실제 코드, 설정, 구체적 행동 | "What is the concrete act?" |

**L0 없이 L3는 존재할 수 없다** — ODD의 핵심 규칙.

---

## Existence-Clinging / 존재교착

**정의:** 코드나 설정이 특정 도구, 플랫폼, 환경에 하드코딩되어 그것 없이는 존재할 수 없는 상태.

**실무 예시:**
- `if platform == "Windows":` — 플랫폼 종속
- `API_KEY = "sk-abc123"` — 인증 하드코딩
- `path = "C:/Users/User/.claude/..."` — 사용자 환경 종속

**ODD 처방:** `/ontology-detach` — 모든 binding에 교체 조건을 명시한다.

---

## Exit Condition / 교체조건

**정의:** "이 binding이 더 이상 유효하지 않을 때"를 미리 선언한 조건.

**예시:**
```
# 교체조건: Windows 전용 배포에서 Linux 배포로 전환 시
platform_path = "C:/Users/..."
```

교체조건이 없는 binding은 ODD에서 위반이다.

---

## SSOT / 단일 진실원 (Single Source of Truth)

**정의:** 동일한 개념의 정의가 코드베이스에서 정확히 한 곳에만 존재하는 상태.

**위반 예시:** 동일한 상태 코드 목록이 `constants.py`, `types.ts`, `README.md` 세 곳에 각각 정의된 경우. 하나가 변경되면 나머지 두 개는 구식이 된다.

**ODD 강제:** `pyramid_guard.py`가 Post-Write 시 중복 진실 탐지.

---

## Ontology-Learning / 온톨로지 학습

**정의:** 실수를 L3(증상) → L2(판단) → L1(구조) → L0(세계관) 순서로 역추적하여 근본 원인을 찾고, 그것을 메모리와 강제 메커니즘으로 영구화하는 과정.

**패칭과의 차이:**
- 패칭: "다음엔 이 변수명을 쓸게" (L3 수준)
- 온톨로지 학습: "파라미터를 원본 확인 없이 가정하는 판단 구조 자체가 잘못됐다" (L0 수준)

---

## Pyramid Thinking / 피라미드사고법

**정의:** 어떤 산출물이든 L0-L3 위계로 조직하는 사고 방법론. 황회선이 창안.

ODD는 이 방법론을 AI 코딩 에이전트 거버넌스에 적용한 것이다.

---

## Vibe-Code Drift

**정의:** AI 코딩 에이전트가 명확한 목적 없이 코드를 생성하면서 원래 목표에서 점점 멀어지는 현상.

ODD의 핵심 해결 대상. `pyramid_ontology_gate` + `ontology_declare_enforce`가 이 현상을 구조적으로 차단한다.

---

## Hook / 훅

**정의:** Claude Code가 특정 도구를 실행하기 전(PreToolUse) 또는 후(PostToolUse), 또는 세션 종료 시(Stop)에 자동으로 실행하는 Python 스크립트.

ODD의 훅은 강제 메커니즘이다 — 위반 시 `exit(2)`로 해당 행동을 차단한다.

---

## Violation Registry / 위반 레지스트리

**정의:** `hooks/violation_registry.json`에 저장된 규칙 목록. 각 규칙은 "어떤 파일에서 어떤 구조가 없으면 차단"을 정의한다.

`ontology_violation_gate.py`가 이 파일을 읽고 모든 Edit/Write에 적용한다.

새 실수 발생 시 `/ontology-learning`으로 이 파일에 새 규칙을 추가한다.
