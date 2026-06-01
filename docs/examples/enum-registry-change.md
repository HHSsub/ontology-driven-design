# SSOT — Changing an Enum Registry

> L0: Developers change an enum value once and have confidence every downstream consumer is updated — no silent divergence, no runtime surprises.

This is the most critical Single Source of Truth (SSOT) scenario in any codebase. Enum-like values (status codes, role names, event types, category labels) tend to be defined in one place but referenced silently in many. Changing one without updating the others creates bugs that survive testing.

---

## The Problem

You have an order status enum. It exists in three places:

**Python backend — `models.py`:**

```python
class OrderStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

**TypeScript frontend — `types.ts`:**

```typescript
export type OrderStatus =
  | "pending"
  | "processing"
  | "shipped"
  | "delivered"
  | "cancelled";
```

**Database migration — `0003_add_status_index.sql`:**

```sql
CREATE INDEX idx_orders_status
ON orders(status)
WHERE status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled');
```

You need to add `FAILED` as a new status.

---

## Without ODD

```
1. Add FAILED to models.py
2. Deploy
3. Frontend TypeScript now accepts strings that don't include "failed"
   → TypeScript silently casts to unknown
   → UI shows blank status for failed orders
4. Database index doesn't cover 'failed'
   → Slow queries on failed order lookups
5. Three weeks later, a bug report arrives
```

The root cause: the developer knew only one of the three locations. The other two were invisible at the time of change.

---

## With ODD — What the Hooks Do

### pyramid_guard fires on every Edit/Write

When you edit `models.py` to add `FAILED`, the `pyramid_guard` PostToolUse hook runs **L2-G: Duplicate Truth detection**.

The hook detects that the string set `{"pending", "processing", "shipped", "delivered", "cancelled"}` — five members, appearing in multiple independent list structures — matches a SSOT violation pattern.

It outputs:

```
⚠️  SSOT VIOLATION DETECTED — L2-G: Duplicate Truth
File: models.py
Pattern: string set {"pending", "processing", "shipped", "delivered", ...} appears in multiple independent locations.

Before changing this enum:
1. grep -r "pending\|processing\|shipped\|delivered\|cancelled" . --include="*.py" --include="*.ts" --include="*.sql"
2. Update ALL locations in the same commit
3. Verify no stale references remain
```

The hook does not proceed until you run the grep and confirm all locations are handled.

### ontology_declare_enforce fires at session end

At session close, the `ontology_declare_enforce` Stop hook checks:

> "Was an enum/concept-set modified this session? If yes, is there Grep evidence in the transcript that the developer searched for all references?"

If you modified `models.py` and no Grep call appears in the transcript, the hook blocks the response:

```
❌ BLOCK: ontology_declare_enforce — L2-B dependency chain
Detected: enum concept set modified in models.py
Required: Grep evidence of dependency search before modification
Missing: no grep/search found in this session's transcript

Run: grep -r "pending\|processing" . --include="*.py" --include="*.ts" --include="*.sql"
Then update all locations and re-run.
```

---

## The ODD Way — Step by Step

### Step 1: Declare L0 at session start

```
L0: Order status changes propagate correctly to all consumers — no silent divergence
L1: Add FAILED status to enum registry and all dependent layers
```

### Step 2: Search before touching

```bash
grep -r "pending\|processing\|shipped\|delivered\|cancelled" . \
  --include="*.py" --include="*.ts" --include="*.sql" \
  -l
```

Output:
```
./models.py
./frontend/types.ts
./migrations/0003_add_status_index.sql
./tests/test_order_flow.py
```

Four files. You now have the complete dependency map before touching anything.

### Step 3: Update all locations in one commit

**Python — `models.py`:**

```python
class OrderStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"          # added
```

**TypeScript — `types.ts`:**

```typescript
export type OrderStatus =
  | "pending"
  | "processing"
  | "shipped"
  | "delivered"
  | "cancelled"
  | "failed";                  // added
```

**SQL — new migration `0004_add_failed_status.sql`:**

```sql
-- L0: Order status index covers all valid states including FAILED
-- L1: Add failed to the partial index used by order lookup queries
-- L2: New migration rather than modifying 0003 — immutable migration history
-- L3: DROP and recreate index to include 'failed'

DROP INDEX IF EXISTS idx_orders_status;
CREATE INDEX idx_orders_status
ON orders(status)
WHERE status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'failed');
```

**Tests — `tests/test_order_flow.py`:**

```python
# Update any hardcoded status string assertions
def test_failed_order_status():
    order = create_order(status="failed")
    assert order.status == OrderStatus.FAILED
```

### Step 4: Verify

```bash
python -m pytest tests/test_order_flow.py
npx tsc --noEmit
```

Both verification commands appear in the transcript. The `tdd_enforce_stop` hook is satisfied.

### Step 5: Commit atomically

```bash
git add models.py frontend/types.ts migrations/0004_add_failed_status.sql tests/test_order_flow.py
git commit -m "feat: add FAILED order status — update all four consumers atomically"
git push origin main
```

The `git_push_enforce_stop` hook clears. Session ends cleanly.

---

## The SSOT Principle in One Rule

> When you find a concept defined in more than one place, you have a divergence waiting to happen. ODD's job is to force you to find all instances before touching any of them.

The `pyramid_guard` hook automates this reminder. It does not replace your judgment about *where* to make changes — it ensures you cannot forget that multiple places exist.

---

## Pattern: Centralizing a Scattered Enum

If the grep reveals the enum is in five or more locations, the correct ODD response is not to update all five — it is to centralize first:

1. Create a single source file: `constants/order_status.py` (Python) or `constants/orderStatus.ts` (TS)
2. Make all other locations import from this single source
3. Run grep again to confirm zero remaining inline definitions
4. Now add `FAILED` in exactly one place

This is L1 structural work before L3 implementation. ODD's hierarchy enforces this sequence.

---

## Related guides

- [Solo developer workflow](./solo-developer.md) — daily ODD usage patterns
- [Legacy refactor guide](./legacy-refactor.md) — adopting ODD on existing codebases
- [Hook reference](../skills/hooks.md) — pyramid_guard and ontology_declare_enforce in detail
