---
name: pyramid-topology
description: Scan the entire codebase and verify L0-L3 ontology integrity — detects unlabeled units, L0 pollution with technical details, orphan files, and hierarchy violations. Run before major refactors or architecture changes.
---

# /pyramid-topology — L0-L3 피라미드 토폴로지 분석

L0: 모든 코드가 목적 위계에 연결돼 있는지 구조적으로 검증
L1: 어떤 언어·형식·플랫폼이든 동일한 위계 원칙으로 정합성 점검
L2: 파일 스캔 → L레벨 파싱 → 위계 맵 구축 → 위반 탐지 → 보고

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

---

## 위반 패턴 탐지 카탈로그

| 위반 유형 | 정의 | 심각도 |
|---|---|---|
| **미라벨 비-trivial 단위** | 5줄 이상인데 `Lx:` 없음 | HIGH |
| **L0 오용 — 기술 세부** | L0에 timeout/API명/파일확장자 | HIGH |
| **L0 탈도구 위반** | L0에 특정 언어·도구 고정 | HIGH |
| **L1 위계 오염** | L1에 retry횟수·파일확장자 | MEDIUM |
| **L0 미연결 L2** | L2 기능이 어떤 L1에도 호출 안 됨 | MEDIUM |
| **고아 파일** | 어디서도 import/참조되지 않는 모듈 | MEDIUM |
| **목적 불명 주석** | `L?: 목적 불명` 태그된 항목 | LOW |

---

## 출력 형식

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 PYRAMID TOPOLOGY REPORT
프로젝트: <프로젝트명>
스캔 파일: N개 | 함수: N개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[L0 선언]
  "<프로젝트 L0 목적>"

[라벨 커버리지]
  L1 파일: N/N (XX%)
  L2 함수: N/N (XX%)
  미라벨 비-trivial 단위: N개 ← 가장 중요

[토폴로지 맵]
  pipeline.py (L1)
    ├─ _pipeline_post_process() (L1)
    │    ├─ _auto_upload() (L2)
    │    └─ _auto_register() (L2)

[🔴 HIGH 위반]
  L0 오용 (기술 세부):
    services/video_merge.py:91 — L0에 'ffmpeg'

[🟡 MEDIUM 위반]
  고아 파일:
    services/mock_data.py (import 없음)

[권고사항]
  1. /pyramid-label 실행으로 미라벨 일괄 적용
  2. L0 오용 N개 → L3 주석으로 이동
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## L0 의미 검증 기준

```
❌ L0 위반 패턴:
  기술 수치:  timeout, 비트레이트, msec, fps
  특정 도구:  ffmpeg, FastAPI, asyncio
  파일형식:   .py, .ts, .mp4

✅ L0 올바른 패턴:
  "SNS 업로드 자동화 — 유저 개입 없이 콘텐츠 발행"
  "비용 투명성 — API 실사용량을 언제든 확인 가능"
```

---

## 활용 시점

```
신규 기능 추가 전:
→ /pyramid-topology → 기존 L2 중 재사용 가능한 것 파악

기능 삭제 전:
→ /pyramid-topology → 삭제 대상 귀속 L2/L3 목록 추출

아키텍처 변경 전:
→ /pyramid-topology → /ontology-review-gate 로 PASS 받은 후 실행
```

---

## 분석 완료 후 다음 액션

- 미라벨 비-trivial 단위 > 20%: `/pyramid-label` 먼저 실행
- L0 오용 존재: 해당 줄의 L0를 L3로 이동
- 고아 파일 존재: 파이프라인 연결 또는 삭제 검토
