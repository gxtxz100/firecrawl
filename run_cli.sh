#!/bin/bash
# 运行交互式命令行工具（自动使用虚拟环境）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 错误: 虚拟环境不存在"
    echo "请先运行: python install.py"
    exit 1
fi

# 激活虚拟环境并运行 CLI
source venv/bin/activate
python firecrawl_cli.py "$@"

