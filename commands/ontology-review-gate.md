# /ontology-review-gate — 존재론 심판 게이트 (Ontology Review Court)

L0: 모든 수정안·계획·리팩토링·거버넌스 변경은 ontology 정합성을 증명하기 전까지 존재할 수 없다.

이 스킬은:

* 코드 작성 전
* 리팩토링 전
* budget 변경 전
* retry 정책 변경 전
* orchestration 수정 전
* agent topology 수정 전
* governance 수정 전

반드시 호출된다.

호출 없이 implementation을 시작하면 architecture violation이다.

---

# 핵심 원칙

이 스킬은:
"좋아보이는 수정"
을 평가하지 않는다.

오직:

* ontology integrity
* hierarchy purity
* execution economics
* topology stability
* adaptive governance

만 심판한다.

즉:
"작동할 것 같다"
는 merge 근거가 아니다.

---

# 강제 실행 순서

모든 수정안은 반드시 아래 순서를 따른다:

1. 수정안 제출
2. ontology-review-gate 호출
3. ontology court verdict 출력
4. REJECT/PASS 결정
5. PASS 이후에만 구현 가능

PASS 전 implementation 금지.

---

# 절대 금지 행동

다음은 기본적으로 REJECT 대상이다:

* magic number 추가
* static retry limit
* static token cap
* 특정 usecase 전용 if문
* hardcoded branch
* local patch
* detector 누더기 추가
* hierarchy contamination
* planner가 execution detail 인지
* leader가 raw text 접근
* repeated reread
* full regeneration
* uncontrolled recursion
* md만 쓰고 종료
* fake abstraction
* dead governance layer
* placeholder architecture

---

# Ontology Court 심사 항목

## [1] Ontology Traceability

모든 수정안은 반드시:

L0 Purpose
→ L1 Architecture
→ L2 Governance
→ L3 Execution

로 역추적 가능해야 한다.

역추적 불가능하면 REJECT.

---

## [2] Local Patch Detection

질문:
"이 수정은 증상만 막는가?"

다음이면 REJECT:

* if문 추가
* limit 숫자 조정
* retry 감소
* timeout 증가
* 특정 case만 우회

반드시 topology-level 설명 필요.

---

## [3] Hierarchy Purity

상위 계층은:

* code 접근 금지
* raw artifact 접근 금지
* implementation detail 접근 금지

하위 계층은:

* policy 변경 금지
* topology 변경 금지

위반 시 REJECT.

---

## [4] Adaptive Governance

다음은 REJECT:

* MAX_LOOP=12
* TOKEN=50000
* RETRY=3

같은 static constant.

반드시:

* complexity-aware
* entropy-aware
* progress-aware
* adaptive

해야 한다.

---

## [5] Execution Economics

모든 tool call은 비용 이벤트다.

다음을 분석하지 않으면 REJECT:

* reread amplification
* retry explosion
* context growth rate
* partial completion zone
* recursive reflection cost
* regeneration overhead

---

## [6] Recursive Stability

다음을 반드시 분석:

* retry recursion
* planner recursion
* critique recursion
* reflection loop
* self repair cycle

bounded proof 없으면 REJECT.

---

## [7] State Machine Integrity

단순 detector collection 금지.

반드시 존재해야 한다:

* state
* transition
* escalation
* halt
* recovery
* abort contract

없으면 REJECT.

---

## [8] Authority Boundary

모든 agent는 반드시 가진다:

* bounded authority
* bounded memory
* bounded visibility
* bounded token budget
* bounded recursion
* bounded tool access

하나라도 무제한이면 REJECT.

---

## [9] Ontology-Detach Validation

모든 binding에 교체조건이 존재해야 한다.

다음을 검사:

* 값
* 상태
* 의존성
* 가정
* 식별자
* 순서

교체조건 없으면 REJECT.

---

## [10] Future Topology Survivability

질문:

"새로운 agent topology가 추가되어도 유지되는가?"

특정 구조 가정 기반이면 REJECT.

---

# 출력 형식 강제

모든 수정안 검토 시 반드시 아래 형식 사용:

[ONTOLOGY COURT]

Proposal:

* 수정안 설명

Verdict:

* PASS / REJECT

Violations:

* ontology violation 목록

Topology Risk:

* future expansion risk
* hierarchy contamination risk
* recursion risk
* economic risk

Required Structural Fix:

* topology-level 수정 요구사항

Implementation Permission:

* PASS일 때만 허용

---

# 자동 호출 규칙

다음 상황에서는 자동 호출 mandatory:

* 새 agent 추가
* orchestration 수정
* retry 수정
* token budget 수정
* governance 수정
* tool policy 수정
* memory policy 수정
* context handling 수정
* reflection 추가
* detector 추가
* planner 수정
* hierarchy 변경
* execution flow 변경

호출 없이 구현 시작 시:
"ontology bypass violation" 으로 간주한다.

---

# 메타 원칙

이 스킬의 목적은:
"좋은 코드"
가 아니다.

목적은:

* ontology collapse 방지
* hierarchy contamination 방지
* recursive explosion 방지
* economic death spiral 방지
* topology rigidity 방지

이다.

수정 속도보다 ontology integrity가 우선이다.
