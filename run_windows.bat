@echo off
REM ============================================================
REM  ParaBank 测试平台 — Windows 启动脚本
REM  首次运行会自动创建 .venv 并安装 requirements.txt
REM ============================================================
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [*] 未找到 .venv，正在创建虚拟环境...
    python -m venv .venv || goto :fail
    echo [*] 安装依赖...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :fail
)

echo [*] 启动测试平台: http://127.0.0.1:5000/
echo [*] 被测系统:     http://127.0.0.1:5000/parabank/login  (admin / admin123)
".venv\Scripts\python.exe" app.py
goto :eof

:fail
echo [x] 环境准备失败，请检查 Python 与网络。
pause
