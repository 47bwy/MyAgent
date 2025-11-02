#!/usr/bin/env python3
"""
Celery Worker 调试启动脚本
使用方式：ENABLE_REMOTE_DEBUG=1 DEBUG_PORT=5679 python worker_debug.py
"""
import os
import sys

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 启用远程调试
ENABLE_DEBUG = os.getenv("ENABLE_REMOTE_DEBUG", "0") == "1"
DEBUG_PORT = int(os.getenv("DEBUG_PORT", "5679"))

if ENABLE_DEBUG:
    try:
        import debugpy
        print(f"🔧 Celery Worker 远程调试已启用，监听端口 {DEBUG_PORT}...")
        debugpy.listen(("0.0.0.0", DEBUG_PORT))
        
        # 可选：等待调试器连接
        WAIT_FOR_CLIENT = os.getenv("DEBUG_WAIT_CLIENT", "0") == "1"
        if WAIT_FOR_CLIENT:
            print("⏳ 等待调试器连接...")
            debugpy.wait_for_client()
            print("✅ 调试器已连接！")
    except ImportError:
        print("⚠️  debugpy 未安装，跳过远程调试")
        print("   安装命令：pipenv install --dev debugpy")
        ENABLE_DEBUG = False

# 导入 Celery 应用
from worker.celery_app import celery_app

if __name__ == '__main__':
    print("🚀 启动 Celery Worker...")
    print(f"📂 项目路径: {project_root}")
    print(f"🔌 Redis: {os.getenv('broker_url', 'redis://localhost:6379/0')}")
    
    # 启动 Worker
    # 注意：必须使用 --pool=solo，多进程模式无法调试
    print("\n📋 Worker 配置:")
    print(f"   Broker: {celery_app.broker_connection().as_uri()}")
    print(f"   Backend: {celery_app.backend.as_uri()}")
    print(f"   默认队列: {celery_app.conf.task_default_queue}")
    print(f"   任务路由: {celery_app.conf.task_routes}")
    print(f"   监听队列: qa_queue")
    print()
    
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',  # 单进程模式，必须用于调试
        '-Q', 'qa_queue'  # 监听 qa_queue 队列
    ])

