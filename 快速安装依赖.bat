@echo off
REM 快速安装免费功能所需的依赖 (Windows)

echo ============================================================
echo 安装免费功能依赖
echo ============================================================
echo.

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 检测到虚拟环境，正在激活...
    call venv\Scripts\activate.bat
) else (
    echo 未检测到虚拟环境
    echo 建议先创建虚拟环境: python -m venv venv
    pause
)

echo.
echo 正在安装依赖...
echo.

REM 安装免费搜索库（优先使用新版本 ddgs）
echo 1. 安装 ddgs (免费搜索，新版本)...
pip install ddgs -q
if %errorlevel% equ 0 (
    echo    ddgs 安装成功
) else (
    echo    ddgs 安装失败，尝试安装旧版本...
    pip install duckduckgo-search -q
    if %errorlevel% equ 0 (
        echo    duckduckgo-search (旧版本) 安装成功
    ) else (
        echo    搜索库安装失败
    )
)

echo.

REM 安装本地提取库
echo 2. 安装本地提取库 (免费文章提取)...
pip install readability-lxml beautifulsoup4 html2text python-dateutil lxml -q
if %errorlevel% equ 0 (
    echo    本地提取库安装成功
) else (
    echo    本地提取库安装失败
)

echo.
echo ============================================================
echo 安装完成！
echo ============================================================
echo.
echo 现在可以使用以下免费功能：
echo   - 免费搜索（不需要 API 密钥）
echo   - 本地提取文章信息（不需要 API 密钥）
echo.
pause

