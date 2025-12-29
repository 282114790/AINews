"""
摘要生成器（支持中文翻译）
"""
import os
import re
from typing import Optional, Dict
from src.utils.logger import get_logger
from src.utils.helpers import clean_text

logger = get_logger(__name__)


class Summarizer:
    """新闻摘要生成器（支持中文翻译）"""
    
    def __init__(self, use_ai: bool = True, max_length: int = 200, translate_to_chinese: bool = True):
        self.use_ai = use_ai and bool(os.getenv("OPENAI_API_KEY"))
        self.max_length = max_length
        self.translate_to_chinese = translate_to_chinese
    
    def summarize(self, article: Dict) -> Dict[str, str]:
        """
        生成摘要（返回原文和翻译）
        
        Args:
            article: 文章字典，包含title和content
            
        Returns:
            dict: {"original": "原文", "translated": "翻译"} 或 {"original": "原文", "translated": None}
        """
        content = article.get("content", "")
        title = article.get("title", "")
        
        if not content:
            summary_original = title[:self.max_length]
        elif self.use_ai:
            # 使用AI生成中文摘要
            summary = self._summarize_with_ai(title, content)
            if not summary:
                summary_original = self._extract_summary(content)
            else:
                summary_original = summary
        else:
            # 简单提取摘要
            summary_original = self._extract_summary(content)
        
        # 如果是英文且需要翻译，进行翻译
        summary_translated = None
        if self.translate_to_chinese and self._is_english(summary_original):
            summary_translated = self._translate_to_chinese(summary_original, title)
        
        return {
            "original": summary_original,
            "translated": summary_translated
        }
    
    def translate_title(self, title: str) -> Optional[str]:
        """
        翻译标题
        
        Args:
            title: 标题文本
            
        Returns:
            str: 翻译后的标题，如果是中文或翻译失败则返回None
        """
        if not self.translate_to_chinese:
            return None
        
        if not self._is_english(title):
            return None
        
        return self._translate_to_chinese(title)
    
    def _is_english(self, text: str) -> bool:
        """检测文本是否主要是英文"""
        if not text:
            return False
        # 统计中文字符数量
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # 如果中文字符少于10%，认为是英文
        return chinese_chars < len(text) * 0.1
    
    def _translate_to_chinese(self, text: str, title: str = "") -> Optional[str]:
        """将英文翻译成中文"""
        # 优先使用OpenAI翻译
        if self.use_ai:
            result = self._translate_with_ai(text, title)
            if result:
                return result
        
        # 使用免费的Google翻译API
        result = self._translate_with_google(text)
        if result:
            return result
        
        # 最后使用简单的词汇替换（作为备选）
        return self._simple_translate(text)
    
    def _translate_with_google(self, text: str) -> Optional[str]:
        """使用Google翻译（免费）"""
        try:
            from deep_translator import GoogleTranslator
            
            # 分段翻译（Google翻译有长度限制）
            if len(text) > 4500:
                text = text[:4500]
            
            translator = GoogleTranslator(source='en', target='zh-CN')
            translation = translator.translate(text)
            
            if translation:
                logger.debug(f"Google翻译成功: {text[:50]}... -> {translation[:50]}...")
                return translation[:self.max_length]
            
        except Exception as e:
            logger.debug(f"Google翻译失败: {e}")
        
        return None
    
    def _translate_with_ai(self, text: str, title: str = "") -> Optional[str]:
        """使用AI翻译"""
        try:
            import openai
            
            prompt = f"""将以下AI新闻摘要翻译成简洁的中文（保持专业术语准确，不超过{self.max_length}字）：

原文：{text}

中文翻译："""
            
            response = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            translation = response.choices[0].message.content.strip()
            return translation[:self.max_length]
            
        except Exception as e:
            logger.debug(f"AI翻译失败: {e}")
            return None
    
    def _simple_translate(self, text: str) -> str:
        """简单词汇替换翻译（备选方案）"""
        # 常用AI术语中英对照
        translations = {
            # 核心AI术语
            "artificial intelligence": "人工智能",
            "machine learning": "机器学习",
            "deep learning": "深度学习",
            "neural network": "神经网络",
            "large language model": "大语言模型",
            "natural language processing": "自然语言处理",
            "computer vision": "计算机视觉",
            "reinforcement learning": "强化学习",
            "generative AI": "生成式AI",
            "transformer": "Transformer模型",
            
            # 常用动词
            "announced": "宣布",
            "launched": "推出",
            "released": "发布",
            "introduced": "推出",
            "unveiled": "发布",
            "developed": "开发",
            "trained": "训练",
            "improved": "改进",
            "enhanced": "增强",
            "updated": "更新",
            
            # 常用名词
            "model": "模型",
            "dataset": "数据集",
            "algorithm": "算法",
            "research": "研究",
            "paper": "论文",
            "benchmark": "基准测试",
            "performance": "性能",
            "accuracy": "准确率",
            "efficiency": "效率",
            "capability": "能力",
            "feature": "功能",
            "tool": "工具",
            "application": "应用",
            "system": "系统",
            "platform": "平台",
            "technology": "技术",
            "company": "公司",
            "startup": "初创公司",
            "funding": "融资",
            "acquisition": "收购",
            "partnership": "合作",
            "collaboration": "协作",
            
            # 公司名称保留英文
            "OpenAI": "OpenAI",
            "Google": "谷歌",
            "Microsoft": "微软",
            "Meta": "Meta",
            "Amazon": "亚马逊",
            "Apple": "苹果",
            "DeepMind": "DeepMind",
            "Anthropic": "Anthropic",
            "NVIDIA": "英伟达",
            
            # 产品名称
            "ChatGPT": "ChatGPT",
            "GPT-4": "GPT-4",
            "GPT-5": "GPT-5",
            "Claude": "Claude",
            "Gemini": "Gemini",
            "Llama": "Llama",
            "Copilot": "Copilot",
        }
        
        result = text.lower()
        for eng, chn in translations.items():
            result = re.sub(re.escape(eng.lower()), chn, result, flags=re.IGNORECASE)
        
        # 如果没有太多替换发生，返回原文
        if result == text.lower():
            return text
        
        return result[:self.max_length]
    
    def _summarize_with_ai(self, title: str, content: str) -> Optional[str]:
        """使用AI生成中文摘要"""
        try:
            import openai
            
            # 限制内容长度
            content = content[:2000]
            
            prompt = f"""请为以下AI相关新闻生成一个简洁的中文摘要（不超过{self.max_length}字）：

标题：{title}
内容：{content}

要求：
1. 用简洁的中文总结主要内容
2. 保持专业术语准确
3. 突出关键信息

中文摘要："""
            
            response = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=150
            )
            
            summary = response.choices[0].message.content.strip()
            return summary[:self.max_length]
            
        except Exception as e:
            logger.debug(f"AI摘要生成失败: {e}")
            return None
    
    def _extract_summary(self, content: str) -> str:
        """简单提取摘要（取第一段或前N个字符）"""
        # 尝试提取第一段
        paragraphs = content.split('\n\n')
        if paragraphs:
            first_para = clean_text(paragraphs[0])
            if len(first_para) <= self.max_length:
                return first_para
        
        # 否则截取前N个字符
        return clean_text(content)[:self.max_length] + "..."
