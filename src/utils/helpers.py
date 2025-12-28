"""
工具函数
"""
import re
from typing import List, Set
from difflib import SequenceMatcher


def clean_text(text: str) -> str:
    """清理文本：去除多余空白、HTML标签等"""
    if not text:
        return ""
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空白
    text = text.strip()
    
    return text


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """提取关键词（简单实现，可后续优化）"""
    if not text:
        return []
    
    # 转换为小写
    text = text.lower()
    
    # 移除标点符号
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 常见停用词（英文）
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # 分词并过滤
    words = text.split()
    keywords = [w for w in words if len(w) > 3 and w not in stop_words]
    
    # 统计词频（简单实现）
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # 按频率排序并返回前N个
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_keywords[:max_keywords]]


def calculate_similarity(text1: str, text2: str) -> float:
    """计算两个文本的相似度（0-1）"""
    if not text1 or not text2:
        return 0.0
    
    # 使用SequenceMatcher计算相似度
    similarity = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    return similarity


def normalize_url(url: str) -> str:
    """规范化URL"""
    if not url:
        return ""
    
    # 移除查询参数中的某些参数（如utm_source等）
    # 这里简化处理，实际可以更复杂
    url = url.split('?')[0]
    url = url.rstrip('/')
    
    return url

