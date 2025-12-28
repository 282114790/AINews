"""
网页爬虫
"""
from datetime import datetime
from typing import List, Dict, Optional
from src.scrapers.base import BaseScraper
from src.utils.logger import get_logger
from src.utils.helpers import clean_text

logger = get_logger(__name__)


class WebScraper(BaseScraper):
    """网页爬虫"""
    
    def __init__(self, name: str, url: str, selectors: Dict[str, str], user_agent: Optional[str] = None):
        super().__init__(name, url, user_agent)
        self.selectors = selectors  # CSS选择器配置
    
    def scrape(self) -> List[Dict]:
        """抓取网页"""
        logger.info(f"开始抓取网页: {self.name} ({self.url})")
        
        html = self.fetch_page(self.url)
        if not html:
            return []
        
        soup = self.parse_html(html)
        articles = []
        
        try:
            # 根据配置的选择器提取内容
            # 这里需要根据具体网站结构调整
            # 示例：假设选择器指向文章列表项
            items = soup.select(self.selectors.get("item", "article"))
            
            for item in items[:50]:  # 限制最多50条
                try:
                    title_elem = item.select_one(self.selectors.get("title", "h2 a"))
                    link_elem = item.select_one(self.selectors.get("link", "a"))
                    
                    if not title_elem or not link_elem:
                        continue
                    
                    title = clean_text(title_elem.get_text())
                    url = link_elem.get("href", "")
                    
                    # 处理相对URL
                    if url and not url.startswith("http"):
                        from urllib.parse import urljoin
                        url = urljoin(self.url, url)
                    
                    # 提取其他信息
                    content_elem = item.select_one(self.selectors.get("content", "p"))
                    content = clean_text(content_elem.get_text()) if content_elem else ""
                    
                    date_elem = item.select_one(self.selectors.get("date", "time"))
                    published_at = self.normalize_date(date_elem.get_text()) if date_elem else datetime.utcnow()
                    
                    img_elem = item.select_one(self.selectors.get("image", "img"))
                    image_url = img_elem.get("src", "") if img_elem else ""
                    
                    if title and url:
                        articles.append({
                            "title": title,
                            "content": content,
                            "url": url,
                            "published_at": published_at,
                            "image_url": image_url,
                        })
                        
                except Exception as e:
                    logger.error(f"处理文章项失败: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(articles)} 条新闻")
            return articles
            
        except Exception as e:
            logger.error(f"解析网页失败 {self.name}: {e}")
            return []

