#!/bin/bash
# 设置 Firecrawl API 密钥

# 使用方法:
# bash 设置API密钥.sh
# 或
# source 设置API密钥.sh

echo "=========================================="
echo "设置 Firecrawl API 密钥"
echo "=========================================="
echo ""

# 检查是否提供了 API 密钥作为参数
if [ -n "$1" ]; then
    API_KEY="$1"
else
    # 提示用户输入 API 密钥
    read -p "请输入您的 Firecrawl API 密钥: " API_KEY
fi

# 验证 API 密钥格式
if [[ ! "$API_KEY" =~ ^fc- ]]; then
    echo "⚠️  警告: API 密钥通常以 'fc-' 开头"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 1
    fi
fi

# 设置环境变量（注意：等号两边不能有空格！）
export FIRECRAWL_API_KEY="$API_KEY"

echo ""
echo "✓ API 密钥已设置"
echo ""
echo "当前会话中有效。要永久保存，请："
echo "1. 添加到 ~/.bashrc 或 ~/.zshrc:"
echo "   echo 'export FIRECRAWL_API_KEY=\"$API_KEY\"' >> ~/.zshrc"
echo ""
echo "2. 或创建 .env 文件:"
echo "   echo 'FIRECRAWL_API_KEY=$API_KEY' > .env"
echo ""
echo "验证设置:"
echo "  echo \$FIRECRAWL_API_KEY"
echo ""

