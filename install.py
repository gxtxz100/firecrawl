#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firecrawl 友好客户端 - Python 安装脚本
自动创建虚拟环境并安装所有依赖
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并显示输出"""
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, capture_output=False)
    return result.returncode == 0


def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"当前 Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 错误: 需要 Python 3.8 或更高版本")
        return False
    
    print("✓ Python 版本检查通过")
    return True


def create_venv(venv_dir="venv"):
    """创建虚拟环境"""
    venv_path = Path(venv_dir)
    
    if venv_path.exists():
        print(f"\n检测到已存在的虚拟环境: {venv_dir}")
        response = input("是否要重新创建虚拟环境？(y/N): ").strip().lower()
        if response == 'y':
            print("删除旧的虚拟环境...")
            import shutil
            shutil.rmtree(venv_path)
        else:
            print("使用现有虚拟环境")
            return True
    
    print(f"\n创建虚拟环境: {venv_dir}")
    if not run_command([sys.executable, "-m", "venv", venv_dir]):
        print("❌ 创建虚拟环境失败")
        return False
    
    print("✓ 虚拟环境创建成功")
    return True


def get_pip_command(venv_dir="venv"):
    """获取虚拟环境中的 pip 命令路径"""
    if platform.system() == "Windows":
        return str(Path(venv_dir) / "Scripts" / "pip.exe")
    else:
        return str(Path(venv_dir) / "bin" / "pip")


def get_python_command(venv_dir="venv"):
    """获取虚拟环境中的 python 命令路径"""
    if platform.system() == "Windows":
        return str(Path(venv_dir) / "Scripts" / "python.exe")
    else:
        return str(Path(venv_dir) / "bin" / "python")


def install_dependencies(venv_dir="venv"):
    """安装依赖包"""
    pip_cmd = get_pip_command(venv_dir)
    python_cmd = get_python_command(venv_dir)
    
    print("\n升级 pip...")
    if not run_command([python_cmd, "-m", "pip", "install", "--upgrade", "pip"]):
        print("⚠️  警告: pip 升级失败，继续安装依赖...")
    
    print("\n安装依赖包...")
    requirements_file = Path("requirements.txt")
    
    if requirements_file.exists():
        if not run_command([pip_cmd, "install", "-r", "requirements.txt"]):
            print("❌ 安装依赖失败")
            return False
    else:
        print("⚠️  警告: 未找到 requirements.txt，尝试安装 firecrawl-py...")
        if not run_command([pip_cmd, "install", "firecrawl-py"]):
            print("❌ 安装 firecrawl-py 失败")
            return False
    
    # 如果是从本地开发，询问是否安装本地 SDK
    sdk_path = Path("apps") / "python-sdk"
    if sdk_path.exists():
        print("\n检测到本地 SDK，是否安装本地版本？(推荐用于开发)")
        response = input("安装本地 SDK? (Y/n): ").strip().lower()
        if response != 'n':
            print("安装本地 SDK...")
            if not run_command([pip_cmd, "install", "-e", str(sdk_path)]):
                print("⚠️  警告: 本地 SDK 安装失败，使用已安装的版本")
    
    print("✓ 依赖安装完成")
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("Firecrawl 友好客户端 - 环境设置")
    print("=" * 50)
    print()
    
    # 检查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 创建虚拟环境
    if not create_venv():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 显示完成信息
    print("\n" + "=" * 50)
    print("✓ 环境设置完成！")
    print("=" * 50)
    print()
    
    # 根据操作系统显示不同的激活命令
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        set_key_cmd = "set FIRECRAWL_API_KEY=your-api-key"
    else:
        activate_cmd = "source venv/bin/activate"
        set_key_cmd = "export FIRECRAWL_API_KEY='your-api-key'"
    
    print("下一步:")
    print(f"1. 激活虚拟环境: {activate_cmd}")
    print(f"2. 设置 API 密钥: {set_key_cmd}")
    print("3. 运行示例: python firecrawl_client_examples.py")
    print()
    print("提示: 每次使用前都需要激活虚拟环境")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

