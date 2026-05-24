import asyncio
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.validation_result import ValidationResult

router = APIRouter()
executor = ThreadPoolExecutor()


def get_latest_result_by_task(db: Session, task_id: uuid.UUID) -> ValidationResult | None:
    """获取指定任务的最新执行结果"""
    return db.query(ValidationResult).filter(
        ValidationResult.task_id == task_id
    ).order_by(ValidationResult.started_at.desc()).first()


@router.get("/tasks/{task_id}/stream")
async def stream_task_progress(task_id: uuid.UUID):
    """SSE 端点：实时推送任务进度和日志"""

    async def event_generator():
        db = SessionLocal()
        try:
            last_progress = -1
            last_log_count = 0
            loop = asyncio.get_event_loop()
            max_iterations = 600  # 最多轮询 10 分钟 (600 * 1秒)

            for _ in range(max_iterations):
                # 使用线程池执行同步查询，避免阻塞 event loop
                result = await loop.run_in_executor(
                    executor,
                    lambda: get_latest_result_by_task(db, task_id)
                )

                if result:
                    # 发送进度更新
                    if result.progress != last_progress:
                        yield f"data: {json.dumps({'type': 'progress', 'value': result.progress, 'status': result.status})}\n\n"
                        last_progress = result.progress

                    # 发送新日志
                    logs = result.logs or []
                    if len(logs) > last_log_count:
                        new_logs = logs[last_log_count:]
                        for log in new_logs:
                            yield f"data: {json.dumps({'type': 'log', 'message': log})}\n\n"
                        last_log_count = len(logs)

                    # 任务完成时发送结束事件
                    if result.status in ("success", "failed", "error"):
                        yield f"data: {json.dumps({'type': 'complete', 'status': result.status})}\n\n"
                        break

                await asyncio.sleep(1)

            # 超时结束
            yield f"data: {json.dumps({'type': 'timeout'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/tasks/{task_id}/current")
def get_current_progress(task_id: uuid.UUID):
    """获取任务当前进度（用于页面加载时获取初始状态）"""
    db = SessionLocal()
    try:
        result = get_latest_result_by_task(db, task_id)
        if not result:
            return {"progress": 0, "status": "idle", "logs": []}
        return {
            "progress": result.progress,
            "status": result.status,
            "logs": result.logs or [],
        }
    finally:
        db.close()
