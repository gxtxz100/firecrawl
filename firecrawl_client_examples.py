#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firecrawl 友好客户端使用示例
============================

这个文件包含了各种使用 Firecrawl 友好客户端的示例代码。
"""

import os
import sys

# 检查是否在虚拟环境中
def check_venv():
    """检查是否在虚拟环境中运行"""
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if not in_venv:
        venv_path = os.path.join(os.path.dirname(__file__), 'venv')
        if os.path.exists(venv_path):
            print("⚠️  警告: 未在虚拟环境中运行")
            print(f"建议使用虚拟环境中的 Python:")
            if sys.platform == 'win32':
                print(f"  {venv_path}\\Scripts\\python.exe {__file__}")
            else:
                print(f"  {venv_path}/bin/python {__file__}")
            print("或者运行: bash run_examples.sh")
            print()
    
    return in_venv

# 检查虚拟环境
check_venv()

try:
    from firecrawl_client import FirecrawlClient, 快速抓取, 网页结果
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n请确保:")
    print("1. 已激活虚拟环境: source venv/bin/activate")
    print("2. 或使用启动脚本: bash run_examples.sh")
    print("3. 或使用虚拟环境中的 Python: venv/bin/python firecrawl_client_examples.py")
    sys.exit(1)


def 示例1_基本抓取():
    """示例 1: 基本网页抓取"""
    print("\n" + "="*50)
    print("示例 1: 基本网页抓取")
    print("="*50)
    
    # 初始化客户端（API 密钥会从环境变量读取）
    client = FirecrawlClient()
    
    # 抓取单个网页
    result = client.抓取网页("https://firecrawl.dev")
    
    # 访问结果
    print(f"标题: {result.标题}")
    print(f"URL: {result.URL}")
    print(f"描述: {result.描述}")
    print(f"\n内容预览（前 200 字符）:\n{result.内容[:200]}...")


def 示例2_爬取网站():
    """示例 2: 爬取整个网站"""
    print("\n" + "="*50)
    print("示例 2: 爬取整个网站")
    print("="*50)
    
    client = FirecrawlClient()
    
    # 爬取网站（限制最多 5 个页面）
    results = client.爬取网站(
        "https://docs.firecrawl.dev",
        最大页面数=5,
        格式=["markdown"]
    )
    
    print(f"\n共抓取 {len(results)} 个页面:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.标题}")
        print(f"   URL: {result.URL}")
        print(f"   内容长度: {len(result.内容)} 字符\n")


def 示例3_搜索网页():
    """示例 3: 搜索网页"""
    print("\n" + "="*50)
    print("示例 3: 搜索网页")
    print("="*50)
    
    client = FirecrawlClient()
    
    # 搜索网页
    results = client.搜索网页("Python 教程", 结果数量=5)
    
    print(f"\n找到 {len(results)} 个结果:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   描述: {result['description']}\n")


def 示例4_获取网站地图():
    """示例 4: 获取网站的所有链接"""
    print("\n" + "="*50)
    print("示例 4: 获取网站地图")
    print("="*50)
    
    client = FirecrawlClient()
    
    # 获取网站地图
    links = client.获取网站地图("https://firecrawl.dev", 最大链接数=10)
    
    print(f"\n找到 {len(links)} 个链接:\n")
    for i, link in enumerate(links, 1):
        print(f"{i}. {link['title']}")
        print(f"   URL: {link['url']}")
        if link['description']:
            print(f"   描述: {link['description']}\n")


def 示例5_批量抓取():
    """示例 5: 批量抓取多个网页"""
    print("\n" + "="*50)
    print("示例 5: 批量抓取多个网页")
    print("="*50)
    
    client = FirecrawlClient()
    
    # 批量抓取
    urls = [
        "https://firecrawl.dev",
        "https://docs.firecrawl.dev",
    ]
    
    results = client.批量抓取(urls, 格式=["markdown"])
    
    print(f"\n批量抓取完成，共 {len(results)} 个结果:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.标题}")
        print(f"   URL: {result.URL}\n")


def 示例6_保存结果():
    """示例 6: 保存抓取结果到文件"""
    print("\n" + "="*50)
    print("示例 6: 保存结果到文件")
    print("="*50)
    
    client = FirecrawlClient()
    
    # 抓取网页
    result = client.抓取网页("https://firecrawl.dev")
    
    # 保存为 Markdown 文件
    result.保存为文件("firecrawl_homepage.md", "markdown")
    print(f"已保存到: firecrawl_homepage.md")
    
    # 保存为 HTML 文件
    result.保存为文件("firecrawl_homepage.html", "html")
    print(f"已保存到: firecrawl_homepage.html")


def 示例7_快速抓取():
    """示例 7: 使用快速抓取函数"""
    print("\n" + "="*50)
    print("示例 7: 快速抓取（便捷函数）")
    print("="*50)
    
    # 使用便捷函数快速抓取
    result = 快速抓取("https://firecrawl.dev")
    
    print(f"标题: {result.标题}")
    print(f"URL: {result.URL}")
    print(f"内容长度: {len(result.内容)} 字符")


def 示例8_高级选项():
    """示例 8: 使用高级选项"""
    print("\n" + "="*50)
    print("示例 8: 使用高级选项")
    print("="*50)
    
    client = FirecrawlClient()
    
    # 使用多种格式和选项
    result = client.抓取网页(
        "https://firecrawl.dev",
        格式=["markdown", "html", "links"],
        仅主要内容=True,
        等待时间=3000,  # 等待 3 秒
        移动端=False
    )
    
    print(f"标题: {result.标题}")
    print(f"Markdown 内容长度: {len(result.内容)} 字符")
    print(f"HTML 内容长度: {len(result.HTML)} 字符")
    print(f"链接数量: {len(result.链接)} 个")


def 示例9_错误处理():
    """示例 9: 错误处理"""
    print("\n" + "="*50)
    print("示例 9: 错误处理")
    print("="*50)
    
    client = FirecrawlClient()
    
    try:
        # 尝试抓取一个不存在的 URL
        result = client.抓取网页("https://this-url-does-not-exist-12345.com")
    except ValueError as e:
        print(f"捕获到 ValueError: {e}")
    except TimeoutError as e:
        print(f"捕获到 TimeoutError: {e}")
    except Exception as e:
        print(f"捕获到其他错误: {e}")


def 示例10_爬取并过滤():
    """示例 10: 爬取网站并过滤特定路径"""
    print("\n" + "="*50)
    print("示例 10: 爬取网站并过滤路径")
    print("="*50)
    
    client = FirecrawlClient()
    
    # 爬取网站，排除某些路径
    results = client.爬取网站(
        "https://docs.firecrawl.dev",
        最大页面数=10,
        排除路径=["/api-reference/*"],  # 排除 API 文档
        格式=["markdown"]
    )
    
    print(f"\n共抓取 {len(results)} 个页面（已排除 API 文档）:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.标题}")


def main():
    """运行所有示例"""
    print("\n" + "="*50)
    print("Firecrawl 友好客户端 - 使用示例")
    print("="*50)
    
    # 检查 API 密钥
    if not os.getenv("FIRECRAWL_API_KEY"):
        print("\n警告: 未设置 FIRECRAWL_API_KEY 环境变量")
        print("请设置环境变量或在使用时提供 API 密钥")
        print("\n示例:")
        print("  export FIRECRAWL_API_KEY='your-api-key'")
        print("  或")
        print("  client = FirecrawlClient(api_key='your-api-key')")
        return
    
    try:
        # 运行示例（可以根据需要注释掉某些示例）
        示例1_基本抓取()
        # 示例2_爬取网站()
        # 示例3_搜索网页()
        # 示例4_获取网站地图()
        # 示例5_批量抓取()
        # 示例6_保存结果()
        # 示例7_快速抓取()
        # 示例8_高级选项()
        # 示例9_错误处理()
        # 示例10_爬取并过滤()
        
        print("\n" + "="*50)
        print("所有示例运行完成！")
        print("="*50)
    
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

