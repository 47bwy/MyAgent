# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/14 18:35:25
@Author  :   47bwy
@Desc    :   None
'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DATABASE_URL = settings.database_url  # SQLite 数据库路径

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 创建 Session 类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 定义基础类
Base = declarative_base()

# 初始化数据库（创建表）
def init_db():
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("Database initialized and tables created.")

# 获取数据库会话的函数
def get_db():
    db = SessionLocal()  # 创建会话
    try:
        yield db
    finally:
        db.close()  # 结束会话时关闭连接

# def get_session():
#     with Session(engine) as session:
#         yield session