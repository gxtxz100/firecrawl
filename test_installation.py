#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试安装是否成功
"""

import sys

def test_imports():
    """测试导入"""
    print("=" * 50)
    print("测试导入...")
    print("=" * 50)
    
    try:
        from firecrawl import Firecrawl
        print("✓ Firecrawl SDK 导入成功")
    except ImportError as e:
        print(f"❌ Firecrawl SDK 导入失败: {e}")
        return False
    
    try:
        from firecrawl_client import FirecrawlClient
        print("✓ Firecrawl 友好客户端导入成功")
    except ImportError as e:
        print(f"❌ Firecrawl 友好客户端导入失败: {e}")
        return False
    
    try:
        from firecrawl.v2.types import Document
        print("✓ Firecrawl 类型导入成功")
    except ImportError as e:
        print(f"❌ Firecrawl 类型导入失败: {e}")
        return False
    
    return True

def test_client_init():
    """测试客户端初始化"""
    print("\n" + "=" * 50)
    print("测试客户端初始化...")
    print("=" * 50)
    
    try:
        from firecrawl_client import FirecrawlClient
        
        # 测试提供无效 API 密钥（应该能创建客户端，但调用时会失败）
        try:
            client = FirecrawlClient(api_key="test-key")
            print("✓ 客户端创建成功（使用测试密钥）")
        except Exception as e:
            print(f"⚠️  客户端创建失败: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 客户端初始化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_version():
    """测试版本信息"""
    print("\n" + "=" * 50)
    print("测试版本信息...")
    print("=" * 50)
    
    try:
        import firecrawl
        version = getattr(firecrawl, '__version__', '未知')
        print(f"✓ Firecrawl SDK 版本: {version}")
    except Exception as e:
        print(f"⚠️  无法获取版本信息: {e}")
    
    try:
        import sys
        print(f"✓ Python 版本: {sys.version}")
    except Exception as e:
        print(f"⚠️  无法获取 Python 版本: {e}")

def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("Firecrawl 安装测试")
    print("=" * 50)
    print()
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败，请检查安装")
        sys.exit(1)
    
    # 测试客户端初始化
    if not test_client_init():
        print("\n⚠️  客户端初始化测试有问题，但可能不影响使用")
    
    # 测试版本信息
    test_version()
    
    print("\n" + "=" * 50)
    print("✓ 所有测试完成！")
    print("=" * 50)
    print()
    print("下一步:")
    print("1. 设置 API 密钥: export FIRECRAWL_API_KEY='your-api-key'")
    print("2. 激活虚拟环境: source venv/bin/activate")
    print("3. 运行示例: python firecrawl_client_examples.py")
    print()

if __name__ == "__main__":
    main()

