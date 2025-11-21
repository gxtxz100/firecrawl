#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firecrawl 友好客户端
===================

这是一个对 Firecrawl API 的友好包装，让您能够更轻松地使用 Firecrawl 进行网页抓取和爬取。

主要特性：
- 简洁易用的 API
- 友好的中文错误提示
- 自动处理常见错误
- 支持多种输出格式
- 内置进度显示

使用示例：
    from firecrawl_client import FirecrawlClient
    
    # 初始化客户端
    client = FirecrawlClient(api_key="your-api-key")
    
    # 抓取单个网页
    result = client.抓取网页("https://example.com")
    print(result.内容)
    
    # 爬取整个网站
    results = client.爬取网站("https://example.com", 最大页面数=10)
    for page in results:
        print(page.标题)
"""

import os
import sys
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

try:
    from firecrawl import Firecrawl
    from firecrawl.v2.types import Document, CrawlJob
except ImportError:
    try:
        # 尝试从本地路径导入（开发环境）
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sdk_path = os.path.join(current_dir, 'apps', 'python-sdk')
        if os.path.exists(sdk_path) and sdk_path not in sys.path:
            sys.path.insert(0, sdk_path)
        from firecrawl import Firecrawl
        from firecrawl.v2.types import Document, CrawlJob
    except ImportError as e:
        print("错误：未找到 firecrawl 库。")
        print("请确保：")
        print("1. 已安装 firecrawl-py: pip install firecrawl-py")
        print("2. 或已激活虚拟环境: source venv/bin/activate")
        print("3. 或在 firecrawl 项目根目录下运行此脚本")
        print(f"\n详细错误: {e}")
        sys.exit(1)


class FirecrawlClient:
    """
    Firecrawl 友好客户端
    
    这个类提供了对 Firecrawl API 的友好包装，让您能够更轻松地进行网页抓取。
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://api.firecrawl.dev",
        timeout: Optional[float] = None,
        max_retries: int = 3
    ):
        """
        初始化 Firecrawl 客户端
        
        参数:
            api_key: Firecrawl API 密钥。如果不提供，将从环境变量 FIRECRAWL_API_KEY 读取
            api_url: API 服务器地址（默认为官方云服务）
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        
        示例:
            # 从环境变量读取 API 密钥
            client = FirecrawlClient()
            
            # 直接提供 API 密钥
            client = FirecrawlClient(api_key="fc-your-api-key")
        """
        # 如果没有提供 API 密钥，尝试从环境变量读取
        if api_key is None:
            api_key = os.getenv("FIRECRAWL_API_KEY")
        
        if not api_key:
            raise ValueError(
                "未找到 API 密钥！\n"
                "请通过以下方式之一提供 API 密钥：\n"
                "1. 作为参数传入：FirecrawlClient(api_key='your-key')\n"
                "2. 设置环境变量：export FIRECRAWL_API_KEY='your-key'\n"
                "3. 在 .env 文件中设置：FIRECRAWL_API_KEY=your-key\n\n"
                "获取 API 密钥：https://firecrawl.dev"
            )
        
        try:
            # Firecrawl 只接受 api_key 和 api_url 参数
            self._client = Firecrawl(
                api_key=api_key,
                api_url=api_url
            )
            self.api_key = api_key
            self.timeout = timeout
            self.max_retries = max_retries
            print(f"✓ Firecrawl 客户端初始化成功")
        except Exception as e:
            raise RuntimeError(f"初始化 Firecrawl 客户端失败: {str(e)}")
    
    def 抓取网页(
        self,
        url: str,
        格式: Optional[List[str]] = None,
        仅主要内容: bool = True,
        等待时间: Optional[int] = None,
        移动端: bool = False,
        **kwargs
    ) -> '网页结果':
        """
        抓取单个网页
        
        参数:
            url: 要抓取的网页 URL
            格式: 输出格式列表，可选值：['markdown', 'html', 'links', 'screenshot']
            仅主要内容: 是否只抓取主要内容（去除导航栏、页脚等）
            等待时间: 等待页面加载的时间（毫秒）
            移动端: 是否使用移动端视图
            **kwargs: 其他可选参数
        
        返回:
            网页结果对象，包含内容、元数据等信息
        
        示例:
            result = client.抓取网页("https://example.com")
            print(result.内容)  # Markdown 格式的内容
            print(result.标题)  # 网页标题
            print(result.元数据)  # 完整的元数据字典
        """
        if 格式 is None:
            格式 = ["markdown"]
        
        try:
            print(f"正在抓取: {url}")
            document = self._client.scrape(
                url=url,
                formats=格式,
                only_main_content=仅主要内容,
                wait_for=等待时间,
                mobile=移动端,
                **kwargs
            )
            print(f"✓ 抓取成功")
            return 网页结果(document)
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                raise ValueError("API 密钥无效，请检查您的密钥是否正确")
            elif "404" in error_msg:
                raise ValueError(f"无法访问该 URL: {url}\n请检查 URL 是否正确")
            elif "timeout" in error_msg.lower():
                raise TimeoutError(f"请求超时: {url}\n请尝试增加等待时间或检查网络连接")
            else:
                raise RuntimeError(f"抓取失败: {error_msg}")
    
    def 爬取网站(
        self,
        url: str,
        最大页面数: Optional[int] = 10,
        格式: Optional[List[str]] = None,
        排除路径: Optional[List[str]] = None,
        包含路径: Optional[List[str]] = None,
        轮询间隔: int = 2,
        超时: Optional[int] = None,
        **kwargs
    ) -> List['网页结果']:
        """
        爬取整个网站
        
        参数:
            url: 起始 URL
            最大页面数: 最多爬取的页面数量
            格式: 输出格式列表
            排除路径: 要排除的 URL 路径模式列表
            包含路径: 要包含的 URL 路径模式列表
            轮询间隔: 检查爬取状态的间隔（秒）
            超时: 整个爬取任务的最大等待时间（秒）
            **kwargs: 其他可选参数
        
        返回:
            网页结果对象列表
        
        示例:
            results = client.爬取网站(
                "https://example.com",
                最大页面数=20,
                排除路径=["/admin/*", "/private/*"]
            )
            for result in results:
                print(f"{result.标题}: {result.URL}")
        """
        if 格式 is None:
            格式 = ["markdown"]
        
        try:
            print(f"开始爬取网站: {url}")
            print(f"最大页面数: {最大页面数}")
            
            scrape_options = {
                "formats": 格式,
                "only_main_content": True
            }
            
            crawl_job = self._client.crawl(
                url=url,
                limit=最大页面数,
                exclude_paths=排除路径,
                include_paths=包含路径,
                scrape_options=scrape_options,
                poll_interval=轮询间隔,
                timeout=超时,
                **kwargs
            )
            
            print(f"✓ 爬取完成: 共 {crawl_job.completed} 个页面")
            
            # 转换为友好的结果列表
            results = []
            if hasattr(crawl_job, 'data') and crawl_job.data:
                for doc in crawl_job.data:
                    results.append(网页结果(doc))
            
            return results
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                raise ValueError("API 密钥无效，请检查您的密钥是否正确")
            elif "timeout" in error_msg.lower():
                raise TimeoutError(f"爬取超时: {url}\n请尝试增加超时时间或减少最大页面数")
            else:
                raise RuntimeError(f"爬取失败: {error_msg}")
    
    def 搜索网页(
        self,
        查询: str,
        结果数量: int = 5,
        抓取内容: bool = False,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        搜索网页
        
        参数:
            查询: 搜索关键词
            结果数量: 返回的结果数量
            抓取内容: 是否抓取搜索结果的内容
            **kwargs: 其他可选参数
        
        返回:
            搜索结果列表，每个结果包含 URL、标题、描述等信息
        
        示例:
            results = client.搜索网页("Python 教程", 结果数量=10)
            for result in results:
                print(f"{result['title']}: {result['url']}")
        """
        try:
            print(f"正在搜索: {查询}")
            
            scrape_options = None
            if 抓取内容:
                scrape_options = {"formats": ["markdown"]}
            
            search_data = self._client.search(
                query=查询,
                limit=结果数量,
                scrape_options=scrape_options,
                **kwargs
            )
            
            print(f"✓ 找到 {len(getattr(search_data, 'web', []) or [])} 个结果")
            
            # 转换为友好的结果格式
            results = []
            web_results = getattr(search_data, 'web', []) or []
            for item in web_results:
                result = {
                    'url': getattr(item, 'url', ''),
                    'title': getattr(item, 'title', ''),
                    'description': getattr(item, 'description', ''),
                }
                # 如果有抓取的内容
                if hasattr(item, 'markdown'):
                    result['content'] = item.markdown
                results.append(result)
            
            return results
        except Exception as e:
            error_msg = str(e)
            raise RuntimeError(f"搜索失败: {error_msg}")
    
    def 获取网站地图(
        self,
        url: str,
        搜索关键词: Optional[str] = None,
        最大链接数: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, str]]:
        """
        获取网站的所有链接（网站地图）
        
        参数:
            url: 网站 URL
            搜索关键词: 可选，用于过滤链接
            最大链接数: 最多返回的链接数量
            **kwargs: 其他可选参数
        
        返回:
            链接列表，每个链接包含 URL、标题、描述
        
        示例:
            links = client.获取网站地图("https://example.com")
            for link in links:
                print(f"{link['title']}: {link['url']}")
        """
        try:
            print(f"正在获取网站地图: {url}")
            
            map_data = self._client.map(
                url=url,
                search=搜索关键词,
                limit=最大链接数,
                **kwargs
            )
            
            links = getattr(map_data, 'links', []) or []
            print(f"✓ 找到 {len(links)} 个链接")
            
            # 转换为友好的格式
            results = []
            for link in links:
                results.append({
                    'url': getattr(link, 'url', ''),
                    'title': getattr(link, 'title', ''),
                    'description': getattr(link, 'description', ''),
                })
            
            return results
        except Exception as e:
            error_msg = str(e)
            raise RuntimeError(f"获取网站地图失败: {error_msg}")
    
    def 批量抓取(
        self,
        urls: List[str],
        格式: Optional[List[str]] = None,
        轮询间隔: int = 2,
        超时: Optional[int] = None,
        **kwargs
    ) -> List['网页结果']:
        """
        批量抓取多个网页
        
        参数:
            urls: URL 列表
            格式: 输出格式列表
            轮询间隔: 检查状态的间隔（秒）
            超时: 最大等待时间（秒）
            **kwargs: 其他可选参数
        
        返回:
            网页结果对象列表
        
        示例:
            urls = [
                "https://example.com/page1",
                "https://example.com/page2",
                "https://example.com/page3"
            ]
            results = client.批量抓取(urls)
            for result in results:
                print(result.标题)
        """
        if 格式 is None:
            格式 = ["markdown"]
        
        try:
            print(f"开始批量抓取 {len(urls)} 个网页...")
            
            batch_job = self._client.batch_scrape(
                urls=urls,
                formats=格式,
                poll_interval=轮询间隔,
                wait_timeout=超时,
                **kwargs
            )
            
            print(f"✓ 批量抓取完成: {batch_job.completed}/{batch_job.total}")
            
            # 转换为友好的结果列表
            results = []
            if hasattr(batch_job, 'data') and batch_job.data:
                for doc in batch_job.data:
                    results.append(网页结果(doc))
            
            return results
        except Exception as e:
            error_msg = str(e)
            raise RuntimeError(f"批量抓取失败: {error_msg}")
    
    # 英文方法别名（兼容性）
    def scrape(self, url: str, **kwargs) -> '网页结果':
        """抓取单个网页（英文方法）"""
        return self.抓取网页(url, **kwargs)
    
    def crawl(self, url: str, **kwargs) -> List['网页结果']:
        """爬取网站（英文方法）"""
        return self.爬取网站(url, **kwargs)
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """搜索网页（英文方法）"""
        return self.搜索网页(query, **kwargs)
    
    def map(self, url: str, **kwargs) -> List[Dict[str, str]]:
        """获取网站地图（英文方法）"""
        return self.获取网站地图(url, **kwargs)
    
    def batch_scrape(self, urls: List[str], **kwargs) -> List['网页结果']:
        """批量抓取（英文方法）"""
        return self.批量抓取(urls, **kwargs)


class 网页结果:
    """
    网页抓取结果
    
    这个类封装了抓取到的网页数据，提供了友好的属性访问方式。
    """
    
    def __init__(self, document: Document):
        """
        初始化网页结果
        
        参数:
            document: Firecrawl Document 对象
        """
        self._document = document
        self._metadata = document.metadata_dict if hasattr(document, 'metadata_dict') else {}
    
    @property
    def 内容(self) -> str:
        """获取 Markdown 格式的内容"""
        return getattr(self._document, 'markdown', '') or ''
    
    @property
    def HTML(self) -> str:
        """获取 HTML 格式的内容"""
        return getattr(self._document, 'html', '') or ''
    
    @property
    def 标题(self) -> str:
        """获取网页标题"""
        return self._metadata.get('title', '') or self._metadata.get('og_title', '') or ''
    
    @property
    def 描述(self) -> str:
        """获取网页描述"""
        return self._metadata.get('description', '') or self._metadata.get('og_description', '') or ''
    
    @property
    def URL(self) -> str:
        """获取网页 URL"""
        return self._metadata.get('source_url', '') or self._metadata.get('url', '') or ''
    
    @property
    def 元数据(self) -> Dict[str, Any]:
        """获取完整的元数据字典"""
        return self._metadata.copy()
    
    @property
    def 链接(self) -> List[str]:
        """获取网页中的所有链接"""
        links = getattr(self._document, 'links', []) or []
        return [link.url if hasattr(link, 'url') else str(link) for link in links]
    
    def 保存为文件(self, 文件路径: str, 格式: str = 'markdown'):
        """
        将结果保存到文件
        
        参数:
            文件路径: 保存的文件路径
            格式: 文件格式，可选值：'markdown', 'html', 'txt'
        
        示例:
            result.保存为文件("output.md", "markdown")
        """
        if 格式.lower() == 'markdown':
            content = self.内容
            ext = '.md'
        elif 格式.lower() == 'html':
            content = self.HTML
            ext = '.html'
        else:
            content = self.内容
            ext = '.txt'
        
        # 确保文件扩展名正确
        if not 文件路径.endswith(ext):
            文件路径 += ext
        
        try:
            with open(文件路径, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 已保存到: {文件路径}")
        except Exception as e:
            raise IOError(f"保存文件失败: {str(e)}")
    
    def __str__(self) -> str:
        """返回结果的字符串表示"""
        return f"网页结果(标题='{self.标题}', URL='{self.URL}')"
    
    def __repr__(self) -> str:
        """返回结果的详细表示"""
        return f"网页结果(标题='{self.标题}', URL='{self.URL}', 内容长度={len(self.内容)})"


# 便捷函数
def 快速抓取(url: str, api_key: Optional[str] = None) -> 网页结果:
    """
    快速抓取单个网页的便捷函数
    
    参数:
        url: 要抓取的 URL
        api_key: API 密钥（可选，会从环境变量读取）
    
    返回:
        网页结果对象
    
    示例:
        result = 快速抓取("https://example.com")
        print(result.内容)
    """
    client = FirecrawlClient(api_key=api_key)
    return client.抓取网页(url)


# 主程序示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Firecrawl 友好客户端示例')
    parser.add_argument('--url', type=str, help='要抓取的 URL')
    parser.add_argument('--api-key', type=str, help='API 密钥')
    parser.add_argument('--action', type=str, choices=['scrape', 'crawl', 'search', 'map'], 
                       default='scrape', help='操作类型')
    parser.add_argument('--query', type=str, help='搜索关键词（用于 search 操作）')
    
    args = parser.parse_args()
    
    try:
        client = FirecrawlClient(api_key=args.api_key)
        
        if args.action == 'scrape' and args.url:
            result = client.抓取网页(args.url)
            print(f"\n标题: {result.标题}")
            print(f"URL: {result.URL}")
            print(f"\n内容预览:\n{result.内容[:500]}...")
        
        elif args.action == 'crawl' and args.url:
            results = client.爬取网站(args.url, 最大页面数=5)
            print(f"\n共抓取 {len(results)} 个页面:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.标题} - {result.URL}")
        
        elif args.action == 'search' and args.query:
            results = client.搜索网页(args.query, 结果数量=5)
            print(f"\n搜索结果:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   {result['url']}")
                print(f"   {result['description']}\n")
        
        elif args.action == 'map' and args.url:
            links = client.获取网站地图(args.url, 最大链接数=10)
            print(f"\n找到 {len(links)} 个链接:")
            for i, link in enumerate(links, 1):
                print(f"{i}. {link['title']} - {link['url']}")
        
        else:
            print("请提供必要的参数。使用 --help 查看帮助信息。")
    
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

