# odd-onboarding

Establishes a project's purpose before implementation begins.

Slash command: `/odd-onboarding`

---

## When to use

- Before starting a new project
- Before adding a new feature
- When direction is unclear and you're about to start building

## What it does

Asks 5 areas of plain-language questions (no jargon) to lock in the L0-L3 ontology.
Output: `ONBOARDING.md` — the project's constitution.

### 5 question areas

| Area | Question focus | Output |
|------|---------------|--------|
| **Purpose** | What pain does this solve? How do you know it worked? | L0 confirmed |
| **Never-Do** | When does this tool make things worse? | Never-Do list confirmed |
| **Auto vs Control** | What should be automatic vs manually controlled? | L1 structure confirmed |
| **Trade-offs** | Simple/fast vs accurate/detailed? How much friction is acceptable? | L2 judgment confirmed |
| **AI autonomy** | What can AI decide alone vs must ask you first? | Autonomy boundary confirmed |

## Forbidden inside this skill

- Mentioning tech stack, language, or framework ❌
- Using jargon (AWS, API, async, etc.) ❌
- Suggesting implementation approaches ❌ — only "what" and "why"

## Output format

```markdown
# ONBOARDING — [project name]

## L0: Purpose
[one sentence — what state are we trying to achieve?]

## Success criteria
## Failure criteria
## Never-Do
## L1: Overall flow
## Automatic vs manual control
## L2: Key trade-off decisions
## AI autonomy boundaries
## Implementation principles derived from this document
```

See the [skill file](https://github.com/HHSsub/ontology-driven-design/blob/main/skills/odd-onboarding/SKILL.md) for full details.
