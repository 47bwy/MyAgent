# 🔧 Celery Worker 调试指南

## 🎯 问题：为什么 `get_answer()` 断点捕获不到？

### 原因

**`get_answer()` 在 Celery Worker 进程中执行，不在 FastAPI 进程中！**

### 执行流程

```
┌─────────────────────┐
│  FastAPI 进程       │  ← 你当前调试的进程（端口 5678）
│  (uvicorn)          │
├─────────────────────┤
│  1. /qa/ask 请求    │
│  2. ask_question()  │
│  3. task.delay()    │ ← 只发送任务到 Redis，不执行！
└─────────────────────┘
         ↓
    [Redis 队列]
         ↓
┌─────────────────────┐
│  Celery Worker      │  ← get_answer() 在这里执行！
│  (独立进程)          │  ← 需要在另一个调试会话中连接（端口 5679）
├─────────────────────┤
│  1. 接收任务        │
│  2. answer_question │
│  3. process_question│
│  4. get_answer()    │ ← 断点应该在这里设置
└─────────────────────┘
```

---

## ✅ 解决方案：调试 Celery Worker

### 步骤 1：在远程服务器上启动 Worker（带调试）

```bash
# SSH 到远程服务器
ssh root@192.168.189.246 -p 20022
cd /root/MyAgent

# 确保 debugpy 已安装
pipenv install --dev debugpy

# 启动 Worker（带调试）
export ENABLE_REMOTE_DEBUG=1
export DEBUG_PORT=5679  # 使用不同端口，避免和 FastAPI 冲突
python worker_debug.py
```

**预期输出：**
```
🔧 Celery Worker 远程调试已启用，监听端口 5679...
🚀 启动 Celery Worker...
[tasks]
  . worker.tasks.answer_question_task
```

### 步骤 2：在本地建立 SSH 隧道

**在本地（新终端）运行：**

```bash
# 建立 Worker 调试端口转发
ssh -f -N -L 5679:localhost:5679 root@192.168.189.246 -p 20022

# 验证连接
nc -zv localhost 5679
```

### 步骤 3：在 Cursor 中连接 Worker 调试器

1. **设置断点**：
   - 在 `app/services/llm_services.py` 的 `get_answer()` 函数中设置断点
   - 在 `worker/tasks.py` 的 `answer_question_task()` 函数中设置断点

2. **启动调试**：
   - 按 `F5`
   - 选择 **"Python: Celery Worker Remote (SSH Tunnel)"**
   - 应该会连接到 Worker 进程

3. **触发任务**：
   - 发送请求到 `/qa/ask`（可以通过 FastAPI 接口或 curl）
   - 断点会在 Worker 进程中触发！

---

## 📊 完整调试流程

### 同时调试两个进程（分步进行）

#### 阶段 1：调试 FastAPI（了解请求流程）

1. 连接调试器到 FastAPI（端口 5678）
2. 在 `app/routers/qa.py:ask_question()` 设置断点
3. 发送请求，查看：
   - 请求参数
   - 任务如何提交到 Redis
   - 返回的 task_id

#### 阶段 2：调试 Worker（了解任务执行）

1. **断开 FastAPI 调试器**
2. 连接调试器到 Worker（端口 5679）
3. 在以下位置设置断点：
   - `worker/tasks.py:answer_question_task()`
   - `app/services/llm_services.py:process_question()`
   - `app/services/llm_services.py:get_answer()` ← **这里！**
4. **发送请求**（或使用之前的 task_id 轮询）
5. 断点会在 Worker 进程中触发！

---

## 🔍 验证 Worker 调试是否生效

### 测试步骤：

1. **在远程服务器上**：确认 Worker 正在运行并监听调试端口
   ```bash
   # 检查端口
   netstat -tuln | grep 5679
   # 应该看到：tcp 0 0.0.0.0:5679 0.0.0.0:* LISTEN
   ```

2. **在本地**：验证 SSH 隧道
   ```bash
   ps aux | grep "5679:localhost:5679"
   nc -zv localhost 5679
   ```

3. **在 Cursor 中**：
   - 连接 Worker 调试器
   - 设置断点在 `get_answer()` 函数开头
   - 发送 `/qa/ask` 请求
   - 应该会暂停在断点处！

---

## 🎯 关键要点

### 1. 两个独立的进程

```
FastAPI 进程（端口 5678）
  ↓ 提交任务
Redis
  ↓ 分发任务
Worker 进程（端口 5679）
  ↓ 执行任务
get_answer() 在这里运行！
```

### 2. 必须使用 `--pool=solo`

Celery Worker 默认使用多进程模式（prefork），无法调试。
必须使用 `--pool=solo`（单进程模式）。

**在 `worker_debug.py` 中已配置：**
```python
celery_app.worker_main([
    'worker',
    '--pool=solo',  # ← 必须！
    ...
])
```

### 3. 使用不同的调试端口

- FastAPI: 5678
- Worker: 5679

避免端口冲突。

---

## 🛠️ 故障排除

### Q: Worker 调试器连接失败？

**检查：**
1. Worker 是否在运行？`ps aux | grep worker_debug`
2. 端口是否监听？`netstat -tuln | grep 5679`
3. SSH 隧道是否建立？`ps aux | grep "5679"`

### Q: 断点设置但没触发？

**可能原因：**
1. 调试器连接到了错误的进程（连接到了 FastAPI 而不是 Worker）
2. 任务没有实际执行（检查 Worker 日志）
3. 代码路径不同（检查是否真的调用了 `get_answer()`）

### Q: 如何确认任务在执行？

**查看 Worker 日志：**
```bash
# 在远程服务器上，Worker 启动时会输出日志
# 当任务执行时，你会看到：
# [INFO] Task worker.tasks.answer_question_task[...] received
# [INFO] Task worker.tasks.answer_question_task[...] succeeded
```

---

## 📝 快速命令参考

### 启动 Worker（调试模式）

```bash
# 远程服务器
cd /root/MyAgent
export ENABLE_REMOTE_DEBUG=1
export DEBUG_PORT=5679
python worker_debug.py
```

### 建立 SSH 隧道

```bash
# 本地
ssh -f -N -L 5679:localhost:5679 root@192.168.189.246 -p 20022
```

### 测试连接

```bash
# 本地
nc -zv localhost 5679
```

### 触发任务

```bash
# 通过 API
curl -X POST http://192.168.189.246:8000/qa/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question": "测试问题"}'
```

---

## 🎉 总结

1. **`get_answer()` 在 Worker 进程中执行**，不在 FastAPI 进程中
2. **需要单独调试 Worker 进程**（使用端口 5679）
3. **使用 `worker_debug.py` 启动 Worker**（带调试支持）
4. **必须使用 `--pool=solo`**（单进程模式才能调试）
5. **设置断点在 Worker 进程中**，然后触发任务

现在你可以调试 `get_answer()` 函数了！🎯

