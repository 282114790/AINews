# 安装指南 - 解决SSL问题

## 当前状态

✅ Python 3.14.2 已安装
✅ 虚拟环境已创建
⚠️ 依赖安装遇到SSL证书问题

## 解决方案

### 方案1: 使用国内镜像源（推荐）

```bash
# 激活虚拟环境
source venv/bin/activate

# 使用清华镜像源安装
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 或使用阿里云镜像
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

### 方案2: 升级pip和证书

```bash
source venv/bin/activate

# 升级pip
python -m pip install --upgrade pip

# 升级certifi
pip install --upgrade certifi

# 然后重新安装依赖
pip install -r requirements.txt
```

### 方案3: 临时禁用SSL验证（不推荐，仅用于测试）

```bash
source venv/bin/activate
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-verify-ssl -r requirements.txt
```

### 方案4: 手动安装核心依赖

如果上述方法都不行，可以手动安装核心包：

```bash
source venv/bin/activate

# 安装核心依赖
pip install fastapi uvicorn sqlalchemy requests beautifulsoup4 feedparser pyyaml loguru python-dotenv apscheduler

# 其他依赖可以后续按需安装
```

## 安装完成后的步骤

### 1. 验证安装

```bash
source venv/bin/activate
python -c "import fastapi; print('FastAPI安装成功')"
python -c "import sqlalchemy; print('SQLAlchemy安装成功')"
```

### 2. 初始化数据库

```bash
source venv/bin/activate
python src/main.py --init-db
```

### 3. 测试爬取（小规模）

先修改 `config.yaml`，只启用1-2个数据源：

```yaml
sources:
  rss:
    - name: "OpenAI Blog"
      url: "https://openai.com/blog/rss.xml"
      enabled: true
    - name: "TechCrunch AI"
      url: "https://techcrunch.com/tag/artificial-intelligence/feed/"
      enabled: false  # 先禁用其他源
```

然后运行：

```bash
source venv/bin/activate
python run_scrape.py
```

### 4. 启动Web服务

```bash
source venv/bin/activate
python src/main.py --reload
```

访问：
- Web界面: http://localhost:8000/static/index.html
- API文档: http://localhost:8000/docs

## 常见问题

### Q: 仍然无法安装依赖？
A: 检查网络连接，或尝试使用VPN/代理

### Q: 某些包版本不兼容？
A: 可以尝试不指定版本号，让pip自动选择兼容版本：
```bash
pip install fastapi uvicorn sqlalchemy  # 不指定版本
```

### Q: Python 3.14太新，某些包不支持？
A: 可以尝试使用Python 3.11或3.12：
```bash
python3.11 -m venv venv311
source venv311/bin/activate
pip install -r requirements.txt
```

## 下一步

安装完成后，请继续执行：
1. ✅ 创建.env文件（已完成）
2. ⬜ 安装依赖（进行中）
3. ⬜ 初始化数据库
4. ⬜ 测试运行
5. ⬜ 启动Web服务

