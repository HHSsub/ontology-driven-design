# LinkML Export Guide

<!-- L0: ODD 스키마를 다양한 표준 형식(JSON Schema, OWL, Python)으로 내보내어 외부 도구와의 연동을 가능하게 한다 -->
<!-- ExitCondition: LinkML 없이도 동등한 export가 가능한 경량 파이프라인이 구축될 때 -->

**Source schema:** [`schemas/odd.linkml.yaml`](../../schemas/odd.linkml.yaml)
**Concept definitions:** [`ontology/concept-registry.yaml`](../../ontology/concept-registry.yaml)

---

## 설치

```bash
pip install linkml
```

Python 3.9 이상 필요. LinkML 공식 문서: https://linkml.io/linkml/

---

## export 명령 모음

### JSON Schema export

```bash
gen-json-schema schemas/odd.linkml.yaml > schemas/odd.generated.schema.json
```

생성된 파일은 ODD 아티팩트를 `jsonschema` 라이브러리로 검증할 때 사용한다:

```python
import json
import jsonschema
import yaml

with open("schemas/odd.generated.schema.json") as f:
    schema = json.load(f)

artifact = {
    "version": "1.0",
    "namespace": "odd",
    "concepts": [...]
}
jsonschema.validate(artifact, schema)  # 위반 시 ValidationError
```

### OWL (Web Ontology Language) export

```bash
gen-owl schemas/odd.linkml.yaml > schemas/odd.owl.ttl
```

생성된 `.ttl` 파일은 Protégé, Apache Jena 등 OWL 도구에서 열 수 있다.
`odd:Purpose`, `odd:ExistenceClinging` 등이 OWL Class로 export된다.

### Python dataclass export

```bash
gen-python schemas/odd.linkml.yaml > odd_model.py
```

생성된 Python 파일로 타입 안전한 ODD 아티팩트를 생성한다:

```python
from odd_model import PyramidDeclaration, PurposeLevel

declaration = PyramidDeclaration(
    l0="L0: 사용자가 의도를 잃지 않고 코드를 진화시킬 수 있도록 한다",
    l1="L1: 4계층 피라미드 위계로 모든 편집 결정을 구조화한다"
)
```

### Markdown 문서 export

```bash
gen-markdown schemas/odd.linkml.yaml -d docs/generated/
```

---

## 수동 검증 (LinkML 없이)

LinkML 설치 없이 concept-registry.yaml의 유효성을 확인하는 방법:

```bash
# YAML 문법 검사
python -c "import yaml; yaml.safe_load(open('ontology/concept-registry.yaml'))"

# 필수 필드 검사
python - <<'EOF'
import yaml

with open("ontology/concept-registry.yaml") as f:
    reg = yaml.safe_load(f)

assert reg["version"], "version missing"
assert reg["namespace"] == "odd", "namespace must be 'odd'"

for concept in reg["concepts"]:
    assert "id" in concept, f"id missing: {concept}"
    assert "label" in concept, f"label missing: {concept['id']}"
    assert "definition" in concept, f"definition missing: {concept['id']}"
    assert concept["id"].startswith("odd:"), f"id must start with 'odd:': {concept['id']}"

print(f"OK: {len(reg['concepts'])} concepts validated")
EOF
```

---

## odd.schema.json 직접 사용 (수동 작성 스키마)

LinkML에서 자동 생성된 스키마 외에, 수동으로 작성된 `schemas/odd.schema.json`을 사용할 수 있다.

```python
import json
import jsonschema

with open("schemas/odd.schema.json") as f:
    schema = json.load(f)

# L0 선언 문자열 검증
l0_schema = schema["$defs"]["L0Declaration"]
jsonschema.validate(
    "L0: 사용자가 의도를 잃지 않고 코드를 진화시킬 수 있도록 한다",
    l0_schema
)
# → 통과

jsonschema.validate("L0: React", l0_schema)
# → ValidationError: 8자 미만
```

---

## export 파일 위치 규칙

| export 형식 | 생성 명령 | 출력 위치 |
|-------------|----------|----------|
| JSON Schema (LinkML auto) | `gen-json-schema` | `schemas/odd.generated.schema.json` |
| JSON Schema (수동 작성) | 없음 | `schemas/odd.schema.json` |
| OWL Turtle | `gen-owl` | `schemas/odd.owl.ttl` |
| Python dataclass | `gen-python` | `odd_model.py` (root) |
| Markdown docs | `gen-markdown` | `docs/generated/` |

자동 생성 파일은 `.gitignore`에 추가하거나, CI에서 생성하여 artifacts로 관리한다.

---

## CI 통합 예시

```yaml
# .github/workflows/schema-export.yml
name: Schema Export
on: [push]
jobs:
  export:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install linkml
      - run: gen-json-schema schemas/odd.linkml.yaml > schemas/odd.generated.schema.json
      - run: gen-owl schemas/odd.linkml.yaml > schemas/odd.owl.ttl
      - uses: actions/upload-artifact@v4
        with:
          name: odd-schema-exports
          path: schemas/
```
