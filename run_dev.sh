#!/bin/bash
# 快速启动开发环境脚本

echo "🚀 启动 MyAgent 开发环境..."

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ] && [ -z "$PIPENV_ACTIVE" ]; then
    echo "⚠️  建议先激活虚拟环境: pipenv shell"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查 Redis 是否运行
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis 未运行，尝试启动..."
    if command -v docker &> /dev/null; then
        echo "使用 Docker 启动 Redis..."
        docker run -d -p 6379:6379 --name myagent-redis redis:7 || echo "Redis 容器可能已存在"
    else
        echo "❌ 请先启动 Redis: redis-server 或使用 Docker"
        exit 1
    fi
fi

echo "✅ Redis 运行正常"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，从 env.example 复制..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ 已创建 .env 文件，请检查配置"
    else
        echo "⚠️  未找到 env.example 文件"
    fi
fi

echo ""
echo "选择启动方式:"
echo "1) 只启动 FastAPI 服务器"
echo "2) 只启动 Celery Worker"
echo "3) 启动 FastAPI + Celery Worker (两个终端)"
echo "4) 启动所有服务 (FastAPI + Celery + Flower)"

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "启动 FastAPI 服务器..."
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo "启动 Celery Worker..."
        celery -A worker.celery_app worker --loglevel=info -Q qa_queue
        ;;
    3)
        echo "请在两个终端中分别运行:"
        echo "终端1: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
        echo "终端2: celery -A worker.celery_app worker --loglevel=info -Q qa_queue"
        ;;
    4)
        echo "启动所有服务..."
        # 在后台启动 Celery
        celery -A worker.celery_app worker --loglevel=info -Q qa_queue &
        CELERY_PID=$!
        # 启动 Flower
        celery -A worker.celery_app flower --port=5555 &
        FLOWER_PID=$!
        # 启动 FastAPI
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        # 清理后台进程
        kill $CELERY_PID $FLOWER_PID 2>/dev/null
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

