"""
Celery Worker 启动脚本

确保只有一个 worker 运行，避免重复启动导致的冲突。
"""
import sys
import subprocess

from app.celery_app.celery_config import check_existing_worker, WORKER_NAME


def main():
    if check_existing_worker():
        print(f"警告: 已有 worker '{WORKER_NAME}' 正在运行，跳过启动")
        print("如需强制重启，请先手动停止现有 worker")
        sys.exit(0)

    print(f"启动 Celery worker: {WORKER_NAME}")
    subprocess.run([
        "celery",
        "-A", "app.celery_app.celery_config",
        "worker",
        "--loglevel=info",
        f"-n {WORKER_NAME}",
    ])


if __name__ == "__main__":
    main()