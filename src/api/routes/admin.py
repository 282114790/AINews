"""
管理API路由（手动触发爬取等）
"""
import threading
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database import get_db, SessionLocal
from src.scheduler.tasks import ScrapeTask
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# 全局状态跟踪
scrape_state = {
    "status": "idle",  # idle, running, completed, failed
    "last_run": None,
    "last_result": None,
    "saved_count": 0,
    "error": None
}
scrape_lock = threading.Lock()


class ScrapeResponse(BaseModel):
    """爬取响应模型"""
    success: bool
    message: str
    scraped_count: int = 0
    saved_count: int = 0


class ScrapeStatusResponse(BaseModel):
    """爬取状态响应模型"""
    status: str
    last_run: str = None
    saved_count: int = 0
    error: str = None


def run_scrape_task():
    """在后台运行爬取任务"""
    global scrape_state
    
    try:
        # 获取新的数据库会话
        db = SessionLocal()
        
        try:
            from src.models.news import News
            before_count = db.query(News).count()
            
            # 执行爬取
            task = ScrapeTask()
            task.scrape_all()
            
            # 重新查询数量
            after_count = db.query(News).count()
            saved_count = max(0, after_count - before_count)
            
            with scrape_lock:
                scrape_state["status"] = "completed"
                scrape_state["saved_count"] = saved_count
                scrape_state["error"] = None
            
            logger.info(f"后台爬取任务完成，新增 {saved_count} 条新闻")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"后台爬取任务失败: {e}")
        with scrape_lock:
            scrape_state["status"] = "failed"
            scrape_state["error"] = str(e)


@router.post("/scrape/trigger")
def trigger_scrape(background_tasks: BackgroundTasks):
    """
    手动触发爬取任务（后台异步执行）
    
    立即返回，任务在后台执行。使用 /scrape/status 查询进度。
    """
    global scrape_state
    
    with scrape_lock:
        if scrape_state["status"] == "running":
            return {
                "success": False,
                "message": "爬取任务正在运行中，请稍后查看状态",
                "saved_count": 0
            }
        
        scrape_state["status"] = "running"
        scrape_state["last_run"] = datetime.now().isoformat()
        scrape_state["saved_count"] = 0
        scrape_state["error"] = None
    
    # 在后台执行爬取任务
    background_tasks.add_task(run_scrape_task)
    
    return {
        "success": True,
        "message": "爬取任务已启动，请稍后查看状态（约1-2分钟）",
        "saved_count": 0
    }


@router.get("/scrape/status")
def get_scrape_status():
    """
    获取爬取任务状态
    """
    with scrape_lock:
        return {
            "status": scrape_state["status"],
            "last_run": scrape_state["last_run"],
            "saved_count": scrape_state["saved_count"],
            "error": scrape_state["error"],
            "next_run": "09:00"
        }

