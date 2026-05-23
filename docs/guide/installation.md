# 설치

## 요구사항

- [Claude Code](https://claude.ai/code) CLI

## 설치 명령어

```bash
# 풀네임 (권장)
claude plugin add HHSsub/ontology-driven-design

# 단축 alias (동일하게 작동)
claude plugin add HHSsub/odd
```

## 확인

설치 후 Claude Code 세션에서:

```bash
/pyramid-ontology
```

스킬이 로드되면 설치 완료입니다.

## 제거

```bash
claude plugin remove HHSsub/ontology-driven-design
```

## 수동 설치

플러그인 시스템을 사용하지 않는 경우, 스킬 파일을 직접 복사할 수 있습니다:

```bash
# 레포 클론
git clone https://github.com/HHSsub/ontology-driven-design.git

# 스킬 복사
cp -r ontology-driven-design/skills/* ~/.claude/skills/
cp ontology-driven-design/commands/* ~/.claude/commands/
```
