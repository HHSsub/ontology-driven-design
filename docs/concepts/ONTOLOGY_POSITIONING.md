# ODD에서 "온톨로지"가 의미하는 것

## 이 문서의 목적

ODD의 이름에는 "Ontology"가 들어간다. 이 단어는 컴퓨터과학에서 정확한 기술적 의미를 가지며, 그 의미는 ODD가 구현하는 것과 다르다. 이 문서는 그 차이를 명확히 한다.

---

## ODD에서 "온톨로지"의 의미

ODD에서 온톨로지는 **존재 이유의 위계**를 뜻한다.

> "이것은 왜 존재하는가?"

이 질문에 답하는 L0-L3 계층 구조가 ODD의 "온톨로지"다. 이것은 철학적 의미의 존재론(ontology)에서 차용한 개념이다 — 각 코드 단위가 "왜 존재해야 하는지"를 명시적으로 선언하도록 강제한다.

### L0-L3 위계

```
L0  존재 이유      — "왜 이것이 있어야 하는가?" (목적의 근거)
L1  구조/설계      — "어떤 구조로 L0에 도달하는가?"
L2  판단/트레이드오프 — "L1을 현실에 적용할 때 어떤 선택을 했는가?"
L3  실행/구체      — "실제로 무엇이 코드로 존재하는가?"
```

---

## ODD가 구현하지 않는 것

### 형식적 온톨로지 (Formal Ontology Engineering)

OWL(Web Ontology Language), RDF(Resource Description Framework), SPARQL 쿼리, Protégé 편집, 추론 엔진(reasoner), 시맨틱 웹 아티팩트 — ODD는 이것들을 구현하지 않는다.

형식적 온톨로지는 기계가 읽을 수 있는 클래스 계층, 속성 정의, 제약 조건을 선언적으로 표현한다. 이것은 Protégé, LinkML, ROBOT 같은 도구의 영역이다.

**ODD는 이 도구들의 대안이 아니다.**

### ODD vs. 형식적 온톨로지 도구 비교

| | ODD | 형식적 온톨로지 도구 |
|---|---|---|
| 목적 | AI 코딩 에이전트 거버넌스 | 지식 표현 및 추론 |
| 표현 방식 | Markdown + Python hooks | OWL/RDF/LinkML |
| 기계 판독 | 부분적 (violation_registry.json) | 완전 (OWL reasoning) |
| 대상 | Claude Code 사용자 | 온톨로지 엔지니어, 시맨틱 웹 개발자 |
| 즉시 사용성 | Claude Code 설치 후 즉시 | 도메인 모델링 전문성 필요 |

---

## ODD의 실제 포지션

ODD는 **목적 거버넌스 레이어(purpose-governed engineering layer)**다.

AI 코딩 에이전트가 구현(L3)에 집중하면서 목적(L0)을 잃어버리는 문제를 막는다. 코드 변경이 일어나기 전에 "왜 이것을 하는가?"를 강제한다.

이것은 형식적 온톨로지 엔지니어링이 아니다. 그러나 그 이름을 쓰는 이유는, 이 접근법이 목적의 존재론적 질문("왜 이것이 있어야 하는가?")을 개발 프로세스의 중심에 놓기 때문이다.

---

## 참고

- ODD의 L0-L3 계층은 [Pyramid Thinking (피라미드사고법)](https://knowgram.vercel.app)에서 파생됐다
- 형식적 온톨로지 도구가 필요하다면: [LinkML](https://linkml.io/), [Protégé](https://protege.stanford.edu/), [ROBOT](http://robot.obolibrary.org/)
- ODD의 미래 로드맵에는 concept registry와 LinkML schema 추가가 포함된다 — 현재는 구현되지 않았다
