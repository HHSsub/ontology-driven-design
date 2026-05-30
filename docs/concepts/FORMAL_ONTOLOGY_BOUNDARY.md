# What ODD Is NOT — Formal Ontology Boundary

이 문서는 ODD가 구현하지 않는 것들을 명확히 정의한다.

형식적 온톨로지 도구를 기대하고 ODD를 설치했다면, 이 문서를 먼저 읽기 바란다.

---

## ODD가 구현하지 않는 것

### ❌ OWL/RDF 표현

ODD는 Web Ontology Language(OWL), Resource Description Framework(RDF), Turtle, N-Triples 형식의 아티팩트를 생성하거나 파싱하지 않는다.

### ❌ SPARQL 쿼리

ODD의 어떤 구성요소도 SPARQL endpoint를 노출하거나 쿼리하지 않는다.

### ❌ 온톨로지 추론 (Reasoning)

클래스 계층으로부터 새로운 사실을 추론하는 reasoner가 없다. "A가 B의 서브클래스이고 B가 C의 서브클래스면 A는 C의 서브클래스"와 같은 추론은 ODD에서 수행되지 않는다.

### ❌ 기계 판독 가능한 개념 레지스트리 (현재)

`violation_registry.json`은 규칙 엔진이지만 형식적 개념 레지스트리가 아니다. 클래스/속성/관계를 선언적으로 정의하는 LinkML/JSON-LD/OWL 스키마는 현재 구현되지 않았다.

### ❌ Protégé 호환

ODD는 Protégé나 다른 온톨로지 편집기와 통합되지 않는다.

### ❌ 온톨로지 재사용 (Ontology Reuse)

Dublin Core, Schema.org, FOAF 같은 기존 온톨로지를 import하거나 재사용하는 기능이 없다.

---

## ODD가 구현하는 것

| 기능 | 구현 수단 |
|------|----------|
| 목적 선언 강제 | `pyramid_ontology_gate.py` — L0 없는 Edit/Write 차단 |
| 구조적 위반 탐지 | `violation_registry.json` + `ontology_violation_gate.py` |
| 단일 진실원 감시 | `pyramid_guard.py` — 중복 진실 탐지 |
| 의존성 체인 추적 | `pyramid_guard.py` — grep 증거 없는 열거형 변경 차단 |
| 에이전트 계층 강제 | `agent_pyramid_gate.py` — 역할 선언 없는 Agent 호출 차단 |
| 실수로부터 진화 | `ontology_learning_enforce_stop.py` + `/ontology-learning` 스킬 |

---

## 앞으로의 방향

ODD의 로드맵에는 다음이 포함된다 (현재 미구현):

- `ontology/concept-registry.yaml` — L0-L3와 연결된 개념 정의
- `schemas/odd.linkml.yaml` — LinkML 기반 스키마 (JSON Schema + OWL export 가능)
- `ontology/constraints.yaml` — 기계 판독 가능한 제약 조건

이 기능들이 구현되면 ODD는 "거버넌스 플러그인"에서 "machine-readable conceptual governance"로 진화한다. 현재는 그 방향을 향한 첫 단계다.

---

## 대안 도구 참고

형식적 온톨로지 엔지니어링이 필요하다면:

- **[LinkML](https://linkml.io/)** — YAML 기반 데이터 모델링, OWL/RDF export
- **[Protégé](https://protege.stanford.edu/)** — GUI 온톨로지 편집기
- **[ROBOT](http://robot.obolibrary.org/)** — 온톨로지 빌드 자동화
- **[Ontop](https://ontop-vkg.org/)** — 관계형 DB → 온톨로지 매핑
