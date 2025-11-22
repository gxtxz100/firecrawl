#!/bin/bash
# 快速安装免费功能所需的依赖

echo "============================================================"
echo "📦 安装免费功能依赖"
echo "============================================================"
echo ""

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "✓ 检测到虚拟环境，正在激活..."
    source venv/bin/activate
else
    echo "⚠️  未检测到虚拟环境"
    echo "建议先创建虚拟环境: python3 -m venv venv"
    read -p "是否继续安装到系统 Python? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "正在安装依赖..."
echo ""

# 安装免费搜索库（优先使用新版本 ddgs）
echo "1. 安装 ddgs (免费搜索，新版本)..."
pip install ddgs -q
if [ $? -eq 0 ]; then
    echo "   ✓ ddgs 安装成功"
else
    echo "   ⚠️  ddgs 安装失败，尝试安装旧版本..."
    pip install duckduckgo-search -q
    if [ $? -eq 0 ]; then
        echo "   ✓ duckduckgo-search (旧版本) 安装成功"
    else
        echo "   ✗ 搜索库安装失败"
    fi
fi

echo ""

# 安装本地提取库
echo "2. 安装本地提取库 (免费文章提取)..."
pip install readability-lxml beautifulsoup4 html2text python-dateutil lxml -q
if [ $? -eq 0 ]; then
    echo "   ✓ 本地提取库安装成功"
else
    echo "   ✗ 本地提取库安装失败"
fi

echo ""
echo "============================================================"
echo "✅ 安装完成！"
echo "============================================================"
echo ""
echo "现在可以使用以下免费功能："
echo "  - 免费搜索（不需要 API 密钥）"
echo "  - 本地提取文章信息（不需要 API 密钥）"
echo ""

