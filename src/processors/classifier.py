"""
分类处理器
"""
import os
from typing import Optional, Dict
from sqlalchemy.orm import Session
from src.models.news import NewsCategory
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Classifier:
    """新闻分类器"""
    
    def __init__(self, db: Session, use_ai: bool = True):
        self.db = db
        self.use_ai = use_ai and bool(os.getenv("OPENAI_API_KEY"))
        self._init_categories()
    
    def _init_categories(self):
        """初始化分类"""
        categories = [
            "技术突破", "产品发布", "融资并购", "政策法规",
            "行业动态", "学术研究", "人物访谈", "其他"
        ]
        
        for cat_name in categories:
            existing = self.db.query(NewsCategory).filter(NewsCategory.name == cat_name).first()
            if not existing:
                self.db.add(NewsCategory(name=cat_name))
        
        self.db.commit()
    
    def classify(self, article: Dict) -> Optional[int]:
        """
        分类文章
        
        Args:
            article: 文章字典
            
        Returns:
            int: 分类ID，如果无法分类返回None
        """
        title = article.get("title", "").lower()
        content = article.get("content", "").lower()
        text = f"{title} {content}"
        
        # 关键词匹配（简单规则）
        category_keywords = {
            "技术突破": ["breakthrough", "突破", "milestone", "里程碑", "achievement", "achieved"],
            "产品发布": ["launch", "发布", "release", "announce", "announcement", "unveil"],
            "融资并购": ["funding", "融资", "raise", "acquisition", "收购", "merger", "并购", "investment"],
            "政策法规": ["policy", "政策", "regulation", "法规", "law", "法律", "government"],
            "学术研究": ["research", "研究", "paper", "论文", "study", "academic"],
            "人物访谈": ["interview", "访谈", "talk", "conversation"],
        }
        
        scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[category] = score
        
        if scores:
            # 选择得分最高的分类
            best_category = max(scores.items(), key=lambda x: x[1])[0]
            category = self.db.query(NewsCategory).filter(NewsCategory.name == best_category).first()
            if category:
                return category.id
        
        # 如果使用AI分类
        if self.use_ai:
            return self._classify_with_ai(article)
        
        # 默认分类为"其他"
        other_category = self.db.query(NewsCategory).filter(NewsCategory.name == "其他").first()
        return other_category.id if other_category else None
    
    def _classify_with_ai(self, article: Dict) -> Optional[int]:
        """使用AI进行分类"""
        try:
            import openai
            
            title = article.get("title", "")
            content = article.get("content", "")[:500]  # 限制长度
            
            prompt = f"""请将以下AI相关新闻分类到以下类别之一：
- 技术突破
- 产品发布
- 融资并购
- 政策法规
- 行业动态
- 学术研究
- 人物访谈
- 其他

标题：{title}
内容：{content}

只返回分类名称，不要其他内容："""
            
            response = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20
            )
            
            category_name = response.choices[0].message.content.strip()
            category = self.db.query(NewsCategory).filter(NewsCategory.name == category_name).first()
            
            if category:
                return category.id
            
        except Exception as e:
            logger.error(f"AI分类失败: {e}")
        
        return None

