@echo off
chcp 65001 >nul 2>&1

call env\Scripts\activate.bat
python main.py
pause