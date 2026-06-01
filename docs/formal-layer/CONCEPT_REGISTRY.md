# ODD Concept Registry — Human-Readable Reference

<!-- L0: ODD 핵심 개념을 기계와 인간 모두 이해할 수 있도록 문서화한다 -->
<!-- SSOT: 이 문서는 ontology/concept-registry.yaml의 human-readable 파생본이다.
     개념 정의를 수정할 때는 concept-registry.yaml을 먼저 수정하고 이 문서를 동기화한다. -->

**Machine-readable source:** [`ontology/concept-registry.yaml`](../../ontology/concept-registry.yaml)
**Schema:** [`schemas/odd.schema.json`](../../schemas/odd.schema.json)
**Version:** 1.0

---

## 피라미드 4계층 개념

### L0 / Purpose (목적 / 존재 이유)
**ID:** `odd:Purpose`
**별칭:** L0, Ontology Layer

코드 단위가 존재해야 하는 가장 근본적 이유. **도구나 플랫폼으로 표현될 수 없다.**

> "The deepest reason a code unit must exist. Cannot be stated in terms of tools or platforms."

**속성:**
- `must_not_reference_tools: true` — "L0: React로 렌더링한다"는 L3 관심사를 L0로 착각한 것
- `required_for_any_edit: true` — L0 없이 편집은 시작될 수 없다

**올바른 예:**
```
L0: 사용자가 의도를 잃지 않고 코드를 진화시킬 수 있도록 한다
L0: Teams can separate business purpose from implementation details
```

**잘못된 예 (도구 바인딩):**
```
L0: React를 사용하여 컴포넌트를 렌더링한다  ← L3 관심사
L0: AWS Lambda로 배포한다                   ← L3 관심사
```

---

### L1 / Architecture (구조 / 아키텍처)
**ID:** `odd:Architecture`
**별칭:** L1, Structure Layer
**상위:** `odd:Purpose`

L0를 현실로 끌어내리는 불변의 설계. **L0가 바뀔 때만 바뀐다.**

> "The invariant design that bridges L0 to reality. Changes only when L0 changes."

**담당 범위:** 시스템 경계, 모듈 계약, 데이터 흐름

---

### L2 / Decision (판단 / 트레이드오프)
**ID:** `odd:Decision`
**별칭:** L2, Logic Layer
**상위:** `odd:Architecture`

구조를 현실에 적용할 때 발생하는 선택. **모든 결정은 기회비용을 수반한다.**

> "Where architecture meets reality, forcing choices. Every decision carries opportunity cost."

**담당 범위:** 알고리즘 선택, 라이브러리 선택, 동시성 전략

---

### L3 / Execution (실행 / 구체)
**ID:** `odd:Execution`
**별칭:** L3, Instance Layer
**상위:** `odd:Decision`

가장 구체적인 실체: 코드, 설정, 물리적 행동. **유효성은 L2에서 파생된다.**

> "The concrete act: code, configuration, physical steps. Derives its validity from L2."

**담당 범위:** 함수, 클래스, 설정 파일, CLI 명령

---

## 안티패턴 개념

### Existence-Clinging (존재교착)
**ID:** `odd:ExistenceClinging`
**위반 대상:** `odd:Purpose`
**탐지 도구:** ontology-detach skill

코드나 설정이 특정 도구나 환경에 하드코딩되어 그것 없이 존재할 수 없는 상태.
구현 세부사항이 존재 이유가 되어 목적 레이어를 위반하는 존재론적 의존성.

> "When code or configuration is hardcoded to a specific tool or environment, unable to exist without it."

**증상:**
- L0 선언이 특정 도구를 주어로 참조한다
- exit_condition이 없거나 정의되지 않았다
- 하나의 도구를 제거하면 전체 모듈을 다시 써야 한다

**처방:** `ExitCondition` 선언 → 존재교착을 "선언된, 범위가 있는 약속"으로 전환

---

### Vibe-Code Drift (목적 표류)
**ID:** `odd:VibeDrift`
**예방 도구:** pyramid_ontology_gate PreToolUse hook

AI가 생성한 코드가 원래 L0 목적과 점점 멀어지는 현상.
반복적 프롬프팅이 선언된 목적보다 지역적 일관성을 최적화하게 할 때 발생한다.

> "The progressive loss of connection between AI-generated code and its original L0 purpose."

**조기 경고 신호:**
- 최근 편집에 L0 선언이 없다
- 코드 주석이 목적 대신 플랫폼 이름을 참조한다
- 함수명이 행동 대신 도구명을 따른다

---

## 원칙 개념

### Exit Condition (교체조건)
**ID:** `odd:ExitCondition`
**필요 조건:** `odd:ExistenceClinging` 존재 시 필수
**강제 도구:** ontology-detach skill

바인딩(도구, 플랫폼, 구현)이 더 이상 유효하지 않을 때를 미리 선언한 조건.

> "The stated condition under which a binding is no longer valid and must be replaced."

**형식:** `# ExitCondition: <조건 서술>`

**예시:**
```python
# ExitCondition: 프로젝트가 AWS 외 플랫폼으로 이전될 때
# ExitCondition: React dependency is removed from the project
# ExitCondition: 팀 규모가 10인 이하로 축소될 때
```

---

### SSOT (단일 진실원)
**ID:** `odd:SSOT`
**강제 도구:** pyramid_guard.py PostToolUse hook

동일한 개념의 정의가 코드베이스에서 정확히 한 곳에만 존재하는 상태.

> "A concept or definition exists in exactly one location. Duplication creates inevitable future inconsistency."

**결론:** 개념 정의를 수정하기 전, grep으로 모든 파생 표현을 먼저 탐색한다.

---

## 거버넌스 제약 요약

| ID | 레이블 | 강제 도구 | 자동 차단 |
|----|--------|----------|----------|
| `odd:C001` | L0 선언 필수 | pyramid_ontology_gate | YES |
| `odd:C002` | L0에 도구 바인딩 금지 | pyramid_guard.py | YES |
| `odd:C003` | 바인딩에 교체조건 필수 | ontology-detach skill | NO (수동) |
| `odd:C004` | SSOT — 개념 정의 중복 금지 | pyramid_guard.py | YES |
| `odd:C005` | 웹 검색 연도 가드 | websearch_yearguard | YES |

자세한 내용: [`ontology/constraints.yaml`](../../ontology/constraints.yaml)

---

## 개념 간 관계 요약

```
odd:Purpose
  ← governs_all: odd:Architecture
    ← governs: odd:Decision
      ← governs: odd:Execution

odd:ExistenceClinging → violates → odd:Purpose
odd:VibeDrift → erodes → odd:Purpose
odd:SSOT → supports → odd:Purpose
odd:ExitCondition → mitigates → odd:ExistenceClinging
```

전체 트리플: [`ontology/relationships.yaml`](../../ontology/relationships.yaml)
