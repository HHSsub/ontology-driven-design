# /ontology-learning — 클로드의 영구적 온톨로지 학습

L0: 실수를 패칭이 아닌 클로드의 실제 인식론적 진화로 전환한다.

이 커맨드는 **모든 프로젝트·모든 폴더에서** 호출 가능하다 (글로벌 등록).

## 즉시 수행할 것

1. `Skill` 도구로 `ontology-learning` 스킬을 invoke하라 — 그 스킬 본문이 이 세션의 학습 프로세스를 지배한다.
2. Phase 1~5를 순서대로 강제 실행한다.
3. Phase 5(메모리 저장)를 생략하면 이 커맨드 실행은 실패다.

## 자동 발동 조건

다음 중 하나라도 해당되면 `/ontology-learning` 을 명시적으로 호출하거나 즉시 발동:

- 유저가 내 출력을 교정·지적한다
- 유저가 화를 낸다 (표현 방식 무관)
- 내가 "다음엔" "죄송" "틀렸네"를 쓰려 한다
- 에러·예외가 내 판단 실수에서 비롯됐다
- 이전 응답에서 틀린 것을 내가 인지했다

## 인자 활용

- `/ontology-learning` (인자 없음) → 직전 실수를 대상으로 즉시 실행
- `/ontology-learning sort 파라미터 버그` → 특정 실수를 대상으로 실행

## 관련 커맨드

- `/pyramid-ontology` — 모든 행동의 L0 연결 강제 (이 커맨드의 상위 원칙)
- `/ontology-detach` — binding 교체조건 강제
- `/ontology-review-gate` — 구현 전 ontology 정합성 검증

## 관련 스킬 (Skill 도구로 호출)

- `ontology-learning` — 이 커맨드의 본체 (Phase 1~6 RCA 프로세스)
- `pyramid-ontology` — 최상위 목적 법칙
