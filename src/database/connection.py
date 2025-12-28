"""
数据库连接和初始化
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

load_dotenv()

# 数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ainews.db")

# 创建引擎
if DATABASE_URL.startswith("sqlite"):
    # SQLite需要特殊配置
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 导入Base（需要在导入模型后）
from src.models.news import Base


def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建表）"""
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成！")


if __name__ == "__main__":
    init_db()

