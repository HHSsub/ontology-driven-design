# /pyramid-ontology — 피라미드 위계 온톨로지 발동

L0: 이번 세션의 모든 행동이 비즈니스 최종 목적에 연결되도록 강제

이 커맨드는 **모든 프로젝트·모든 폴더에서** 호출 가능하다 (글로벌 등록).

## 즉시 수행할 것

1. `Skill` 도구로 `pyramid-ontology` 스킬을 invoke하라 — 그 스킬 본문이 이 세션의 모든 후속 행동의 헌법이 된다.
2. 첫 번째 답변 전에 반드시 선언:
   ```
   L0: [이 세션의 비즈니스 최종 목적]
   L1: [지금 작업의 시스템 목표]
   L2: [지금 수행할 구체 태스크]
   ```
3. L0를 말할 수 없으면 — STOP. 사용자에게 먼저 물어라. 추측 금지.

## 적용 범위 (코드뿐 아니라)

- 코드, 보고서, PPT, 이메일, 분석, 요약 — **어떤 산출물이든 동일하게 적용**
- 모든 파일 첫 줄에 `L0: ...` 선언 (주석 형식은 파일 종류에 맞춰 자유)
- 파일 삭제·외부 API 호출·DB 변경·이메일 발송 등 비가역 행동 전 L0 연결 확인 필수

## 인자 활용

- `/pyramid-ontology` (인자 없음) → 현재 세션·요청에 즉시 적용
- `/pyramid-ontology 보고서 작성` → 그 작업의 L0~L2 선언 후 시작
- `/pyramid-ontology 배포` → 비가역 행동이므로 L0 확인 절차 강제

## 관련 커맨드

- `/ontology-detach` — 모든 binding에 교체조건 강제 (탈존재 원칙)
- `/pyramid-label` — 파일·코드에 L0~L3 라벨 일괄 적용
- `/pyramid-topology` — 시스템 전체의 위계 토폴로지 점검

## 관련 스킬 (Skill 도구로 호출)

- `pyramid-ontology` — 이 커맨드의 본체
- `ontology-detach` — 탈존재 원칙
- `test-driven-development` — L2/L3 구현의 검증 강제
- `verification-before-completion` — L0 달성 확인 전 완료 선언 금지
