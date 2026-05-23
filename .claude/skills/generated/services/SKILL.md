---
name: services
description: "Skill for the Services area of MedicalDQC. 10 symbols across 5 files."
---

# Services

10 symbols | 5 files | Cohesion: 100%

## When to Use

- Working with code in `backend/`
- Understanding how generate_html_report, run_expectations, build_connection_url work
- Modifying services-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `backend/app/services/datasource_service.py` | build_connection_url, test_connection, get_tables, get_columns |
| `backend/app/api/datasources.py` | test_ds_connection, list_tables, list_columns |
| `backend/app/services/report_service.py` | generate_html_report |
| `backend/app/services/gx_engine.py` | run_expectations |
| `backend/app/celery_app/tasks.py` | run_validation_task |

## Entry Points

Start here when exploring this area:

- **`generate_html_report`** (Function) — `backend/app/services/report_service.py:11`
- **`run_expectations`** (Function) — `backend/app/services/gx_engine.py:6`
- **`build_connection_url`** (Function) — `backend/app/services/datasource_service.py:4`
- **`test_connection`** (Function) — `backend/app/services/datasource_service.py:18`
- **`get_tables`** (Function) — `backend/app/services/datasource_service.py:28`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `generate_html_report` | Function | `backend/app/services/report_service.py` | 11 |
| `run_expectations` | Function | `backend/app/services/gx_engine.py` | 6 |
| `build_connection_url` | Function | `backend/app/services/datasource_service.py` | 4 |
| `test_connection` | Function | `backend/app/services/datasource_service.py` | 18 |
| `get_tables` | Function | `backend/app/services/datasource_service.py` | 28 |
| `get_columns` | Function | `backend/app/services/datasource_service.py` | 34 |
| `test_ds_connection` | Function | `backend/app/api/datasources.py` | 65 |
| `list_tables` | Function | `backend/app/api/datasources.py` | 76 |
| `list_columns` | Function | `backend/app/api/datasources.py` | 88 |
| `run_validation_task` | Function | `backend/app/celery_app/tasks.py` | 13 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_validation_task → Build_connection_url` | intra_community | 3 |

## How to Explore

1. `gitnexus_context({name: "generate_html_report"})` — see callers and callees
2. `gitnexus_query({query: "services"})` — find related execution flows
3. Read key files listed above for implementation details
