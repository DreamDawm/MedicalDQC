from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import datasources, builtin_rules, validation_rules, tasks, results, task_progress

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
app.include_router(task_progress.router, prefix="/api", tags=["任务进度"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
