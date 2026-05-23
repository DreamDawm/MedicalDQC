from celery import Celery

from app.config import settings

# 固定的 worker 节点名，确保只有一个 worker 运行
WORKER_NAME = "dataqc-worker"

celery_app = Celery(
    "dataqc",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# 自动发现任务模块
celery_app.autodiscover_tasks(["app.celery_app"])

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    beat_schedule={},
    # 优化连接池，减少首次调用延迟
    broker_pool_limit=10,
    broker_connection_timeout=5,
    result_backend_transport_options={
        "max_connections": 10,
    },
)


def check_existing_worker() -> bool:
    """检查是否已有同名 worker 在运行"""
    inspect = celery_app.control.inspect()
    active = inspect.active()
    if active is None:
        return False
    # 检查是否有同名 worker
    for worker_name in active.keys():
        if worker_name == WORKER_NAME or worker_name.endswith(WORKER_NAME):
            return True
    return False
