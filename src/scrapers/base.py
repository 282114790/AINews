"""
基础爬虫类
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseScraper(ABC):
    """爬虫基类"""
    
    def __init__(self, name: str, url: str, user_agent: Optional[str] = None):
        self.name = name
        self.url = url
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
    
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        抓取新闻
        
        Returns:
            List[Dict]: 新闻列表，每个字典包含：
                - title: 标题
                - content: 内容（可选）
                - url: 链接
                - published_at: 发布时间
                - author: 作者（可选）
                - image_url: 配图（可选）
        """
        pass
    
    def fetch_page(self, url: str, timeout: int = 30) -> Optional[str]:
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"获取页面失败 {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """解析HTML"""
        return BeautifulSoup(html, "lxml")
    
    def normalize_date(self, date_str: str) -> Optional[datetime]:
        """规范化日期字符串"""
        from dateutil import parser
        try:
            return parser.parse(date_str)
        except:
            return None

