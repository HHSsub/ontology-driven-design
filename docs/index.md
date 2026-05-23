---
layout: home
title: ODD — Ontology Driven Design
hero:
  name: "ODD"
  text: "Ontology Driven Design"
  tagline: "목적 없는 코드는 쓰레기다. 기능이 동작해도 목적이 없으면 실패다."
  actions:
    - theme: brand
      text: 시작하기
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
    details: 어떤 작업이든 L0(비즈니스 목적) 선언 없이는 시작할 수 없다. 코드, 보고서, 이메일 — 모든 산출물에 적용.
  - icon: 🔓
    title: 탈존재 원칙 (ontology-detach)
    details: 모든 binding에 교체조건을 강제한다. 하드코딩은 거짓말이다. 시간이 지나면 반드시 깨진다.
  - icon: 🗺️
    title: 위상도 재빌드 (ontology-rebuild)
    details: 프로젝트 전체의 L0-L3 위상도를 자동 생성. 폴더별 ONTOLOGY.md + 루트 _WIKI.md.
  - icon: 🏷️
    title: 라벨링 (pyramid-label)
    details: 어떤 언어든 코드 단위 전체에 L0-L3 라벨을 일괄 적용. Python, TypeScript, Go, YAML, Markdown.
  - icon: 📐
    title: 위계 점검 (pyramid-topology)
    details: 미라벨 단위, L0 오염, 고아 파일, 순환 의존을 탐지. 리팩토링 전 필수.
  - icon: ⚖️
    title: 심판 게이트 (ontology-review-gate)
    details: 구현 전 ontology court 심사. PASS 없이는 코드를 짤 수 없다.
---

## 설치

```bash
claude plugin add HHSsub/ontology-driven-design
# 또는 단축명
claude plugin add HHSsub/odd
```

## L0-L3 위계

```
L0  존재론 / 목적          궁극적 융합과 내재화 — 이것이 존재해야 하는 가장 심연의 이유
L1  추상 / 구조            질서의 아키텍처 — L0를 현실로 끌어내리는 불변의 설계도
L2  로직 / 트레이드오프    현실과의 타협과 선택 — 구조가 현실에 부딪힐 때의 의사결정 기록
L3  실행 / 인스턴스        물리적 닻 — 코드, 도구, 구체적 행동
```

**법칙:** L0를 말할 수 없으면 중단하고 먼저 물어라.

> 이것은 요구사항 추적 프레임워크가 아니다. L0는 존재론적 층위다. L2는 기능 분해가 아니라 트레이드오프 기록이다.

---

*Created by [황회선 (Hwang Hoe Sun)](https://knowgram.vercel.app) · [피라미드사고법](https://knowgram.vercel.app) 기반*
