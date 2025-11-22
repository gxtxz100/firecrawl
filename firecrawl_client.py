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
import re
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# 尝试导入 DuckDuckGo 搜索库（可选，用于免费搜索）
# 新版本使用 ddgs，旧版本使用 duckduckgo_search
DDGS = None
DDG_AVAILABLE = False
try:
    # 优先使用新版本 ddgs
    from ddgs import DDGS
    DDG_AVAILABLE = True
except ImportError:
    try:
        # 回退到旧版本 duckduckgo_search
        from duckduckgo_search import DDGS
        DDG_AVAILABLE = True
    except ImportError:
        DDG_AVAILABLE = False

# 尝试导入本地文章提取库（可选，用于免费提取）
try:
    from readability.readability import Document as ReadabilityDocument
    from bs4 import BeautifulSoup
    import html2text
    from dateutil import parser as date_parser
    import requests
    LOCAL_EXTRACT_AVAILABLE = True
except ImportError:
    try:
        # 尝试另一种导入方式
        from readability import Document as ReadabilityDocument
        from bs4 import BeautifulSoup
        import html2text
        from dateutil import parser as date_parser
        import requests
        LOCAL_EXTRACT_AVAILABLE = True
    except ImportError:
        LOCAL_EXTRACT_AVAILABLE = False

try:
    from firecrawl import Firecrawl
    from firecrawl.v2.types import Document, CrawlJob, ScrapeOptions
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
        from firecrawl.v2.types import Document, CrawlJob, ScrapeOptions
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
        
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        # 如果没有 API 密钥，只初始化用于免费搜索（不初始化 Firecrawl 客户端）
        if not api_key:
            self._client = None
            print(f"💡 未设置 API 密钥，仅可使用免费搜索功能")
            print(f"   如需使用完整功能，请设置 API 密钥：https://firecrawl.dev")
            return
        
        # 有 API 密钥时，初始化 Firecrawl 客户端
        try:
            # Firecrawl 只接受 api_key 和 api_url 参数
            self._client = Firecrawl(
                api_key=api_key,
                api_url=api_url
            )
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
        
        if not self._client:
            raise ValueError("此功能需要 API 密钥。请设置 FIRECRAWL_API_KEY 或使用免费搜索功能。")
        
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
        
        if not self._client:
            raise ValueError("此功能需要 API 密钥。请设置 FIRECRAWL_API_KEY。")
        
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
        使用免费搜索: bool = False,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        搜索网页
        
        参数:
            查询: 搜索关键词
            结果数量: 返回的结果数量
            抓取内容: 是否抓取搜索结果的内容（仅 Firecrawl API）
            使用免费搜索: 如果为 True，使用 DuckDuckGo 免费搜索（不需要 API 密钥）
            **kwargs: 其他可选参数
        
        返回:
            搜索结果列表，每个结果包含 URL、标题、描述等信息
        
        示例:
            # 使用 Firecrawl API 搜索（需要 API 密钥）
            results = client.搜索网页("Python 教程", 结果数量=10)
            
            # 使用免费搜索（不需要 API 密钥）
            results = client.搜索网页("Python 教程", 结果数量=10, 使用免费搜索=True)
        """
        # 如果使用免费搜索，使用 DuckDuckGo
        if 使用免费搜索:
            return self._免费搜索(查询, 结果数量)
        
        # 否则使用 Firecrawl API
        if not self._client:
            raise ValueError("Firecrawl API 搜索需要 API 密钥。请设置 FIRECRAWL_API_KEY 或使用 使用免费搜索=True。")
        
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
    
    def _包含中文(self, 文本: str) -> bool:
        if not 文本:
            return False
        return any('\u4e00' <= ch <= '\u9fff' for ch in 文本)
    
    def _结果相关(self, 查询: str, result: Dict[str, Any]) -> bool:
        if not 查询:
            return True
        title = result.get('title') or ''
        description = result.get('description') or ''
        combined = f"{title} {description}".lower()
        url = (result.get('url') or '').lower()
        has_chinese = self._包含中文(查询)
        
        tokens = [token.lower() for token in re.split(r'\s+', 查询) if token.strip()]
        if not tokens:
            tokens = [查询.lower()]
        
        for token in tokens:
            if token and token in combined:
                return True
            if token and token in url:
                return True
        
        if has_chinese:
            joined = 查询.replace(' ', '')
            if joined and joined in title + description:
                return True
        
        return False
    
    def _过滤搜索结果(self, 查询: str, 原始结果: List[Dict[str, Any]], 目标数量: int) -> List[Dict[str, Any]]:
        if not 原始结果:
            return []
        
        filtered: List[Dict[str, Any]] = []
        fallback: List[Dict[str, Any]] = []
        seen_urls = set()
        
        for item in 原始结果:
            url = item.get('url')
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            
            if self._结果相关(查询, item):
                filtered.append(item)
            else:
                fallback.append(item)
        
        if len(filtered) < 目标数量:
            needed = 目标数量 - len(filtered)
            filtered.extend(fallback[:needed])
        
        return filtered[:目标数量]
    
    def _清理文本(self, 文本: str) -> str:
        if not 文本:
            return ""
        cleaned = 文本.replace("\u00a0", " ")
        cleaned = re.sub(r"\r\n?", "\n", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
        return cleaned.strip()
    
    def _免费搜索(
        self,
        查询: str,
        结果数量: int = 5
    ) -> List[Dict[str, Any]]:
        """
        使用 DuckDuckGo 进行免费搜索（不需要 API 密钥）
        
        参数:
            查询: 搜索关键词
            结果数量: 返回的结果数量
        
        返回:
            搜索结果列表
        """
        if not DDG_AVAILABLE:
            error_msg = (
                "DuckDuckGo 搜索库未安装。\n"
                "请运行以下命令安装：\n"
                "  pip install ddgs\n"
                "  或者（旧版本）: pip install duckduckgo-search\n"
                "\n"
                "或者在虚拟环境中：\n"
                "  source venv/bin/activate\n"
                "  pip install ddgs\n"
                "\n"
                "或者安装所有依赖：\n"
                "  pip install -r requirements.txt"
            )
            raise RuntimeError(error_msg)
        
        try:
            print(f"正在使用 DuckDuckGo 免费搜索: {查询}")
            print("💡 提示：这是免费搜索，不需要 API 密钥")
            
            raw_results: List[Dict[str, Any]] = []
            max_retries = 3
            retry_count = 0
            has_chinese = self._包含中文(查询)
            region = 'cn-zh' if has_chinese else 'wt-wt'
            fetch_limit = max(结果数量 * 3, 15)
            
            while retry_count < max_retries:
                try:
                    with DDGS() as ddgs:
                        count = 0
                        search_iter = ddgs.text(
                            查询,
                            max_results=fetch_limit,
                            region=region,
                            safesearch='Off'
                        )
                        
                        for r in search_iter:
                            if r is None:
                                continue
                            
                            # 处理不同的返回格式（兼容新旧版本）
                            url = r.get('href') or r.get('url') or ''
                            title = r.get('title') or r.get('text') or ''
                            description = r.get('body') or r.get('description') or r.get('snippet') or ''
                            
                            # 只添加有效的 URL
                            if url and url.startswith(('http://', 'https://')):
                                raw_results.append({
                                    'url': url,
                                    'title': title or '无标题',
                                    'description': description or '',
                                })
                                count += 1
                    
                    # 如果找到了结果，退出重试循环
                    if len(raw_results) > 0:
                        break
                    else:
                        # 如果没有结果，可能是搜索失败，尝试重试
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"⚠️  未找到结果，正在重试 ({retry_count}/{max_retries})...")
                            import time
                            time.sleep(2)  # 等待2秒后重试
                        else:
                            break
                        
                except StopIteration:
                    # 迭代器结束，这是正常的
                    break
                except Exception as retry_error:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"⚠️  搜索失败，正在重试 ({retry_count}/{max_retries})...")
                        import time
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        raise retry_error
            
            if len(raw_results) == 0:
                raise RuntimeError(
                    "未能获取到搜索结果。\n"
                    "可能的原因：\n"
                    "1. 网络连接问题\n"
                    "2. DuckDuckGo 服务暂时不可用\n"
                    "3. 搜索关键词可能被限制\n"
                    "\n"
                    "建议：\n"
                    "1. 检查网络连接\n"
                    "2. 稍后重试\n"
                    "3. 尝试使用不同的搜索关键词"
                )
            
            filtered_results = self._过滤搜索结果(查询, raw_results, 结果数量)
            if len(filtered_results) < 结果数量:
                print(f"⚠️  仅找到 {len(filtered_results)} 个相关结果（目标 {结果数量} 个）")
            print(f"✓ 找到 {len(filtered_results)} 个结果")
            return filtered_results
            
        except RuntimeError:
            # 重新抛出 RuntimeError（已经包含友好的错误信息）
            raise
        except Exception as e:
            error_msg = str(e)
            raise RuntimeError(
                f"免费搜索失败: {error_msg}\n"
                "\n"
                "建议：\n"
                "1. 检查网络连接\n"
                "2. 更新搜索库: pip install --upgrade ddgs\n"
                "3. 稍后重试"
            )
    
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
        if not self._client:
            raise ValueError("此功能需要 API 密钥。请设置 FIRECRAWL_API_KEY。")
        
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
        
        if not self._client:
            raise ValueError("此功能需要 API 密钥。请设置 FIRECRAWL_API_KEY。")
        
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
    
    def 提取文章信息(
        self,
        url: str,
        使用本地提取: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        提取文章的核心信息：标题、作者、发表时间、主文
        
        参数:
            url: 要提取的文章 URL
            使用本地提取: 如果为 True，使用本地提取（不需要 API 密钥）
            **kwargs: 其他可选参数
        
        返回:
            包含标题、作者、发表时间、主文的字典
        
        示例:
            # 使用本地提取（不需要 API 密钥）
            article = client.提取文章信息("https://example.com/article", 使用本地提取=True)
            
            # 使用 Firecrawl API 提取（需要 API 密钥，更准确）
            article = client.提取文章信息("https://example.com/article")
        """
        # 如果使用本地提取，使用本地方法
        if 使用本地提取:
            return self._本地提取文章信息(url)
        
        # 否则使用 Firecrawl API（需要 API 密钥）
        if not self._client:
            # 如果没有 API 密钥，尝试使用本地提取
            print("💡 未设置 API 密钥，将使用本地提取（免费）")
            return self._本地提取文章信息(url)
        
        # 定义提取的 JSON Schema
        schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "文章标题"
                },
                "author": {
                    "type": "string",
                    "description": "文章作者，如果找不到则返回空字符串"
                },
                "publish_time": {
                    "type": "string",
                    "description": "文章发表时间，格式为 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS，如果找不到则返回空字符串"
                },
                "content": {
                    "type": "string",
                    "description": "文章正文内容，去除导航栏、页脚、广告等无关信息，只保留正文"
                }
            },
            "required": ["title", "content"]
        }
        
        # 定义提取提示
        prompt = (
            "从网页中提取以下信息：\n"
            "1. 标题：文章的标题\n"
            "2. 作者：文章的作者（如果找不到则返回空字符串）\n"
            "3. 发表时间：文章的发表或更新时间（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS，如果找不到则返回空字符串）\n"
            "4. 主文：文章的正文内容，去除所有无关信息（导航栏、页脚、广告、侧边栏、评论等），只保留正文内容\n\n"
            "注意：只提取上述四个字段，其他信息不要提取。"
        )
        
        try:
            print(f"正在使用 Firecrawl API 提取文章信息: {url}")
            print("这可能需要一些时间，请稍候...")
            
            # 创建 ScrapeOptions 对象
            scrape_options = ScrapeOptions(
                formats=["markdown"],
                only_main_content=True
            )
            
            # 使用 extract API 提取结构化数据
            extract_response = self._client.extract(
                urls=[url],
                prompt=prompt,
                schema=schema,
                scrape_options=scrape_options,
                **kwargs
            )
            
            # 检查提取结果
            if hasattr(extract_response, 'data') and extract_response.data:
                data = extract_response.data
                # 如果 data 是列表，取第一个元素
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
                
                # 确保返回的字典包含所有必需字段
                result = {
                    "title": data.get("title", ""),
                    "author": data.get("author", ""),
                    "publish_time": data.get("publish_time", ""),
                    "content": data.get("content", ""),
                    "url": url
                }
                
                print("✓ 提取成功")
                return result
            else:
                raise RuntimeError("提取结果为空")
        
        except Exception as e:
            error_msg = str(e)
            # 如果 API 提取失败，尝试本地提取
            print(f"⚠️  API 提取失败: {error_msg}")
            print("💡 尝试使用本地提取...")
            return self._本地提取文章信息(url)
    
    def _本地提取文章信息(self, url: str) -> Dict[str, Any]:
        """
        使用本地方法提取文章信息（不需要 API 密钥）
        
        参数:
            url: 要提取的文章 URL
        
        返回:
            包含标题、作者、发表时间、主文的字典
        """
        if not LOCAL_EXTRACT_AVAILABLE:
            error_msg = (
                "本地提取库未安装。\n"
                "请运行以下命令安装：\n"
                "  pip install readability-lxml beautifulsoup4 html2text python-dateutil lxml\n"
                "\n"
                "或者在虚拟环境中：\n"
                "  source venv/bin/activate\n"
                "  pip install readability-lxml beautifulsoup4 html2text python-dateutil lxml\n"
                "\n"
                "或者安装所有依赖：\n"
                "  pip install -r requirements.txt"
            )
            raise RuntimeError(error_msg)
        
        try:
            print(f"正在使用本地方法提取文章信息: {url}")
            print("💡 提示：这是本地提取，不需要 API 密钥")
            
            # 下载网页（带重试机制）
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            max_retries = 3
            retry_count = 0
            html = None
            
            while retry_count < max_retries:
                try:
                    response = requests.get(
                        url,
                        headers=headers,
                        timeout=30,
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    
                    encoding = response.encoding
                    if not encoding or encoding.lower() == 'iso-8859-1':
                        encoding = response.apparent_encoding or 'utf-8'
                    response.encoding = encoding or 'utf-8'
                    html = response.text or response.content.decode(response.encoding, errors='replace')
                    break
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 403:
                        raise RuntimeError(f"访问被拒绝 (403): 该网站可能阻止了自动访问。\nURL: {url}")
                    elif e.response.status_code == 404:
                        raise RuntimeError(f"页面不存在 (404): {url}")
                    elif e.response.status_code >= 500:
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"  ⚠️  服务器错误，正在重试 ({retry_count}/{max_retries})...")
                            import time
                            time.sleep(2)
                            continue
                        else:
                            raise RuntimeError(f"服务器错误 ({e.response.status_code}): {url}")
                    else:
                        raise RuntimeError(f"HTTP 错误 ({e.response.status_code}): {url}")
                except requests.exceptions.ConnectionError as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"  ⚠️  连接错误，正在重试 ({retry_count}/{max_retries})...")
                        import time
                        time.sleep(2)
                        continue
                    else:
                        raise RuntimeError(f"连接失败: 无法连接到服务器。\nURL: {url}\n错误: {str(e)}")
                except requests.exceptions.Timeout:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"  ⚠️  请求超时，正在重试 ({retry_count}/{max_retries})...")
                        import time
                        time.sleep(2)
                        continue
                    else:
                        raise RuntimeError(f"请求超时: {url}")
            
            if html is None:
                raise RuntimeError("无法获取网页内容")
            
            # 使用 readability 提取主要内容
            # 修复 Pydantic 兼容性问题
            try:
                # 方式1：直接传递 HTML 字符串（最常见）
                doc = ReadabilityDocument(html)
            except (TypeError, ValueError) as e:
                # 如果失败，尝试使用 lxml 解析
                try:
                    from lxml import html as lxml_html
                    doc_html = lxml_html.fromstring(html.encode('utf-8'))
                    doc = ReadabilityDocument(doc_html)
                except Exception as e2:
                    # 如果还是失败，尝试传递字节
                    try:
                        doc = ReadabilityDocument(html.encode('utf-8'))
                    except Exception as e3:
                        raise RuntimeError(
                            f"无法解析 HTML 内容。\n"
                            f"错误1: {str(e)}\n"
                            f"错误2: {str(e2)}\n"
                            f"错误3: {str(e3)}\n"
                            f"建议：检查 HTML 内容是否有效"
                        )
            
            title = self._清理文本(doc.title() if hasattr(doc, 'title') else "")
            content_html = doc.summary() if hasattr(doc, 'summary') else ""
            
            # 创建 BeautifulSoup 对象（用于后续提取）
            original_soup = BeautifulSoup(html, 'lxml')
            
            # 如果 readability 没有提取到内容，使用备用方法
            if not content_html or len(content_html.strip()) < 50:
                fallback_soup = BeautifulSoup(html, 'lxml')
                for script in fallback_soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()
                content_html = str(fallback_soup.find('body') or fallback_soup)
            
            # 解析 HTML
            soup = BeautifulSoup(content_html, 'lxml')
            
            # 转换为 Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0
            content = h.handle(str(soup))
            content = self._清理文本(content)
            
            # 提取作者（尝试多种常见的 meta 标签和属性）
            author = ""
            author_selectors = [
                ('meta', {'name': 'author'}),
                ('meta', {'property': 'article:author'}),
                ('meta', {'property': 'og:article:author'}),
                ('meta', {'name': 'twitter:creator'}),
                ('span', {'class': 'author'}),
                ('span', {'class': 'by-author'}),
                ('div', {'class': 'author'}),
                ('a', {'rel': 'author'}),
            ]
            for tag_name, attrs in author_selectors:
                tags = original_soup.find_all(tag_name, attrs)
                if tags:
                    for tag in tags:
                        if tag_name == 'meta':
                            author = tag.get('content', '')
                        else:
                            author = tag.get_text(strip=True)
                        if author:
                            break
                if author:
                    break
            
            # 提取发表时间（尝试多种常见的 meta 标签和属性）
            publish_time = ""
            time_selectors = [
                ('meta', {'property': 'article:published_time'}),
                ('meta', {'property': 'article:modified_time'}),
                ('meta', {'name': 'publishdate'}),
                ('meta', {'name': 'pubdate'}),
                ('time', {'datetime': True}),
                ('time', {'pubdate': True}),
            ]
            
            for tag_name, attrs in time_selectors:
                tags = original_soup.find_all(tag_name, attrs)
                if tags:
                    for tag in tags:
                        if tag_name == 'meta':
                            time_str = tag.get('content', '')
                        else:
                            time_str = tag.get('datetime', '')
                        
                        if time_str:
                            try:
                                # 尝试解析日期
                                dt = date_parser.parse(time_str)
                                publish_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                publish_time = time_str
                            break
                if publish_time:
                    break
            
            # 清理内容
            content = content.strip()
            if not content:
                # 如果 readability 没有提取到内容，尝试提取 body
                body = original_soup.find('body')
                if body:
                    # 移除脚本和样式
                    for script in body(["script", "style", "nav", "header", "footer", "aside"]):
                        script.decompose()
                    content = h.handle(str(body))
                    content = self._清理文本(content)
            
            result = {
                "title": title,
                "author": author.strip() if author else "",
                "publish_time": publish_time.strip() if publish_time else "",
                "content": content,
                "url": url
            }
            
            print("✓ 本地提取成功")
            return result
            
        except Exception as e:
            error_msg = str(e)
            raise RuntimeError(f"本地提取失败: {error_msg}")


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

