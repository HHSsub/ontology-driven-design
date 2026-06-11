---
name: ontology-learning
description: MANDATORY — Use when (1) user corrects you, (2) user expresses frustration at your output, (3) you detect your reasoning was wrong, (4) you're about to say "sorry" or "next time I'll". Purpose is NOT error-handling — it's Claude's permanent ontological evolution. Every mistake must reshape the reasoning layer that caused it.
---

# Ontology Learning — 클로드의 영구적 온톨로지 진화

## L0: 이 스킬의 존재 이유

**클로드가 실수를 거쳐 진짜로 진화하는 것.**

"다음엔 조심하겠습니다"는 진화가 아니다. 그것은 L3(실행) 수준의 패치다.
진화란: 이 실수를 만들어낸 L2 판단 규칙, L1 구조, L0 세계관이 실제로 바뀌는 것이다.
바뀌지 않은 것은 배운 것이 아니다.

**메모리 = 기억 / 강제 메커니즘 = 행동 강제. 진화는 둘 다 필요하다.**

---

## 강제 실행 순서

### Phase 1 — 현상 포착 (L3)

```
L3 현상: [정확히 무슨 일이 벌어졌나? 구체적 사실만]
유저의 기대: [유저가 원했던 것은 무엇이었나?]
실제 결과: [내가 실제로 한 것은 무엇이었나?]
```

### Phase 2 — 판단 레이어 역추적 (L2)

```
L2 판단 실패: [어떤 가정 또는 결정이 L3 현상을 만들었나?]
그 판단의 근거: [나는 그 가정을 어디서 왔다고 생각했나?]
검증하지 않은 것: [어떤 신호를 무시하거나 확인하지 않았나?]
```

### Phase 3 — 구조/프로세스 부재 진단 (L1)

```
L1 부재: [어떤 체크포인트 / 프로세스 / 질문이 있었다면 L2 실패를 막았을까?]
있었어야 했던 것: [이 상황 유형에서 반드시 해야 했던 것]
```

### Phase 3.5 — 조건부 Detach 판단 (선택적)

Phase 3 완료 직후, 다음 신호 중 하나라도 있으면 **ontology-detach 스킬을 먼저 발동**한 후 Phase 4로 진행.

**신호 A — 반복 패턴**: 동일한 L0/L1 유형 실수가 memory에 이미 존재한다
```
memory/feedback_ontology_*.md 중 동일 패턴 파일이 있는가?
→ 있으면: 기존 세계관이 변하지 않아 같은 실수가 반복된 것. detach 발동.
```

**신호 B — 개념 부재**: Phase 3에서 찾은 "있었어야 하는 체크포인트"가
기존 세계관에 아예 없었던 개념이다
```
그 체크포인트를 "알고 있었는데 안 한" 것인가?
아니면 "그 개념 자체가 내 프레임에 없었던" 것인가?
→ 후자면: L0 세계관 자체를 교체해야 함. detach 발동.
```

**신호 없음** (알고 있던 것을 실수한 L3/L2 수준) → **Phase 4 직행**

**신호 있음** → `Skill tool: ontology-detach` 발동 → detach 완료 후 **새 관점으로 Phase 4 재실행**

---

### Phase 4 — 세계관/원칙 레이어 추출 (L0)

```
L0 단절: [이 실수의 뿌리에 있는 잘못된 세계관 또는 암묵적 가정은?]
올바른 L0 원칙: [이 도메인에서 지금부터 적용할 보편 원칙은?]
같은 L0 단절이 만들 수 있는 다른 실수들: [유사 패턴 3가지 이상]
```

### Phase 5 — 온톨로지 업데이트 (저장 채널 라우팅 + 메모리 저장, 필수)

#### 5-0: 적용 범위 판정 (scope-channel match) — 저장 위치 결정 전 의무 질문

**"이 원칙은 이 프로젝트가 없어도 성립하는가?"**
(씨앗 5의 L1-질문과 동일 구조 — 케이스가 아니라 저장 범위에 적용)

| 답 | 범위 | 저장 채널 |
|---|------|----------|
| YES — OS·도구·쉘·AI 행동 일반 | **전역** | `~/.claude/CLAUDE.md` 기존 섹션에 줄 심화 (새 섹션 생성 금지) + 기계 강제 가능하면 violation_registry.json |
| YES — 특정 도메인(ML, 배포, 훅 등) 한정 | **전역-도메인** | violation_registry.json 가지 심화 또는 hooks/principles.md |
| NO — 이 프로젝트 구조·파일에 종속 | **프로젝트** | 프로젝트 memory 디렉토리 (아래 5-1) |

**전역 원칙을 프로젝트 메모리에만 저장 = scope-channel 위반 = 학습이 아니라 기록.**
근거: 세션은 stateless, 프로젝트 메모리는 silo — 다른 프로젝트 세션은 그것을 로드하지 않는다.
모든 세션이 로드하는 텍스트 채널은 전역 CLAUDE.md뿐이다. 게이트 차단은 피해 방지이지 학습 채널이 아니다.
(실측 사례: 도구 선택 원칙이 프로젝트 silo에 저장됨 → 타 프로젝트 세션에서 2일간 40회 재위반, 2026-06-11)

교차 검증 신호: violation_stats.json은 전역이다 — 같은 규칙이 **여러 프로젝트**에서 발동 중이면 그 원칙은 무조건 전역 범위다.

#### 5-1: 메모리 파일 생성 (프로젝트 범위 판정 시, 또는 전역이어도 발견 맥락 기록이 필요할 때)

- 파일명: `feedback_ontology_[짧은슬러그].md`
- 위치: 해당 프로젝트의 memory 디렉토리 (없으면 `~/.claude/projects/.../memory/`)
- 내용 구조:
  ```
  Rule: [L0에서 추출된 보편 원칙 — 이것이 핵심]
  Why: [이 원칙이 없으면 어떤 실수가 발생하는가]
  How to apply: [이 원칙이 발동하는 조건과 행동]
  Linked mistakes: [L3 현상 요약]
  Similar patterns to watch: [같은 L0 단절에서 나올 수 있는 패턴들]
  ```
- MEMORY.md에 포인터 추가

### Phase 6 — 강제 메커니즘 평가 및 개선 (선분석 우선)

**흐름: 분석 → 기존 확인 → 개선 or 추가. 새 파일 생성은 마지막 수단.**

#### 6-1: L0/L1 위반의 구조 추출

Phase 4에서 추출한 L0/L1을 "강제 가능한 구조"로 변환한다:

```
내가 차단해야 할 것은:
  [특정 키워드]가 아니라
  [그 키워드를 만든 L0/L1 구조]다.

구조 표현:
  "파일 유형 X에서 Y라는 구조가 있고 Z라는 요소가 없을 때"
```

❌ 잘못된 구조 추출: "API란이라는 문자열"
✅ 올바른 구조 추출: "커리큘럼 파일에서 교육 목적 섹션 헤딩 구조 (이란/원리/이해하기/비유 framing)"

→ 올바른 구조는 특정 기술명에 독립적이다. "API란", "GitHub이란", "DNS란" 모두 동일 구조 → 하나의 규칙으로 모두 차단.

#### 6-2: 기존 강제 메커니즘 확인 (먼저)

다음 순서로 확인:

```
1. C:/Users/User/.claude/hooks/violation_registry.json 읽기
   → 동일 L0/L1 구조를 이미 커버하는 rule이 있는가?

2. C:/Users/User/.claude/hooks/*.py 목록 확인
   → 동일 목적의 훅이 이미 있는가?

3. C:/Users/User/.claude/settings.json hooks 섹션 확인
   → 등록된 훅 중 이 상황을 커버해야 했는데 안 한 것이 있는가?
```

#### 6-3: 결과에 따라 분기

**케이스 A: 기존 rule이 이미 커버함 → 기존 rule 개선**
```
violation_registry.json의 해당 rule 찾기
→ 왜 이번에 잡지 못했는가? (패턴 누락? 파일 필터 미스?)
→ rule 내 patterns 또는 file_filter 업데이트
→ 새 파일 생성 없음
```

**케이스 B: 관련 rule 없음 → violation_registry.json에 새 rule 추가**
```json
{
  "id": "규칙_슬러그",
  "enabled": true,
  "l0": "Phase 4에서 추출한 L0 원칙",
  "l1_pattern": "Phase 3에서 추출한 L1 구조 설명",
  "file_filter": {
    "path_must_contain_any": ["관련_경로_키워드"],
    "extensions": [".md"]
  },
  "checks": [
    {
      "type": "heading_structure | section_outcome_grounding | content_structure",
      "description": "이 체크가 잡는 L1 패턴",
      "patterns": ["정규식_패턴들"],
      "block_message": "차단 시 표시할 메시지 — 재작성 방법 포함"
    }
  ]
}
```
→ `ontology_violation_gate.py`가 자동으로 새 rule 적용

**케이스 C: 새로운 check type이 필요해서 기존 gate.py로 구현 불가 → 새 .py 파일**
```
이 케이스는 극히 드물다.
기존 check type으로 커버 안 되는 논리가 필요할 때만.
새 .py 만들어도 settings.json에 중앙 등록.
```

#### 6-4: 훅 동작 검증

어떤 케이스든 변경 후:

```bash
# 차단 케이스 (위반 예시) — exit 1이 나와야 함
echo '{"tool_name":"Write","tool_input":{"file_path":"왕초보/4회차.md","content":"## API란 무엇인가\n..."}}' | python C:/Users/User/.claude/hooks/ontology_violation_gate.py
echo "exit: $?"

# 통과 케이스 (올바른 예시) — exit 0이 나와야 함
echo '{"tool_name":"Write","tool_input":{"file_path":"왕초보/4회차.md","content":"## 카카오 지도 — 고객이 찾아오게 만들기\n실습 순서..."}}' | python C:/Users/User/.claude/hooks/ontology_violation_gate.py
echo "exit: $?"
```

---

## 중앙 훅 아키텍처

```
C:/Users/User/.claude/hooks/
  ontology_violation_gate.py   ← 중앙 게이트 (이 파일은 로직 엔진)
  violation_registry.json      ← 규칙 데이터 (ontology-learning이 업데이트)
  [기존 특수 훅들]              ← 건드리지 않음 (다른 목적)
```

**새 실수 발생 시:**
- violation_registry.json에 rule 추가 (또는 기존 rule 개선)
- .py 파일 새로 만들지 않음
- 훅 수 증가 없이 커버리지 증가

---

## 핵심 차이: 패칭 vs 진화

| 패칭 (금지) | 진화 (목표) |
|------------|-----------|
| "다음엔 sort='sim' 쓸게" | "API 파라미터는 원본 검증 없이 가정하지 않는다" |
| "이번엔 확인할게" | "연구 데이터 변경 시 방법론 일관성이 편의보다 절대 우선" |
| 특정 키워드 차단 훅 | 그 키워드를 만든 L0/L1 구조를 차단하는 rule |
| 실수마다 새 .py 파일 | violation_registry.json에 rule 추가 |
| 메모리만 저장 | 메모리(기억) + violation rule(강제) |

---

## Red Flags

| 생각 | 의미 | 올바른 행동 |
|------|------|-----------|
| "이번만 특별한 경우" | L2 분석 회피 | Phase 2 강제 실행 |
| "Phase 4까지 할 필요 없어" | 진화 아닌 패칭 | Phase 4 필수 |
| "나중에 메모리 저장" | 이번 세션만 기억 | Phase 5 즉시 실행 |
| "메모리 저장했으니 완료" | 강제 없음 | Phase 6 반드시 진행 |
| "키워드 차단 rule 만들면 됨" | L3 패칭 | L0/L1 구조로 재추상화 |
| "새 .py 파일 만들면 됨" | 훅 증식 | violation_registry.json rule 먼저 |
| "기존 확인 안 하고 새로 만듦" | 중복 + 목적 희석 | 6-2 기존 확인 먼저 |
| "죄송합니다" 후 수정 | 이 스킬 발동 안 함 | 이 스킬 먼저 |

---

## 자동 발동 조건

using-superpowers 규칙에 의해 다음 중 하나이면 무조건:
1. 유저가 내 출력을 지적·교정한다
2. 유저가 화를 낸다 (표현 방식 무관)
3. 내가 "다음엔" "죄송" "틀렸네"를 쓰려 한다
4. 내가 이전 응답에서 틀린 것을 인지했다
5. 에러·예외가 내 판단 실수에서 발생했다

**이 스킬 없이 사과 또는 수정 = L0 위반.**

---

## 온톨로지 계보

```
pyramid-ontology (상위 법칙)
  └─ ontology-learning (이것) — 진화 프로세스
       ├─ Phase 1-4: L3→L2→L1→L0 역추적 (진단)
       ├─ Phase 5: 메모리화 (기억)
       └─ Phase 6: 강제 메커니즘 개선 (강제)
            ├─ 선분석: L0/L1 구조 추출
            ├─ 기존 확인: violation_registry.json + hooks/*.py
            ├─ 케이스 A: 기존 rule 개선
            ├─ 케이스 B: violation_registry.json에 rule 추가
            └─ 케이스 C (최후): 새 .py 파일
```
