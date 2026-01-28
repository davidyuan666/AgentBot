import subprocess
import pyautogui
import psutil
import os
from typing import Dict, Any
from utils.logger import logger

class PCControl:
    """Windows PC control module"""
    
    @staticmethod
    def execute_command(command: str) -> Dict[str, Any]:
        """Execute Windows shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "命令执行超时"}
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def open_application(app_path: str) -> Dict[str, Any]:
        """Open application by path"""
        try:
            subprocess.Popen(app_path, creationflags=subprocess.CREATE_NO_WINDOW)
            return {"success": True, "message": f"已打开: {app_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get Windows system information"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('C:\\').percent,
                "running_processes": len(psutil.pids())
            }
        except Exception as e:
            logger.error(f"System info error: {e}")
            return {}
    
    @staticmethod
    def mouse_move(x: int, y: int) -> Dict[str, Any]:
        """Move mouse to coordinates"""
        try:
            pyautogui.moveTo(x, y, duration=0.5)
            return {"success": True, "message": f"鼠标已移动到 ({x}, {y})"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def mouse_click(button: str = "left") -> Dict[str, Any]:
        """Click mouse button"""
        try:
            pyautogui.click(button=button)
            return {"success": True, "message": f"已执行{button}键点击"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def keyboard_type(text: str) -> Dict[str, Any]:
        """Type text using keyboard"""
        try:
            pyautogui.typewrite(text, interval=0.05)
            return {"success": True, "message": f"已输入: {text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def take_screenshot() -> Dict[str, Any]:
        """Take screenshot"""
        try:
            screenshot = pyautogui.screenshot()
            filename = "screenshot.png"
            screenshot.save(filename)
            return {"success": True, "message": "截图已保存", "path": filename}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def shutdown(delay: int = 0) -> Dict[str, Any]:
        """Shutdown Windows"""
        try:
            if delay > 0:
                os.system(f"shutdown /s /t {delay}")
                return {"success": True, "message": f"系统将在{delay}秒后关闭"}
            else:
                os.system("shutdown /s /t 0")
                return {"success": True, "message": "系统正在关闭"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def restart() -> Dict[str, Any]:
        """Restart Windows"""
        try:
            os.system("shutdown /r /t 0")
            return {"success": True, "message": "系统正在重启"}
        except Exception as e:
            return {"success": False, "error": str(e)}