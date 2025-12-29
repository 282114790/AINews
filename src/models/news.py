"""
新闻数据模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class NewsSource(Base):
    """新闻来源表"""
    __tablename__ = "news_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, comment="来源名称")
    url = Column(String(500), nullable=False, comment="来源URL")
    source_type = Column(String(50), nullable=False, comment="来源类型：rss/web/api")
    enabled = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    news = relationship("News", back_populates="source")


class NewsCategory(Base):
    """新闻分类表"""
    __tablename__ = "news_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, comment="分类名称")
    description = Column(Text, comment="分类描述")
    created_at = Column(DateTime, default=datetime.utcnow)


class News(Base):
    """新闻表"""
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, comment="标题")
    title_translated = Column(String(500), comment="标题中文翻译")
    content = Column(Text, comment="正文内容")
    summary = Column(Text, comment="摘要")
    summary_translated = Column(Text, comment="摘要中文翻译")
    url = Column(String(1000), nullable=False, unique=True, comment="原文链接")
    image_url = Column(String(1000), comment="配图URL")
    
    # 外键
    source_id = Column(Integer, ForeignKey("news_sources.id"), nullable=False, comment="来源ID")
    category_id = Column(Integer, ForeignKey("news_categories.id"), comment="分类ID")
    
    # 元数据
    author = Column(String(200), comment="作者")
    published_at = Column(DateTime, nullable=False, index=True, comment="发布时间")
    scraped_at = Column(DateTime, default=datetime.utcnow, comment="抓取时间")
    
    # 处理结果
    importance_score = Column(Float, default=0.0, index=True, comment="重要性评分（0-1）")
    keywords = Column(String(500), comment="关键词（逗号分隔）")
    language = Column(String(10), default="en", comment="语言")
    
    # 状态
    is_processed = Column(Boolean, default=False, comment="是否已处理")
    is_duplicate = Column(Boolean, default=False, comment="是否重复")
    is_featured = Column(Boolean, default=False, index=True, comment="是否精选")
    
    # 关系
    source = relationship("NewsSource", back_populates="news")
    category = relationship("NewsCategory")
    
    # 索引
    __table_args__ = (
        Index("idx_published_at", "published_at"),
        Index("idx_importance_score", "importance_score"),
        Index("idx_source_published", "source_id", "published_at"),
    )
    
    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title[:50]}...', score={self.importance_score})>"

