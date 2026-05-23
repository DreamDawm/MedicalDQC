---
name: models
description: "Skill for the Models area of MedicalDQC. 6 symbols across 6 files."
---

# Models

6 symbols | 6 files | Cohesion: 100%

## When to Use

- Working with code in `backend/`
- Understanding how Base, ValidationTask, ValidationRule work
- Modifying models-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `backend/app/database.py` | Base |
| `backend/app/models/validation_task.py` | ValidationTask |
| `backend/app/models/validation_rule.py` | ValidationRule |
| `backend/app/models/validation_result.py` | ValidationResult |
| `backend/app/models/datasource.py` | Datasource |
| `backend/app/models/builtin_rule.py` | BuiltinRule |

## Entry Points

Start here when exploring this area:

- **`Base`** (Class) — `backend/app/database.py:9`
- **`ValidationTask`** (Class) — `backend/app/models/validation_task.py:10`
- **`ValidationRule`** (Class) — `backend/app/models/validation_rule.py:10`
- **`ValidationResult`** (Class) — `backend/app/models/validation_result.py:10`
- **`Datasource`** (Class) — `backend/app/models/datasource.py:10`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `Base` | Class | `backend/app/database.py` | 9 |
| `ValidationTask` | Class | `backend/app/models/validation_task.py` | 10 |
| `ValidationRule` | Class | `backend/app/models/validation_rule.py` | 10 |
| `ValidationResult` | Class | `backend/app/models/validation_result.py` | 10 |
| `Datasource` | Class | `backend/app/models/datasource.py` | 10 |
| `BuiltinRule` | Class | `backend/app/models/builtin_rule.py` | 10 |

## How to Explore

1. `gitnexus_context({name: "Base"})` — see callers and callees
2. `gitnexus_query({query: "models"})` — find related execution flows
3. Read key files listed above for implementation details
