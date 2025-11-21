@echo off
REM 运行示例脚本（自动使用虚拟环境）

cd /d "%~dp0"

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo 错误: 虚拟环境不存在
    echo 请先运行: python install.py
    exit /b 1
)

REM 激活虚拟环境并运行示例
call venv\Scripts\activate.bat
python firecrawl_client_examples.py %*

