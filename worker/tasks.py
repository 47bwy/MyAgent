# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 16:54:09
@Author  :   47bwy
@Desc    :   Celery worker 执行任务
'''

import time

from app.core.logger import get_logger
from app.services.llm_services import process_question
from worker.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task
def answer_question_task(question: str, user_id: str) -> str:
    logger.info(f"celery app Received task for question: {question}")
    time.sleep(1)
    # 这里可以加载本地模型并推理
    return process_question(question, user_id)