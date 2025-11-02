# ⚡ 快速开始

## 🚀 5 分钟快速启动

### 1. 安装依赖

```bash
pipenv install
pipenv install --dev  # 安装开发依赖（包括 debugpy）
```

### 2. 配置环境变量

```bash
cp env.example .env
# 编辑 .env 文件（如果需要）
```

### 3. 启动 Redis

```bash
# macOS (使用 Homebrew)
brew services start redis

# 或使用 Docker
docker run -d -p 6379:6379 redis:7

# 验证 Redis 运行
redis-cli ping  # 应该返回 PONG
```

### 4. 启动服务

**方式 A：使用脚本（推荐）**
```bash
./run_dev.sh
```

**方式 B：手动启动**

终端 1 - FastAPI 服务器：
```bash
pipenv shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

终端 2 - Celery Worker：
```bash
pipenv shell
celery -A worker.celery_app worker --loglevel=info -Q qa_queue
```

### 5. 访问服务

- 🌐 Web 界面：http://localhost:8000
- 📚 API 文档：http://localhost:8000/docs
- 📖 交互式 API：http://localhost:8000/redoc

---

## 🐛 在 Cursor 中调试

1. **安装 debugpy**（如果还没安装）
   ```bash
   pipenv install --dev debugpy
   ```

2. **设置断点**
   - 在代码行号左侧点击，添加断点（红点）

3. **启动调试**
   - 按 `F5` 或点击左侧调试图标
   - 选择 "Python: FastAPI"
   - 点击绿色运行按钮

4. **测试断点**
   - 访问 http://localhost:8000
   - 或发送 API 请求
   - 调试器会在断点处暂停

详细调试指南：查看 `DEBUG.md`

---

## 🧪 运行测试

```bash
pipenv shell
pytest tests/ -v
```

或运行特定测试：
```bash
pytest tests/test_auth.py -v
pytest tests/test_pydantic_validation.py -v
```

---

## 📝 快速测试 API

### 注册用户
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

### 登录
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 提问（需要先登录获取 token）
```bash
# 1. 登录获取 token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. 提交问题
curl -X POST "http://localhost:8000/qa/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question": "什么是人工智能？"}'
```

---

## ⚠️ 常见问题

**Q: Redis 连接失败？**  
A: 确保 Redis 正在运行：`redis-cli ping`

**Q: 端口被占用？**  
A: 修改端口：`uvicorn app.main:app --port 8001`

**Q: 模块导入错误？**  
A: 确保在项目根目录运行，并使用 `pipenv shell`

---

## 📚 更多文档

- 详细启动指南：`START.md`
- 调试指南：`DEBUG.md`
- 项目 README：`README.md`

