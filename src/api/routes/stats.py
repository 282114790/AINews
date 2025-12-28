"""
统计API路由
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from src.database import get_db
from src.models.news import News, NewsCategory

router = APIRouter()


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    """获取概览统计"""
    total_news = db.query(News).count()
    today_news = db.query(News).filter(
        func.date(News.published_at) == func.date(func.now())
    ).count()
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_news = db.query(News).filter(News.published_at >= week_ago).count()
    
    avg_score = db.query(func.avg(News.importance_score)).scalar() or 0.0
    
    return {
        "total_news": total_news,
        "today_news": today_news,
        "week_news": week_news,
        "average_score": round(float(avg_score), 3)
    }


@router.get("/by-category")
def get_stats_by_category(db: Session = Depends(get_db)):
    """按分类统计"""
    stats = db.query(
        NewsCategory.name,
        func.count(News.id).label("count")
    ).join(
        News, News.category_id == NewsCategory.id, isouter=True
    ).group_by(NewsCategory.name).all()
    
    return [{"category": name, "count": count} for name, count in stats]


@router.get("/by-source")
def get_stats_by_source(db: Session = Depends(get_db)):
    """按来源统计"""
    from src.models.news import NewsSource
    
    stats = db.query(
        NewsSource.name,
        func.count(News.id).label("count")
    ).join(
        News, News.source_id == NewsSource.id, isouter=True
    ).group_by(NewsSource.name).all()
    
    return [{"source": name, "count": count} for name, count in stats]


@router.get("/trending")
def get_trending(days: int = 7, limit: int = 10, db: Session = Depends(get_db)):
    """获取热门新闻（按评分）"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    news_list = db.query(News).filter(
        News.published_at >= start_date
    ).order_by(
        desc(News.importance_score)
    ).limit(limit).all()
    
    return [{
        "id": news.id,
        "title": news.title,
        "score": news.importance_score,
        "url": news.url,
        "published_at": news.published_at.isoformat()
    } for news in news_list]

