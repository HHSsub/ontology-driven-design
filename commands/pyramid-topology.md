# /pyramid-topology — L0-L3 피라미드 토폴로지 분석

L0: 모든 코드가 목적 위계에 연결돼 있는지 구조적으로 검증
L1: 어떤 언어·형식·플랫폼이든 동일한 위계 원칙으로 정합성 점검
L2: 파일 스캔 → L레벨 파싱 → 위계 맵 구축 → 위반 탐지 → 보고

이 커맨드는 코드베이스 전체의 L0-L3 라벨 구조를 분석하고,
목적 위반·연결 단절·라벨 누락·위계 오용을 탐지한다.
**어떤 언어도 예외 없다.** Python, TypeScript, Go, YAML, Markdown 모두 동일한 원칙으로 분석.

**사용법**:
- `/pyramid-topology` → 전체 분석
- `/pyramid-topology backend/services/` → 특정 폴더
- `/pyramid-topology --violations-only` → 위반 항목만 출력

---

## 분석 목적 — 커버리지 측정이 아니라 Ontology 정합성 검증

1. 모든 코드 단위가 L0(최종 목적)에 연결되어 있는가?
2. L2가 L1에, L3가 L2에 체계적으로 귀속되어 있는가?
3. 목적 없이 떠 있는 "고아 단위"가 없는가?
4. L0 선언이 비즈니스 목적인가, 아니면 기술 세부사항으로 오염됐는가?
5. L1/L2에 L3 구현 세부사항이 올라와 있지 않은가?

---

## 분석 절차

### STEP 1 — 파일 목록 수집 (언어·형식 무관)

```
포함 대상 (로직·의도가 담긴 모든 파일):
  코드: .py, .ts, .js, .jsx, .tsx, .go, .rb, .java, .cs, .rs, .php, .swift, .kt
  설정: .yaml, .yml (로직/의도 포함된 것)
  문서: .md (CLAUDE.md, 설계문서, 핸드오버 등)
  스크립트: .sh, .bash

제외 대상 (순수 데이터·생성물):
  __pycache__/, dist/, build/, .next/, node_modules/
  alembic/versions/, migrations/ (자동 생성)
  *.lock, *.sum, package-lock.json
  *.min.js, *.min.css
  바이너리, 미디어 파일
```

### STEP 2 — 각 파일 파싱 (언어별 L3 구현, 원칙은 공통)

각 파일에서 추출:
- 파일 최상단 L0/L1 선언 (어떤 주석 형식이든: `# L0:`, `// L0:`, `<!-- L0:`, `L0:`)
- 각 함수·클래스·주요 블록의 `Lx:` 라벨
- 라벨 내용이 해당 레벨에 적합한지 (L0에 timeout값 등 L3 내용 있는지)
- 함수 이름, 줄 번호

### STEP 3 — 토폴로지 맵 구축

```
L0 (프로젝트 CLAUDE.md 기준)
  └─ L1 파일·모듈들 (end-to-end 흐름 조율)
       └─ L2 함수·기능들 (독립 기능 단위)
            └─ L3 함수·표현들 (구현 세부)
```

### STEP 4 — 위반 패턴 탐지 카탈로그

| 위반 유형 | 정의 | 심각도 |
|---|---|---|
| **미라벨 비-trivial 단위** | 5줄 이상인데 `Lx:` 없음 | HIGH |
| **L0 오용 — 기술 세부** | L0에 timeout/bitrate/API명/파일확장자 | HIGH |
| **L0 탈도구 위반** | L0에 특정 언어·도구·파일형식 고정 | HIGH |
| **함수 내부 L0 오용** | 일반 함수 body에 L0 (파이프라인 실행자 제외) | HIGH |
| **L1 위계 오염** | L1에 retry횟수·파일확장자·구현 메서드 | MEDIUM |
| **L0 미연결 L2** | L2 기능이 어떤 L1 파이프라인에도 호출 안 됨 | MEDIUM |
| **고아 파일** | 어디서도 import/참조되지 않는 모듈 | MEDIUM |
| **L3가 L0 직접 수행** | L3 함수가 실제로 YouTube 업로드 등 L0 작업 수행 | MEDIUM |
| **목적 불명 주석** | `# L?: 목적 불명` 태그된 항목 | LOW |

---

## 출력 형식

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 PYRAMID TOPOLOGY REPORT
프로젝트: <프로젝트명>
스캔 파일: N개 | 함수: N개 | 언어: Python N, TypeScript N, 기타 N
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[L0 선언]
  CLAUDE.md 기준: "<프로젝트 L0 목적>"

[라벨 커버리지]
  L1 파일: N/N (XX%)
  L2 함수: N/N (XX%)
  L3 함수: N/N (XX%)
  미라벨 비-trivial 단위: N개 ← 가장 중요

[토폴로지 맵]
  pipeline.py (L1)
    ├─ _pipeline_post_process() (L1)
    │    ├─ _auto_youtube_upload() (L2)
    │    └─ _auto_copyright_register() (L2)
    └─ _run_music_video_background() (L1)

[🔴 HIGH 위반]
  L0 오용 (기술 세부):
    services/video_extender.py:187 — L0에 'RT비율'
    services/video_merge.py:91 — L0에 'ffmpeg'

  함수 내부 L0:
    services/video_extender.py:233 — _make_variation_clip() 내부 L0

  미라벨 비-trivial 단위:
    services/video_builder.py:45 → build_music_video()
    routers/pipeline.py:97 → upload_to_youtube()

[🟡 MEDIUM 위반]
  고아 파일:
    services/mock_data.py (import 없음)

  L0 미연결 L2:
    services/payment.py → PaymentService (호출 없음)

[✅ 정상 연결]
  pipeline.py → _pipeline_post_process → YouTube 업로드 (L0 달성)

[권고사항]
  1. /pyramid-label 실행으로 미라벨 일괄 적용
  2. L0 오용 N개 → L3 주석으로 이동
  3. 고아 파일 N개 → 삭제 또는 파이프라인에 연결
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## L0 의미 검증 기준 (탐지 규칙)

분석 시 아래 패턴이 L0 줄에 있으면 위반으로 표시:

```
❌ L0 위반 패턴:
  기술 수치:  timeout, 비트레이트, RT 비율, msec, fps, \d+Mbps
  특정 도구:  ffmpeg, subprocess, asyncio, FastAPI, ffprobe
  파일형식:   .py, .ts, .mp4, .json
  하드웨어:   단일코어, thread, CPU, 메모리
  계산식:     video_duration * N, setpts, pts_ratio

✅ L0 올바른 패턴:
  "SNS(YouTube) 업로드 자동화 — 유저 개입 없이 콘텐츠 발행"
  "비용 투명성 — API 실사용량을 언제든 확인 가능"
  "모든 산출물이 존재 목적에 연결되도록 강제"
```

---

## 시스템 목적 변화 시 활용

```
신규 기능 추가 전:
→ /pyramid-topology 실행
→ 기존 L2 중 재사용 가능한 것 파악
→ L0에 이 기능이 연결되는지 확인

기능 삭제 전:
→ /pyramid-topology 실행
→ 삭제 대상에 귀속된 L2/L3 목록 추출
→ 연쇄 삭제 범위 확인 후 제거

아키텍처 변경 전:
→ /pyramid-topology 실행
→ L1 파이프라인 재정렬 영향 범위 파악
→ /ontology-review-gate 로 PASS 받은 후 실행
```

---

## 분석 완료 후 다음 액션

- 미라벨 비-trivial 단위 > 20%: `/pyramid-label` 먼저 실행
- L0 오용 존재: 해당 줄의 L0를 L3로 이동, 파일 L0 재확인
- 고아 파일 존재: 파이프라인 연결 또는 삭제 검토
- L0 미연결 L2 존재: 파이프라인에 연결하거나 삭제
