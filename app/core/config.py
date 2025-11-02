# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 16:49:58
@Author  :   47bwy
@Desc    :   配置加载
'''

import os

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Settings:
    # Celery 配置（带默认值）
    broker_url: str = os.getenv("broker_url", "redis://localhost:6379/0")
    backend_url: str = os.getenv("backend_url", "redis://localhost:6379/0")
    
    # 模型配置
    local_model: str = os.getenv("local_model", "./models/bert-base-chinese")
    
    # 数据库配置（带默认值）
    database_url: str = os.getenv("database_url", "sqlite:///./test.db")
    
    # JWT 配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

settings = Settings()