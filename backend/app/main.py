import multiprocessing
import os
import sys

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

# Celery worker 进程
celery_process = None


@app.on_event("startup")
def startup_event():
    """启动 Celery worker"""
    global celery_process
    import subprocess

    # 使用 Popen 启动子进程，可以正常终止
    celery_process = subprocess.Popen([
        sys.executable, "-m", "celery",
        "-A", "app.celery_app.celery_config",
        "worker",
        "--pool=solo",
        "--loglevel=info",
        "-n", "worker-%h",
    ])


@app.on_event("shutdown")
def shutdown_event():
    """停止 Celery worker"""
    global celery_process
    if celery_process:
        celery_process.terminate()
        try:
            celery_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            celery_process.kill()


@app.get("/api/health")
def health():
    return {"status": "ok"}
