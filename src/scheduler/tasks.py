"""
定时任务
"""
import yaml
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from src.database import SessionLocal, init_db
from src.models.news import News, NewsSource
from src.scrapers import RSSScraper, WebScraper
from src.processors import Deduplicator, Classifier, Summarizer, Scorer
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScrapeTask:
    """爬取任务"""
    
    def __init__(self):
        self.db: Session = SessionLocal()
        self.config = self._load_config()
        self.deduplicator = Deduplicator(self.db)
        self.classifier = Classifier(self.db)
        
        # 从配置中读取摘要设置
        summarization_config = self.config.get("processing", {}).get("summarization", {})
        self.summarizer = Summarizer(
            max_length=summarization_config.get("max_length", 200),
            translate_to_chinese=summarization_config.get("translate_to_chinese", True)
        )
        self.scorer = Scorer()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        config_path = Path("config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _get_or_create_source(self, name: str, url: str, source_type: str) -> NewsSource:
        """获取或创建新闻来源"""
        source = self.db.query(NewsSource).filter(NewsSource.name == name).first()
        if not source:
            source = NewsSource(name=name, url=url, source_type=source_type)
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)
        return source
    
    def scrape_all(self):
        """执行所有爬取任务"""
        logger.info("开始执行爬取任务...")
        
        sources_config = self.config.get("sources", {})
        total_scraped = 0
        total_saved = 0
        
        # RSS源
        for rss_config in sources_config.get("rss", []):
            if not rss_config.get("enabled", True):
                continue
            
            try:
                scraper = RSSScraper(
                    name=rss_config["name"],
                    url=rss_config["url"]
                )
                articles = scraper.scrape()
                total_scraped += len(articles)
                
                saved = self._process_articles(articles, rss_config["name"], rss_config["url"], "rss")
                total_saved += saved
                
            except Exception as e:
                logger.error(f"爬取RSS源失败 {rss_config['name']}: {e}")
        
        # Web源
        for web_config in sources_config.get("web", []):
            if not web_config.get("enabled", True):
                continue
            
            try:
                scraper = WebScraper(
                    name=web_config["name"],
                    url=web_config["url"],
                    selectors=web_config.get("selectors", {})
                )
                articles = scraper.scrape()
                total_scraped += len(articles)
                
                saved = self._process_articles(articles, web_config["name"], web_config["url"], "web")
                total_saved += saved
                
            except Exception as e:
                logger.error(f"爬取Web源失败 {web_config['name']}: {e}")
        
        logger.info(f"爬取任务完成：抓取 {total_scraped} 条，保存 {total_saved} 条")
        
        # 标记精选新闻
        self._mark_featured()
        
        self.db.close()
    
    def _process_articles(self, articles: List[Dict], source_name: str, source_url: str, source_type: str) -> int:
        """处理文章列表"""
        # 去重
        unique_articles = self.deduplicator.mark_duplicates(articles)
        
        # 获取或创建来源
        source = self._get_or_create_source(source_name, source_url, source_type)
        
        saved_count = 0
        
        for article in unique_articles:
            try:
                # 分类
                category_id = self.classifier.classify(article)
                
                # 生成摘要
                summary = self.summarizer.summarize(article)
                
                # 计算重要性评分
                importance_score = self.scorer.score(article, source_weight=0.2)
                
                # 创建新闻记录
                news = News(
                    title=article["title"],
                    content=article.get("content", ""),
                    summary=summary,
                    url=article["url"],
                    image_url=article.get("image_url"),
                    source_id=source.id,
                    category_id=category_id,
                    author=article.get("author"),
                    published_at=article.get("published_at", datetime.utcnow()),
                    importance_score=importance_score,
                    is_processed=True
                )
                
                self.db.add(news)
                saved_count += 1
                
            except Exception as e:
                logger.error(f"处理文章失败: {e}")
                # 如果是唯一约束错误（重复URL），回滚当前事务继续
                if "UNIQUE constraint" in str(e) or "IntegrityError" in str(type(e).__name__):
                    self.db.rollback()
                continue
        
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"提交事务失败: {e}")
            self.db.rollback()
        
        return saved_count
    
    def _mark_featured(self):
        """标记精选新闻（评分最高的前10%）"""
        # 获取最近7天的新闻
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_news = self.db.query(News).filter(
            News.published_at >= week_ago,
            News.is_featured == False
        ).all()
        
        if not recent_news:
            return
        
        # 按评分排序
        sorted_news = sorted(recent_news, key=lambda x: x.importance_score, reverse=True)
        
        # 标记前10%为精选
        featured_count = max(1, len(sorted_news) // 10)
        for news in sorted_news[:featured_count]:
            news.is_featured = True
        
        self.db.commit()
        logger.info(f"标记了 {featured_count} 条精选新闻")


def setup_scheduler():
    """设置定时任务调度器"""
    scheduler = BackgroundScheduler()
    
    # 加载配置
    config_path = Path("config.yaml")
    config = {}
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    
    scheduler_config = config.get("scheduler", {})
    
    if scheduler_config.get("enabled", True):
        # 获取每日执行时间
        time_str = scheduler_config.get("daily_scrape_time", "09:00")
        hour, minute = map(int, time_str.split(":"))
        timezone = scheduler_config.get("timezone", "Asia/Shanghai")
        
        # 添加定时任务
        scheduler.add_job(
            ScrapeTask().scrape_all,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
            id="daily_scrape",
            name="每日新闻爬取",
            replace_existing=True
        )
        
        logger.info(f"定时任务已设置：每天 {time_str} 执行")
    
    return scheduler
