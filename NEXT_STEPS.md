# 下一步行动指南

## 🚀 立即开始（5-10分钟）

### 步骤1: 检查环境
```bash
# 检查Python版本（需要3.9+）
python3 --version

# 检查是否已安装依赖
pip3 list | grep fastapi
```

### 步骤2: 安装依赖
```bash
# 创建虚拟环境（如果还没有）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装所有依赖
pip install -r requirements.txt
```

### 步骤3: 配置环境变量
```bash
# 创建.env文件（如果还没有）
cp .env.example .env

# 编辑.env文件，至少设置：
# DATABASE_URL=sqlite:///./ainews.db
# OPENAI_API_KEY=your_key_here  # 可选
```

### 步骤4: 初始化数据库
```bash
python src/main.py --init-db
```

### 步骤5: 测试运行（小规模测试）
```bash
# 先测试单个数据源，修改config.yaml只启用1-2个源
# 然后运行手动爬取
python run_scrape.py
```

### 步骤6: 启动Web服务
```bash
# 开发模式（自动重载）
python src/main.py --reload

# 访问 http://localhost:8000/static/index.html
```

## 📊 验证和测试（10-15分钟）

### 1. 检查数据采集
- ✅ 查看日志文件：`logs/ainews.log`
- ✅ 检查数据库：`ainews.db` 是否创建
- ✅ 验证数据源：确认RSS源可以正常访问

### 2. 测试API接口
访问以下URL验证API是否正常：
- http://localhost:8000/api/news/ - 新闻列表
- http://localhost:8000/api/stats/overview - 统计数据
- http://localhost:8000/docs - API文档（Swagger UI）

### 3. 检查Web界面
- 打开 http://localhost:8000/static/index.html
- 查看新闻是否正常显示
- 测试筛选功能

## 🔧 优化和调整（可选）

### 优先级1: 数据源优化

#### 测试数据源有效性
```bash
# 创建一个测试脚本 test_sources.py
python3 << EOF
import feedparser
sources = [
    "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "https://openai.com/blog/rss.xml",
    # 添加其他源测试
]
for url in sources:
    try:
        feed = feedparser.parse(url)
        print(f"✅ {url}: {len(feed.entries)} 条")
    except Exception as e:
        print(f"❌ {url}: {e}")
EOF
```

#### 调整数据源配置
- 根据测试结果，禁用无效的数据源
- 调整 `enabled: true/false` 来控制哪些源启用
- 建议先启用3-5个核心源，测试稳定后再添加更多

### 优先级2: 性能优化

#### 限制爬取数量
在 `src/scrapers/rss_scraper.py` 中，当前限制为50条：
```python
for entry in feed.entries[:50]:  # 可以调整为更小的数字
```

#### 调整爬取频率
在 `config.yaml` 中：
```yaml
scheduler:
  daily_scrape_time: "09:00"  # 可以改为其他时间
```

### 优先级3: 内容处理优化

#### 调整去重阈值
如果发现太多重复或漏掉重复：
```yaml
processing:
  deduplication_threshold: 0.85  # 调整这个值（0-1之间）
```

#### 优化关键词
在 `config.yaml` 中添加更多相关关键词：
```yaml
keywords:
  high_priority:
    - "你的关键词"
```

### 优先级4: 前端优化

#### 改进界面
- 修改 `static/index.html` 的样式
- 添加更多筛选选项
- 改进移动端显示

#### 添加功能
- 搜索功能
- 收藏功能
- 分享功能

## 🎯 功能扩展建议

### 短期（1-2周）

1. **添加搜索功能**
   - 在前端添加搜索框
   - 实现标题和内容搜索
   - 使用SQL的LIKE查询或全文搜索

2. **优化分类**
   - 改进分类准确性
   - 添加子分类
   - 显示分类统计

3. **数据可视化**
   - 添加图表展示
   - 时间线视图
   - 关键词云图

### 中期（1-2月）

1. **用户系统**
   - 用户注册/登录
   - 个性化推荐
   - 收藏和订阅

2. **通知功能**
   - 邮件通知
   - 微信/Telegram机器人
   - 浏览器推送

3. **高级搜索**
   - 全文搜索（Elasticsearch）
   - 高级筛选
   - 保存搜索条件

### 长期（3-6月）

1. **移动应用**
   - iOS/Android应用
   - 推送通知
   - 离线阅读

2. **AI增强**
   - 更智能的摘要
   - 自动翻译
   - 情感分析

3. **数据分析**
   - 趋势分析
   - 预测模型
   - 报告生成

## 🐛 常见问题排查

### 问题1: 爬取失败
**症状**: 日志显示连接错误或超时

**解决方案**:
```bash
# 1. 检查网络连接
ping google.com

# 2. 测试单个RSS源
python3 -c "import feedparser; print(feedparser.parse('RSS_URL'))"

# 3. 检查代理设置（如果需要）
# 在.env中添加代理配置
```

### 问题2: 数据库错误
**症状**: 数据库相关错误

**解决方案**:
```bash
# 1. 删除旧数据库重新初始化
rm ainews.db
python src/main.py --init-db

# 2. 检查文件权限
ls -l ainews.db
```

### 问题3: 导入错误
**症状**: ModuleNotFoundError

**解决方案**:
```bash
# 1. 确认虚拟环境已激活
which python  # 应该指向venv/bin/python

# 2. 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 3. 检查Python路径
python -c "import sys; print(sys.path)"
```

### 问题4: 端口被占用
**症状**: Address already in use

**解决方案**:
```bash
# 1. 查找占用端口的进程
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 2. 使用其他端口
python src/main.py --port 8001
```

## 📝 检查清单

在正式使用前，确认以下事项：

- [ ] Python 3.9+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖已安装
- [ ] .env文件已配置
- [ ] 数据库已初始化
- [ ] 至少1个数据源测试成功
- [ ] Web服务可以正常启动
- [ ] API接口可以正常访问
- [ ] Web界面可以正常显示
- [ ] 日志文件正常生成

## 🎉 成功标志

如果看到以下情况，说明项目运行成功：

1. ✅ `python run_scrape.py` 执行后，日志显示成功抓取新闻
2. ✅ 数据库文件 `ainews.db` 中有数据
3. ✅ 访问 http://localhost:8000/api/news/ 返回新闻列表
4. ✅ Web界面显示新闻卡片
5. ✅ 日志文件中有正常的INFO级别日志

## 📚 参考文档

- `README.md` - 项目概述
- `QUICKSTART.md` - 快速开始指南
- `IMPLEMENTATION.md` - 详细实现方案
- `DATA_SOURCES.md` - 数据源说明
- `PROJECT_SUMMARY.md` - 项目总结

## 💡 提示

1. **从小规模开始**: 先启用少量数据源，测试稳定后再添加更多
2. **关注日志**: 定期查看日志文件，及时发现问题
3. **定期备份**: 定期备份数据库文件
4. **监控性能**: 注意爬取频率，避免对目标网站造成压力
5. **遵守规则**: 遵守各网站的robots.txt和使用条款

祝使用愉快！如有问题，请查看日志文件或参考文档。

