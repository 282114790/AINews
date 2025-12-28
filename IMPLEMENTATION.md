# 实现方案详细说明

## 一、系统架构设计

### 1.1 整体架构

```
┌─────────────┐
│   前端界面   │  (HTML/React)
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│  FastAPI    │  (RESTful API)
└──────┬──────┘
       │
┌──────▼──────────────────────────┐
│         核心处理层                │
├─────────────────────────────────┤
│  ┌──────────┐  ┌──────────────┐ │
│  │  爬虫模块  │  │  内容处理模块  │ │
│  └──────────┘  └──────────────┘ │
│  ┌──────────┐  ┌──────────────┐ │
│  │  定时任务  │  │  数据存储    │ │
│  └──────────┘  └──────────────┘ │
└──────┬──────────────────────────┘
       │
┌──────▼──────┐
│   数据库     │  (SQLite/PostgreSQL)
└─────────────┘
```

### 1.2 数据流

1. **采集阶段**
   - 定时任务触发 → 爬虫模块 → 抓取各数据源 → 原始数据

2. **处理阶段**
   - 原始数据 → 去重 → 分类 → 摘要生成 → 评分 → 结构化数据

3. **存储阶段**
   - 结构化数据 → 数据库存储 → 索引建立

4. **展示阶段**
   - 数据库 → API查询 → 前端展示

## 二、核心模块详解

### 2.1 数据采集模块 (`src/scrapers/`)

#### RSS爬虫 (`rss_scraper.py`)
- **功能**: 从RSS源抓取新闻
- **技术**: `feedparser`库解析RSS/Atom格式
- **特点**: 
  - 支持标准RSS和Atom格式
  - 自动提取标题、内容、发布时间、作者
  - 支持图片提取

#### 网页爬虫 (`web_scraper.py`)
- **功能**: 从普通网页抓取新闻
- **技术**: `BeautifulSoup` + CSS选择器
- **特点**:
  - 可配置CSS选择器
  - 支持相对URL转换
  - 灵活适应不同网站结构

#### 扩展性
- 继承`BaseScraper`基类，易于添加新数据源
- 统一的接口和错误处理

### 2.2 内容处理模块 (`src/processors/`)

#### 去重器 (`deduplicator.py`)
- **策略**:
  1. URL完全匹配（主要方法）
  2. 标题相似度匹配（最近7天，阈值0.85）
- **算法**: `SequenceMatcher`计算文本相似度

#### 分类器 (`classifier.py`)
- **方法1**: 关键词匹配（快速，无需API）
  - 预定义关键词库
  - 多类别评分
- **方法2**: AI分类（可选，需要OpenAI API）
  - 使用GPT模型进行智能分类
  - 更准确但成本较高

#### 摘要生成器 (`summarizer.py`)
- **方法1**: 简单提取（取第一段或前N字符）
- **方法2**: AI生成（使用GPT模型）
  - 生成简洁的中文摘要
  - 限制长度（默认200字）

#### 评分器 (`scorer.py`)
- **评分维度**:
  1. 关键词匹配（30%）
     - 高优先级关键词（GPT、ChatGPT、LLM等）
     - 中优先级关键词（AI、机器学习等）
  2. 来源权重（20%）
  3. 内容长度（10%）
  4. 时效性（20%）
     - 7天内为满分，之后递减
  5. 互动数据（20%，预留）

### 2.3 数据存储模块 (`src/models/`, `src/database/`)

#### 数据模型
- **NewsSource**: 新闻来源表
- **NewsCategory**: 新闻分类表
- **News**: 新闻主表
  - 基础信息：标题、内容、URL、图片
  - 元数据：作者、发布时间、抓取时间
  - 处理结果：分类、摘要、评分、关键词
  - 状态标记：是否处理、是否重复、是否精选

#### 索引优化
- `published_at`: 时间查询
- `importance_score`: 排序
- `source_id + published_at`: 联合查询
- `is_featured`: 精选筛选

### 2.4 API模块 (`src/api/`)

#### 新闻API (`/api/news/`)
- `GET /`: 获取新闻列表（支持分页、筛选、排序）
- `GET /{id}`: 获取新闻详情
- `GET /categories/list`: 获取分类列表
- `GET /sources/list`: 获取来源列表

#### 统计API (`/api/stats/`)
- `GET /overview`: 概览统计
- `GET /by-category`: 按分类统计
- `GET /by-source`: 按来源统计
- `GET /trending`: 热门新闻

### 2.5 定时任务模块 (`src/scheduler/`)

#### 任务调度器
- **框架**: APScheduler
- **触发方式**: Cron表达式（每日定时）
- **配置**: `config.yaml`中的`scheduler`部分

#### 任务流程
1. 加载配置的数据源
2. 遍历每个启用的数据源
3. 调用对应的爬虫
4. 处理抓取的数据（去重、分类、摘要、评分）
5. 保存到数据库
6. 标记精选新闻

## 三、配置说明

### 3.1 环境变量 (`.env`)
- `DATABASE_URL`: 数据库连接字符串
- `OPENAI_API_KEY`: OpenAI API密钥（可选）
- `OPENAI_MODEL`: 使用的模型（默认gpt-3.5-turbo）
- `SCRAPE_INTERVAL_HOURS`: 爬取间隔
- `LOG_LEVEL`: 日志级别

### 3.2 配置文件 (`config.yaml`)
- **sources**: 数据源配置
  - `rss`: RSS源列表
  - `web`: 网页源列表
- **processing**: 处理配置
  - `deduplication_threshold`: 去重阈值
  - `categories`: 分类列表
  - `summarization`: 摘要配置
  - `scoring`: 评分权重
- **keywords**: 关键词配置
  - `high_priority`: 高优先级关键词
  - `medium_priority`: 中优先级关键词
- **scheduler**: 定时任务配置
  - `daily_scrape_time`: 每日执行时间
  - `timezone`: 时区

## 四、部署方案

### 4.1 开发环境
```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑.env文件

# 4. 初始化数据库
python src/main.py --init-db

# 5. 运行应用
python src/main.py --reload
```

### 4.2 生产环境

#### 使用Docker（推荐）
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python src/main.py --init-db

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 使用systemd服务
创建`/etc/systemd/system/ainews.service`:
```ini
[Unit]
Description=AI News Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ainews
ExecStart=/opt/ainews/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4.3 数据库迁移
使用Alembic进行数据库版本管理：
```bash
# 初始化迁移
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

## 五、扩展建议

### 5.1 功能扩展
1. **多语言支持**
   - 添加语言检测
   - 支持多语言摘要和分类

2. **用户系统**
   - 用户注册/登录
   - 个性化推荐
   - 收藏和订阅

3. **通知推送**
   - 邮件通知
   - 微信/Telegram机器人
   - 浏览器推送

4. **数据分析**
   - 趋势分析
   - 关键词云图
   - 时间线可视化

5. **全文搜索**
   - 集成Elasticsearch
   - 高级搜索功能

### 5.2 性能优化
1. **缓存**
   - Redis缓存热门查询
   - API响应缓存

2. **异步处理**
   - 使用Celery处理耗时任务
   - 异步爬取和处理

3. **数据库优化**
   - 读写分离
   - 分表策略（按时间）

4. **CDN**
   - 静态资源CDN
   - 图片缓存

### 5.3 监控和日志
1. **监控指标**
   - 爬取成功率
   - API响应时间
   - 数据库性能

2. **告警**
   - 爬取失败告警
   - 系统异常告警

3. **日志分析**
   - 集中式日志（ELK）
   - 错误追踪

## 六、测试策略

### 6.1 单元测试
- 爬虫模块测试
- 处理器模块测试
- API路由测试

### 6.2 集成测试
- 端到端爬取流程
- API完整调用链

### 6.3 性能测试
- 并发爬取测试
- API压力测试

## 七、安全考虑

1. **API安全**
   - 添加认证机制（JWT）
   - 限流保护
   - CORS配置

2. **数据安全**
   - 敏感信息加密
   - 数据库备份

3. **爬虫合规**
   - 遵守robots.txt
   - 控制请求频率
   - 尊重网站服务条款

