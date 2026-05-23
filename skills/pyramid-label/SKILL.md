---
name: pyramid-label
description: Apply L0-L3 pyramid hierarchy labels to any file or folder — code, config, docs, scripts. Language-agnostic. Use before code review or after adding new files to ensure every unit declares its purpose level.
---

# /pyramid-label — L0-L3 Ontology 라벨링 적용

L0: 모든 산출물이 존재 목적에 연결되도록 — 목적 없는 코드·문서·설정은 없다
L1: 어떤 언어·형식·플랫폼이든 동일한 위계 원칙으로 라벨링 적용
L2: 파일 목적 파악 → L레벨 결정 → 라벨 삽입 → 위계 정합성 검증

**사용법**:
- `/pyramid-label` → 현재 프로젝트 전체
- `/pyramid-label src/services/uploader.ts` → 단일 파일
- `/pyramid-label backend/ frontend/src/` → 복수 경로

---

## 위계 정의

| 레벨 | 의미 | 무엇을 기술하는가 | 무엇을 쓰면 안 되는가 |
|---|---|---|---|
| **L0** | 비즈니스 최종 목적 | 이 시스템이 왜 존재하는가 | 도구명, 언어, 파일형식, timeout값, API명 |
| **L1** | 원칙적 전략 | L0 달성을 위한 흐름·전략 | retry횟수, 특정 라이브러리명 |
| **L2** | 기능 단위 | 독립 테스트 가능한 기능 이름 + 한 줄 목적 | 구현 메서드, 수치 제약 |
| **L3** | 구현 세부 | 구체적 수단, API명, timeout값 | (제한 없음) |

### 판별 기준

```
이 내용을 다른 언어로 바꿔 구현해도 동일한가?
  → YES: L0 또는 L1 (도구 무관)
  → NO (특정 도구에 묶임): L2 또는 L3

이 내용이 기능 단위 이름인가?
  → YES: L2

이 내용에 숫자·파일확장자·API명이 들어가는가?
  → YES: L3
```

---

## 라벨 형식 — 언어별 주석

```python
# Python
# L0: SNS 업로드 자동화 — 유저 개입 없이 콘텐츠 발행
async def extend_video(...):
    # L2: 영상 확장 진입점 — temporal_type 기반 전략 라우팅
```

```typescript
// TypeScript
// L0: 사용자 콘텐츠를 SNS에 자동 발행
export function fetchUploadHistory(): Promise<UploadItem[]> {
  // L2: YouTube 업로드 이력 목록 조회
}
```

```yaml
# YAML
# L0: 서비스 가용성 보장
services:
  backend:
    # L2: FastAPI 백엔드 컨테이너
```

```markdown
L0: 팀이 올바른 아키텍처 결정을 내릴 수 있도록

## 현황 분석
L2: 현재 시스템의 병목 지점 식별
```

---

## 적용 절차

### STEP 1 — 대상 파일 목록 수집

포함: `.py .ts .js .jsx .tsx .go .rb .java .yaml .yml .md .sh`
제외: `__pycache__/ dist/ build/ node_modules/ *.lock *.min.js`

### STEP 2 — 각 파일 분석 및 라벨 적용

1. 파일 목적 파악
2. 파일 레벨 결정 (L1 흐름 조율? vs L2 단일 기능?)
3. 파일 최상단에 L0/L1 선언 추가
4. 각 로직 단위(함수·클래스) 레벨 결정
5. 로직 단위 시작부에 `Lx: 목적` 라벨 추가

### STEP 3 — 결정 트리

```
여러 L2를 조율하는 end-to-end 흐름? → L1
독립적인 기능 단위? → L2
L2 내부에서만 쓰이는 구현 수단? → L3
어떤 L과도 연결 안 됨? → "L?: 목적 불명" 표시 → 삭제 후보
```

---

## 위반 패턴

```python
# ❌ L0에 구현 세부사항
# L0: ffmpeg로 영상 인코딩  ← 도구 고정 → L3

# ❌ L1에 retry횟수
# L1: retry 3회 간격 10초로 API 호출  ← L3 세부가 L1에 올라옴

# ✅ 올바른 L2
def merge_video_with_bgm(...):
    # L2: 영상에 BGM 합성 — 원본 오디오 제거 후 새 음악 삽입
```

---

## 완료 후 보고 형식

```
=== pyramid-label 완료 ===
처리 파일: N개
추가된 라벨: N개 (L0: N, L1: N, L2: N, L3: N)
목적 불명 함수: N개
위계 위반 발견: N개
```
