#!/bin/bash
# Celery 连接和队列诊断脚本
# 在远程服务器上运行

echo "========================================="
echo "🔍 Celery Worker 诊断"
echo "========================================="
echo ""

echo "1️⃣  检查 Redis 连接："
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "   ✅ Redis 正在运行"
        REDIS_URL=$(grep broker_url .env 2>/dev/null | cut -d'=' -f2 || echo "redis://localhost:6379/0")
        echo "   Redis URL: $REDIS_URL"
    else
        echo "   ❌ Redis 未运行或无法连接"
        echo "   启动命令: redis-server 或 docker run -d -p 6379:6379 redis:7"
    fi
else
    echo "   ⚠️  redis-cli 未安装"
fi
echo ""

echo "2️⃣  检查 Celery Worker 进程："
WORKER_PROCESSES=$(ps aux | grep -E "celery.*worker" | grep -v grep)
if [ -n "$WORKER_PROCESSES" ]; then
    echo "   ✅ Worker 进程正在运行："
    echo "$WORKER_PROCESSES" | sed 's/^/   /'
    
    # 提取进程信息
    WORKER_PID=$(echo "$WORKER_PROCESSES" | awk '{print $2}' | head -1)
    echo "   Worker PID: $WORKER_PID"
    
    # 检查监听的队列
    if echo "$WORKER_PROCESSES" | grep -q "qa_queue"; then
        echo "   ✅ Worker 正在监听 qa_queue 队列"
    else
        echo "   ⚠️  Worker 可能未监听 qa_queue 队列"
    fi
else
    echo "   ❌ Worker 进程未运行"
    echo "   启动命令: celery -A worker.celery_app worker --loglevel=info -Q qa_queue"
fi
echo ""

echo "3️⃣  检查队列配置："
if [ -f "worker/celery_config.py" ]; then
    echo "   ✅ celery_config.py 存在"
    if grep -q "task_default_queue.*qa_queue" worker/celery_config.py; then
        echo "   ✅ 默认队列配置为 qa_queue"
    else
        echo "   ⚠️  默认队列可能未配置为 qa_queue"
    fi
    if grep -q "task_routes.*qa_queue" worker/celery_config.py; then
        echo "   ✅ 任务路由配置存在"
    else
        echo "   ⚠️  任务路由可能未配置"
    fi
else
    echo "   ❌ celery_config.py 不存在"
fi
echo ""

echo "4️⃣  检查 Redis 队列消息（如果 Redis 可访问）："
if command -v redis-cli &> /dev/null && redis-cli ping &> /dev/null; then
    echo "   默认队列 (celery) 消息数:"
    redis-cli LLEN celery 2>/dev/null || echo "   无法读取"
    
    echo "   自定义队列 (qa_queue) 消息数:"
    redis-cli LLEN qa_queue 2>/dev/null || echo "   无法读取"
    
    echo "   所有 Celery 相关键:"
    redis-cli KEYS "celery*" 2>/dev/null | head -10 || echo "   无"
else
    echo "   ⚠️  Redis 不可访问，跳过队列检查"
fi
echo ""

echo "5️⃣  检查环境变量："
if [ -f ".env" ]; then
    echo "   ✅ .env 文件存在"
    if grep -q "broker_url" .env; then
        echo "   ✅ broker_url 已配置"
    else
        echo "   ⚠️  broker_url 未配置"
    fi
    if grep -q "backend_url" .env; then
        echo "   ✅ backend_url 已配置"
    else
        echo "   ⚠️  backend_url 未配置"
    fi
else
    echo "   ❌ .env 文件不存在"
    echo "   运行: cp env.example .env"
fi
echo ""

echo "========================================="
echo "📋 快速修复命令："
echo "========================================="
echo ""
echo "如果队列配置不匹配，修复方法："
echo "1. 编辑 worker/celery_config.py"
echo "2. 取消注释并启用："
echo "   task_default_queue = 'qa_queue'"
echo "   task_routes = {'worker.tasks.answer_question_task': {'queue': 'qa_queue'}}"
echo ""
echo "3. 重启 Worker"
echo ""

