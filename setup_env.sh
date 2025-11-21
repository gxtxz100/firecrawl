#!/bin/bash
# Firecrawl 友好客户端 - 环境设置脚本
# 此脚本会自动创建虚拟环境并安装所有依赖

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Firecrawl 友好客户端 - 环境设置"
echo "=========================================="
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "当前 Python 版本: $PYTHON_VERSION"

# 检查是否满足最低版本要求（3.8+）
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ 错误: 需要 Python 3.8 或更高版本"
    echo "当前版本: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python 版本检查通过"
echo ""

# 虚拟环境目录名
VENV_DIR="venv"

# 检查虚拟环境是否已存在
if [ -d "$VENV_DIR" ]; then
    echo "检测到已存在的虚拟环境: $VENV_DIR"
    read -p "是否要重新创建虚拟环境？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除旧的虚拟环境..."
        rm -rf "$VENV_DIR"
    else
        echo "使用现有虚拟环境"
        source "$VENV_DIR/bin/activate"
        echo "✓ 虚拟环境已激活"
        echo ""
        echo "更新依赖包..."
        pip install --upgrade pip
        pip install -r requirements.txt
        echo ""
        echo "=========================================="
        echo "✓ 环境设置完成！"
        echo "=========================================="
        echo ""
        echo "使用说明:"
        echo "1. 激活虚拟环境: source venv/bin/activate"
        echo "2. 设置 API 密钥: export FIRECRAWL_API_KEY='your-api-key'"
        echo "3. 运行示例: python firecrawl_client_examples.py"
        echo ""
        exit 0
    fi
fi

# 创建虚拟环境
echo "创建虚拟环境: $VENV_DIR"
python3 -m venv "$VENV_DIR"

# 激活虚拟环境
echo "激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖包..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  警告: 未找到 requirements.txt，尝试安装 firecrawl-py..."
    pip install firecrawl-py
fi

# 如果是从本地开发，尝试安装本地 SDK
if [ -d "apps/python-sdk" ]; then
    echo ""
    echo "检测到本地 SDK，是否安装本地版本？(推荐用于开发)"
    read -p "安装本地 SDK? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "安装本地 SDK..."
        pip install -e apps/python-sdk/
    fi
fi

echo ""
echo "=========================================="
echo "✓ 环境设置完成！"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 设置 API 密钥: export FIRECRAWL_API_KEY='your-api-key'"
echo "3. 运行示例: python firecrawl_client_examples.py"
echo ""
echo "提示: 每次使用前都需要激活虚拟环境"
echo "     或者使用: source venv/bin/activate"
echo ""

