"""
重要性评分器
"""
import yaml
from typing import Dict
from pathlib import Path
from src.utils.logger import get_logger
from src.utils.helpers import extract_keywords

logger = get_logger(__name__)


class Scorer:
    """新闻重要性评分器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.high_priority_keywords = self.config.get("keywords", {}).get("high_priority", [])
        self.medium_priority_keywords = self.config.get("keywords", {}).get("medium_priority", [])
        self.scoring_weights = self.config.get("processing", {}).get("scoring", {})
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
        
        return {}
    
    def score(self, article: Dict, source_weight: float = 0.2) -> float:
        """
        计算重要性评分（0-1）
        
        Args:
            article: 文章字典
            source_weight: 来源权重
            
        Returns:
            float: 评分（0-1）
        """
        title = article.get("title", "").lower()
        content = article.get("content", "").lower()
        text = f"{title} {content}"
        
        score = 0.0
        
        # 1. 关键词评分
        keyword_score = self._calculate_keyword_score(text)
        keyword_weight = self.scoring_weights.get("keyword_weight", 0.3)
        score += keyword_score * keyword_weight
        
        # 2. 来源评分（传入参数）
        score += source_weight * self.scoring_weights.get("source_weight", 0.2)
        
        # 3. 长度评分
        length_score = min(len(content) / 1000, 1.0)  # 内容越长分数越高，最高1.0
        length_weight = self.scoring_weights.get("length_weight", 0.1)
        score += length_score * length_weight
        
        # 4. 时效性评分（越新分数越高）
        from datetime import datetime, timedelta
        import pytz
        published_at = article.get("published_at")
        if isinstance(published_at, datetime):
            # 统一时区处理
            utc = pytz.UTC
            now = datetime.now(utc)
            if published_at.tzinfo is None:
                # 如果没有时区信息，假设是UTC
                published_at = utc.localize(published_at)
            else:
                # 转换为UTC
                published_at = published_at.astimezone(utc)
            
            days_old = (now - published_at).days
            recency_score = max(0, 1.0 - days_old / 7.0)  # 7天内为1.0，之后递减
        else:
            recency_score = 0.5  # 默认值
        
        recency_weight = self.scoring_weights.get("recency_weight", 0.2)
        score += recency_score * recency_weight
        
        # 确保分数在0-1之间
        score = min(max(score, 0.0), 1.0)
        
        return round(score, 3)
    
    def _calculate_keyword_score(self, text: str) -> float:
        """计算关键词得分"""
        score = 0.0
        
        # 高优先级关键词
        high_count = sum(1 for keyword in self.high_priority_keywords if keyword.lower() in text)
        score += min(high_count * 0.3, 0.6)  # 每个高优先级关键词0.3分，最高0.6
        
        # 中优先级关键词
        medium_count = sum(1 for keyword in self.medium_priority_keywords if keyword.lower() in text)
        score += min(medium_count * 0.1, 0.3)  # 每个中优先级关键词0.1分，最高0.3
        
        return min(score, 1.0)

