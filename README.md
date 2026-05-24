# DataQC - 数据质量校验平台

基于 Great Expectations (GX Core) 框架的数据质量校验平台，支持通过 Web 界面配置校验规则、连接多种数据库、执行校验任务并生成报告。

## 功能特性

- 多数据源管理：支持 PostgreSQL、MySQL、SQL Server 等数据库连接
- 内置 30+ 校验规则：基于 GX Core expectations，覆盖空值、唯一性、范围、格式等常见场景
- 跨列业务校验：支持列间比较（如 A >= B）
- 定时任务调度：基于 Cron 表达式的自动化校验
- 可视化报告：校验结果统计、趋势分析、详细 HTML 报告
- 异步执行：Celery 分布式任务队列，支持并发校验

## 技术栈

| 层 | 技术 |
|---|------|
| 后端 | FastAPI + SQLAlchemy + Alembic |
| 前端 | Vue 3 + Element Plus + ECharts + Vite |
| 校验引擎 | Great Expectations Core |
| 异步任务 | Celery + Redis |
| 元数据库 | PostgreSQL |

## 快速开始

### 环境要求

- Docker Desktop（推荐）
- PostgreSQL 数据库
- Redis 服务

### Docker 部署（推荐）

```bash
# 克隆仓库
git clone https://github.com/DreamDawm/MedicalDQC.git
cd MedicalDQC

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入实际的数据库和 Redis 连接信息

# 启动所有服务
docker-compose up -d

# 初始化数据库（首次部署）
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed_rules.py
```

服务启动后：
- 前端：http://localhost:3000
- 后端 API：http://localhost:8999
- API 文档：http://localhost:8999/docs

### 本地开发（不使用 Docker）

#### 后端

```bash
cd backend
pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 初始化内置规则
python seed_rules.py

# 启动 API 服务
python -m uvicorn app.main:app --host 127.0.0.1 --port 8999 --reload

# 启动 Celery worker
celery -A app.celery_app.celery_config worker --loglevel=info

# 启动定时任务调度
celery -A app.celery_app.celery_config beat --loglevel=info
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── celery_app/     # Celery 配置和任务
│   │   ├── models/         # SQLAlchemy 数据模型
│   │   ├── services/       # 业务逻辑（gx_engine, datasource）
│   │   └── templates/      # 报告模板
│   ├── alembic/            # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile.dev
├── frontend/
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 通用组件
│   │   └── router/         # 路由配置
│   ├── package.json
│   └── Dockerfile.dev
├── docker-compose.yml
└── .env.example
```

## 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `DATABASE_URL` | PostgreSQL 元数据库连接 | `postgresql://user:pass@localhost:5432/dataqc` |
| `REDIS_URL` | Redis 连接（Celery broker） | `redis://localhost:6379/0` |
| `SECRET_KEY` | 加密密钥 | `your-secret-key` |
| `REPORT_DIR` | 报告输出目录 | `./reports` |

## 使用流程

1. **添加数据源** - 配置目标数据库连接并测试连通性
2. **配置校验规则** - 选择表、列，配置内置校验规则及参数
3. **创建校验任务** - 组合多条规则，可设置定时执行
4. **执行校验** - 手动触发或等待定时调度
5. **查看报告** - 查看校验结果统计和详细 HTML 报告

## License

MIT
