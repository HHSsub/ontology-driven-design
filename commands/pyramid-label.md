# /pyramid-label — L0-L3 Ontology 라벨링 적용

L0: 모든 산출물이 존재 목적에 연결되도록 — 목적 없는 코드·문서·설정은 없다
L1: 어떤 언어·형식·플랫폼이든 동일한 위계 원칙으로 라벨링 적용
L2: 파일 목적 파악 → L레벨 결정 → 라벨 삽입 → 위계 정합성 검증

이 커맨드는 지정한 파일·폴더의 모든 코드 단위(함수·클래스·모듈)에 L0-L3 피라미드 위계 라벨을 적용한다.
**어떤 언어도, 어떤 파일 형식도 예외 없다.** 파이썬도, 타입스크립트도, Go도, YAML도, Markdown 문서도 동일한 원칙으로.

**사용법**:
- `/pyramid-label` → 현재 프로젝트 전체 (소스 파일 전부)
- `/pyramid-label src/services/uploader.ts` → 단일 파일
- `/pyramid-label backend/ frontend/src/` → 복수 경로

---

## 위계 정의 (언어·도메인 무관 공통 법칙)

| 레벨 | 의미 | 무엇을 기술하는가 | 무엇을 쓰면 안 되는가 |
|---|---|---|---|
| **L0** | 비즈니스 최종 목적·존재이유 | 이 시스템이 왜 존재하는가 | 도구명, 언어, 파일형식, timeout값, API명 |
| **L1** | 원칙적 전략·인프라 목표 | L0 달성을 위한 흐름·전략 (멀티플랫폼 고려) | retry횟수, 특정 라이브러리명, 파일확장자 |
| **L2** | 구체적 전술·기능 단위 | 독립 테스트 가능한 기능 이름 + 한 줄 목적 | 구현 메서드, 수치 제약, 내부 변수명 |
| **L3** | 구현 세부 | 구체적 수단, API명, timeout값, 알고리즘 | (제한 없음 — 구현 세부는 여기에 다 허용) |

### 판별 기준 — "이 레벨이 맞는가?" 자가질문

```
이 내용을 다른 언어로 바꿔 구현해도 동일한가?
  → YES: L0 또는 L1 수준 (도구 무관)
  → NO (특정 도구/언어에 묶임): L2 또는 L3

이 내용이 기능 단위 이름인가?
  → YES: L2 (예: "YouTube 메타데이터 생성")
  → NO (구현 방법이 섞임): L3로 내리거나 분리

이 내용에 숫자·파일확장자·API명이 들어가는가?
  → YES: L3
  → NO: L2 이상 가능
```

---

## 라벨 형식 — 언어별 주석 방식

모든 언어에서 `L레벨: 목적설명` 패턴. 주석 기호만 언어에 맞게.

```python
# Python
# L0: SNS(YouTube) 업로드 자동화 — 유저 개입 없이 콘텐츠 발행
# L1: 음악→영상→확장→합성→YouTube end-to-end 파이프라인

async def extend_video(...):
    # L1: 영상 확장 진입점 — temporal_type 기반 전략 라우팅 및 실행

async def _make_variation_clip(...):
    # L3: setpts 슬로우 + 선택적 색조 — 재시작 없는 단일 패스 슬로우모션 클립
```

```typescript
// TypeScript / JavaScript
// L0: 사용자 콘텐츠를 SNS에 자동 발행
// L1: 업로드 이력 관리 — 조회·삭제·상태 동기화

export function fetchUploadHistory(): Promise<UploadItem[]> {
  // L2: YouTube 업로드 이력 목록 조회 — API 호출 및 상태 정규화
}

function formatDate(iso?: string): string {
  // L3: ISO 날짜 문자열 → 한국어 형식 변환
}
```

```yaml
# YAML / 설정파일
# L0: 서비스 가용성 보장 — 단일 장애점 없는 배포
# L1: 컨테이너 오케스트레이션 전략

services:
  backend:
    # L2: FastAPI 백엔드 컨테이너 — API 요청 처리
```

```markdown
L0: 팀이 올바른 아키텍처 결정을 내릴 수 있도록 — 의사결정자 설득

## 현황 분석
L2: 현재 시스템의 병목 지점 식별 및 근거 제시
```

---

## 적용 절차

### STEP 1 — 대상 파일 목록 수집

**언어·형식 무관 원칙**: 코드·로직·의도가 담긴 파일이면 전부 대상.

```
포함 대상:
  코드 파일: .py, .ts, .js, .jsx, .tsx, .go, .rb, .java, .cs, .rs, .php, .swift, .kt
  설정 파일 (의도가 담긴 것): .yaml, .yml, docker-compose.yml
  문서 (구조적 내용): .md (CLAUDE.md, README.md, 설계문서 등)
  셸 스크립트: .sh, .bash

제외 대상 (순수 데이터·생성물·바이너리):
  잠금파일: package-lock.json, yarn.lock, *.lock, *.sum
  생성물: __pycache__/, dist/, build/, .next/, node_modules/
  마이그레이션 자동생성: alembic/versions/, migrations/
  테스트 픽스처: test_fixtures/, *.fixture.*
  바이너리/미디어: *.png, *.mp4, *.db, *.pdf 등
  순수 선언: requirements.txt, package.json (스크립트 없는 것)
```

### STEP 2 — 각 파일 분석 및 라벨 적용

1. **파일 목적 파악**: 파일명, import 구조, 주요 심볼(함수·클래스·상수) 읽기
2. **파일 레벨 결정**: 이 파일이 L1(흐름 조율)인가 L2(단일 기능)인가?
3. **파일 최상단에 L0/L1 선언 추가** (없으면) — 어떤 언어든 적합한 주석 형식으로
4. **각 로직 단위(함수·클래스·섹션) 레벨 결정** (아래 결정 트리)
5. **로직 단위 시작부에 `Lx: 목적` 라벨 추가** (없으면) — 언어 주석 형식에 맞게

### STEP 3 — 결정 트리 (언어 무관 공통)

```
이 단위가 여러 L2를 조율하는 end-to-end 흐름인가?
  → YES: L1
  (예: _pipeline_post_process, runPipeline, main orchestration)

이 단위가 독립적으로 의미 있는 기능 단위인가?
  → YES: L2
  (예: generate_youtube_metadata, fetchUploadHistory, parseVideoAnalysis)

이 단위가 L2 내부에서만 쓰이는 구현 수단인가?
  → YES: L3
  (예: _probe_video, formatDate, _extract_last_frame)

이 단위가 파이프라인의 L0 목적을 직접 실행하는 배경 작업인가?
  → L0 + L1 + L2 모두 명시 필수
  (예: _run_*background, _auto_*upload, _pipeline_*)

이 단위가 어떤 L과도 연결되지 않는가?
  → "# L?: 목적 불명 — 검토 필요" 표시 → 삭제 후보
```

---

## 위반 패턴 — 이렇게 쓰면 안 된다

```
# ❌ L레벨 없이 기능 설명만 (목적 연결 없음)
def merge_video(...):
    """Merge video with background music."""

# ❌ L레벨은 있는데 내용이 없음 (라벨이 의미를 못 전달)
def merge_video(...):
    # L2

# ❌ L0에 구현 세부사항 (상위가 하위에 종속됨)
# L0: ffmpeg로 영상 인코딩 (도구 고정 → L3)
# L0: timeout 10초 이내 완료 (수치 → L3)
# L0: .py 파일에서 py_compile 실행 (파일형식+도구 → L3)

# ❌ L1에 retry횟수·파일확장자 (L3 세부가 L1에 올라옴)
# L1: retry 3회 간격 10초로 Kling API 호출 → L3 세부가 L1에 있음

# ✅ 올바른 L2 + 목적 + 기여하는 L1 흐름
def merge_video_with_bgm(...):
    # L2: 영상에 BGM 합성 — 원본 오디오 제거 후 새 음악 삽입
```

---

## 라벨링 완료 후 자가검증 (언어별 검증 방법)

```
Python   → python -m py_compile <file>
TypeScript → npx tsc --noEmit (해당 파일 포함된 tsconfig 기준)
JavaScript → node --check <file>
Go         → go vet ./...
기타        → 육안 확인: syntax 오류 없는지, 들여쓰기 깨짐 없는지
공통        → 5줄 이상 함수 전부에 Lx: 있는지 확인
공통        → _run_*/_auto_*/_pipeline_* 함수에 L0+L1+L2 전부 있는지 확인
```

---

## 적용 완료 후 보고 형식

```
=== pyramid-label 완료 ===
처리 파일: N개 (Python: N, TypeScript: N, 기타: N)
추가된 라벨: N개 (L0: N, L1: N, L2: N, L3: N)
목적 불명 함수: N개 (파일명:줄번호 목록)
삭제 후보: N개
위계 위반 발견: N개 (L0에 도구명 / L1에 retry횟수 등)
```
