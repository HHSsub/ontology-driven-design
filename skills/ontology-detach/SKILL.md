---
name: ontology-detach
description: Use whenever you write or review code that binds, fixes, or persists something — values, dependencies, state, assumptions, identifiers, sequences. Detects "존재집착" (existence-clinging) where code freezes a transient choice into permanent law, then guides the redesign so every binding has an exit condition and truth is re-derived at the moment of use, not stored as fact.
---

# Ontology Detach — 탈존재화 (De-Existence) Principle

## L0: WHY — 원칙

**모든 binding에는 교체조건이 있어야 한다. 없으면 탈존재 위반.**

코드는 끊임없이 "고정"하려 한다 — 값을 변수에, 의존성을 import에, 상태를 파일에, 가정을 하드코딩에, 순서를 절차적 흐름에, ID를 정적 매핑에. 각 고정은 "지금 이 선택이 영원할 것"이라는 거짓 전제다. 외부 환경(시간, 프로세스, 사용자, 데이터, API)은 반드시 변하므로 교체조건 없는 모든 고정은 결국 거짓말이 된다.

## L1: 진단 — 존재집착의 6가지 차원

각 차원에서 같은 질문을 한다: **"이 binding의 교체조건은 무엇인가? 명시되어 있는가?"**

### 1. 상태(State)의 고정
- 진실(truth)이 영구 저장소에 frozen → 외부 변화 후 거짓말 시작
- 교체조건: live signal과 cross-check 후 stale이면 재도출

### 2. 의존성(Dependency)의 고정
- 특정 라이브러리·서비스·인터페이스를 직접 호출 → 그게 사라지면 전체 붕괴
- 교체조건: 추상 경계(인터페이스, adapter, port)로 격리, 구현 swap 가능

### 3. 값(Value)의 고정
- 매직넘버, 하드코딩 임의값(timeout 60s, retry 3회, batch 100) → 환경 바뀌면 부적절
- 교체조건: 외부 시그널(공식 헤더·문서값·환경변수·실측 통계) 우선, 없을 때만 fallback

### 4. 가정(Assumption)의 고정
- "X는 항상 Y일 것" 무검증 가정 → Y 아닌 입력 들어오면 침묵의 오류
- 교체조건: 경계에서 검증, 가정 위반 시 명시적 실패

### 5. 식별자(Identifier)의 고정
- 같은 개체에 여러 ID(job_id, session_id, request_id) 분리 → 동기화 깨짐
- 교체조건: 1:1 매핑되면 단일 ID, 다대다일 때만 분리하고 매핑 함수 명시

### 6. 순서(Sequence)의 고정
- "A → B → C" 절차가 코드 흐름에 박혀있음 → 중간 실패 시 처음부터
- 교체조건: 각 단계 idempotent, resume token으로 재진입 가능

## L2: HOW — 탈존재 설계 원칙

### 원칙 1: 진실은 최신 도출이다, 저장된 사실이 아니다
저장은 캐시·로그·복원포인트로 격하시키고, 의사결정은 live observation 기준으로.

### 원칙 2: 외부가 정한 시그널이 임의값보다 우선한다
공식 docs·response 헤더·운영체제 시그널 등이 있으면 그걸 따른다. 없을 때만 fallback. fallback에는 출처 코멘트를 붙인다.

### 원칙 3: 무한 누적은 반드시 차단된다
어떤 컬렉션이든 "끝없이 자랄 수 있는가?"를 묻는다. 가능하면 cap·rotation·indexing·summarization 중 하나가 반드시 있어야 한다.

### 원칙 4: 라이프사이클 게이트는 정상로/예외로 모두 닫는다
획득한 자원·등록한 상태·열린 핸들은 try/except/finally 트리플 또는 context manager로 무조건 정리.

### 원칙 5: 분리되는 것은 분리하고, 1:1은 통합한다
서로 다른 변동 주기·관심사·소유자를 가지면 분리한다. 항상 같이 움직이는 두 개는 하나로 합친다.

### 원칙 6: 단계는 어디서든 다시 시작 가능해야 한다
긴 작업이라면 "절반 진행 후 죽으면 어떻게 되는가?"가 답해져야 한다.

## L3: 적용 체크 — 코드 작성·리뷰 시 자가질문

작성 직전:
- "이 binding(값/의존성/상태/가정/ID/순서)의 교체조건은?"
- 답이 "없음"이면 탈존재 위반. 다시 설계하거나 교체조건을 명시한다.

리뷰 시:
- 정적 파일·in-memory dict·하드코딩 상수 발견 → 진실의 출처를 묻는다
- try/except 발견 → finally가 있는가, silent crash 시 어떻게 되는가
- 누적되는 자료구조(list, dict, log file) 발견 → 상한이 어디 있는가
- 두 개 이상의 ID가 같은 개체를 가리킴 발견 → 통합 가능한가
- 절차적 흐름 발견 → 중간 실패 시 어디로 가는가

## 메타원칙

이 스킬 자체도 탈존재해야 한다 — 위 6차원·6원칙은 현재 필요한 분류법일 뿐 영구 진리가 아니다. 새 패턴이 보이면 분류를 갱신하라.
