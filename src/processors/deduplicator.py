"""
去重处理器
"""
from typing import List, Dict
from sqlalchemy.orm import Session
from src.models.news import News
from src.utils.logger import get_logger
from src.utils.helpers import calculate_similarity, normalize_url

logger = get_logger(__name__)


class Deduplicator:
    """新闻去重器"""
    
    def __init__(self, db: Session, threshold: float = 0.85):
        self.db = db
        self.threshold = threshold
    
    def is_duplicate(self, article: Dict) -> bool:
        """
        检查文章是否重复
        
        Args:
            article: 文章字典，包含title和url
            
        Returns:
            bool: 是否重复
        """
        url = normalize_url(article.get("url", ""))
        title = article.get("title", "")
        
        if not url or not title:
            return False
        
        # 方法1: URL完全匹配
        existing = self.db.query(News).filter(News.url == url).first()
        if existing:
            logger.debug(f"发现URL重复: {url}")
            return True
        
        # 方法2: 标题相似度匹配（最近7天的新闻）
        from datetime import datetime, timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_news = self.db.query(News).filter(
            News.published_at >= seven_days_ago
        ).all()
        
        for news in recent_news:
            similarity = calculate_similarity(title, news.title)
            if similarity >= self.threshold:
                logger.debug(f"发现标题相似重复: {title} vs {news.title} (相似度: {similarity:.2f})")
                return True
        
        return False
    
    def mark_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        标记重复文章
        
        Returns:
            List[Dict]: 去重后的文章列表
        """
        unique_articles = []
        duplicate_count = 0
        
        for article in articles:
            if not self.is_duplicate(article):
                unique_articles.append(article)
            else:
                duplicate_count += 1
        
        if duplicate_count > 0:
            logger.info(f"过滤掉 {duplicate_count} 条重复新闻")
        
        return unique_articles

