# 数据源说明文档

本文档列出了AI News工具支持的所有数据源，以及如何添加和管理数据源。

## 当前数据源列表

### 📰 英文科技媒体（6个）

1. **TechCrunch AI**
   - URL: `https://techcrunch.com/tag/artificial-intelligence/feed/`
   - 类型: RSS
   - 特点: 科技创业新闻，AI相关报道丰富
   - 更新频率: 每日多次

2. **VentureBeat AI**
   - URL: `https://venturebeat.com/ai/feed/`
   - 类型: RSS
   - 特点: 专注于AI和机器学习的企业新闻
   - 更新频率: 每日多次

3. **MIT Technology Review**
   - URL: `https://www.technologyreview.com/topic/artificial-intelligence/feed/`
   - 类型: RSS
   - 特点: 权威科技媒体，深度分析
   - 更新频率: 每周多次

4. **The Verge AI**
   - URL: `https://www.theverge.com/ai-artificial-intelligence/rss/index.xml`
   - 类型: RSS
   - 特点: 科技新闻，AI产品评测
   - 更新频率: 每日多次

5. **Wired AI**
   - URL: `https://www.wired.com/feed/tag/artificial-intelligence/rss`
   - 类型: RSS
   - 特点: 科技文化杂志，AI深度报道
   - 更新频率: 每周多次

6. **IEEE Spectrum AI**
   - URL: `https://spectrum.ieee.org/rss/blog/artificial-intelligence/fulltext`
   - 类型: RSS
   - 特点: 工程和技术视角的AI新闻
   - 更新频率: 每周多次

### 🤖 AI专业博客（5个）

7. **Google AI Blog**
   - URL: `https://ai.googleblog.com/feeds/posts/default`
   - 类型: RSS/Atom
   - 特点: Google AI研究和技术发布
   - 更新频率: 每周1-2次

8. **OpenAI Blog**
   - URL: `https://openai.com/blog/rss.xml`
   - 类型: RSS
   - 特点: OpenAI官方博客，GPT相关重要发布
   - 更新频率: 每月多次

9. **DeepMind Blog**
   - URL: `https://deepmind.com/blog/feed/basic/`
   - 类型: RSS
   - 特点: DeepMind研究进展和突破
   - 更新频率: 每月多次

10. **Anthropic Blog**
    - URL: `https://www.anthropic.com/index.xml`
    - 类型: RSS
    - 特点: Claude模型相关新闻
    - 更新频率: 每月多次

11. **AI News**
    - URL: `https://www.ai.news/feed/`
    - 类型: RSS
    - 特点: AI新闻聚合网站
    - 更新频率: 每日多次

### 🎓 学术和研究（2个）

12. **ArXiv AI Papers**
    - URL: `http://arxiv.org/rss/cs.AI`
    - 类型: RSS
    - 特点: AI领域最新论文
    - 更新频率: 每日多次
    - 注意: 论文标题和摘要，需要筛选

13. **Nature Machine Intelligence**
    - URL: `https://www.nature.com/nmachintell.rss`
    - 类型: RSS
    - 特点: 顶级AI学术期刊
    - 更新频率: 每周多次

### 🇨🇳 中文AI媒体（3个）

14. **机器之心**
    - URL: `https://www.jiqizhixin.com/rss`
    - 类型: RSS
    - 特点: 中文AI专业媒体
    - 更新频率: 每日多次

15. **AI科技大本营**
    - URL: `https://www.csdn.net/tags/MtTaEg0sMzYyMjQtYmxvZwO0O0O0O0O0O.html/rss`
    - 类型: RSS
    - 状态: 已禁用（需要验证RSS地址）
    - 特点: CSDN AI频道

16. **36氪AI**
    - URL: `https://36kr.com/feed/tag/ai`
    - 类型: RSS
    - 特点: 科技创业媒体AI频道
    - 更新频率: 每日多次

### 👥 社交媒体和社区（3个）

17. **Reddit r/MachineLearning**
    - URL: `https://www.reddit.com/r/MachineLearning/.rss`
    - 类型: RSS
    - 特点: 机器学习社区讨论
    - 更新频率: 每日多次

18. **Reddit r/artificial**
    - URL: `https://www.reddit.com/r/artificial/.rss`
    - 类型: RSS
    - 特点: 人工智能综合讨论
    - 更新频率: 每日多次

19. **Hacker News AI**
    - URL: `https://hnrss.org/newest?q=AI+OR+machine+learning+OR+GPT+OR+LLM`
    - 类型: RSS（通过hnrss.org）
    - 特点: Hacker News AI相关帖子
    - 更新频率: 每日多次

### 🌐 网页爬虫（2个，默认禁用）

20. **Hacker News**
    - URL: `https://news.ycombinator.com/`
    - 类型: Web Scraper
    - 状态: 已禁用
    - 注意: 需要配置CSS选择器

21. **AI Research Papers**
    - URL: `https://paperswithcode.com/`
    - 类型: Web Scraper
    - 状态: 已禁用
    - 注意: 需要配置CSS选择器

## 如何添加新数据源

### 添加RSS源

在 `config.yaml` 文件的 `sources.rss` 部分添加：

```yaml
sources:
  rss:
    - name: "数据源名称"
      url: "RSS/Atom Feed URL"
      enabled: true  # 或 false 来禁用
```

### 添加网页爬虫

在 `config.yaml` 文件的 `sources.web` 部分添加：

```yaml
sources:
  web:
    - name: "数据源名称"
      url: "网页URL"
      enabled: true
      selectors:
        item: "CSS选择器 - 文章列表项"
        title: "CSS选择器 - 标题"
        link: "CSS选择器 - 链接"
        content: "CSS选择器 - 内容（可选）"
        date: "CSS选择器 - 日期（可选）"
```

### 验证RSS源

可以使用以下方法验证RSS源是否可用：

1. **浏览器访问**: 直接在浏览器中打开RSS URL，应该能看到XML格式的内容
2. **RSS验证工具**: 使用在线RSS验证工具
3. **测试爬取**: 运行 `python run_scrape.py` 查看日志

## 数据源管理建议

### 启用/禁用数据源

- 将 `enabled` 设置为 `true` 启用数据源
- 将 `enabled` 设置为 `false` 禁用数据源（不会删除配置）

### 数据源优先级

建议根据以下因素调整数据源：

1. **更新频率**: 高频更新的源（如Reddit）可能产生大量数据
2. **内容质量**: 专业博客和学术源通常质量更高
3. **语言**: 中英文混合可能影响分类和摘要效果
4. **去重效果**: 某些源可能与其他源有重复内容

### 性能优化

- 如果数据源过多，考虑分批启用
- 监控爬取日志，及时发现失效的数据源
- 定期检查RSS URL是否仍然有效

## 推荐的额外数据源

### 可以考虑添加的源：

1. **Twitter/X API**: AI相关账号的推文（需要API密钥）
2. **LinkedIn**: AI公司官方账号（需要API）
3. **YouTube**: AI相关频道（需要API）
4. **GitHub Trending**: AI相关开源项目
5. **Medium**: AI相关文章（需要RSS或API）
6. **Substack**: AI相关订阅源

### 中文数据源：

1. **AI科技评论**: 需要查找RSS地址
2. **量子位**: 需要查找RSS地址
3. **AI前线**: 需要查找RSS地址
4. **新智元**: 需要查找RSS地址

## 故障排查

### 常见问题

1. **RSS源无法访问**
   - 检查URL是否正确
   - 检查网络连接
   - 查看日志文件了解详细错误

2. **爬取内容为空**
   - 验证RSS源是否正常更新
   - 检查RSS格式是否标准
   - 查看爬虫日志

3. **内容重复**
   - 调整去重阈值
   - 检查是否有多个源发布相同内容

4. **网页爬虫失败**
   - 验证CSS选择器是否正确
   - 检查网站结构是否变化
   - 确认网站是否允许爬取（robots.txt）

## 更新日志

- **2024-01**: 初始版本，包含19个RSS源和2个网页爬虫配置
- 定期检查并更新失效的数据源

