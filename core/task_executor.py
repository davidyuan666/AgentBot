from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable

from core.deepseek_api import DeepSeekAPI
from core.pc_control import PCControl
from utils.logger import logger


@dataclass
class StepResult:
    index: int
    action: str
    args: Dict[str, Any]
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


def _safe_json_extract(text: str) -> Optional[dict]:
    """
    Expect model to output a JSON object. Try best-effort extraction.
    """
    t = (text or "").strip()
    if not t:
        return None
    # Try direct
    try:
        return json.loads(t)
    except Exception:
        pass

    # Try fenced ```json ... ```
    if "```" in t:
        parts = t.split("```")
        for p in parts:
            p = p.strip()
            if not p:
                continue
            if p.startswith("json"):
                p = p[4:].strip()
            try:
                return json.loads(p)
            except Exception:
                continue
    return None


async def plan_steps_from_task(task_text: str) -> List[Dict[str, Any]]:
    """
    Ask DeepSeek to convert task.md to an executable plan in JSON.
    """
    system = (
        "你是 Windows 自动化任务规划器。把用户的 task.md 转换为可执行的步骤 JSON。\n"
        "只输出 JSON，不要输出任何多余文字。\n"
        "JSON 格式必须为：\n"
        "{\n"
        '  "steps": [\n'
        '    {"action": "get_system_info", "args": {}},\n'
        '    {"action": "execute_command", "args": {"command": "mkdir output"}},\n'
        '    {"action": "take_screenshot", "args": {}},\n'
        "    ...\n"
        "  ]\n"
        "}\n"
        "action 只能使用以下之一：execute_command/open_application/mouse_move/mouse_click/keyboard_type/get_system_info/take_screenshot/shutdown/restart。\n"
        "args 必须与 action 对应方法参数一致。\n"
        "遇到写文件内容这类需求，优先使用 execute_command（例如 powershell 写文件）。\n"
    )

    deepseek = DeepSeekAPI()
    try:
        resp = await deepseek.chat(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": f"task.md 内容如下：\n\n{task_text}"},
            ],
            temperature=0.2,
            max_tokens=2048,
        )
    finally:
        await deepseek.close()

    data = _safe_json_extract(resp)
    if not data or "steps" not in data or not isinstance(data["steps"], list):
        raise ValueError(f"无法从模型输出解析 steps JSON。原始输出前 300 字：{resp[:300]}")
    return data["steps"]


def _execute_one(step: Dict[str, Any]) -> Dict[str, Any]:
    action = step.get("action")
    args = step.get("args") or {}
    if not isinstance(args, dict):
        args = {}

    fn = getattr(PCControl, action, None)
    if not fn:
        return {"success": False, "error": f"未知 action: {action}"}

    try:
        return fn(**args) if args else fn()
    except TypeError as e:
        return {"success": False, "error": f"参数不匹配: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def execute_plan(
    steps: List[Dict[str, Any]],
    progress: Optional[Callable[[str], Any]] = None,
) -> List[StepResult]:
    """
    Execute steps sequentially. `progress` receives human-readable updates.
    """
    results: List[StepResult] = []
    for idx, step in enumerate(steps, start=1):
        action = str(step.get("action", ""))
        args = step.get("args") or {}
        if progress:
            progress(f"⏳ 第 {idx}/{len(steps)} 步开始：{action} {args}")

        r = _execute_one(step)
        sr = StepResult(
            index=idx,
            action=action,
            args=args if isinstance(args, dict) else {},
            success=bool(r.get("success")),
            output=r.get("output") or r.get("message"),
            error=r.get("error"),
            extra={k: v for k, v in r.items() if k not in {"success", "output", "message", "error"}},
        )
        results.append(sr)

        if progress:
            if sr.success:
                progress(f"✅ 第 {idx} 步完成：{sr.output or 'ok'}")
            else:
                progress(f"❌ 第 {idx} 步失败：{sr.error or 'unknown error'}")

    return results


def render_summary(results: List[StepResult]) -> str:
    ok = sum(1 for r in results if r.success)
    total = len(results)
    lines = [f"执行完成：{ok}/{total} 成功"]
    for r in results:
        status = "✅" if r.success else "❌"
        msg = r.output if r.success else r.error
        lines.append(f"{status} 第{r.index}步 {r.action}: {msg}")
        if r.extra and "path" in r.extra:
            lines.append(f"   - path: {r.extra['path']}")
    return "\n".join(lines)
