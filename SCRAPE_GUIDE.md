# 爬取任务指南

## 📅 当前抓取频率

根据 `config.yaml` 配置：

- **定时抓取**: 每天 **09:00**（北京时间）
- **时区**: Asia/Shanghai
- **状态**: ✅ 已启用

### 修改抓取时间

编辑 `config.yaml` 文件：

```yaml
scheduler:
  daily_scrape_time: "09:00"  # 修改为你想要的时间，24小时制
  timezone: "Asia/Shanghai"
  enabled: true
```

修改后需要重启Web服务才能生效。

## 🔧 手动抓取方法

### 方法1: 使用命令行脚本（推荐）

```bash
cd /Users/wesleyzhang/AINews/AINews
source venv/bin/activate
PYTHONPATH=/Users/wesleyzhang/AINews/AINews python run_scrape.py
```

**优点**:
- 简单直接
- 可以看到实时日志输出
- 适合调试

### 方法2: 使用API接口

#### 触发爬取
```bash
curl -X POST http://localhost:8000/api/admin/scrape/trigger
```

#### 查看爬取状态
```bash
curl http://localhost:8000/api/admin/scrape/status
```

**优点**:
- 可以通过HTTP请求触发
- 适合集成到其他系统
- 可以从前端调用

### 方法3: 在Python代码中调用

```python
from src.scheduler.tasks import ScrapeTask

# 创建任务实例
task = ScrapeTask()

# 执行爬取
task.scrape_all()
```

## 🌐 通过Web界面手动抓取

### 添加手动抓取按钮（可选）

如果你想在前端添加一个"立即抓取"按钮，可以：

1. **在HTML中添加按钮**:
```html
<button id="trigger-scrape" onclick="triggerScrape()" 
        style="background: #667eea; color: white; padding: 10px 20px; 
               border: none; border-radius: 4px; cursor: pointer;">
    🔄 立即抓取新闻
</button>
```

2. **添加JavaScript函数**:
```javascript
async function triggerScrape() {
    const button = document.getElementById('trigger-scrape');
    button.disabled = true;
    button.textContent = '抓取中...';
    
    try {
        const response = await fetch('/api/admin/scrape/trigger', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            alert(`抓取成功！新增 ${result.saved_count} 条新闻`);
            // 刷新页面数据
            loadStats();
            loadNews(1);
        } else {
            alert('抓取失败：' + result.message);
        }
    } catch (error) {
        alert('抓取失败：' + error.message);
    } finally {
        button.disabled = false;
        button.textContent = '🔄 立即抓取新闻';
    }
}
```

## 📊 查看抓取结果

### 查看日志
```bash
tail -f logs/ainews.log
```

### 查看数据库统计
```bash
source venv/bin/activate
PYTHONPATH=/Users/wesleyzhang/AINews/AINews python -c "
from src.database import SessionLocal
from src.models.news import News
db = SessionLocal()
count = db.query(News).count()
print(f'当前共有 {count} 条新闻')
db.close()
"
```

### 通过API查看
```bash
curl http://localhost:8000/api/stats/overview
```

## ⚙️ 配置选项

### 禁用定时任务

如果只想手动抓取，可以禁用定时任务：

编辑 `config.yaml`:
```yaml
scheduler:
  enabled: false  # 改为false
```

### 修改抓取间隔（如果需要更频繁）

目前只支持每日定时，如果需要更频繁的抓取，可以：

1. **修改定时任务配置**（需要修改代码）
2. **使用cron任务**（系统级）:
```bash
# 每6小时执行一次
0 */6 * * * cd /path/to/AINews && source venv/bin/activate && python run_scrape.py
```

## 🔍 故障排查

### 抓取失败

1. **检查网络连接**
```bash
ping google.com
```

2. **检查数据源URL**
```bash
curl -I https://openai.com/blog/rss.xml
```

3. **查看详细日志**
```bash
tail -50 logs/ainews.log
```

### 抓取速度慢

- 数据源较多时，抓取可能需要几分钟
- 可以临时禁用部分数据源来加快速度
- 查看日志了解每个源的抓取时间

### 没有新数据

- 检查数据源是否有更新
- 检查去重逻辑是否过于严格
- 查看日志中的抓取和保存数量

## 💡 最佳实践

1. **定期手动抓取**: 在重要事件发生时手动触发
2. **监控日志**: 定期查看日志了解抓取状态
3. **调整数据源**: 根据实际需求启用/禁用数据源
4. **备份数据**: 定期备份数据库文件

## 📝 示例：完整的抓取流程

```bash
# 1. 进入项目目录
cd /Users/wesleyzhang/AINews/AINews

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 执行抓取
PYTHONPATH=/Users/wesleyzhang/AINews/AINews python run_scrape.py

# 4. 查看结果
curl http://localhost:8000/api/stats/overview

# 5. 查看日志（如果需要）
tail -20 logs/ainews.log
```

## 🎯 快速参考

| 操作 | 命令 |
|------|------|
| 手动抓取 | `python run_scrape.py` |
| API触发 | `curl -X POST http://localhost:8000/api/admin/scrape/trigger` |
| 查看状态 | `curl http://localhost:8000/api/admin/scrape/status` |
| 查看统计 | `curl http://localhost:8000/api/stats/overview` |
| 查看日志 | `tail -f logs/ainews.log` |

