# /tdd — 테스트 주도 개발 강제

L0: 코드 변경의 "완료"는 파일 작성이 아니라 동작 검증이다

이 커맨드는 Superpowers test-driven-development 스킬을 발동한다.

## 즉시 수행할 것

`Skill` 도구로 `superpowers:test-driven-development` 스킬을 invoke하라.

## TDD 사이클 (스킬이 강제)

1. **Red** — 실패하는 테스트 먼저 작성
2. **Green** — 테스트를 통과시키는 최소 코드 작성
3. **Refactor** — 동작 유지하며 코드 정리

검증 없이 완료 선언 = L0 위반.

## 훅 연동

`tdd_enforce_stop.py` Stop 훅이 세션 종료 시 자동 감시:
- 마지막 Edit/Write 이후 검증 명령 없으면 차단
- `pytest`, `npx tsc --noEmit`, `curl localhost`, `go test` 등 인정

## 관련 커맨드

- `/debug` — 테스트 실패 시 근본 원인 탐색
- `/ontology-learning` — TDD 위반 실수 발생 시 온톨로지 진화
