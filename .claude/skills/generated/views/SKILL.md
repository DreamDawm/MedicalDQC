---
name: views
description: "Skill for the Views area of MedicalDQC. 18 symbols across 4 files."
---

# Views

18 symbols | 4 files | Cohesion: 88%

## When to Use

- Working with code in `frontend/`
- Understanding how getTables, onDatasourceChange, handleEdit work
- Modifying views-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `frontend/src/views/RuleConfigView.vue` | onDatasourceChange, handleEdit, onEditDatasourceChange, loadColumnComments, onTableChange (+5) |
| `frontend/src/views/TaskView.vue` | loadData, handleCreate, handleUpdate, handleDelete |
| `frontend/src/api/index.js` | getTables, getColumns |
| `frontend/src/views/DatasourceView.vue` | loadData, handleDelete |

## Entry Points

Start here when exploring this area:

- **`getTables`** (Function) — `frontend/src/api/index.js:14`
- **`onDatasourceChange`** (Function) — `frontend/src/views/RuleConfigView.vue:265`
- **`handleEdit`** (Function) — `frontend/src/views/RuleConfigView.vue:303`
- **`onEditDatasourceChange`** (Function) — `frontend/src/views/RuleConfigView.vue:339`
- **`getColumns`** (Function) — `frontend/src/api/index.js:15`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `getTables` | Function | `frontend/src/api/index.js` | 14 |
| `onDatasourceChange` | Function | `frontend/src/views/RuleConfigView.vue` | 265 |
| `handleEdit` | Function | `frontend/src/views/RuleConfigView.vue` | 303 |
| `onEditDatasourceChange` | Function | `frontend/src/views/RuleConfigView.vue` | 339 |
| `getColumns` | Function | `frontend/src/api/index.js` | 15 |
| `loadColumnComments` | Function | `frontend/src/views/RuleConfigView.vue` | 223 |
| `onTableChange` | Function | `frontend/src/views/RuleConfigView.vue` | 276 |
| `onEditTableChange` | Function | `frontend/src/views/RuleConfigView.vue` | 350 |
| `loadData` | Function | `frontend/src/views/TaskView.vue` | 164 |
| `handleCreate` | Function | `frontend/src/views/TaskView.vue` | 188 |
| `handleUpdate` | Function | `frontend/src/views/TaskView.vue` | 239 |
| `handleDelete` | Function | `frontend/src/views/TaskView.vue` | 262 |
| `loadData` | Function | `frontend/src/views/RuleConfigView.vue` | 205 |
| `handleCreate` | Function | `frontend/src/views/RuleConfigView.vue` | 289 |
| `handleUpdate` | Function | `frontend/src/views/RuleConfigView.vue` | 363 |
| `handleDelete` | Function | `frontend/src/views/RuleConfigView.vue` | 377 |
| `loadData` | Function | `frontend/src/views/DatasourceView.vue` | 44 |
| `handleDelete` | Function | `frontend/src/views/DatasourceView.vue` | 72 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `HandleCreate → GetColumns` | cross_community | 4 |
| `HandleUpdate → GetColumns` | cross_community | 4 |
| `HandleDelete → GetColumns` | cross_community | 4 |

## How to Explore

1. `gitnexus_context({name: "getTables"})` — see callers and callees
2. `gitnexus_query({query: "views"})` — find related execution flows
3. Read key files listed above for implementation details
