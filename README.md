# AI News - AI新闻聚合工具

## 项目简介

AI News 是一个自动化工具，每天收集、整理并展示全球AI相关的关键事件和新闻。通过智能化的内容处理和分类，帮助用户快速了解AI领域的最新动态。

## 核心功能

1. **数据采集**
   - 从多个新闻源自动抓取AI相关新闻
   - 支持RSS订阅、API接口、网页爬虫等多种数据源
   - 定时自动采集（每天执行）

2. **内容处理**
   - 智能去重（避免重复新闻）
   - 自动分类（技术突破、产品发布、政策法规、融资并购等）
   - 生成摘要（提取关键信息）
   - 重要性评分（筛选关键事件）

3. **数据存储**
   - 存储新闻标题、内容、来源、时间等信息
   - 支持全文搜索
   - 历史数据归档

4. **Web展示**
   - 每日新闻概览
   - 分类浏览
   - 搜索功能
   - 时间线展示

## 技术架构

### 后端技术栈
- **语言**: Python 3.9+
- **Web框架**: FastAPI（提供RESTful API）
- **数据库**: SQLite（开发）/ PostgreSQL（生产）
- **ORM**: SQLAlchemy
- **爬虫**: requests + BeautifulSoup4 / Scrapy
- **AI处理**: OpenAI API / 本地LLM（用于摘要和分类）
- **定时任务**: APScheduler
- **任务队列**: Celery（可选，用于异步处理）

### 前端技术栈
- **框架**: React + TypeScript（或Vue.js）
- **UI库**: Tailwind CSS / Ant Design
- **状态管理**: Zustand / Redux
- **图表**: ECharts / Recharts

### 数据源建议
1. **新闻网站**
   - TechCrunch AI
   - The Verge AI
   - MIT Technology Review
   - VentureBeat AI
   - AI News（ai.news）

2. **RSS源**
   - Hacker News（AI相关）
   - Reddit r/MachineLearning
   - Twitter/X（AI相关账号）

3. **专业平台**
   - arXiv（AI论文）
   - GitHub Trending（AI项目）

## 项目结构

```
AINews/
├── README.md                 # 项目说明
├── requirements.txt          # Python依赖
├── config.yaml              # 配置文件
├── .env.example             # 环境变量示例
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   └── news.py
│   ├── database/            # 数据库相关
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── migrations/
│   ├── scrapers/            # 爬虫模块
│   │   ├── __init__.py
│   │   ├── base.py          # 基础爬虫类
│   │   ├── rss_scraper.py   # RSS爬虫
│   │   ├── web_scraper.py   # 网页爬虫
│   │   └── sources/         # 具体数据源
│   ├── processors/           # 内容处理模块
│   │   ├── __init__.py
│   │   ├── deduplicator.py  # 去重
│   │   ├── classifier.py    # 分类
│   │   ├── summarizer.py    # 摘要生成
│   │   └── scorer.py        # 重要性评分
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── news.py
│   │   │   └── stats.py
│   ├── scheduler/           # 定时任务
│   │   ├── __init__.py
│   │   └── tasks.py
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── frontend/                # 前端项目（可选）
│   ├── package.json
│   ├── src/
│   └── public/
└── tests/                   # 测试文件
    ├── test_scrapers.py
    └── test_processors.py
```

## 实现方案

### 阶段一：核心功能（MVP）
1. ✅ 项目结构搭建
2. ⬜ 数据库模型设计
3. ⬜ 基础爬虫实现（1-2个数据源）
4. ⬜ 简单去重逻辑
5. ⬜ FastAPI基础接口
6. ⬜ 简单的HTML展示页面

### 阶段二：智能化处理
1. ⬜ 集成AI API进行摘要和分类
2. ⬜ 重要性评分算法
3. ⬜ 多数据源支持
4. ⬜ 定时任务调度

### 阶段三：优化和扩展
1. ⬜ 前端界面优化
2. ⬜ 搜索功能
3. ⬜ 数据可视化
4. ⬜ 邮件/通知推送
5. ⬜ 性能优化

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+（如果使用前端）

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd AINews
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入API密钥等配置
```

5. 初始化数据库
```bash
python src/main.py --init-db
```

6. 运行应用
```bash
python src/main.py
```

## 配置说明

主要配置项：
- `OPENAI_API_KEY`: OpenAI API密钥（用于摘要和分类）
- `DATABASE_URL`: 数据库连接字符串
- `SCRAPE_INTERVAL`: 爬取间隔（小时）
- `SOURCES`: 数据源列表

## 许可证

MIT License

