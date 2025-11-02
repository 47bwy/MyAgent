# 🚀 远程服务器快速设置

## ⚠️ 当前错误修复

### 错误信息
```
sqlalchemy.exc.ArgumentError: Expected string or URL object, got None
```

**原因**：`.env` 文件不存在或未正确加载

### 解决步骤

#### 1. SSH 到远程服务器
```bash
ssh root@192.168.189.246 -p 20022
```

#### 2. 进入项目目录
```bash
cd /root/MyAgent
```

#### 3. 创建 `.env` 文件
```bash
# 如果 env.example 存在
cp env.example .env

# 或手动创建
cat > .env << 'EOF'
# Celery 配置
broker_url=redis://localhost:6379/0
backend_url=redis://localhost:6379/0

# 本地模型路径
local_model=./models/bert-base-chinese

# 数据库配置
database_url=sqlite:///./test.db

# JWT 配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256

# PyTorch/CUDA 配置
CUDA_VISIBLE_DEVICES=
EOF
```

#### 4. 验证配置
```bash
# 检查文件
cat .env

# 测试 Python 能否读取
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('DATABASE_URL:', os.getenv('database_url'))"
```

#### 5. 重新启动应用
```bash
# 如果使用 systemd 或 supervisor
sudo systemctl restart myagent
# 或
supervisorctl restart myagent

# 如果手动运行
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📋 远程服务器完整设置清单

### 必需配置

- [ ] Python 3.8+ 已安装
- [ ] pipenv 已安装
- [ ] `.env` 文件已创建并配置
- [ ] Redis 已安装并运行
- [ ] 项目依赖已安装（`pipenv install`）

### 验证命令

```bash
# 1. 检查 Python
python3 --version

# 2. 检查 pipenv
pipenv --version

# 3. 检查 Redis
redis-cli ping  # 应该返回 PONG

# 4. 检查 .env
ls -la .env
cat .env | grep database_url

# 5. 检查依赖
pipenv install
```

---

## 🔧 启动应用（远程服务器）

### 方式 1：普通启动
```bash
cd /root/MyAgent
pipenv shell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 方式 2：使用调试脚本
```bash
cd /root/MyAgent
export ENABLE_REMOTE_DEBUG=1
python start_with_debug.py
```

### 方式 3：后台运行（使用 nohup）
```bash
cd /root/MyAgent
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

### 方式 4：使用 systemd（生产环境推荐）

创建 `/etc/systemd/system/myagent.service`：

```ini
[Unit]
Description=MyAgent FastAPI Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/MyAgent
Environment="PATH=/root/.local/share/virtualenvs/MyAgent-xxx/bin"
ExecStart=/root/.local/share/virtualenvs/MyAgent-xxx/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable myagent
sudo systemctl start myagent
sudo systemctl status myagent
```

---

## 🐛 远程调试设置

详细步骤请查看 `REMOTE_DEBUG.md`

### 快速开始

1. **在远程服务器上安装 debugpy**
```bash
pipenv install --dev debugpy
```

2. **启动应用（带调试）**
```bash
export ENABLE_REMOTE_DEBUG=1
python start_with_debug.py
```

3. **在本地建立 SSH 隧道**
```bash
ssh -f -N -L 5678:localhost:5678 root@192.168.189.246 -p 20022
```

4. **在 Cursor 中连接调试器**
   - 按 `F5`
   - 选择 "Python: Remote Attach (SSH Tunnel)"

---

## 🔍 故障排除

### 1. 检查日志
```bash
# 查看应用日志
tail -f app.log

# 查看系统日志
journalctl -u myagent -f  # 如果使用 systemd
```

### 2. 检查端口
```bash
# 检查端口是否在监听
netstat -tuln | grep 8000
ss -tuln | grep 8000
```

### 3. 检查进程
```bash
# 查看 Python 进程
ps aux | grep uvicorn
ps aux | grep python
```

### 4. 测试连接
```bash
# 从本地测试远程 API
curl http://192.168.189.246:8000/docs
```

---

## 📝 环境变量说明

确保 `.env` 文件包含：

```bash
# 数据库（必需）
database_url=sqlite:///./test.db

# Redis（必需，如果使用 Celery）
broker_url=redis://localhost:6379/0
backend_url=redis://localhost:6379/0

# JWT（必需）
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# 模型（可选）
local_model=./models/bert-base-chinese

# CUDA（可选）
CUDA_VISIBLE_DEVICES=
```

---

## 🎯 快速命令参考

```bash
# SSH 连接
ssh root@192.168.189.246 -p 20022

# 进入项目
cd /root/MyAgent

# 检查环境
cat .env
python3 -c "from app.core.config import settings; print(settings.database_url)"

# 启动应用
python start_with_debug.py

# 查看日志
tail -f app.log

# 重启应用
pkill -f uvicorn
python start_with_debug.py
```

