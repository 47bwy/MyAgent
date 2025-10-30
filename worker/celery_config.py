# -*- encoding: utf-8 -*-
'''
@Time    :   2025/09/11 21:41:39
@Author  :   47bwy
@Desc    :   None
'''

from app.core.config import settings

broker_url = settings.broker_url
result_backend = settings.backend_url

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Shanghai'
enable_utc = True

task_acks_late = True
worker_prefetch_multiplier = 1
task_reject_on_worker_lost = True

# task_default_queue = 'qa_queue'
# task_routes = {'worker.tasks.answer_question_task': {'queue': 'qa_queue'}}

# 可选：生产环境建议开启
worker_max_tasks_per_child = 100
worker_max_memory_per_child = 120000  # 单位KB