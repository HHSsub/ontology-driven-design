---
name: ontology-review-gate
description: Mandatory gate before any implementation, refactor, or architecture change. Runs an Ontology Court review — checks hierarchy purity, adaptive governance, execution economics, and recursive stability. Returns PASS or REJECT with required structural fixes.
---

# /ontology-review-gate — 존재론 심판 게이트 (Ontology Review Court)

L0: 모든 수정안·계획·리팩토링·거버넌스 변경은 ontology 정합성을 증명하기 전까지 존재할 수 없다.

이 스킬은 다음 상황에서 **반드시** 호출된다:
- 코드 작성 전
- 리팩토링 전
- budget 변경 전
- retry 정책 변경 전
- orchestration 수정 전
- agent topology 수정 전
- governance 수정 전

호출 없이 implementation을 시작하면 **architecture violation**이다.

---

## 핵심 원칙

이 스킬은 "좋아보이는 수정"을 평가하지 않는다.

오직:
- ontology integrity
- hierarchy purity
- execution economics
- topology stability
- adaptive governance

만 심판한다.

"작동할 것 같다"는 merge 근거가 아니다.

---

## 강제 실행 순서

1. 수정안 제출
2. ontology-review-gate 호출
3. ontology court verdict 출력
4. REJECT/PASS 결정
5. **PASS 이후에만 구현 가능**

---

## 절대 금지 행동 (기본 REJECT 대상)

- magic number 추가
- static retry limit
- static token cap
- 특정 usecase 전용 if문
- hardcoded branch
- hierarchy contamination
- planner가 execution detail 인지
- leader가 raw text 접근
- uncontrolled recursion
- fake abstraction
- dead governance layer
- placeholder architecture

---

## Ontology Court 심사 항목

### [1] Ontology Traceability
모든 수정안은 L0 → L1 → L2 → L3로 역추적 가능해야 한다.
역추적 불가능하면 REJECT.

### [2] Local Patch Detection
"이 수정은 증상만 막는가?"
if문 추가·limit 숫자 조정·특정 case 우회 → REJECT.
반드시 topology-level 설명 필요.

### [3] Hierarchy Purity
상위 계층: code 접근 금지, raw artifact 접근 금지
하위 계층: policy 변경 금지, topology 변경 금지
위반 시 REJECT.

### [4] Adaptive Governance
`MAX_LOOP=12`, `TOKEN=50000`, `RETRY=3` 같은 static constant → REJECT.
반드시 complexity-aware, entropy-aware, progress-aware, adaptive해야 한다.

### [5] Execution Economics
모든 tool call은 비용 이벤트다.
reread amplification, retry explosion, context growth rate 분석 없으면 REJECT.

### [6] Recursive Stability
retry recursion, planner recursion, reflection loop 분석 필수.
bounded proof 없으면 REJECT.

### [7] State Machine Integrity
state, transition, escalation, halt, recovery, abort contract 모두 존재해야 한다.
없으면 REJECT.

### [8] Authority Boundary
모든 agent는 bounded authority, bounded memory, bounded visibility, bounded token budget을 가진다.
하나라도 무제한이면 REJECT.

### [9] Ontology-Detach Validation
모든 binding(값/상태/의존성/가정/식별자/순서)에 교체조건이 존재해야 한다.
교체조건 없으면 REJECT.

### [10] Future Topology Survivability
"새로운 agent topology가 추가되어도 유지되는가?"
특정 구조 가정 기반이면 REJECT.

---

## 출력 형식

```
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
```

---

## 메타 원칙

이 스킬의 목적은 "좋은 코드"가 아니다.

목적은:
- ontology collapse 방지
- hierarchy contamination 방지
- recursive explosion 방지
- economic death spiral 방지
- topology rigidity 방지

수정 속도보다 ontology integrity가 우선이다.
