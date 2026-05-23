---
name: api
description: "Skill for the Api area of MedicalDQC. 8 symbols across 5 files."
---

# Api

8 symbols | 5 files | Cohesion: 100%

## When to Use

- Working with code in `frontend/`
- Understanding how test, testConnection, run work
- Modifying api-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `frontend/src/api/index.js` | test, run, trend, reportUrl |
| `frontend/src/views/DatasourceView.vue` | testConnection |
| `frontend/src/views/TaskView.vue` | handleRun |
| `frontend/src/views/TrendView.vue` | loadData |
| `frontend/src/views/ResultView.vue` | downloadReport |

## Entry Points

Start here when exploring this area:

- **`test`** (Function) — `frontend/src/api/index.js:13`
- **`testConnection`** (Function) — `frontend/src/views/DatasourceView.vue:59`
- **`run`** (Function) — `frontend/src/api/index.js:35`
- **`handleRun`** (Function) — `frontend/src/views/TaskView.vue:253`
- **`trend`** (Function) — `frontend/src/api/index.js:41`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test` | Function | `frontend/src/api/index.js` | 13 |
| `testConnection` | Function | `frontend/src/views/DatasourceView.vue` | 59 |
| `run` | Function | `frontend/src/api/index.js` | 35 |
| `handleRun` | Function | `frontend/src/views/TaskView.vue` | 253 |
| `trend` | Function | `frontend/src/api/index.js` | 41 |
| `loadData` | Function | `frontend/src/views/TrendView.vue` | 35 |
| `reportUrl` | Function | `frontend/src/api/index.js` | 42 |
| `downloadReport` | Function | `frontend/src/views/ResultView.vue` | 77 |

## How to Explore

1. `gitnexus_context({name: "test"})` — see callers and callees
2. `gitnexus_query({query: "api"})` — find related execution flows
3. Read key files listed above for implementation details
