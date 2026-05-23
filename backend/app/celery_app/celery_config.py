from celery import Celery

from app.config import settings

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
