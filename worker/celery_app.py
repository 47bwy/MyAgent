# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 17:04:19
@Author  :   47bwy
@Desc    :   None
'''

from celery import Celery

from app.core.config import settings

# 创建 Celery 实例
celery_app = Celery("worker")
celery_app.config_from_object("worker.celery_config")
celery_app.autodiscover_tasks(["worker"])

