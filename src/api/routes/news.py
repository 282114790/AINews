"""
新闻API路由
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from src.database import get_db
from src.models.news import News, NewsCategory

router = APIRouter()


class NewsResponse(BaseModel):
    """新闻响应模型"""
    id: int
    title: str
    title_translated: Optional[str] = None
    summary: Optional[str]
    summary_translated: Optional[str] = None
    url: str
    image_url: Optional[str]
    source_name: str
    category_name: Optional[str]
    published_at: datetime
    importance_score: float
    is_featured: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[NewsResponse])
def get_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    source: Optional[str] = None,
    featured: Optional[bool] = None,
    days: Optional[int] = Query(None, ge=1, le=30),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """获取新闻列表"""
    query = db.query(News)
    
    # 分类筛选
    if category:
        category_obj = db.query(NewsCategory).filter(NewsCategory.name == category).first()
        if category_obj:
            query = query.filter(News.category_id == category_obj.id)
    
    # 来源筛选
    if source:
        from src.models.news import NewsSource
        source_obj = db.query(NewsSource).filter(NewsSource.name == source).first()
        if source_obj:
            query = query.filter(News.source_id == source_obj.id)
    
    # 精选筛选
    if featured is not None:
        query = query.filter(News.is_featured == featured)
    
    # 时间范围筛选
    if days:
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(News.published_at >= start_date)
    
    # 最低评分筛选
    if min_score is not None:
        query = query.filter(News.importance_score >= min_score)
    
    # 排序和分页
    query = query.order_by(desc(News.published_at), desc(News.importance_score))
    total = query.count()
    news_list = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 转换为响应模型
    result = []
    for news in news_list:
        result.append(NewsResponse(
            id=news.id,
            title=news.title,
            title_translated=getattr(news, 'title_translated', None),
            summary=news.summary,
            summary_translated=getattr(news, 'summary_translated', None),
            url=news.url,
            image_url=news.image_url,
            source_name=news.source.name,
            category_name=news.category.name if news.category else None,
            published_at=news.published_at,
            importance_score=news.importance_score,
            is_featured=news.is_featured
        ))
    
    return result


@router.get("/{news_id}", response_model=NewsResponse)
def get_news_detail(news_id: int, db: Session = Depends(get_db)):
    """获取新闻详情"""
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="新闻不存在")
    
    return NewsResponse(
        id=news.id,
        title=news.title,
        title_translated=getattr(news, 'title_translated', None),
        summary=news.summary,
        summary_translated=getattr(news, 'summary_translated', None),
        url=news.url,
        image_url=news.image_url,
        source_name=news.source.name,
        category_name=news.category.name if news.category else None,
        published_at=news.published_at,
        importance_score=news.importance_score,
        is_featured=news.is_featured
    )


@router.get("/categories/list")
def get_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    categories = db.query(NewsCategory).all()
    return [{"id": cat.id, "name": cat.name} for cat in categories]


@router.get("/sources/list")
def get_sources(db: Session = Depends(get_db)):
    """获取所有来源"""
    from src.models.news import NewsSource
    sources = db.query(NewsSource).filter(NewsSource.enabled == True).all()
    return [{"id": src.id, "name": src.name, "type": src.source_type} for src in sources]

