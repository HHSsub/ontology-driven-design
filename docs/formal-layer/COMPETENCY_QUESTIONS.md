# ODD Ontology Competency Questions

<!-- L0: ODD 온톨로지가 "답할 수 있는 질문"을 명시하여 온톨로지 완전성을 검증한다 -->
<!-- 출처: concept-registry.yaml의 개념 체계로부터 파생 -->

Competency Questions(역량 질문)은 온톨로지가 반드시 답해야 하는 질문 목록이다.
ODD 온톨로지가 이 질문에 답할 수 없다면 개념 체계가 불완전하다는 신호다.

---

## 1. 개념 정의 질문 (What is X?)

**Q1.** "이 파일의 L0는 무엇인가?"
- **참조 개념:** `odd:Purpose`
- **답변 방법:** 파일 헤더의 `# L0:` 주석을 추출. concept-registry.yaml의 `odd:Purpose.properties.required_for_any_edit` 검증.
- **기계적 쿼리:** `grep -n "^# L0:" <file>`

**Q2.** "이 코드 단위는 피라미드의 어느 레이어에 속하는가?"
- **참조 개념:** `odd:Purpose`, `odd:Architecture`, `odd:Decision`, `odd:Execution`
- **답변 방법:** 파일 헤더의 `# L0/L1/L2/L3:` 레이블 파싱.
- **기계적 쿼리:** `grep -n "^# L[0-3]:" <file>`

**Q3.** "존재교착이란 무엇인가?"
- **참조 개념:** `odd:ExistenceClinging`
- **답변 방법:** concept-registry.yaml의 `odd:ExistenceClinging.definition` 반환.

**Q4.** "교체조건의 올바른 형식은 무엇인가?"
- **참조 개념:** `odd:ExitCondition`
- **답변 방법:** `odd:ExitCondition.format` 필드 반환 → `# ExitCondition: <조건 서술>`

---

## 2. 위반 탐지 질문 (Is X violating Y?)

**Q5.** "이 L0 선언이 도구 바인딩을 포함하는가?"
- **참조 제약:** `odd:C002`
- **참조 개념:** `odd:ExistenceClinging`
- **답변 방법:** L0 선언이 도구명(React, AWS, Python, etc.)을 주어로 포함하는지 패턴 매칭.
- **기계적 쿼리:** constraints.yaml의 `odd:C002` → hook_file `hooks/pyramid_guard.py` 실행

**Q6.** "이 코드 파일이 SSOT를 위반하는가?"
- **참조 제약:** `odd:C004`
- **참조 개념:** `odd:SSOT`
- **답변 방법:** 동일한 개념 정의가 N > 1곳에 존재하는지 grep 탐색.
- **기계적 쿼리:** `grep -rn "<concept_text>" .` → 2개 이상 결과 = 위반

**Q7.** "이 편집이 L0 선언 없이 시작되었는가?"
- **참조 제약:** `odd:C001`
- **답변 방법:** pyramid_ontology_gate.py의 PreToolUse 훅이 반환한 exit_code 확인.
- **exit_code 2** = 차단됨 (L0 없음), **exit_code 0** = 통과

**Q8.** "이 바인딩에 교체조건이 선언되어 있는가?"
- **참조 개념:** `odd:ExitCondition`
- **참조 제약:** `odd:C003`
- **답변 방법:** 바인딩 코드 주변 `# ExitCondition:` 주석 탐색.
- **기계적 쿼리:** `grep -n "ExitCondition:" <file>`

**Q9.** "이 세션이 목적 표류(VibeDrift) 상태인가?"
- **참조 개념:** `odd:VibeDrift`
- **답변 방법:**
  1. 최근 5개 편집에 L0 선언이 있는가?
  2. 함수명이 도구명을 포함하는가?
  3. 주석이 플랫폼을 목적으로 설명하는가?
- 3개 중 2개 이상 해당 시 = VibeDrift 위험

---

## 3. 구조 쿼리 질문 (What governs X?)

**Q10.** "odd:Decision을 지배하는 상위 개념은 무엇인가?"
- **참조 관계:** `odd:Architecture governs odd:Decision`
- **답변 방법:** relationships.yaml에서 `object: odd:Decision` 트리플 조회 → `subject: odd:Architecture`

**Q11.** "odd:Purpose를 침식하는 안티패턴은 무엇인가?"
- **참조 관계:** `odd:VibeDrift erodes odd:Purpose`, `odd:ExistenceClinging violates odd:Purpose`
- **답변 방법:** relationships.yaml에서 `object: odd:Purpose`이고 predicate가 `violates` 또는 `erodes`인 트리플 조회

**Q12.** "어떤 훅이 odd:C001을 강제하는가?"
- **참조 제약:** `odd:C001`
- **답변 방법:** constraints.yaml에서 `id: odd:C001` → `hook_file: hooks/pyramid_ontology_gate.py`

**Q13.** "자동 강제되지 않는 제약은 무엇인가?"
- **답변 방법:** constraints.yaml에서 `auto_enforced: false` 필터링 → `odd:C003`

---

## 4. 관계 추론 질문 (Why does X exist?)

**Q14.** "ExitCondition이 왜 필요한가?"
- **추론 체인:**
  `odd:ExistenceClinging violates odd:Purpose` +
  `odd:ExitCondition mitigates odd:ExistenceClinging` +
  `odd:Purpose governs_all odd:Architecture`
- **결론:** ExistenceClinging이 피라미드를 역전시키므로, ExitCondition으로 바인딩의 범위를 제한해야 L0의 지배력이 회복된다.

**Q15.** "SSOT가 L0를 지지하는 이유는?"
- **추론 체인:**
  `odd:SSOT supports odd:Purpose`
- **설명:** 동일 개념의 복제가 있으면 어느 것이 "진짜" 정의인지 불분명해져 L0 선언의 권위가 희석된다.

**Q16.** "L3 코드를 L0 없이 작성하면 왜 위험한가?"
- **추론 체인:**
  `odd:Execution` → derives validity from → `odd:Decision` → derives validity from → `odd:Architecture` → derives validity from → `odd:Purpose`
- **결론:** 유효성 체인이 L0에서 끊기면 L3의 모든 유효성 근거가 사라진다 = VibeDrift 가속

---

## 5. 도구 연동 질문 (Which tool handles X?)

**Q17.** "존재교착을 탐지하는 도구는?"
- **답변:** `ontology-detach` skill → `skills/ontology-detach.md`

**Q18.** "L0 없는 편집을 자동 차단하는 훅은?"
- **답변:** `pyramid_ontology_gate.py` (PreToolUse, exit_code 2)

**Q19.** "SSOT 위반을 감지하는 훅은?"
- **답변:** `pyramid_guard.py` (PostToolUse)

**Q20.** "세션 종료 시 L0 선언을 검증하는 훅은?"
- **답변:** `ontology_declare_enforce.py` (Stop hook)

---

## 온톨로지 완전성 자가 체크

이 질문 목록으로 concept-registry.yaml을 검증하는 방법:

```bash
# Q1 검증: odd:Purpose가 정의되어 있는가?
python -c "
import yaml
with open('ontology/concept-registry.yaml') as f:
    reg = yaml.safe_load(f)
ids = [c['id'] for c in reg['concepts']]
assert 'odd:Purpose' in ids, 'odd:Purpose missing'
print('Q1 OK')
"

# Q12 검증: odd:C001에 hook_file이 있는가?
python -c "
import yaml
with open('ontology/constraints.yaml') as f:
    con = yaml.safe_load(f)
c001 = next(c for c in con['constraints'] if c['id'] == 'odd:C001')
assert 'hook_file' in c001, 'hook_file missing from odd:C001'
print('Q12 OK: hook_file =', c001['hook_file'])
"
```
