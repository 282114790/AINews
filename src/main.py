"""
AI News 主程序
"""
import argparse
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from src.database import init_db
from src.api import api_router
from src.scheduler import setup_scheduler
from src.utils.logger import get_logger, setup_logger

# 初始化日志
setup_logger()
logger = get_logger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AI News API",
    description="AI新闻聚合工具API",
    version="0.1.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api")

# 静态文件（用于前端）
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("AI News 应用启动中...")
    
    # 初始化数据库
    init_db()
    logger.info("数据库初始化完成")
    
    # 启动定时任务调度器
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("定时任务调度器已启动")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("AI News 应用关闭中...")


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "AI News API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI News 应用")
    parser.add_argument("--init-db", action="store_true", help="初始化数据库")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="主机地址")
    parser.add_argument("--port", type=int, default=8000, help="端口号")
    parser.add_argument("--reload", action="store_true", help="自动重载（开发模式）")
    
    args = parser.parse_args()
    
    if args.init_db:
        init_db()
        logger.info("数据库初始化完成")
        return
    
    # 运行服务器
    uvicorn.run(
        "src.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()

