# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 16:49:58
@Author  :   47bwy
@Desc    :   配置加载
'''

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    broker_url: str = os.getenv("broker_url")
    backend_url: str = os.getenv("backend_url")
    local_model: str = os.getenv("local_model")
    database_url: str = os.getenv("database_url")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")

settings = Settings()