# 🌐 远程调试指南

## ⚠️ 首先解决当前错误

从错误信息看，`DATABASE_URL` 是 `None`，说明 `.env` 文件没有正确加载。

### 在远程服务器上：

1. **创建 `.env` 文件**
```bash
# SSH 到远程服务器
ssh root@192.168.189.246 -p 20022

# 进入项目目录
cd /root/MyAgent

# 创建 .env 文件（从 env.example 复制）
cp env.example .env

# 编辑 .env 文件，确保所有配置正确
nano .env
```

2. **确认 `.env` 文件内容**
```bash
# 检查文件是否存在
ls -la .env

# 查看文件内容（确认 database_url 已设置）
cat .env | grep database_url
```

3. **验证环境变量加载**
```bash
# 测试 Python 是否能读取环境变量
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('DATABASE_URL:', os.getenv('database_url'))"
```

---

## 🔧 远程调试配置

远程调试有两种方式：

### 方式 1：SSH 端口转发（推荐，更安全）

这种方法通过 SSH 隧道连接调试器，不需要开放额外端口。

#### 步骤 1：在远程服务器上安装 debugpy

```bash
# SSH 到远程服务器
ssh root@192.168.189.246 -p 20022

# 进入项目目录
cd /root/MyAgent

# 安装 debugpy
pipenv install --dev debugpy
# 或
pip install debugpy
```

#### 步骤 2：修改远程服务器代码，添加调试监听

创建一个启动脚本或在代码中添加调试监听：

**选项 A：创建调试启动脚本（推荐）**

在远程服务器上创建 `start_with_debug.py`：

```python
# start_with_debug.py
import debugpy

# 监听所有接口（0.0.0.0），端口 5678
debugpy.listen(('0.0.0.0', 5678))
print("等待调试器连接... (端口 5678)")

# 可选：等待调试器连接（阻塞模式）
# debugpy.wait_for_client()
# print("调试器已连接！")

# 启动应用
import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
```

**选项 B：在代码中直接添加（开发时）**

在 `app/main.py` 开头添加：

```python
# 只在开发模式下启用远程调试
import os
if os.getenv("ENABLE_REMOTE_DEBUG") == "1":
    import debugpy
    debugpy.listen(('0.0.0.0', 5678))
    print("远程调试已启用，等待连接...")
```

#### 步骤 3：在远程服务器上启动应用（带调试）

```bash
# SSH 到远程服务器
ssh root@192.168.189.246 -p 20022

cd /root/MyAgent

# 设置环境变量启用调试
export ENABLE_REMOTE_DEBUG=1
export PYTHONPATH=/root/MyAgent

# 启动应用（使用调试脚本）
python start_with_debug.py

# 或直接运行
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 步骤 4：在本地配置 SSH 端口转发

在**本地**（你的电脑）打开终端：

```bash
# 建立 SSH 端口转发（后台运行）
ssh -N -L 5678:localhost:5678 root@192.168.189.246 -p 20022

# 或者使用 -f 参数让它在后台运行
ssh -f -N -L 5678:localhost:5678 root@192.168.189.246 -p 20022
```

**说明**：
- `-N`：不执行远程命令，只做端口转发
- `-L 5678:localhost:5678`：本地 5678 端口 → 远程 5678 端口
- `-f`：后台运行

#### 步骤 5：在本地 Cursor/VSCode 中连接

1. **更新 `.vscode/launch.json`**（添加远程调试配置）：

```json
{
    "name": "Python: Remote Attach",
    "type": "debugpy",
    "request": "attach",
    "connect": {
        "host": "localhost",  // 通过 SSH 隧道连接
        "port": 5678
    },
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}",
            "remoteRoot": "/root/MyAgent"  // 远程服务器上的项目路径
        }
    ],
    "justMyCode": false
}
```

2. **启动调试**：
   - 按 `F5`
   - 选择 "Python: Remote Attach"
   - 应该会连接到远程服务器

---

### 方式 2：直接连接（需要防火墙配置）

如果你的服务器防火墙开放了端口，可以直接连接。

#### 步骤 1：配置防火墙（如果需要）

```bash
# 在远程服务器上
# Ubuntu/Debian
sudo ufw allow 5678/tcp

# CentOS/RHEL
sudo firewall-cmd --add-port=5678/tcp --permanent
sudo firewall-cmd --reload
```

#### 步骤 2：在本地配置连接

更新 `.vscode/launch.json`：

```json
{
    "name": "Python: Remote Direct",
    "type": "debugpy",
    "request": "attach",
    "connect": {
        "host": "192.168.189.246",  // 远程服务器 IP
        "port": 5678
    },
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}",
            "remoteRoot": "/root/MyAgent"
        }
    ],
    "justMyCode": false
}
```

---

## 🔍 调试步骤总结

### 完整流程：

1. **SSH 到远程服务器**
   ```bash
   ssh root@192.168.189.246 -p 20022
   cd /root/MyAgent
   ```

2. **确保 .env 文件存在且正确**
   ```bash
   cat .env  # 查看配置
   ```

3. **安装 debugpy（如果还没安装）**
   ```bash
   pipenv install --dev debugpy
   ```

4. **启动应用（带调试监听）**
   ```bash
   # 方法1：使用调试脚本
   python start_with_debug.py
   
   # 方法2：设置环境变量
   export ENABLE_REMOTE_DEBUG=1
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

5. **在本地建立 SSH 隧道（新终端）**
   ```bash
   ssh -f -N -L 5678:localhost:5678 root@192.168.189.246 -p 20022
   ```

6. **在 Cursor 中连接调试器**
   - 设置断点
   - 按 `F5`，选择 "Python: Remote Attach"
   - 开始调试！

---

## 🛠️ 创建调试启动脚本

在远程服务器上创建 `start_with_debug.py`：

```python
#!/usr/bin/env python3
"""
远程调试启动脚本
使用方式：python start_with_debug.py
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 启用远程调试
import debugpy
DEBUG_PORT = int(os.getenv("DEBUG_PORT", "5678"))

print(f"🔧 启用远程调试，监听端口 {DEBUG_PORT}...")
debugpy.listen(("0.0.0.0", DEBUG_PORT))

# 可选：等待调试器连接（取消注释以启用）
# print("⏳ 等待调试器连接...")
# debugpy.wait_for_client()
# print("✅ 调试器已连接！")

# 导入并运行应用
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动 FastAPI 应用...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 远程调试时建议关闭 reload
        log_level="info"
    )
```

使脚本可执行：
```bash
chmod +x start_with_debug.py
```

---

## 📝 更新 launch.json

我已经更新了 `.vscode/launch.json`，添加了远程调试配置。

---

## ⚠️ 常见问题

### 1. **连接被拒绝**

**问题**：`Connection refused` 或无法连接

**解决**：
- 确认远程服务器上 debugpy 正在监听
- 确认 SSH 端口转发已建立：`ps aux | grep "5678:localhost:5678"`
- 检查防火墙设置

### 2. **断点不生效**

**问题**：断点设置了但不暂停

**解决**：
- 确认 `pathMappings` 配置正确
- 确认本地和远程代码路径匹配
- 使用绝对路径而不是相对路径

### 3. **环境变量问题**

**问题**：`DATABASE_URL is None`

**解决**：
```bash
# 在远程服务器上
cd /root/MyAgent
cat .env  # 检查文件是否存在
ls -la .env  # 检查权限
```

### 4. **端口被占用**

**问题**：端口 5678 已被使用

**解决**：
```bash
# 查看端口占用
netstat -tuln | grep 5678
# 或使用其他端口
export DEBUG_PORT=5679
```

---

## 🔒 安全建议

1. **使用 SSH 端口转发**：避免直接在防火墙开放调试端口
2. **生产环境关闭调试**：只在开发/测试时启用
3. **使用强密码**：SSH 连接使用密钥认证
4. **限制访问 IP**：如果必须开放端口，限制访问来源

---

## 📚 相关资源

- [debugpy 远程调试文档](https://github.com/microsoft/debugpy#debugpy)
- [VSCode 远程调试指南](https://code.visualstudio.com/docs/python/debugging#remote-debugging)
- [SSH 端口转发](https://www.ssh.com/academy/ssh/tunneling/example)

