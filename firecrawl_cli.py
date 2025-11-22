#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firecrawl 友好客户端 - 交互式命令行工具
========================================

一个简单易用的交互式命令行工具，让您轻松使用 Firecrawl 的各种功能。
"""

import os
import sys
import json
import signal
from typing import Optional
from datetime import datetime

# 检查虚拟环境
def check_venv():
    """检查是否在虚拟环境中"""
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    return in_venv

# 导入客户端
try:
    from firecrawl_client import FirecrawlClient, 快速抓取, 网页结果
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n请确保:")
    print("1. 已激活虚拟环境: source venv/bin/activate")
    print("2. 或使用启动脚本: bash run_examples.sh")
    sys.exit(1)


def clear_screen():
    """清屏"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header():
    """打印标题"""
    print("\n" + "=" * 60)
    print("🔥 Firecrawl 友好客户端 - 交互式工具")
    print("=" * 60)
    print()


def print_menu():
    """打印主菜单"""
    print("\n" + "-" * 60)
    print("请选择功能：")
    print("-" * 60)
    print("1. 📄 抓取单个网页")
    print("2. 📰 提取文章信息（仅标题、作者、时间、正文）⭐")
    print("3. 🕷️  爬取整个网站")
    print("4. 🔍 搜索网页")
    print("5. 🗺️  获取网站地图（所有链接）")
    print("6. 📦 批量抓取多个网页")
    print("7. ⚙️  设置 API 密钥")
    print("8. ℹ️  查看使用说明")
    print("0. 🚪 退出")
    print("-" * 60)


def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """获取用户输入"""
    if default:
        user_input = input(f"{prompt} (默认: {default}): ").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"{prompt}: ").strip()
            if user_input:
                return user_input
            print("⚠️  输入不能为空，请重新输入")


def check_api_key() -> bool:
    """检查 API 密钥是否设置"""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("\n⚠️  未设置 API 密钥！")
        print("\n请选择：")
        print("1. 现在设置 API 密钥")
        print("2. 稍后设置（某些功能可能无法使用）")
        choice = input("\n请选择 (1/2): ").strip()
        
        if choice == "1":
            set_api_key()
            return True
        else:
            return False
    return True


def set_api_key():
    """设置 API 密钥"""
    print("\n" + "=" * 60)
    print("设置 API 密钥")
    print("=" * 60)
    print("\n获取 API 密钥: https://firecrawl.dev")
    print("API 密钥通常以 'fc-' 开头")
    print()
    
    api_key = get_user_input("请输入您的 API 密钥")
    
    # 验证格式
    if not api_key.startswith("fc-"):
        print("⚠️  警告: API 密钥通常以 'fc-' 开头")
        confirm = input("是否继续？(y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
    
    # 设置环境变量（当前会话）
    os.environ["FIRECRAWL_API_KEY"] = api_key
    print(f"\n✓ API 密钥已设置（当前会话有效）")
    print("\n提示: 要永久保存，请运行:")
    print(f"  export FIRECRAWL_API_KEY='{api_key}'")
    print("  或创建 .env 文件")


def extract_article():
    """提取文章信息（仅标题、作者、时间、正文）"""
    print("\n" + "=" * 60)
    print("📰 提取文章信息")
    print("=" * 60)
    print("将提取：标题、作者、发表时间、正文内容")
    print("（自动去除导航栏、页脚、广告等无关信息）")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    url = get_user_input("请输入文章 URL")
    
    print(f"\n正在提取文章信息: {url}")
    print("这可能需要一些时间，请稍候...")
    
    try:
        client = FirecrawlClient()
        article = client.提取文章信息(url)
        
        print("\n" + "=" * 60)
        print("✓ 提取成功！")
        print("=" * 60)
        
        print(f"\n📌 标题: {article.get('title', '未找到')}")
        print(f"✍️  作者: {article.get('author', '未找到') or '未找到'}")
        print(f"📅 发表时间: {article.get('publish_time', '未找到') or '未找到'}")
        print(f"🔗 URL: {article.get('url', url)}")
        
        content = article.get('content', '')
        if content:
            print(f"\n📝 正文内容 ({len(content)} 字符):")
            print("-" * 60)
            # 显示前 500 字符预览
            preview = content[:500]
            print(preview)
            if len(content) > 500:
                print(f"... (还有 {len(content) - 500} 字符)")
            print("-" * 60)
        else:
            print("\n⚠️  未找到正文内容")
        
        # 询问是否保存
        save = input("\n是否保存到文件？(y/N): ").strip().lower()
        if save == 'y':
            # 生成文件名
            safe_title = "".join(c for c in article.get('title', 'article') if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            safe_title = safe_title.replace(' ', '_')
            filename = f"article_{safe_title}.md"
            
            # 保存内容
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# {article.get('title', '无标题')}\n\n")
                    if article.get('author'):
                        f.write(f"**作者**: {article.get('author')}\n\n")
                    if article.get('publish_time'):
                        f.write(f"**发表时间**: {article.get('publish_time')}\n\n")
                    f.write(f"**URL**: {article.get('url', url)}\n\n")
                    f.write("---\n\n")
                    f.write(article.get('content', ''))
                print(f"\n✓ 已保存到: {filename}")
                print(f"  完整路径: {os.path.abspath(filename)}")
            except Exception as e:
                print(f"\n❌ 保存失败: {e}")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def scrape_single_page():
    """抓取单个网页"""
    print("\n" + "=" * 60)
    print("📄 抓取单个网页")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    url = get_user_input("请输入要抓取的网页 URL")
    
    print("\n选择输出格式:")
    print("1. Markdown (推荐)")
    print("2. HTML")
    print("3. Markdown + HTML")
    format_choice = input("请选择 (1-3, 默认: 1): ").strip() or "1"
    
    formats_map = {
        "1": ["markdown"],
        "2": ["html"],
        "3": ["markdown", "html"]
    }
    formats = formats_map.get(format_choice, ["markdown"])
    
    print(f"\n正在抓取: {url}")
    print("请稍候...")
    
    try:
        client = FirecrawlClient()
        result = client.抓取网页(url, 格式=formats)
        
        print("\n" + "=" * 60)
        print("✓ 抓取成功！")
        print("=" * 60)
        print(f"\n标题: {result.标题}")
        print(f"URL: {result.URL}")
        if result.描述:
            print(f"描述: {result.描述}")
        print(f"\n内容长度: {len(result.内容)} 字符")
        
        # 显示内容预览
        preview = result.内容[:500] if result.内容 else ""
        if preview:
            print(f"\n内容预览:\n{'-' * 60}")
            print(preview)
            if len(result.内容) > 500:
                print(f"... (还有 {len(result.内容) - 500} 字符)")
        
        # 询问是否保存
        save = input("\n是否保存到文件？(y/N): ").strip().lower()
        if save == 'y':
            filename = get_user_input("请输入文件名", "output.md")
            result.保存为文件(filename, "markdown")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def crawl_website():
    """爬取整个网站"""
    print("\n" + "=" * 60)
    print("🕷️  爬取整个网站")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    url = get_user_input("请输入起始 URL")
    max_pages = int(get_user_input("最多爬取页面数", "10"))
    
    print(f"\n开始爬取: {url}")
    print(f"最多爬取: {max_pages} 个页面")
    print("这可能需要一些时间，请稍候...")
    
    try:
        client = FirecrawlClient()
        results = client.爬取网站(url, 最大页面数=max_pages)
        
        print("\n" + "=" * 60)
        print(f"✓ 爬取完成！共 {len(results)} 个页面")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.标题}")
            print(f"   URL: {result.URL}")
            print(f"   内容长度: {len(result.内容)} 字符")
        
        # 询问是否保存所有结果
        save = input(f"\n是否保存所有 {len(results)} 个页面？(y/N): ").strip().lower()
        if save == 'y':
            for i, result in enumerate(results, 1):
                safe_title = "".join(c for c in result.标题 if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                filename = f"page_{i:03d}_{safe_title}.md"
                result.保存为文件(filename, "markdown")
                print(f"  已保存: {filename}")
            print(f"\n✓ 所有页面已保存")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def search_web():
    """搜索网页"""
    print("\n" + "=" * 60)
    print("🔍 搜索网页")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    query = get_user_input("请输入搜索关键词")
    limit = int(get_user_input("返回结果数量", "5"))
    
    # 询问处理方式
    print("\n请选择处理方式：")
    print("1. 仅显示链接和描述（快速）")
    print("2. 抓取完整内容（较慢，但可以保存）")
    print("3. 提取文章信息（仅标题、作者、时间、正文）⭐")
    mode_choice = input("请选择 (1/2/3, 默认: 1): ").strip() or "1"
    
    print(f"\n正在搜索: {query}")
    print("请稍候...")
    
    try:
        client = FirecrawlClient()
        
        # 先获取搜索结果（不抓取内容）
        results = client.搜索网页(query, 结果数量=limit, 抓取内容=False)
        
        print("\n" + "=" * 60)
        print(f"✓ 找到 {len(results)} 个结果")
        print("=" * 60)
        
        # 显示搜索结果列表
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('title', '无标题')}")
            print(f"   URL: {result.get('url', '')}")
            if result.get('description'):
                print(f"   描述: {result.get('description')}")
        
        # 根据用户选择处理
        if mode_choice == "1":
            # 仅显示，不做其他处理
            print("\n✓ 搜索完成（仅显示链接和描述）")
            return
        
        elif mode_choice == "2":
            # 抓取完整内容
            print(f"\n正在抓取 {len(results)} 个网页的完整内容...")
            print("这可能需要一些时间，请稍候...")
            
            # 重新搜索并抓取内容
            results_with_content = client.搜索网页(query, 结果数量=limit, 抓取内容=True)
            
            print("\n" + "=" * 60)
            print("✓ 抓取完成")
            print("=" * 60)
            
            for i, result in enumerate(results_with_content, 1):
                print(f"\n{i}. {result.get('title', '无标题')}")
                print(f"   URL: {result.get('url', '')}")
                if result.get('content'):
                    content_len = len(result.get('content', ''))
                    print(f"   内容长度: {content_len} 字符")
            
            # 询问是否保存
            if any(r.get('content') for r in results_with_content):
                save = input(f"\n是否保存所有 {len(results_with_content)} 个搜索结果？(y/N): ").strip().lower()
                if save == 'y':
                    save_dir = "search_results"
                    os.makedirs(save_dir, exist_ok=True)
                    
                    safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                    safe_query = safe_query.replace(' ', '_')
                    
                    print(f"\n正在保存到目录: {save_dir}/")
                    saved_count = 0
                    
                    for i, result in enumerate(results_with_content, 1):
                        if result.get('content'):
                            safe_title = "".join(c for c in result.get('title', '无标题') if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                            safe_title = safe_title.replace(' ', '_')
                            filename = os.path.join(save_dir, f"{i:03d}_{safe_query}_{safe_title}.md")
                            
                            try:
                                with open(filename, 'w', encoding='utf-8') as f:
                                    f.write(f"# {result.get('title', '无标题')}\n\n")
                                    f.write(f"**URL**: {result.get('url', '')}\n\n")
                                    if result.get('description'):
                                        f.write(f"**描述**: {result.get('description')}\n\n")
                                    f.write("---\n\n")
                                    f.write(result.get('content', ''))
                                print(f"  ✓ 已保存: {filename}")
                                saved_count += 1
                            except Exception as e:
                                print(f"  ✗ 保存失败 {filename}: {e}")
                    
                    if saved_count > 0:
                        print(f"\n✓ 成功保存 {saved_count} 个结果到 {save_dir}/ 目录")
                        print(f"  完整路径: {os.path.abspath(save_dir)}")
        
        elif mode_choice == "3":
            # 提取文章信息（仅标题、作者、时间、正文）
            print(f"\n正在提取 {len(results)} 个结果的文章信息...")
            print("（仅提取：标题、作者、发表时间、正文）")
            print("💡 提示：结果会自动保存，可随时按 Ctrl+C 安全退出")
            print("=" * 60)
            
            # 准备保存目录和文件名
            save_dir = "search_results"
            os.makedirs(save_dir, exist_ok=True)
            
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            safe_query = safe_query.replace(' ', '_')
            
            # 进度文件路径
            progress_file = os.path.join(save_dir, f".progress_{safe_query}.json")
            
            # 加载已有进度（断点续传）
            processed_urls = set()
            saved_count = 0
            
            if os.path.exists(progress_file):
                try:
                    with open(progress_file, 'r', encoding='utf-8') as f:
                        progress_data = json.load(f)
                        processed_urls = set(progress_data.get('processed_urls', []))
                        saved_count = progress_data.get('saved_count', 0)
                    print(f"📂 检测到进度文件，已处理 {len(processed_urls)} 个，将继续处理剩余 {len(results) - len(processed_urls)} 个")
                except:
                    pass
            
            extracted_articles = []
            failed_urls = []
            
            # 定义保存函数
            def save_article(item_data, index):
                """保存单个文章"""
                article = item_data['article']
                safe_title = "".join(c for c in article.get('title', '无标题') if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                safe_title = safe_title.replace(' ', '_')
                filename = os.path.join(save_dir, f"{index:03d}_{safe_query}_{safe_title}.md")
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"# {article.get('title', '无标题')}\n\n")
                        if article.get('author'):
                            f.write(f"**作者**: {article.get('author')}\n\n")
                        if article.get('publish_time'):
                            f.write(f"**发表时间**: {article.get('publish_time')}\n\n")
                        f.write(f"**URL**: {article.get('url', '')}\n\n")
                        f.write("---\n\n")
                        f.write(article.get('content', ''))
                    return True, filename
                except Exception as e:
                    return False, str(e)
            
            # 定义保存进度函数
            def save_progress():
                """保存进度"""
                try:
                    progress_data = {
                        'query': query,
                        'processed_urls': list(processed_urls),
                        'saved_count': saved_count,
                        'last_update': datetime.now().isoformat()
                    }
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump(progress_data, f, ensure_ascii=False, indent=2)
                except:
                    pass
            
            # 定义中断处理函数
            def handle_interrupt(signum, frame):
                """处理中断信号"""
                print(f"\n\n⚠️  检测到中断信号，正在保存已提取的结果...")
                save_progress()
                if extracted_articles:
                    print(f"✓ 已保存 {saved_count} 个结果")
                    print(f"  保存目录: {os.path.abspath(save_dir)}")
                    print(f"  进度文件: {progress_file}")
                    print(f"\n💡 提示：下次运行时会自动从断点继续")
                print("\n👋 程序已安全退出")
                sys.exit(0)
            
            # 注册中断处理（Windows 兼容）
            try:
                signal.signal(signal.SIGINT, handle_interrupt)
            except (AttributeError, ValueError):
                # Windows 上可能不支持某些信号
                pass
            
            # 开始提取
            start_time = datetime.now()
            
            for i, result in enumerate(results, 1):
                url = result.get('url', '')
                if not url:
                    continue
                
                # 跳过已处理的URL
                if url in processed_urls:
                    print(f"[{i}/{len(results)}] ⏭️  已处理，跳过: {url[:60]}...")
                    continue
                
                # 显示进度（简化输出以提高速度）
                elapsed = (datetime.now() - start_time).total_seconds()
                avg_time = elapsed / max(saved_count, 1)
                remaining = len(results) - i + 1
                estimated_time = avg_time * remaining
                print(f"[{i}/{len(results)}] 提取中... (已保存: {saved_count}, 预计剩余: {int(estimated_time)}秒) {url[:50]}...")
                
                try:
                    article = client.提取文章信息(url)
                    
                    # 立即保存
                    success, result_info = save_article({
                        'index': i,
                        'original': result,
                        'article': article
                    }, i)
                    
                    if success:
                        extracted_articles.append({
                            'index': i,
                            'original': result,
                            'article': article
                        })
                        processed_urls.add(url)
                        saved_count += 1
                        # 每5个保存一次进度
                        if saved_count % 5 == 0:
                            save_progress()
                        print(f"  ✓ 提取并保存成功: {os.path.basename(result_info)}")
                    else:
                        print(f"  ✗ 保存失败: {result_info}")
                        failed_urls.append({'url': url, 'error': f'保存失败: {result_info}'})
                        
                except KeyboardInterrupt:
                    # 用户中断
                    raise
                except Exception as e:
                    error_msg = str(e)[:100]
                    print(f"  ✗ 提取失败: {error_msg}")
                    failed_urls.append({'url': url, 'error': error_msg})
                    # 即使失败也记录，避免重复尝试
                    processed_urls.add(url)
                    save_progress()
            
            # 保存最终进度
            save_progress()
            
            # 删除进度文件（任务完成）
            if os.path.exists(progress_file):
                try:
                    os.remove(progress_file)
                except:
                    pass
            
            # 显示提取结果摘要
            print("\n" + "=" * 60)
            print(f"✓ 提取完成！成功: {len(extracted_articles)}, 失败: {len(failed_urls)}")
            print(f"✓ 已保存 {saved_count} 个结果到 {save_dir}/ 目录")
            print("=" * 60)
            
            # 显示前5个结果预览
            if extracted_articles:
                print("\n前5个结果预览:")
                for item in extracted_articles[:5]:
                    article = item['article']
                    print(f"\n{item['index']}. {article.get('title', '无标题')[:50]}")
                    if article.get('author'):
                        print(f"   作者: {article.get('author')}")
                    if article.get('content'):
                        content_len = len(article.get('content', ''))
                        print(f"   正文: {content_len} 字符")
            
            if failed_urls and len(failed_urls) <= 10:
                print(f"\n⚠️  以下 {len(failed_urls)} 个 URL 提取失败:")
                for failed in failed_urls[:10]:
                    print(f"   - {failed['url'][:60]}...")
            elif failed_urls:
                print(f"\n⚠️  共 {len(failed_urls)} 个 URL 提取失败（仅显示前10个）:")
                for failed in failed_urls[:10]:
                    print(f"   - {failed['url'][:60]}...")
            
            if saved_count > 0:
                print(f"\n📁 所有结果已自动保存到: {os.path.abspath(save_dir)}")
                print(f"   共 {saved_count} 个文件")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def get_site_map():
    """获取网站地图"""
    print("\n" + "=" * 60)
    print("🗺️  获取网站地图")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    url = get_user_input("请输入网站 URL")
    max_links = int(get_user_input("最多返回链接数", "20"))
    
    print(f"\n正在获取网站地图: {url}")
    print("请稍候...")
    
    try:
        client = FirecrawlClient()
        links = client.获取网站地图(url, 最大链接数=max_links)
        
        print("\n" + "=" * 60)
        print(f"✓ 找到 {len(links)} 个链接")
        print("=" * 60)
        
        for i, link in enumerate(links, 1):
            print(f"\n{i}. {link.get('title', '无标题')}")
            print(f"   URL: {link.get('url', '')}")
            if link.get('description'):
                print(f"   描述: {link.get('description')}")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def batch_scrape():
    """批量抓取"""
    print("\n" + "=" * 60)
    print("📦 批量抓取多个网页")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    print("\n请输入要抓取的 URL（每行一个，输入空行结束）:")
    urls = []
    while True:
        url = input(f"URL {len(urls) + 1}: ").strip()
        if not url:
            break
        urls.append(url)
    
    if not urls:
        print("⚠️  未输入任何 URL")
        return
    
    print(f"\n将抓取 {len(urls)} 个网页")
    print("这可能需要一些时间，请稍候...")
    
    try:
        client = FirecrawlClient()
        results = client.批量抓取(urls)
        
        print("\n" + "=" * 60)
        print(f"✓ 批量抓取完成！共 {len(results)} 个结果")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.标题}")
            print(f"   URL: {result.URL}")
            print(f"   内容长度: {len(result.内容)} 字符")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def show_help():
    """显示帮助信息"""
    print("\n" + "=" * 60)
    print("ℹ️  使用说明")
    print("=" * 60)
    print("""
Firecrawl 友好客户端使用说明
============================

1. 抓取单个网页
   - 输入网页 URL
   - 选择输出格式（Markdown/HTML）
   - 可以保存结果到文件

2. 提取文章信息 ⭐
   - 仅提取：标题、作者、发表时间、正文
   - 自动去除无关信息（导航栏、页脚、广告等）
   - 适合提取新闻、博客等文章内容

3. 爬取整个网站
   - 输入起始 URL
   - 设置最多爬取页面数
   - 可以保存所有页面

4. 搜索网页
   - 输入搜索关键词
   - 设置返回结果数量
   - 选择处理方式：
     * 仅显示链接和描述（快速）
     * 抓取完整内容（可保存）
     * 提取文章信息（仅标题、作者、时间、正文）⭐
   - 可以保存所有结果到文件
   - 保存位置: search_results/ 目录

5. 获取网站地图
   - 输入网站 URL
   - 获取网站所有链接
   - 显示链接列表

6. 批量抓取
   - 输入多个 URL
   - 批量抓取所有网页
   - 显示所有结果

7. 设置 API 密钥
   - 设置 Firecrawl API 密钥
   - 获取密钥: https://firecrawl.dev

更多信息:
- 查看 firecrawl_client_README.md
- 查看 firecrawl_client_examples.py
""")


def main():
    """主函数"""
    # 检查虚拟环境
    if not check_venv():
        print("⚠️  警告: 未在虚拟环境中运行")
        print("建议使用: source venv/bin/activate")
        input("\n按 Enter 继续...")
    
    while True:
        clear_screen()
        print_header()
        
        # 检查 API 密钥状态
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if api_key:
            print(f"✓ API 密钥已设置: {api_key[:10]}...")
        else:
            print("⚠️  API 密钥未设置（某些功能可能无法使用）")
        
        print_menu()
        
        choice = input("\n请选择 (0-8): ").strip()
        
        if choice == "0":
            print("\n👋 再见！")
            break
        elif choice == "1":
            scrape_single_page()
        elif choice == "2":
            extract_article()
        elif choice == "3":
            crawl_website()
        elif choice == "4":
            search_web()
        elif choice == "5":
            get_site_map()
        elif choice == "6":
            batch_scrape()
        elif choice == "7":
            set_api_key()
        elif choice == "8":
            show_help()
        else:
            print("\n❌ 无效选择，请重新输入")
        
        if choice != "0":
            input("\n按 Enter 返回主菜单...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  程序被中断")
        print("💡 提示：如果正在提取文章，已保存的结果不会丢失")
        print("👋 程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

