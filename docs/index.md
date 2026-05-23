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
L0  비즈니스 최종 목적    WHY — 왜 존재하는가
L1  시스템/문서 목표      HOW — 어떻게 달성하는가
L2  기능/섹션 단위        WHAT — 무엇을 만드는가
L3  구현/표현 세부        WITH WHAT — 어떤 도구로
```

**법칙:** L0를 말할 수 없으면 중단하고 먼저 물어라.

---

*Created by [황회선 (Hwang Hoe Sun)](https://knowgram.vercel.app) · [피라미드사고법](https://knowgram.vercel.app) 기반*
