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
