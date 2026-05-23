# DataQC 平台设计文档

## 概述

基于 Great Expectations (GX Core) 框架的数据质量校验平台，支持通过 Web 界面配置校验规则、连接多种数据库、执行校验任务并生成报告。

## 技术栈

- **后端**: FastAPI + Celery + Redis + PostgreSQL
- **前端**: Vue 3 + Element Plus + ECharts
- **校验引擎**: Great Expectations Core (通过 SQLAlchemy 连接目标库)
- **部署**: Docker Compose / 本地开发

## 系统架构

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│  Vue 3 Frontend │ ◄──────────► │  FastAPI Backend │
│  (Element Plus) │               │   (REST API)    │
└─────────────────┘               └────────┬────────┘
                                           │ Celery Task
                                           ▼
┌─────────────────┐               ┌─────────────────┐
│  基础设施        │               │  Celery Worker  │
│  - PostgreSQL   │               │  + GX Core      │
│  - Redis        │               │  + Celery Beat  │
└─────────────────┘               └────────┬────────┘
                                           │ SQLAlchemy
                                           ▼
                                  ┌─────────────────┐
                                  │  目标校验数据库   │
                                  │  - MySQL        │
                                  │  - PostgreSQL   │
                                  │  - SQL Server   │
                                  └─────────────────┘
```

## 用户模式

单用户本地使用，无认证。

## 数据模型

### datasources（数据源）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | String | 数据源名称 |
| db_type | Enum | mysql / postgresql / sqlserver |
| host | String | 主机地址 |
| port | Integer | 端口 |
| database | String | 数据库名 |
| username | String | 用户名 |
| password | String | 密码（加密存储） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### builtin_rules（内置规则映射）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| expectation_type | String | GX Expectation 类名 |
| display_name | String | 中文显示名 |
| category | String | 类别 |
| description | String | 中文描述 |
| parameters_schema | JSON | 参数定义（前端动态渲染表单） |
| usage_count | Integer | 使用次数（下拉排序依据） |
| created_at | DateTime | 创建时间 |

### validation_rules（校验规则配置）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| datasource_id | FK | 数据源 |
| table_name | String | 表名 |
| column_name | String | 列名（表级规则时为空） |
| builtin_rule_id | FK | 内置规则 |
| parameters | JSON | 用户填写的参数值 |
| mostly | Float | 容忍度（0-1） |
| severity | Enum | critical / warning / info |
| row_condition | String | 行条件过滤表达式 |
| enabled | Boolean | 是否启用 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### validation_tasks（校验任务）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | String | 任务名称 |
| datasource_id | FK | 数据源 |
| rule_ids | JSON | 关联的规则 ID 列表 |
| schedule_cron | String | cron 表达式（可为空） |
| is_active | Boolean | 是否激活 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### validation_results（校验结果）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| task_id | FK | 所属任务 |
| status | Enum | running / success / failed / error |
| started_at | DateTime | 开始时间 |
| finished_at | DateTime | 结束时间 |
| total_expectations | Integer | 总规则数 |
| passed_count | Integer | 通过数 |
| failed_count | Integer | 失败数 |
| result_detail | JSON | 每条规则的详细结果 |
| report_path | String | 导出的 HTML 报告路径 |

## 内置校验规则（30 条）

### 一、完整性校验（5 条）

| # | 中文名 | GX Expectation |
|---|--------|----------------|
| 1 | 非空检查 | expect_column_values_to_not_be_null |
| 2 | 空值检查 | expect_column_values_to_be_null |
| 3 | 行数精确匹配 | expect_table_row_count_to_equal |
| 4 | 行数范围检查 | expect_table_row_count_to_be_between |
| 5 | 唯一值比例检查 | expect_column_proportion_of_unique_values_to_be_between |

### 二、唯一性与主键校验（3 条）

| # | 中文名 | GX Expectation |
|---|--------|----------------|
| 6 | 唯一性检查 | expect_column_values_to_be_unique |
| 7 | 复合唯一性检查 | expect_compound_columns_to_be_unique |
| 8 | 记录内列唯一性 | expect_select_column_values_to_be_unique_within_record |

### 三、数据类型与格式校验（5 条）

| # | 中文名 | GX Expectation |
|---|--------|----------------|
| 9 | 数据类型检查 | expect_column_values_to_be_of_type |
| 10 | 正则匹配 | expect_column_values_to_match_regex |
| 11 | 日期格式检查 | expect_column_values_to_match_strftime_format |
| 12 | 字符串长度范围 | expect_column_value_lengths_to_be_between |
| 13 | 正则排除 | expect_column_values_to_not_match_regex |

### 四、数据范围与数值校验（6 条）

| # | 中文名 | GX Expectation |
|---|--------|----------------|
| 14 | 值范围检查 | expect_column_values_to_be_between |
| 15 | 最大值范围检查 | expect_column_max_to_be_between |
| 16 | 最小值范围检查 | expect_column_min_to_be_between |
| 17 | 均值范围检查 | expect_column_mean_to_be_between |
| 18 | 中位数范围检查 | expect_column_median_to_be_between |
| 19 | 标准差范围检查 | expect_column_stdev_to_be_between |

### 五、枚举值与参照完整性校验（3 条）

| # | 中文名 | GX Expectation |
|---|--------|----------------|
| 20 | 值集合检查 | expect_column_values_to_be_in_set |
| 21 | 类型列表检查 | expect_column_values_to_be_in_type_list |
| 22 | 禁止值检查 | expect_column_values_to_not_be_in_set |

### 六、排序与序列校验（4 条）

| # | 中文名 | GX Expectation |
|---|--------|----------------|
| 23 | 递增检查 | expect_column_values_to_be_increasing |
| 24 | 递减检查 | expect_column_values_to_be_decreasing |
| 25 | 非递减检查 | expect_column_values_to_be_non_decreasing |
| 26 | 非递增检查 | expect_column_values_to_be_non_increasing |

### 七、跨列与业务规则校验（4 条）

| # | 中文名 | GX Expectation |
|---|--------|----------------|
| 27 | 双列相等检查 | expect_column_pair_values_to_be_equal |
| 28 | 双列组合集合检查 | expect_column_pair_values_to_be_in_set |
| 29 | A列大于B列 | expect_column_pair_values_A_to_be_greater_than_B |
| 30 | A列大于等于B列 | expect_column_pair_values_A_to_be_greater_than_or_equal_to_B |

### 通用参数

所有规则均支持以下通用参数：

- **mostly** (Float 0-1): 容忍度，如 0.95 表示允许 5% 异常
- **severity** (Enum): critical / warning / info，区分严重等级
- **row_condition** (String): 行条件过滤，将校验应用于数据子集

## API 设计

### 数据源管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/datasources | 创建数据源连接 |
| GET | /api/datasources | 获取所有数据源列表 |
| GET | /api/datasources/{id} | 获取单个数据源详情 |
| PUT | /api/datasources/{id} | 更新数据源 |
| DELETE | /api/datasources/{id} | 删除数据源 |
| POST | /api/datasources/{id}/test | 测试连接 |
| GET | /api/datasources/{id}/tables | 获取所有表 |
| GET | /api/datasources/{id}/tables/{table}/columns | 获取列信息 |

### 内置规则

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/builtin-rules | 规则列表（按 usage_count 降序） |
| GET | /api/builtin-rules/{id} | 规则详情（含 parameters_schema） |

### 校验规则配置

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/validation-rules | 创建校验规则配置 |
| GET | /api/validation-rules | 获取所有配置 |
| PUT | /api/validation-rules/{id} | 更新配置 |
| DELETE | /api/validation-rules/{id} | 删除配置 |

### 校验任务

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/tasks | 创建校验任务 |
| GET | /api/tasks | 获取任务列表 |
| PUT | /api/tasks/{id} | 更新任务 |
| DELETE | /api/tasks/{id} | 删除任务 |
| POST | /api/tasks/{id}/run | 手动触发执行 |

### 校验结果

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/results | 结果列表（分页、按 task_id 筛选） |
| GET | /api/results/{id} | 单次校验详情 |
| GET | /api/results/{id}/report | 下载 HTML 报告 |
| GET | /api/results/trend | 趋势数据（按时间聚合通过率） |

## 前端页面结构

### 页面导航

DataQC | 数据源 | 校验规则 | 校验任务 | 校验报告 | 趋势分析

### 页面职责

1. **数据源管理** — 新增/编辑/删除连接，选择数据库类型，测试连接，浏览表/列
2. **校验规则配置** — 级联选择（数据源→表→列），下拉选规则（中文，按使用频率排序），动态参数表单 + 通用参数
3. **校验任务** — 组合多条规则为任务，设置定时 cron，手动触发执行，查看状态
4. **校验报告** — 结果列表，每条规则通过率详情，失败数据样本预览，HTML 报告导出
5. **趋势分析** — 按任务/数据源筛选，ECharts 折线图（通过率变化），规则维度柱状图

### 用户操作流程

配置数据源 → 浏览表/列 → 选择规则配置参数 → 组合为任务 → 执行 → 查看报告 → 分析趋势

## 项目目录结构

```
dataqc/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   └── celery_app/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   ├── components/
│   │   ├── api/
│   │   ├── router/
│   │   └── App.vue
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Docker Compose 服务

| 服务 | 镜像/构建 | 端口 | 职责 |
|------|-----------|------|------|
| postgres | postgres:16 | 5432 | 平台元数据库 |
| redis | redis:7 | 6379 | Celery 消息队列 |
| backend | ./backend | 8000 | FastAPI REST API |
| celery-worker | ./backend | - | GX Core 校验执行 |
| celery-beat | ./backend | - | 定时任务调度 |
| frontend | ./frontend | 3000 | Vue 3 前端 |
