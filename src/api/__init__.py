from fastapi import APIRouter

api_router = APIRouter()

from .routes import news, stats, admin

api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

