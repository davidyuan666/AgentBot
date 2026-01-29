from __future__ import annotations

import os
from typing import Optional

from config import config
from core.task_executor import plan_steps_from_task, execute_plan, render_summary
from utils.logger import logger


def _read_text_file(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"未找到任务文件: {path}")
    if os.path.isdir(path):
        raise IsADirectoryError(f"任务路径是目录，不是文件: {path}")

    # Prefer utf-8; tolerate BOM; fallback to system default if needed
    for encoding in ("utf-8-sig", "utf-8", "gbk"):
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read().strip()
        except UnicodeDecodeError:
            continue

    # Last resort
    with open(path, "r") as f:
        return f.read().strip()


async def run_task_md(task_path: Optional[str] = None) -> str:
    """
    Read local task.md, ask DeepSeek to execute/solve, return final result text.
    This is intentionally independent of chat adapters so it can be triggered anywhere.
    """
    path = task_path or config.TASK_MD_PATH
    # Allow relative paths (workspace execution) by normalizing
    path = os.path.abspath(path)

    logger.info(f"[task.md] Reading tasks from: {path}")
    task_text = _read_text_file(path)
    if not task_text:
        return f"⚠️ task.md 为空: {path}"

    logger.info("[task.md] Planning executable steps via DeepSeek...")
    steps = await plan_steps_from_task(task_text)
    logger.info(f"[task.md] Planned {len(steps)} steps, executing...")

    results = await execute_plan(steps)
    summary = render_summary(results)
    return f"✅ task.md 执行结果（{os.path.basename(path)}）\n\n{summary}"
