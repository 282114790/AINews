"""
RSS爬虫（支持SSL跳过）
"""
import feedparser
import urllib.request
import socket
import ssl
from datetime import datetime
from typing import List, Dict, Optional
from src.scrapers.base import BaseScraper
from src.utils.logger import get_logger
from src.utils.helpers import clean_text

logger = get_logger(__name__)

# 设置全局超时
socket.setdefaulttimeout(15)

# 创建不验证SSL的上下文（用于证书过期的网站）
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# 浏览器 User-Agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


class RSSScraper(BaseScraper):
    """RSS源爬虫"""
    
    def scrape(self) -> List[Dict]:
        """抓取RSS源"""
        logger.info(f"开始抓取RSS源: {self.name} ({self.url})")
        
        try:
            # 先尝试普通方式
            feed = self._fetch_feed()
            
            if feed.bozo:
                logger.warning(f"RSS解析警告: {feed.bozo_exception}")
            
            articles = []
            
            for entry in feed.entries[:50]:  # 限制最多50条
                try:
                    article = {
                        "title": clean_text(entry.get("title", "")),
                        "content": clean_text(entry.get("summary", "") or entry.get("description", "")),
                        "url": entry.get("link", ""),
                        "published_at": self._parse_date(entry.get("published")),
                        "author": entry.get("author", ""),
                        "image_url": self._extract_image(entry),
                    }
                    
                    # 验证必要字段
                    if article["title"] and article["url"]:
                        articles.append(article)
                    else:
                        logger.warning(f"跳过无效文章: {entry.get('title', 'N/A')}")
                        
                except Exception as e:
                    logger.error(f"处理RSS条目失败: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(articles)} 条新闻")
            return articles
            
        except Exception as e:
            logger.error(f"抓取RSS源失败 {self.name}: {e}")
            return []
    
    def _fetch_feed(self):
        """获取RSS feed，支持SSL跳过"""
        headers = {'User-Agent': USER_AGENT}
        
        # 已知需要SSL跳过的域名
        ssl_skip_domains = ['jiqizhixin.com', 'anthropic.com']
        needs_ssl_skip = any(domain in self.url for domain in ssl_skip_domains)
        
        # 如果需要SSL跳过，直接使用SSL跳过方式
        if needs_ssl_skip and self.url.startswith('https'):
            logger.debug(f"使用SSL跳过模式: {self.name}")
            try:
                opener = urllib.request.build_opener(
                    urllib.request.HTTPSHandler(context=SSL_CONTEXT)
                )
                opener.addheaders = [('User-Agent', USER_AGENT)]
                response = opener.open(self.url, timeout=15)
                content = response.read()
                feed = feedparser.parse(content)
                logger.info(f"SSL跳过模式获取 {len(feed.entries)} 条: {self.name}")
                return feed
            except Exception as e:
                logger.warning(f"SSL跳过失败 {self.name}: {e}")
        
        # 普通请求
        try:
            feed = feedparser.parse(self.url, request_headers=headers)
            if feed.entries:
                return feed
        except Exception as e:
            logger.debug(f"普通请求失败: {e}")
        
        # 如果是HTTPS且普通请求失败，尝试跳过SSL验证
        if self.url.startswith('https') and not needs_ssl_skip:
            try:
                opener = urllib.request.build_opener(
                    urllib.request.HTTPSHandler(context=SSL_CONTEXT)
                )
                opener.addheaders = [('User-Agent', USER_AGENT)]
                response = opener.open(self.url, timeout=15)
                content = response.read()
                feed = feedparser.parse(content)
                if feed.entries:
                    logger.info(f"通过SSL跳过成功获取: {self.name}")
                return feed
            except Exception as e:
                logger.warning(f"SSL跳过也失败: {e}")
        
        # 返回原始解析结果
        return feedparser.parse(self.url, request_headers=headers)
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期"""
        if not date_str:
            return datetime.utcnow()
        
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except:
            return datetime.utcnow()
    
    def _extract_image(self, entry) -> Optional[str]:
        """提取图片URL"""
        # 尝试多种方式获取图片
        if hasattr(entry, "media_content") and entry.media_content:
            for media in entry.media_content:
                if media.get("type", "").startswith("image"):
                    return media.get("url")
        
        if hasattr(entry, "links"):
            for link in entry.links:
                if link.get("type", "").startswith("image"):
                    return link.get("href")
        
        # 从内容中提取图片
        if hasattr(entry, "summary"):
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(entry.summary, "html.parser")
            img = soup.find("img")
            if img and img.get("src"):
                return img["src"]
        
        return None

