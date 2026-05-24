"""
开发环境 Celery Worker 启动器
监听 Python 文件变化，自动重启 worker，确保始终运行最新代码。

用法: python dev_worker.py
"""
import subprocess
import sys
import time
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("需要安装 watchdog: pip install watchdog")
    sys.exit(1)


class WorkerReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.last_reload = 0
        self.start_worker()

    def start_worker(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("\n[dev_worker] Worker 已停止，正在重启...")
        else:
            print("[dev_worker] 启动 Celery Worker...")

        self.process = subprocess.Popen(
            [sys.executable, "-m", "celery",
             "-A", "app.celery_app.celery_config",
             "worker", "--loglevel=info", "--pool=solo"],
            cwd=str(Path(__file__).parent),
        )
        self.last_reload = time.time()

    def on_modified(self, event):
        if not event.src_path.endswith(".py"):
            return
        if time.time() - self.last_reload < 2:
            return
        print(f"\n[dev_worker] 检测到文件变化: {event.src_path}")
        self.start_worker()


if __name__ == "__main__":
    watch_path = str(Path(__file__).parent / "app")
    print(f"[dev_worker] 监听目录: {watch_path}")
    print("[dev_worker] 修改 .py 文件后 worker 将自动重启\n")

    handler = WorkerReloader()
    observer = Observer()
    observer.schedule(handler, watch_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if handler.process:
            handler.process.terminate()
    observer.join()
