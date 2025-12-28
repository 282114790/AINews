# 快速开始指南

## 前置要求

- Python 3.9 或更高版本
- pip（Python包管理器）

## 安装步骤

### 1. 克隆或进入项目目录

```bash
cd AINews
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少配置以下内容：

```env
DATABASE_URL=sqlite:///./ainews.db
OPENAI_API_KEY=your_key_here  # 可选，如果不使用AI功能可以不填
```

### 5. 初始化数据库

```bash
python src/main.py --init-db
```

### 6. 运行应用

开发模式（自动重载）：

```bash
python src/main.py --reload
```

生产模式：

```bash
python src/main.py
```

应用将在 `http://localhost:8000` 启动。

### 7. 访问应用

- **Web界面**: http://localhost:8000/static/index.html
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 手动触发爬取任务

如果需要立即执行一次爬取任务（不等待定时任务）：

```python
from src.scheduler.tasks import ScrapeTask

task = ScrapeTask()
task.scrape_all()
```

或者创建一个简单的脚本 `run_scrape.py`:

```python
from src.scheduler.tasks import ScrapeTask

if __name__ == "__main__":
    task = ScrapeTask()
    task.scrape_all()
```

然后运行：

```bash
python run_scrape.py
```

## 配置数据源

编辑 `config.yaml` 文件，在 `sources` 部分添加或修改数据源：

```yaml
sources:
  rss:
    - name: "TechCrunch AI"
      url: "https://techcrunch.com/tag/artificial-intelligence/feed/"
      enabled: true
```

## 常见问题

### 1. 导入错误

如果遇到 `ModuleNotFoundError`，确保：
- 虚拟环境已激活
- 在项目根目录运行命令
- 所有依赖已安装

### 2. 数据库错误

如果数据库相关错误：
- 确保数据库文件有写入权限
- 尝试删除现有数据库文件重新初始化：`rm ainews.db && python src/main.py --init-db`

### 3. 爬取失败

- 检查网络连接
- 确认数据源URL可访问
- 查看日志文件 `logs/ainews.log`

### 4. OpenAI API错误

如果使用AI功能：
- 确认API密钥正确
- 检查账户余额
- 如果不使用AI功能，可以不配置OPENAI_API_KEY，系统会使用基于规则的分类和摘要

## 下一步

1. 查看 `IMPLEMENTATION.md` 了解详细实现方案
2. 查看 `README.md` 了解项目概述
3. 根据需要修改 `config.yaml` 配置
4. 添加更多数据源
5. 自定义分类和评分规则

## 开发建议

1. **添加新数据源**: 在 `config.yaml` 中添加配置，或创建新的爬虫类
2. **自定义分类**: 修改 `src/processors/classifier.py` 中的关键词规则
3. **调整评分**: 修改 `config.yaml` 中的 `scoring` 权重
4. **前端定制**: 修改 `static/index.html` 或使用React/Vue等框架重构

