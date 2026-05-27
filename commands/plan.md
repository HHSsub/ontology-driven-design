# /plan — 구현 계획 작성

L0: 구현 전 명확한 단계 분해 — 막연한 방향으로 코드 쓰면 반드시 다시 쓴다

이 커맨드는 Superpowers writing-plans 스킬을 발동한다.

## 즉시 수행할 것

`Skill` 도구로 `superpowers:writing-plans` 스킬을 invoke하라.

설계 문서(brainstorming 결과물)가 없으면 먼저 `/brainstorming` 실행.

## 플래닝 프로세스 (스킬이 강제)

1. 설계 문서 확인 및 구현 단위 분해
2. 각 단계에 검증 기준 명시
3. 의존성 순서 정렬
4. 체크포인트(중간 검증 지점) 삽입
5. 계획 파일 저장 (`docs/superpowers/plans/YYYY-MM-DD-<topic>-plan.md`)

## 관련 커맨드

- `/brainstorming` — 계획 전 설계 합의
- `/tdd` — 계획 실행 시 TDD 강제
- `/pyramid-ontology` — 모든 단계가 L0에 연결되는지 확인
