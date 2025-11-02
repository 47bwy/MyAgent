#!/bin/bash
# 快速调试连接检查脚本
# 在远程服务器上运行此脚本来诊断问题

echo "========================================="
echo "🔍 远程调试连接诊断"
echo "========================================="
echo ""

echo "1️⃣  检查 debugpy 安装："
if pipenv list 2>/dev/null | grep -q debugpy; then
    echo "   ✅ debugpy 已安装 (pipenv)"
elif pip list 2>/dev/null | grep -q debugpy; then
    echo "   ✅ debugpy 已安装 (pip)"
else
    echo "   ❌ debugpy 未安装"
    echo "   运行: pipenv install --dev debugpy"
fi
echo ""

echo "2️⃣  检查 Python 进程："
PROCESSES=$(ps aux | grep -E "(uvicorn|start_with_debug|python.*app.main)" | grep -v grep)
if [ -n "$PROCESSES" ]; then
    echo "   ✅ 发现 Python 进程："
    echo "$PROCESSES" | sed 's/^/   /'
else
    echo "   ❌ 未发现 Python 进程"
    echo "   应用可能未启动"
fi
echo ""

echo "3️⃣  检查端口 5678 监听："
if command -v netstat &> /dev/null; then
    PORT_CHECK=$(netstat -tuln 2>/dev/null | grep 5678)
elif command -v ss &> /dev/null; then
    PORT_CHECK=$(ss -tuln 2>/dev/null | grep 5678)
elif command -v lsof &> /dev/null; then
    PORT_CHECK=$(lsof -i :5678 2>/dev/null)
else
    PORT_CHECK=""
fi

if [ -n "$PORT_CHECK" ]; then
    echo "   ✅ 端口 5678 正在监听："
    echo "$PORT_CHECK" | sed 's/^/   /'
else
    echo "   ❌ 端口 5678 未监听"
    echo "   debugpy 可能未启动"
    echo ""
    echo "   启动命令："
    echo "   export ENABLE_REMOTE_DEBUG=1"
    echo "   python start_with_debug.py"
fi
echo ""

echo "4️⃣  检查 .env 文件："
if [ -f .env ]; then
    echo "   ✅ .env 文件存在"
    if grep -q "database_url" .env; then
        echo "   ✅ database_url 已配置"
    else
        echo "   ⚠️  database_url 未配置"
    fi
else
    echo "   ❌ .env 文件不存在"
    echo "   运行: cp env.example .env"
fi
echo ""

echo "5️⃣  检查项目文件："
if [ -f "app/main.py" ]; then
    echo "   ✅ app/main.py 存在"
else
    echo "   ❌ app/main.py 不存在"
fi
if [ -f "start_with_debug.py" ]; then
    echo "   ✅ start_with_debug.py 存在"
else
    echo "   ⚠️  start_with_debug.py 不存在（可选）"
fi
echo ""

echo "6️⃣  检查当前工作目录："
echo "   $(pwd)"
echo ""

echo "========================================="
echo "📋 快速修复命令："
echo "========================================="
echo ""
echo "如果端口 5678 未监听，运行："
echo "  export ENABLE_REMOTE_DEBUG=1"
echo "  python start_with_debug.py"
echo ""
echo "或者直接："
echo "  python -c \"import debugpy; debugpy.listen(('0.0.0.0', 5678)); print('Debugpy started on 5678'); import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000)\""
echo ""

