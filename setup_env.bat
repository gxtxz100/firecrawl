@echo off
REM Firecrawl 友好客户端 - Windows 环境设置脚本
REM 此脚本会自动创建虚拟环境并安装所有依赖

echo ==========================================
echo Firecrawl 友好客户端 - 环境设置
echo ==========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

echo 检查 Python 版本...
python --version
echo.

REM 虚拟环境目录名
set VENV_DIR=venv

REM 检查虚拟环境是否已存在
if exist "%VENV_DIR%" (
    echo 检测到已存在的虚拟环境: %VENV_DIR%
    set /p RECREATE="是否要重新创建虚拟环境？(y/N): "
    if /i "%RECREATE%"=="y" (
        echo 删除旧的虚拟环境...
        rmdir /s /q "%VENV_DIR%"
    ) else (
        echo 使用现有虚拟环境
        call "%VENV_DIR%\Scripts\activate.bat"
        echo 虚拟环境已激活
        echo.
        echo 更新依赖包...
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        echo.
        echo ==========================================
        echo 环境设置完成！
        echo ==========================================
        echo.
        echo 使用说明:
        echo 1. 激活虚拟环境: venv\Scripts\activate
        echo 2. 设置 API 密钥: set FIRECRAWL_API_KEY=your-api-key
        echo 3. 运行示例: python firecrawl_client_examples.py
        echo.
        pause
        exit /b 0
    )
)

REM 创建虚拟环境
echo 创建虚拟环境: %VENV_DIR%
python -m venv "%VENV_DIR%"

REM 激活虚拟环境
echo 激活虚拟环境...
call "%VENV_DIR%\Scripts\activate.bat"

REM 升级 pip
echo 升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 安装依赖包...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo 警告: 未找到 requirements.txt，尝试安装 firecrawl-py...
    pip install firecrawl-py
)

REM 如果是从本地开发，尝试安装本地 SDK
if exist "apps\python-sdk" (
    echo.
    echo 检测到本地 SDK，是否安装本地版本？(推荐用于开发)
    set /p INSTALL_LOCAL="安装本地 SDK? (Y/n): "
    if /i not "%INSTALL_LOCAL%"=="n" (
        echo 安装本地 SDK...
        pip install -e apps\python-sdk\
    )
)

echo.
echo ==========================================
echo 环境设置完成！
echo ==========================================
echo.
echo 下一步:
echo 1. 激活虚拟环境: venv\Scripts\activate
echo 2. 设置 API 密钥: set FIRECRAWL_API_KEY=your-api-key
echo 3. 运行示例: python firecrawl_client_examples.py
echo.
echo 提示: 每次使用前都需要激活虚拟环境
echo      或者使用: venv\Scripts\activate
echo.
pause

