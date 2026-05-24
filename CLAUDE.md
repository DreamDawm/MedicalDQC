<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **MedicalDQC** (761 symbols, 1063 relationships, 4 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.



## 前后端默认的端口

​	前端默认端口是3000

​	后端默认端口是8999

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/MedicalDQC/context` | Codebase overview, check index freshness |
| `gitnexus://repo/MedicalDQC/clusters` | All functional areas |
| `gitnexus://repo/MedicalDQC/processes` | All execution flows |
| `gitnexus://repo/MedicalDQC/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |
| Work in the Views area (18 symbols) | `.claude/skills/generated/views/SKILL.md` |
| Work in the Services area (10 symbols) | `.claude/skills/generated/services/SKILL.md` |
| Work in the Api area (8 symbols) | `.claude/skills/generated/api/SKILL.md` |
| Work in the Models area (6 symbols) | `.claude/skills/generated/models/SKILL.md` |

<!-- gitnexus:end -->

---

# DataQC Platform

数据质量校验平台，基于 Great Expectations (GX Core) 框架，支持通过 Web 界面配置校验规则、连接多种数据库、执行校验任务并生成报告。

## 技术栈

- **后端**: FastAPI + Celery + Redis + PostgreSQL
- **前端**: Vue 3 + Element Plus + ECharts + Vite
- **校验引擎**: Great Expectations Core (via SQLAlchemy)
- **异步任务**: Celery with Redis broker

## 开发命令

### 后端

```bash
# 安装依赖
cd backend && pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 初始化内置规则（30条 GX expectations）
python seed_rules.py

# 启动开发服务器
python -m uvicorn app.main:app --host 127.0.0.1 --port 8999

# 启动 Celery worker（执行校验）
celery -A app.celery_app.celery_config worker --loglevel=info

# 启动 Celery beat（定时任务调度）
celery -A app.celery_app.celery_config beat --loglevel=info

# 运行测试
pytest
```

### 前端

```bash
# 安装依赖
cd frontend && npm install

# 启动开发服务器（代理后端 localhost:8000）
npm run dev

# 构建生产版本
npm run build
```

## 核心架构

### 数据流

1. 用户创建 **Datasource**（数据库连接）
2. 用户配置 **ValidationRules**（数据源→表→列→内置规则→参数）
3. 用户创建 **ValidationTask**（组合多条规则，可选 cron 定时）
4. 触发任务（手动或定时）→ Celery worker 通过 `gx_engine.py` 执行
5. 存储 **ValidationResult**，生成 HTML 报告

### 关键模块

| 模块 | 职责 |
|------|------|
| `services/gx_engine.py` | GX Core 集成，创建 ExpectationSuite，执行校验 |
| `celery_app/tasks.py` | 异步任务，按表分组规则，调用 gx_engine，聚合结果 |
| `services/datasource_service.py` | 数据库元数据获取（表、列、注释） |
| `seed_rules.py` | 30条内置 GX expectations 映射 |

### 前端组件

| 组件 | 职责 |
|------|------|
| `RuleSelector.vue` | 规则下拉选择（按 usage_count 排序） |
| `ParameterForm.vue` | 根据 parameters_schema 动态渲染参数表单 |
| `CronSelector.vue` | Cron 表达式下拉选择（预设常用定时） |

## API 端点

| 前缀 | 用途 |
|------|------|
| `/api/datasources` | 数据源连接、测试连接、获取表/列 |
| `/api/builtin-rules` | 内置规则列表（按使用频率排序） |
| `/api/validation-rules` | 用户规则配置 |
| `/api/tasks` | 任务管理、手动触发 |
| `/api/results` | 校验结果、趋势数据、HTML 报告 |

## 环境配置

后端读取 `.env` 文件（见 `config.py`）：
- `database_url`: PostgreSQL 元数据库
- `redis_url`: Celery 消息队列
- `secret_key`: 密码加密密钥
- `report_dir`: HTML 报告输出目录
