#!/usr/bin/env python3
"""
远程调试启动脚本
使用方式：python start_with_debug.py
或：ENABLE_REMOTE_DEBUG=1 python start_with_debug.py
"""
import os
import sys

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 启用远程调试（可选）
ENABLE_DEBUG = os.getenv("ENABLE_REMOTE_DEBUG", "0") == "1"
DEBUG_PORT = int(os.getenv("DEBUG_PORT", "5678"))

if ENABLE_DEBUG:
    try:
        import debugpy
        print(f"🔧 启用远程调试，监听端口 {DEBUG_PORT}...")
        debugpy.listen(("0.0.0.0", DEBUG_PORT))
        
        # 可选：等待调试器连接（取消注释以启用）
        WAIT_FOR_CLIENT = os.getenv("DEBUG_WAIT_CLIENT", "0") == "1"
        if WAIT_FOR_CLIENT:
            print("⏳ 等待调试器连接...")
            debugpy.wait_for_client()
            print("✅ 调试器已连接！")
    except ImportError:
        print("⚠️  debugpy 未安装，跳过远程调试")
        print("   安装命令：pipenv install --dev debugpy")
elif os.getenv("REMOTE_DEBUG") == "1":
    # 兼容旧的环境变量名
    try:
        import debugpy
        print(f"🔧 启用远程调试（兼容模式），监听端口 {DEBUG_PORT}...")
        debugpy.listen(("0.0.0.0", DEBUG_PORT))
    except ImportError:
        print("⚠️  debugpy 未安装")

# 导入并运行应用
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动 FastAPI 应用...")
    print(f"📂 项目路径: {project_root}")
    print(f"🌐 访问地址: http://0.0.0.0:8000")
    print(f"📚 API 文档: http://0.0.0.0:8000/docs")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 远程调试时建议关闭 reload
        log_level="info"
    )

