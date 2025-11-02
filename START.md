# 🚀 项目启动指南

## 📋 前置要求

- Python 3.8+
- pipenv (pip install pipenv)
- Redis (用于 Celery 消息队列)
- (可选) Docker & Docker Compose

---

## 🔧 方式一：本地开发启动（推荐用于调试）

### 1. 安装依赖

```bash
# 安装 pipenv（如果没有）
pip install pipenv

# 安装项目依赖
pipenv install

# 激活虚拟环境
pipenv shell
```

### 2. 配置环境变量

创建 `.env` 文件（参考 `.env.example`）：

```bash
cp .env.example .env
# 然后编辑 .env 文件，填入实际配置
```

### 3. 启动 Redis（必需）

```bash
# macOS
brew install redis
brew services start redis

# 或使用 Docker
docker run -d -p 6379:6379 redis:7
```

### 4. 启动 FastAPI 服务

```bash
# 基础启动（开发模式，自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 pipenv
pipenv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**访问：**
- API 文档：http://localhost:8000/docs
- 前端页面：http://localhost:8000

### 5. 启动 Celery Worker（在另一个终端）

```bash
# 激活虚拟环境
pipenv shell

# 启动 Celery Worker
celery -A worker.celery_app worker --loglevel=info -Q qa_queue
```

### 6. 启动 Flower（Celery 监控，可选）

```bash
pipenv shell
celery -A worker.celery_app flower --port=5555
```

访问：http://localhost:5555

---

## 🐳 方式二：Docker Compose 启动（生产/测试）

### 1. 配置环境变量

创建 `.env` 文件（确保所有配置正确）

### 2. 启动所有服务

```bash
# 构建并启动
docker-compose up --build

# 后台运行
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**服务访问：**
- FastAPI: http://localhost:8000
- Redis: localhost:6379
- Flower (如果添加): http://localhost:5555

---

## 🧪 运行测试

```bash
# 激活虚拟环境
pipenv shell

# 运行测试（如果有测试文件）
pytest

# 或运行特定测试文件
pytest tests/test_auth.py -v
```

---

## 📝 快速测试 API

### 1. 注册用户

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "confirm_password": "password123"
  }'
```

### 2. 登录

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 3. 提问（需要 token）

```bash
# 先登录获取 token
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}' \
  | jq -r '.access_token')

# 提交问题
curl -X POST "http://localhost:8000/qa/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question": "什么是人工智能？"}'
```

---

## 🐛 调试模式

**参考 `DEBUG.md` 查看详细的调试配置**

在 Cursor/VSCode 中：
1. 按 `F5` 启动调试
2. 或点击左侧调试面板，选择配置后启动

---

## ⚠️ 常见问题

### 1. Redis 连接失败

```bash
# 检查 Redis 是否运行
redis-cli ping
# 应该返回 PONG

# 如果没有运行，启动 Redis
redis-server
# 或使用 Docker
docker run -d -p 6379:6379 redis:7
```

### 2. 端口被占用

```bash
# 查看端口占用（macOS/Linux）
lsof -i :8000
kill -9 <PID>

# 或修改端口
uvicorn app.main:app --port 8001
```

### 3. 数据库初始化失败

```bash
# 删除旧数据库（SQLite）
rm test.db

# 重新启动服务，会自动创建数据库
```

### 4. Celery Worker 无法连接 Redis

检查 `.env` 中的 `broker_url` 和 `backend_url` 配置是否正确。

---

## 📚 更多信息

- API 文档：http://localhost:8000/docs
- 交互式 API 测试：http://localhost:8000/redoc
- Celery 监控（如果启动了 Flower）：http://localhost:5555

