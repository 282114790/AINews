# 故障排查指南

## 问题：页面一直显示"加载中..."

### 可能的原因和解决方案

#### 1. Web服务未启动

**检查方法**:
```bash
curl http://localhost:8000/health
```

**解决方案**:
```bash
cd /Users/wesleyzhang/AINews/AINews
source venv/bin/activate
PYTHONPATH=/Users/wesleyzhang/AINews/AINews python src/main.py --reload
```

#### 2. 浏览器控制台错误

**检查方法**:
1. 打开浏览器开发者工具（F12）
2. 查看Console标签页
3. 查看Network标签页，检查API请求是否成功

**常见错误**:
- CORS错误：检查FastAPI的CORS配置
- 404错误：检查API路径是否正确
- 500错误：查看服务器日志

#### 3. API路径问题

**检查API是否正常**:
```bash
# 测试新闻API
curl http://localhost:8000/api/news/

# 测试统计API
curl http://localhost:8000/api/stats/overview

# 测试分类API
curl http://localhost:8000/api/news/categories/list

# 测试来源API
curl http://localhost:8000/api/news/sources/list
```

#### 4. 数据库问题

**检查数据库**:
```bash
source venv/bin/activate
PYTHONPATH=/Users/wesleyzhang/AINews/AINews python -c "
from src.database import SessionLocal
from src.models.news import News
db = SessionLocal()
count = db.query(News).count()
print(f'数据库中有 {count} 条新闻')
if count == 0:
    print('⚠️ 数据库为空，请先运行爬取任务')
db.close()
"
```

**如果没有数据**:
```bash
source venv/bin/activate
PYTHONPATH=/Users/wesleyzhang/AINews/AINews python run_scrape.py
```

#### 5. 前端JavaScript错误

**检查方法**:
1. 打开浏览器开发者工具（F12）
2. 查看Console标签页的错误信息
3. 检查Network标签页，看哪些请求失败了

**常见问题**:
- `fetch` API不支持：使用现代浏览器
- 跨域问题：检查CORS配置
- JSON解析错误：检查API返回格式

#### 6. 端口被占用

**检查端口**:
```bash
lsof -i :8000
```

**解决方案**:
- 停止占用端口的进程
- 或使用其他端口：`python src/main.py --port 8001`

## 快速诊断步骤

### 步骤1: 检查服务状态
```bash
curl http://localhost:8000/health
```
应该返回: `{"status":"ok"}`

### 步骤2: 检查API
```bash
curl http://localhost:8000/api/news/ | python -m json.tool | head -20
```
应该返回新闻列表JSON

### 步骤3: 检查数据库
```bash
ls -lh ainews.db
```
文件应该存在且有内容

### 步骤4: 检查浏览器
1. 打开 http://localhost:8000/static/index.html
2. 按F12打开开发者工具
3. 查看Console和Network标签页
4. 检查是否有错误

### 步骤5: 查看日志
```bash
tail -f logs/ainews.log
```
查看服务器日志中的错误信息

## 常见错误信息

### "加载失败: Failed to fetch"
- **原因**: Web服务未启动或无法连接
- **解决**: 启动Web服务

### "加载失败: HTTP 404"
- **原因**: API路径错误
- **解决**: 检查API路由配置

### "加载失败: HTTP 500"
- **原因**: 服务器内部错误
- **解决**: 查看服务器日志，检查数据库连接

### "暂无新闻数据"
- **原因**: 数据库为空
- **解决**: 运行爬取任务

### "初始化失败"
- **原因**: JavaScript执行错误
- **解决**: 查看浏览器控制台错误信息

## 调试技巧

### 1. 启用详细日志
在浏览器控制台运行：
```javascript
// 查看API响应
fetch('/api/news/').then(r => r.json()).then(console.log)
```

### 2. 检查网络请求
在浏览器Network标签页：
- 查看请求URL是否正确
- 查看响应状态码
- 查看响应内容

### 3. 测试API端点
使用curl或Postman测试各个API端点

### 4. 查看服务器日志
```bash
tail -f logs/ainews.log
```

## 如果问题仍然存在

1. **重启所有服务**:
   ```bash
   # 停止现有服务
   pkill -f "python src/main.py"
   
   # 重新启动
   cd /Users/wesleyzhang/AINews/AINews
   source venv/bin/activate
   PYTHONPATH=/Users/wesleyzhang/AINews/AINews python src/main.py --reload
   ```

2. **清除浏览器缓存**:
   - 按Ctrl+Shift+R (Windows/Linux) 或 Cmd+Shift+R (Mac) 强制刷新

3. **检查防火墙**:
   - 确保8000端口未被防火墙阻止

4. **查看完整错误日志**:
   ```bash
   cat logs/ainews.log | tail -50
   ```

## 联系支持

如果以上方法都无法解决问题，请提供：
1. 浏览器控制台的错误信息
2. 服务器日志的最后50行
3. API测试结果
4. 数据库状态

