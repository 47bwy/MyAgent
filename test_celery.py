#!/usr/bin/env python3
"""
测试 Celery 任务发送和接收
运行方式：python test_celery.py
"""
import sys
import time

# 添加项目路径
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from worker.tasks import answer_question_task
from worker.celery_app import celery_app

def test_task_send():
    """测试任务发送"""
    print("=" * 50)
    print("🧪 测试 Celery 任务发送")
    print("=" * 50)
    
    # 1. 检查 Redis 连接
    print("\n1️⃣ 检查 Redis 连接...")
    try:
        from app.core.config import settings
        import redis
        r = redis.from_url(settings.broker_url)
        r.ping()
        print(f"   ✅ Redis 连接成功: {settings.broker_url}")
    except Exception as e:
        print(f"   ❌ Redis 连接失败: {e}")
        return False
    
    # 2. 检查 Celery 配置
    print("\n2️⃣ 检查 Celery 配置...")
    print(f"   Broker: {celery_app.broker_connection().as_uri()}")
    print(f"   Backend: {celery_app.backend.as_uri()}")
    print(f"   Tasks: {list(celery_app.tasks.keys())}")
    
    # 3. 检查队列配置
    print("\n3️⃣ 检查任务路由...")
    routes = celery_app.conf.task_routes or {}
    default_queue = celery_app.conf.task_default_queue or 'celery'
    print(f"   默认队列: {default_queue}")
    print(f"   任务路由: {routes}")
    
    # 4. 发送测试任务
    print("\n4️⃣ 发送测试任务...")
    try:
        task = answer_question_task.delay("测试问题", "testuser")
        print(f"   ✅ 任务已发送")
        print(f"   任务 ID: {task.id}")
        print(f"   任务状态: {task.state}")
        
        # 5. 等待任务完成（最多 30 秒）
        print("\n5️⃣ 等待任务执行...")
        try:
            result = task.get(timeout=30)
            print(f"   ✅ 任务执行成功")
            print(f"   结果: {result}")
            return True
        except Exception as e:
            print(f"   ⚠️ 任务未在 30 秒内完成: {e}")
            print(f"   当前状态: {task.state}")
            print(f"   提示: 检查 Worker 是否正在运行")
            return False
            
    except Exception as e:
        print(f"   ❌ 发送任务失败: {e}")
        return False

if __name__ == "__main__":
    success = test_task_send()
    sys.exit(0 if success else 1)

