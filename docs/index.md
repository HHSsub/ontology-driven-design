---
layout: home
title: ODD — Ontology Driven Design
hero:
  name: "ODD"
  text: "Ontology Driven Design"
  tagline: "AI 코딩 에이전트의 목적 거버넌스 레이어. 코드 변경이 일어나기 전에 개념 위계와 단일 진실원을 강제하여 vibe-code drift를 막는다."
  actions:
    - theme: brand
      text: 5분 퀵스타트
      link: /guide/getting-started
    - theme: alt
      text: GitHub
      link: https://github.com/HHSsub/ontology-driven-design
    - theme: alt
      text: English
      link: /en/

features:
  - icon: 🎯
    title: 목적 강제 (pyramid-ontology)
    details: L0 선언 없이는 어떤 편집도 시작할 수 없다. 코드, 보고서, 이메일 — 모든 산출물에 적용.
  - icon: 🔓
    title: 탈존재 원칙 (ontology-detach)
    details: 모든 binding에 교체조건을 강제한다. 하드코딩은 거짓말이다 — 시간이 지나면 반드시 깨진다.
  - icon: 🧠
    title: 영구 학습 (ontology-learning)
    details: 실수를 L3→L2→L1→L0로 역추적. 발견한 원칙을 규칙으로 영구화. ODD는 자신의 실수에서 진화한다.
  - icon: ⚖️
    title: 구현 심판 게이트 (ontology-review-gate)
    details: 구현 전 ontology court 심사. PASS 없이는 코드를 짤 수 없다. 조기 L3 실행을 차단.
  - icon: 📐
    title: 위계 무결성 (pyramid-topology)
    details: 미라벨 단위, L0 오염, 고아 파일, 순환 의존성 탐지. 리팩토링 전 필수.
  - icon: 🗺️
    title: 위상도 재빌드 (ontology-rebuild)
    details: 프로젝트 전체의 L0-L3 위상도 자동 생성. 폴더별 ONTOLOGY.md.
  - icon: 🏷️
    title: 위계 라벨링 (pyramid-label)
    details: 어떤 언어, 어떤 파일 형식이든 코드 단위 전체에 L0-L3 라벨 일괄 적용.
  - icon: 🔒
    title: 자동 강제 훅 13개
    details: 목적 없는 편집 차단, SSOT 위반 탐지, TDD 강제 — 파일이 변경되기 전에 작동한다.
---

## L0-L3 위계

ODD가 강제하는 4계층 목적 위계. 모든 산출물에 동일하게 적용된다.

| 레벨 | 층위 | 질문 | 이것으로 표현할 수 없음 |
|------|------|------|---------------------|
| **L0** | 목적 / 존재 이유 | *이것이 왜 존재해야 하는가?* | 도구명, 플랫폼명 |
| **L1** | 구조 / 아키텍처 | *L0를 현실로 끌어내리는 불변 설계는?* | L0 없이 독립 존재 불가 |
| **L2** | 판단 / 트레이드오프 | *무엇을 선택하고 무엇을 포기했는가?* | 기록 없이 암묵 처리 불가 |
| **L3** | 실행 / 구체 | *실제 행동은 무엇인가?* | L0와 무관한 고아 코드 |

**법칙:** L0를 말할 수 없으면 중단하고 먼저 물어라.

> **ODD는 자기 적용이 가능하다.** ODD 자체를 개선할 때도 동일한 L0-L3 위계가 작동했다.
> 스케일이 달라도 같은 규칙이 반복되는 프랙탈 구조다. [케이스 스터디 →](/guide/getting-started)

---

## 설치

```bash
claude plugin add HHSsub/ontology-driven-design
```

> 설치 명령어는 Claude Code 버전에 따라 다를 수 있습니다. [수동 설치 →](/guide/installation)

---

*Created by [황회선 (Hwang Hoe Sun)](https://knowgram.vercel.app) · [피라미드사고법](https://knowgram.vercel.app) 기반*
