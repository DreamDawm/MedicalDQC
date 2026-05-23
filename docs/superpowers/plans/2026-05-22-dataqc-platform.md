# DataQC 平台实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建基于 GX Core 的全栈数据质量校验平台，支持多数据库连接、30 条内置规则、异步任务执行和趋势分析。

**Architecture:** FastAPI 后端提供 REST API，Celery Worker 执行 GX Core 校验任务，PostgreSQL 存储元数据，Redis 作为消息队列。Vue 3 前端通过 Element Plus 提供配置界面，ECharts 展示趋势图表。

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, Celery, Redis, Great Expectations, Vue 3, Vite, Element Plus, ECharts, Docker Compose

---

## 文件结构

```
dataqc/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── datasource.py
│   │   │   ├── builtin_rule.py
│   │   │   ├── validation_rule.py
│   │   │   ├── validation_task.py
│   │   │   └── validation_result.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── datasource.py
│   │   │   ├── builtin_rule.py
│   │   │   ├── validation_rule.py
│   │   │   ├── validation_task.py
│   │   │   └── validation_result.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── datasources.py
│   │   │   ├── builtin_rules.py
│   │   │   ├── validation_rules.py
│   │   │   ├── tasks.py
│   │   │   └── results.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── datasource_service.py
│   │   │   ├── gx_engine.py
│   │   │   └── report_service.py
│   │   └── celery_app/
│   │       ├── __init__.py
│   │       ├── celery_config.py
│   │       └── tasks.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── seed_rules.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/index.js
│   │   ├── api/index.js
│   │   ├── views/
│   │   │   ├── DatasourceView.vue
│   │   │   ├── RuleConfigView.vue
│   │   │   ├── TaskView.vue
│   │   │   ├── ResultView.vue
│   │   │   └── TrendView.vue
│   │   └── components/
│   │       ├── DatasourceForm.vue
│   │       ├── RuleSelector.vue
│   │       ├── ParameterForm.vue
│   │       └── TrendChart.vue
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── tests/
    └── backend/
        ├── conftest.py
        ├── test_datasource_api.py
        ├── test_builtin_rules_api.py
        ├── test_validation_rules_api.py
        ├── test_tasks_api.py
        ├── test_results_api.py
        └── test_gx_engine.py
```

---

## Phase 1: 后端基础设施

### Task 1: 项目初始化与依赖配置

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `.env.example`

- [ ] **Step 1: 创建 requirements.txt**

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
alembic==1.13.2
psycopg2-binary==2.9.9
celery[redis]==5.4.0
redis==5.1.0
great-expectations==1.0.0
pymysql==1.1.1
pyodbc==5.1.0
pydantic==2.9.0
pydantic-settings==2.5.0
python-dotenv==1.0.1
cryptography==43.0.0
jinja2==3.1.4
httpx==0.27.0
pytest==8.3.0
pytest-asyncio==0.24.0
```

- [ ] **Step 2: 创建 .env.example**

```env
DATABASE_URL=postgresql://dataqc:dataqc@localhost:5432/dataqc
REDIS_URL=redis://localhost:6379/0
REPORT_DIR=./reports
SECRET_KEY=change-me-in-production
```

- [ ] **Step 3: 创建 config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://dataqc:dataqc@localhost:5432/dataqc"
    redis_url: str = "redis://localhost:6379/0"
    report_dir: str = "./reports"
    secret_key: str = "change-me-in-production"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 4: 创建 backend/app/__init__.py**

```python
```

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/app/__init__.py backend/app/config.py .env.example
git commit -m "feat: 初始化后端项目结构与依赖配置"
```

---

### Task 2: 数据库连接与 SQLAlchemy 配置

**Files:**
- Create: `backend/app/database.py`

- [ ] **Step 1: 创建 database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/database.py
git commit -m "feat: 添加 SQLAlchemy 数据库连接配置"
```

---

### Task 3: 数据模型定义

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/datasource.py`
- Create: `backend/app/models/builtin_rule.py`
- Create: `backend/app/models/validation_rule.py`
- Create: `backend/app/models/validation_task.py`
- Create: `backend/app/models/validation_result.py`

- [ ] **Step 1: 创建 models/__init__.py**

```python
from app.models.datasource import Datasource
from app.models.builtin_rule import BuiltinRule
from app.models.validation_rule import ValidationRule
from app.models.validation_task import ValidationTask
from app.models.validation_result import ValidationResult

__all__ = [
    "Datasource",
    "BuiltinRule",
    "ValidationRule",
    "ValidationTask",
    "ValidationResult",
]
```

- [ ] **Step 2: 创建 datasource.py 模型**

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Datasource(Base):
    __tablename__ = "datasources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100))
    db_type: Mapped[str] = mapped_column(String(20))
    host: Mapped[str] = mapped_column(String(255))
    port: Mapped[int] = mapped_column(Integer)
    database: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
```

- [ ] **Step 3: 创建 builtin_rule.py 模型**

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BuiltinRule(Base):
    __tablename__ = "builtin_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    expectation_type: Mapped[str] = mapped_column(String(200), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(500))
    parameters_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
```

- [ ] **Step 4: 创建 validation_rule.py 模型**

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Float, Boolean, DateTime, JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ValidationRule(Base):
    __tablename__ = "validation_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    datasource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("datasources.id")
    )
    table_name: Mapped[str] = mapped_column(String(200))
    column_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    builtin_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("builtin_rules.id")
    )
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    mostly: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="warning")
    row_condition: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
```

- [ ] **Step 5: 创建 validation_task.py 模型**

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ValidationTask(Base):
    __tablename__ = "validation_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200))
    datasource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("datasources.id")
    )
    rule_ids: Mapped[list] = mapped_column(JSON, default=list)
    schedule_cron: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
```

- [ ] **Step 6: 创建 validation_result.py 模型**

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("validation_tasks.id")
    )
    status: Mapped[str] = mapped_column(String(20), default="running")
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    total_expectations: Mapped[int] = mapped_column(Integer, default=0)
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    result_detail: Mapped[dict] = mapped_column(JSON, default=dict)
    report_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/
git commit -m "feat: 添加全部数据模型（数据源、规则、任务、结果）"
```

---

### Task 4: Alembic 迁移配置

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

- [ ] **Step 1: 在 backend 目录初始化 alembic**

Run: `cd backend && alembic init alembic`

- [ ] **Step 2: 修改 alembic/env.py 导入模型**

```python
from app.config import settings
from app.database import Base
from app.models import *  # noqa: F401, F403

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata
```

- [ ] **Step 3: 生成初始迁移**

Run: `cd backend && alembic revision --autogenerate -m "initial tables"`

- [ ] **Step 4: Commit**

```bash
git add backend/alembic/ backend/alembic.ini
git commit -m "feat: 配置 Alembic 数据库迁移"
```

---

### Task 5: 30 条内置规则种子数据

**Files:**
- Create: `backend/seed_rules.py`

- [ ] **Step 1: 创建种子脚本**

```python
from app.database import SessionLocal, engine, Base
from app.models.builtin_rule import BuiltinRule

RULES = [
    {
        "expectation_type": "expect_column_values_to_not_be_null",
        "display_name": "非空检查",
        "category": "完整性校验",
        "description": "检查列值是否为非空",
        "parameters_schema": {},
    },
    {
        "expectation_type": "expect_column_values_to_be_null",
        "display_name": "空值检查",
        "category": "完整性校验",
        "description": "检查列值是否全部为空",
        "parameters_schema": {},
    },
    {
        "expectation_type": "expect_table_row_count_to_equal",
        "display_name": "行数精确匹配",
        "category": "完整性校验",
        "description": "检查表行数是否等于指定值",
        "parameters_schema": {"value": {"type": "integer", "label": "期望行数"}},
    },
    # ... 完整 30 条规则（见设计文档）
]
```

完整的 30 条规则数据将在实现时根据设计文档中的规则表逐一填写，包含所有 7 个类别的规则及其 `parameters_schema` 定义。

- [ ] **Step 2: 运行种子脚本验证**

Run: `cd backend && python seed_rules.py`
Expected: 数据库中插入 30 条规则记录

- [ ] **Step 3: Commit**

```bash
git add backend/seed_rules.py
git commit -m "feat: 添加 30 条内置规则种子数据"
```

---

## Phase 2: 后端 API 层

### Task 6: Pydantic Schemas 定义

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/datasource.py`
- Create: `backend/app/schemas/builtin_rule.py`
- Create: `backend/app/schemas/validation_rule.py`
- Create: `backend/app/schemas/validation_task.py`
- Create: `backend/app/schemas/validation_result.py`

- [ ] **Step 1: 创建 schemas/datasource.py**

```python
import uuid
from datetime import datetime

from pydantic import BaseModel


class DatasourceCreate(BaseModel):
    name: str
    db_type: str
    host: str
    port: int
    database: str
    username: str
    password: str


class DatasourceUpdate(BaseModel):
    name: str | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None
    username: str | None = None
    password: str | None = None


class DatasourceResponse(BaseModel):
    id: uuid.UUID
    name: str
    db_type: str
    host: str
    port: int
    database: str
    username: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TableInfo(BaseModel):
    table_name: str


class ColumnInfo(BaseModel):
    column_name: str
    data_type: str
    is_nullable: bool
```

- [ ] **Step 2: 创建其余 schemas 文件**

每个 schema 文件遵循相同模式：Create、Update、Response 三个类。
`builtin_rule.py` 包含 `BuiltinRuleResponse`。
`validation_rule.py` 包含 `ValidationRuleCreate`、`ValidationRuleUpdate`、`ValidationRuleResponse`。
`validation_task.py` 包含 `TaskCreate`、`TaskUpdate`、`TaskResponse`。
`validation_result.py` 包含 `ResultResponse`、`TrendDataPoint`。

- [ ] **Step 3: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: 添加全部 Pydantic schemas"
```

---

### Task 7: FastAPI 应用入口与路由注册

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py`

- [ ] **Step 1: 创建 main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import datasources, builtin_rules, validation_rules, tasks, results

app = FastAPI(title="DataQC", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasources.router, prefix="/api/datasources", tags=["数据源"])
app.include_router(builtin_rules.router, prefix="/api/builtin-rules", tags=["内置规则"])
app.include_router(validation_rules.router, prefix="/api/validation-rules", tags=["校验规则"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["校验任务"])
app.include_router(results.router, prefix="/api/results", tags=["校验结果"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 2: 创建 api/__init__.py**

```python
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/main.py backend/app/api/__init__.py
git commit -m "feat: 创建 FastAPI 应用入口与路由注册"
```

---

### Task 8: 数据源 API 端点

**Files:**
- Create: `backend/app/api/datasources.py`
- Create: `backend/app/services/datasource_service.py`
- Test: `tests/backend/test_datasource_api.py`

- [ ] **Step 1: 创建 datasource_service.py**

```python
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError


def build_connection_url(db_type: str, host: str, port: int,
                         database: str, username: str, password: str) -> str:
    if db_type == "mysql":
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    elif db_type == "postgresql":
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    elif db_type == "sqlserver":
        return (
            f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
        )
    raise ValueError(f"Unsupported db_type: {db_type}")


def test_connection(url: str) -> dict:
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"success": True, "message": "连接成功"}
    except OperationalError as e:
        return {"success": False, "message": str(e)}


def get_tables(url: str) -> list[str]:
    engine = create_engine(url)
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_columns(url: str, table_name: str) -> list[dict]:
    engine = create_engine(url)
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return [
        {
            "column_name": col["name"],
            "data_type": str(col["type"]),
            "is_nullable": col.get("nullable", True),
        }
        for col in columns
    ]
```

- [ ] **Step 2: 创建 api/datasources.py 路由**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.datasource import Datasource
from app.schemas.datasource import (
    DatasourceCreate, DatasourceUpdate, DatasourceResponse,
    TableInfo, ColumnInfo,
)
from app.services.datasource_service import (
    build_connection_url, test_connection, get_tables, get_columns,
)

router = APIRouter()


@router.post("", response_model=DatasourceResponse)
def create_datasource(data: DatasourceCreate, db: Session = Depends(get_db)):
    ds = Datasource(**data.model_dump())
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds


@router.get("", response_model=list[DatasourceResponse])
def list_datasources(db: Session = Depends(get_db)):
    return db.query(Datasource).all()


@router.get("/{ds_id}", response_model=DatasourceResponse)
def get_datasource(ds_id: uuid.UUID, db: Session = Depends(get_db)):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    return ds


@router.put("/{ds_id}", response_model=DatasourceResponse)
def update_datasource(
    ds_id: uuid.UUID, data: DatasourceUpdate, db: Session = Depends(get_db)
):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(ds, key, val)
    db.commit()
    db.refresh(ds)
    return ds


@router.delete("/{ds_id}")
def delete_datasource(ds_id: uuid.UUID, db: Session = Depends(get_db)):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    db.delete(ds)
    db.commit()
    return {"message": "已删除"}


@router.post("/{ds_id}/test")
def test_ds_connection(ds_id: uuid.UUID, db: Session = Depends(get_db)):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    url = build_connection_url(
        ds.db_type, ds.host, ds.port, ds.database, ds.username, ds.password
    )
    return test_connection(url)


@router.get("/{ds_id}/tables", response_model=list[TableInfo])
def list_tables(ds_id: uuid.UUID, db: Session = Depends(get_db)):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    url = build_connection_url(
        ds.db_type, ds.host, ds.port, ds.database, ds.username, ds.password
    )
    tables = get_tables(url)
    return [{"table_name": t} for t in tables]


@router.get("/{ds_id}/tables/{table}/columns", response_model=list[ColumnInfo])
def list_columns(
    ds_id: uuid.UUID, table: str, db: Session = Depends(get_db)
):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    url = build_connection_url(
        ds.db_type, ds.host, ds.port, ds.database, ds.username, ds.password
    )
    return get_columns(url, table)
```

- [ ] **Step 3: 编写测试**

Run: `cd backend && pytest tests/backend/test_datasource_api.py -v`

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/datasources.py backend/app/services/datasource_service.py tests/backend/test_datasource_api.py
git commit -m "feat: 实现数据源 CRUD API 与连接测试"
```

---

### Task 9: 内置规则与校验规则配置 API

**Files:**
- Create: `backend/app/api/builtin_rules.py`
- Create: `backend/app/api/validation_rules.py`
- Test: `tests/backend/test_builtin_rules_api.py`
- Test: `tests/backend/test_validation_rules_api.py`

- [ ] **Step 1: 创建 api/builtin_rules.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.builtin_rule import BuiltinRule
from app.schemas.builtin_rule import BuiltinRuleResponse

router = APIRouter()


@router.get("", response_model=list[BuiltinRuleResponse])
def list_rules(db: Session = Depends(get_db)):
    return db.query(BuiltinRule).order_by(
        BuiltinRule.usage_count.desc()
    ).all()


@router.get("/{rule_id}", response_model=BuiltinRuleResponse)
def get_rule(rule_id, db: Session = Depends(get_db)):
    rule = db.query(BuiltinRule).filter(BuiltinRule.id == rule_id).first()
    if not rule:
        raise HTTPException(404, "规则不存在")
    return rule
```

- [ ] **Step 2: 创建 api/validation_rules.py**

实现 CRUD 操作，创建规则时递增对应 builtin_rule 的 usage_count。

- [ ] **Step 3: 编写测试并验证**

Run: `cd backend && pytest tests/backend/test_builtin_rules_api.py tests/backend/test_validation_rules_api.py -v`

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/builtin_rules.py backend/app/api/validation_rules.py tests/backend/
git commit -m "feat: 实现内置规则查询与校验规则配置 CRUD API"
```

---

### Task 10: 校验任务与结果 API

**Files:**
- Create: `backend/app/api/tasks.py`
- Create: `backend/app/api/results.py`
- Test: `tests/backend/test_tasks_api.py`
- Test: `tests/backend/test_results_api.py`

- [ ] **Step 1: 创建 api/tasks.py**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.validation_task import ValidationTask
from app.schemas.validation_task import TaskCreate, TaskUpdate, TaskResponse
from app.celery_app.tasks import run_validation_task

router = APIRouter()


@router.post("", response_model=TaskResponse)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = ValidationTask(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(ValidationTask).all()


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: uuid.UUID, data: TaskUpdate, db: Session = Depends(get_db)
):
    task = db.query(ValidationTask).filter(
        ValidationTask.id == task_id
    ).first()
    if not task:
        raise HTTPException(404, "任务不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(task, key, val)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    task = db.query(ValidationTask).filter(
        ValidationTask.id == task_id
    ).first()
    if not task:
        raise HTTPException(404, "任务不存在")
    db.delete(task)
    db.commit()
    return {"message": "已删除"}


@router.post("/{task_id}/run")
def trigger_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    task = db.query(ValidationTask).filter(
        ValidationTask.id == task_id
    ).first()
    if not task:
        raise HTTPException(404, "任务不存在")
    celery_task = run_validation_task.delay(str(task_id))
    return {"message": "任务已提交", "celery_task_id": celery_task.id}
```

- [ ] **Step 2: 创建 api/results.py**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.validation_result import ValidationResult
from app.schemas.validation_result import ResultResponse, TrendDataPoint

router = APIRouter()


@router.get("", response_model=list[ResultResponse])
def list_results(
    task_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(ValidationResult)
    if task_id:
        query = query.filter(ValidationResult.task_id == task_id)
    query = query.order_by(ValidationResult.started_at.desc())
    return query.offset((page - 1) * page_size).limit(page_size).all()


@router.get("/trend", response_model=list[TrendDataPoint])
def get_trend(
    task_id: uuid.UUID | None = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    query = db.query(
        func.date(ValidationResult.started_at).label("date"),
        func.avg(
            ValidationResult.passed_count * 100.0
            / func.nullif(ValidationResult.total_expectations, 0)
        ).label("pass_rate"),
    ).filter(ValidationResult.status == "success")
    if task_id:
        query = query.filter(ValidationResult.task_id == task_id)
    query = query.group_by(func.date(ValidationResult.started_at))
    query = query.order_by(func.date(ValidationResult.started_at))
    rows = query.all()
    return [{"date": str(r.date), "pass_rate": round(r.pass_rate, 2)} for r in rows]


@router.get("/{result_id}", response_model=ResultResponse)
def get_result(result_id: uuid.UUID, db: Session = Depends(get_db)):
    result = db.query(ValidationResult).filter(
        ValidationResult.id == result_id
    ).first()
    if not result:
        raise HTTPException(404, "结果不存在")
    return result


@router.get("/{result_id}/report")
def download_report(result_id: uuid.UUID, db: Session = Depends(get_db)):
    result = db.query(ValidationResult).filter(
        ValidationResult.id == result_id
    ).first()
    if not result or not result.report_path:
        raise HTTPException(404, "报告不存在")
    return FileResponse(result.report_path, filename="report.html")
```

- [ ] **Step 3: 编写测试并验证**

Run: `cd backend && pytest tests/backend/test_tasks_api.py tests/backend/test_results_api.py -v`

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/tasks.py backend/app/api/results.py tests/backend/
git commit -m "feat: 实现校验任务管理与结果查询 API"
```

---

## Phase 3: GX Core 集成与 Celery 异步任务

### Task 11: Celery 配置

**Files:**
- Create: `backend/app/celery_app/__init__.py`
- Create: `backend/app/celery_app/celery_config.py`

- [ ] **Step 1: 创建 celery_config.py**

```python
from celery import Celery

from app.config import settings

celery_app = Celery(
    "dataqc",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    beat_schedule={},
)
```

- [ ] **Step 2: 创建 celery_app/__init__.py**

```python
from app.celery_app.celery_config import celery_app

__all__ = ["celery_app"]
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/celery_app/
git commit -m "feat: 配置 Celery 应用与 Redis 连接"
```

---

### Task 12: GX Core 校验引擎封装

**Files:**
- Create: `backend/app/services/gx_engine.py`
- Test: `tests/backend/test_gx_engine.py`

- [ ] **Step 1: 创建 gx_engine.py**

```python
import great_expectations as gx
from great_expectations.core import ExpectationSuite
from great_expectations.datasource.fluent import SQLDatasource

from app.services.datasource_service import build_connection_url


def run_expectations(
    db_type: str,
    host: str,
    port: int,
    database: str,
    username: str,
    password: str,
    table_name: str,
    expectations: list[dict],
) -> dict:
    connection_url = build_connection_url(
        db_type, host, port, database, username, password
    )

    context = gx.get_context()

    datasource = context.data_sources.add_sql(
        name="runtime_ds",
        connection_string=connection_url,
    )

    asset = datasource.add_table_asset(
        name="runtime_asset",
        table_name=table_name,
    )

    batch_definition = asset.add_batch_definition_whole_table(
        name="runtime_batch"
    )

    suite = ExpectationSuite(name="runtime_suite")

    for exp in expectations:
        exp_type = exp["expectation_type"]
        kwargs = exp.get("kwargs", {})
        suite.add_expectation(
            gx.expectations.registry.get_expectation_impl(exp_type)(**kwargs)
        )

    batch = batch_definition.get_batch()

    validation_result = batch.validate(suite)

    results = []
    for r in validation_result.results:
        results.append({
            "expectation_type": r.expectation_config.type,
            "success": r.success,
            "kwargs": r.expectation_config.kwargs,
            "result": r.result if hasattr(r, "result") else {},
        })

    return {
        "success": validation_result.success,
        "results": results,
        "statistics": {
            "evaluated": len(results),
            "passed": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
        },
    }
```

- [ ] **Step 2: 编写单元测试（mock GX context）**

Run: `cd backend && pytest tests/backend/test_gx_engine.py -v`

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/gx_engine.py tests/backend/test_gx_engine.py
git commit -m "feat: 实现 GX Core 校验引擎封装"
```

---

### Task 13: Celery 异步任务定义

**Files:**
- Create: `backend/app/celery_app/tasks.py`

- [ ] **Step 1: 创建 tasks.py**

```python
from datetime import datetime

from app.celery_app.celery_config import celery_app
from app.database import SessionLocal
from app.models.datasource import Datasource
from app.models.builtin_rule import BuiltinRule
from app.models.validation_rule import ValidationRule
from app.models.validation_task import ValidationTask
from app.models.validation_result import ValidationResult
from app.services.gx_engine import run_expectations
from app.services.report_service import generate_html_report


@celery_app.task(bind=True)
def run_validation_task(self, task_id: str):
    db = SessionLocal()
    try:
        task = db.query(ValidationTask).filter(
            ValidationTask.id == task_id
        ).first()
        if not task:
            return {"error": "Task not found"}

        ds = db.query(Datasource).filter(
            Datasource.id == task.datasource_id
        ).first()

        result_record = ValidationResult(
            task_id=task.id,
            status="running",
        )
        db.add(result_record)
        db.commit()

        rules = db.query(ValidationRule).filter(
            ValidationRule.id.in_(task.rule_ids),
            ValidationRule.enabled == True,
        ).all()

        tables_expectations = {}
        for rule in rules:
            builtin = db.query(BuiltinRule).filter(
                BuiltinRule.id == rule.builtin_rule_id
            ).first()
            table = rule.table_name
            if table not in tables_expectations:
                tables_expectations[table] = []

            kwargs = {**rule.parameters}
            if rule.column_name:
                kwargs["column"] = rule.column_name
            if rule.mostly is not None:
                kwargs["mostly"] = rule.mostly

            tables_expectations[table].append({
                "expectation_type": builtin.expectation_type,
                "kwargs": kwargs,
            })

        all_results = []
        for table, expectations in tables_expectations.items():
            table_result = run_expectations(
                db_type=ds.db_type,
                host=ds.host,
                port=ds.port,
                database=ds.database,
                username=ds.username,
                password=ds.password,
                table_name=table,
                expectations=expectations,
            )
            all_results.extend(table_result["results"])

        passed = sum(1 for r in all_results if r["success"])
        failed = len(all_results) - passed

        report_path = generate_html_report(task.name, all_results)

        result_record.status = "success" if failed == 0 else "failed"
        result_record.finished_at = datetime.utcnow()
        result_record.total_expectations = len(all_results)
        result_record.passed_count = passed
        result_record.failed_count = failed
        result_record.result_detail = {"results": all_results}
        result_record.report_path = report_path
        db.commit()

        return {"status": result_record.status, "passed": passed, "failed": failed}

    except Exception as e:
        result_record.status = "error"
        result_record.finished_at = datetime.utcnow()
        result_record.result_detail = {"error": str(e)}
        db.commit()
        return {"error": str(e)}
    finally:
        db.close()
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/celery_app/tasks.py
git commit -m "feat: 实现 Celery 异步校验任务执行"
```

---

### Task 14: HTML 报告生成服务

**Files:**
- Create: `backend/app/services/report_service.py`
- Create: `backend/app/templates/report.html`

- [ ] **Step 1: 创建 report_service.py**

```python
import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from app.config import settings

template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
env = Environment(loader=FileSystemLoader(template_dir))


def generate_html_report(task_name: str, results: list[dict]) -> str:
    os.makedirs(settings.report_dir, exist_ok=True)

    template = env.get_template("report.html")

    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    pass_rate = round(passed / len(results) * 100, 1) if results else 0

    html = template.render(
        task_name=task_name,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total=len(results),
        passed=passed,
        failed=failed,
        pass_rate=pass_rate,
        results=results,
    )

    filename = f"{task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(settings.report_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filepath
```

- [ ] **Step 2: 创建 Jinja2 报告模板**

创建 `backend/app/templates/report.html`，包含任务名称、执行时间、总计/通过/失败统计、每条规则详情表格。

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/report_service.py backend/app/templates/
git commit -m "feat: 实现 HTML 报告生成服务"
```

---

## Phase 4: 前端应用

### Task 15: Vue 3 项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: 使用 Vite 创建 Vue 3 项目**

Run: `cd frontend && npm create vite@latest . -- --template vue`

- [ ] **Step 2: 安装依赖**

Run: `cd frontend && npm install element-plus vue-router@4 axios echarts vue-echarts`

- [ ] **Step 3: 配置 vite.config.js 代理**

```javascript
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

- [ ] **Step 4: 配置 main.js 引入 Element Plus**

```javascript
import { createApp } from "vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import zhCn from "element-plus/dist/locale/zh-cn.mjs";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.use(ElementPlus, { locale: zhCn });
app.use(router);
app.mount("#app");
```

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "feat: 初始化 Vue 3 + Element Plus 前端项目"
```

---

### Task 16: 路由与布局

**Files:**
- Create: `frontend/src/router/index.js`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: 创建路由配置**

```javascript
import { createRouter, createWebHistory } from "vue-router";

const routes = [
  { path: "/", redirect: "/datasources" },
  {
    path: "/datasources",
    name: "Datasources",
    component: () => import("../views/DatasourceView.vue"),
  },
  {
    path: "/rules",
    name: "Rules",
    component: () => import("../views/RuleConfigView.vue"),
  },
  {
    path: "/tasks",
    name: "Tasks",
    component: () => import("../views/TaskView.vue"),
  },
  {
    path: "/results",
    name: "Results",
    component: () => import("../views/ResultView.vue"),
  },
  {
    path: "/trend",
    name: "Trend",
    component: () => import("../views/TrendView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
```

- [ ] **Step 2: 创建 App.vue 布局**

```vue
<template>
  <el-container style="height: 100vh">
    <el-header>
      <el-menu mode="horizontal" :router="true" :default-active="$route.path">
        <el-menu-item disabled style="font-weight: bold; font-size: 18px">
          DataQC
        </el-menu-item>
        <el-menu-item index="/datasources">数据源</el-menu-item>
        <el-menu-item index="/rules">校验规则</el-menu-item>
        <el-menu-item index="/tasks">校验任务</el-menu-item>
        <el-menu-item index="/results">校验报告</el-menu-item>
        <el-menu-item index="/trend">趋势分析</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/router/ frontend/src/App.vue
git commit -m "feat: 添加前端路由与导航布局"
```

---

### Task 17: API 封装层

**Files:**
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: 创建 Axios API 封装**

```javascript
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export const datasourceApi = {
  list: () => api.get("/datasources"),
  get: (id) => api.get(`/datasources/${id}`),
  create: (data) => api.post("/datasources", data),
  update: (id, data) => api.put(`/datasources/${id}`, data),
  delete: (id) => api.delete(`/datasources/${id}`),
  test: (id) => api.post(`/datasources/${id}/test`),
  tables: (id) => api.get(`/datasources/${id}/tables`),
  columns: (id, table) =>
    api.get(`/datasources/${id}/tables/${table}/columns`),
};

export const builtinRuleApi = {
  list: () => api.get("/builtin-rules"),
  get: (id) => api.get(`/builtin-rules/${id}`),
};

export const validationRuleApi = {
  list: () => api.get("/validation-rules"),
  create: (data) => api.post("/validation-rules", data),
  update: (id, data) => api.put(`/validation-rules/${id}`, data),
  delete: (id) => api.delete(`/validation-rules/${id}`),
};

export const taskApi = {
  list: () => api.get("/tasks"),
  create: (data) => api.post("/tasks", data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
  run: (id) => api.post(`/tasks/${id}/run`),
};

export const resultApi = {
  list: (params) => api.get("/results", { params }),
  get: (id) => api.get(`/results/${id}`),
  trend: (params) => api.get("/results/trend", { params }),
};
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/
git commit -m "feat: 添加前端 API 封装层"
```

---

### Task 18: 数据源管理页面

**Files:**
- Create: `frontend/src/views/DatasourceView.vue`
- Create: `frontend/src/components/DatasourceForm.vue`

- [ ] **Step 1: 创建 DatasourceForm.vue 组件**

```vue
<template>
  <el-dialog :title="isEdit ? '编辑数据源' : '新增数据源'" v-model="visible">
    <el-form :model="form" label-width="100px">
      <el-form-item label="名称">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="数据库类型">
        <el-select v-model="form.db_type">
          <el-option label="MySQL" value="mysql" />
          <el-option label="PostgreSQL" value="postgresql" />
          <el-option label="SQL Server" value="sqlserver" />
        </el-select>
      </el-form-item>
      <el-form-item label="主机">
        <el-input v-model="form.host" />
      </el-form-item>
      <el-form-item label="端口">
        <el-input-number v-model="form.port" />
      </el-form-item>
      <el-form-item label="数据库名">
        <el-input v-model="form.database" />
      </el-form-item>
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>
```

Script 部分包含 props（`modelValue`, `editData`）、emit、表单提交逻辑。

- [ ] **Step 2: 创建 DatasourceView.vue 页面**

包含数据源列表表格（el-table）、新增按钮、测试连接按钮、编辑/删除操作列。

- [ ] **Step 3: 启动前端验证页面渲染**

Run: `cd frontend && npm run dev`
验证：访问 http://localhost:3000/datasources 页面正常渲染

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/DatasourceView.vue frontend/src/components/DatasourceForm.vue
git commit -m "feat: 实现数据源管理页面"
```

---

### Task 19: 校验规则配置页面

**Files:**
- Create: `frontend/src/views/RuleConfigView.vue`
- Create: `frontend/src/components/RuleSelector.vue`
- Create: `frontend/src/components/ParameterForm.vue`

- [ ] **Step 1: 创建 RuleSelector.vue**

规则下拉选择器，按 usage_count 降序排列，显示中文名和类别分组。

```vue
<template>
  <el-select v-model="selected" filterable placeholder="选择校验规则">
    <el-option-group
      v-for="group in groupedRules"
      :key="group.category"
      :label="group.category"
    >
      <el-option
        v-for="rule in group.rules"
        :key="rule.id"
        :label="rule.display_name"
        :value="rule.id"
      />
    </el-option-group>
  </el-select>
</template>
```

- [ ] **Step 2: 创建 ParameterForm.vue**

根据选中规则的 `parameters_schema` 动态渲染表单字段，加上通用参数（mostly、severity、row_condition）。

- [ ] **Step 3: 创建 RuleConfigView.vue**

级联选择流程：数据源 → 表 → 列 → 规则 → 参数。包含已配置规则列表。

- [ ] **Step 4: 验证页面功能**

Run: `cd frontend && npm run dev`
验证：访问 http://localhost:3000/rules 页面正常渲染，级联选择可用

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/RuleConfigView.vue frontend/src/components/RuleSelector.vue frontend/src/components/ParameterForm.vue
git commit -m "feat: 实现校验规则配置页面（级联选择+动态参数表单）"
```

---

### Task 20: 校验任务页面

**Files:**
- Create: `frontend/src/views/TaskView.vue`

- [ ] **Step 1: 创建 TaskView.vue**

功能：
- 任务列表表格（名称、数据源、规则数、cron、状态）
- 新建任务对话框（选择数据源、勾选规则、设置 cron）
- 手动执行按钮（调用 POST /api/tasks/{id}/run）
- 执行状态实时刷新（轮询）

- [ ] **Step 2: 验证页面功能**

Run: `cd frontend && npm run dev`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/TaskView.vue
git commit -m "feat: 实现校验任务管理页面"
```

---

### Task 21: 校验报告页面

**Files:**
- Create: `frontend/src/views/ResultView.vue`

- [ ] **Step 1: 创建 ResultView.vue**

功能：
- 结果列表表格（任务名、状态、通过率、执行时间）
- 点击查看详情：每条规则的通过/失败状态、参数、失败样本
- 下载 HTML 报告按钮

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/ResultView.vue
git commit -m "feat: 实现校验报告页面"
```

---

### Task 22: 趋势分析页面

**Files:**
- Create: `frontend/src/views/TrendView.vue`
- Create: `frontend/src/components/TrendChart.vue`

- [ ] **Step 1: 创建 TrendChart.vue**

```vue
<template>
  <v-chart :option="chartOption" autoresize style="height: 400px" />
</template>

<script setup>
import { computed } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { LineChart, BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

use([LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps({ data: Array });

const chartOption = computed(() => ({
  tooltip: { trigger: "axis" },
  xAxis: { type: "category", data: props.data.map((d) => d.date) },
  yAxis: { type: "value", name: "通过率 (%)", max: 100 },
  series: [
    {
      name: "通过率",
      type: "line",
      data: props.data.map((d) => d.pass_rate),
      smooth: true,
    },
  ],
}));
</script>
```

- [ ] **Step 2: 创建 TrendView.vue**

包含筛选条件（任务/数据源/时间范围）和 TrendChart 组件。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/TrendView.vue frontend/src/components/TrendChart.vue
git commit -m "feat: 实现趋势分析页面（ECharts 折线图）"
```

---

## Phase 5: Docker 部署与测试

### Task 23: Docker Compose 配置

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`

- [ ] **Step 1: 创建 backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: 创建 frontend/Dockerfile**

```dockerfile
FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 3: 创建 docker-compose.yml**

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: dataqc
      POSTGRES_PASSWORD: dataqc
      POSTGRES_DB: dataqc
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://dataqc:dataqc@postgres:5432/dataqc
      REDIS_URL: redis://redis:6379/0
      REPORT_DIR: /app/reports
    depends_on:
      - postgres
      - redis
    volumes:
      - reports:/app/reports

  celery-worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://dataqc:dataqc@postgres:5432/dataqc
      REDIS_URL: redis://redis:6379/0
      REPORT_DIR: /app/reports
    depends_on:
      - postgres
      - redis
    volumes:
      - reports:/app/reports

  celery-beat:
    build: ./backend
    command: celery -A app.celery_app beat --loglevel=info
    environment:
      DATABASE_URL: postgresql://dataqc:dataqc@postgres:5432/dataqc
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  pgdata:
  reports:
```

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml backend/Dockerfile frontend/Dockerfile
git commit -m "feat: 添加 Docker Compose 部署配置（6 服务）"
```

---

### Task 24: 测试基础设施

**Files:**
- Create: `tests/backend/conftest.py`
- Create: `backend/pytest.ini`

- [ ] **Step 1: 创建 pytest.ini**

```ini
[pytest]
testpaths = tests
asyncio_mode = auto
```

- [ ] **Step 2: 创建 conftest.py**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

- [ ] **Step 3: 验证测试框架可运行**

Run: `cd backend && pytest --co -q`
Expected: 收集到测试文件，无导入错误

- [ ] **Step 4: Commit**

```bash
git add tests/backend/conftest.py backend/pytest.ini
git commit -m "feat: 配置 pytest 测试基础设施"
```

---

### Task 25: 集成验证与启动

- [ ] **Step 1: 启动 Docker Compose**

Run: `docker compose up -d`
Expected: 6 个服务全部启动

- [ ] **Step 2: 运行数据库迁移**

Run: `docker compose exec backend alembic upgrade head`

- [ ] **Step 3: 导入种子数据**

Run: `docker compose exec backend python seed_rules.py`

- [ ] **Step 4: 验证 API 健康检查**

Run: `curl http://localhost:8000/api/health`
Expected: `{"status": "ok"}`

- [ ] **Step 5: 验证前端访问**

访问 http://localhost:3000 确认页面正常加载

- [ ] **Step 6: 端到端流程验证**

1. 创建数据源连接
2. 测试连接
3. 浏览表和列
4. 配置校验规则
5. 创建任务并执行
6. 查看结果和报告

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "chore: 集成验证通过，项目可运行"
```

---

## 执行顺序总结

| Phase | Tasks | 说明 |
|-------|-------|------|
| 1 | 1-5 | 后端基础设施（配置、模型、迁移、种子数据） |
| 2 | 6-10 | 后端 API 层（schemas、路由、CRUD） |
| 3 | 11-14 | GX Core 集成与 Celery 异步任务 |
| 4 | 15-22 | 前端应用（Vue 3 全部页面） |
| 5 | 23-25 | Docker 部署与集成验证 |

每个 Task 独立可提交，Phase 之间有依赖关系（Phase 2 依赖 Phase 1，Phase 4 依赖 Phase 2 的 API）。
