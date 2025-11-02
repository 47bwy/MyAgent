# 🔍 Celery 任务调试指南

## ❌ 问题：页面提交任务但 Worker 没有日志

测试脚本成功，说明 Celery 配置正确，但通过页面提交时 Worker 没有收到任务。

---

## 🔍 可能的原因

### 1. **任务没有实际发送**

虽然 API 返回了 `task_id`，但任务可能没有真正发送到队列。

### 2. **FastAPI 和 Worker 使用不同的 Celery 实例**

可能 FastAPI 和 Worker 使用了不同的 Redis 连接或配置。

### 3. **任务路由配置不匹配**

虽然已配置，但可能存在缓存或配置未生效。

### 4. **异常被静默处理**

可能有异常但没有日志输出。

---

## ✅ 调试步骤

### 步骤 1：添加详细日志

我已经在 `app/routers/qa.py` 中添加了日志，现在可以看到：
- 请求是否到达路由
- 任务是否成功提交
- 是否有异常

### 步骤 2：检查 FastAPI 日志

在远程服务器上查看 FastAPI 日志：

```bash
# 如果使用 uvicorn 直接运行
# 日志会输出到控制台

# 如果使用 systemd，查看日志
journalctl -u myagent -f

# 或查看日志文件
tail -f app.log
```

**你应该看到：**
```
INFO: 收到问题提交请求，用户: guest, 问题: 你的问题
INFO: 提交 Celery 任务，问题: 你的问题, 用户: guest
INFO: 任务已提交，task_id: xxx
```

### 步骤 3：验证任务是否发送到 Redis

```bash
# 在远程服务器上
redis-cli

# 查看队列中的消息
> LLEN qa_queue
> LRANGE qa_queue 0 -1

# 查看 Celery 相关键
> KEYS celery*
```

### 步骤 4：检查 Worker 日志

确保 Worker 正在运行并监听正确的队列：

```bash
# 查看 Worker 进程
ps aux | grep celery

# 查看 Worker 输出（如果在前台运行）
# 应该看到：
# [tasks]
#   . worker.tasks.answer_question_task
```

### 步骤 5：测试任务发送

**在远程服务器上运行：**
```bash
cd /root/MyAgent
python test_celery.py
```

如果测试成功但页面不工作，问题可能在于：
- 前端请求格式
- API 路由处理
- 认证/授权问题

---

## 🛠️ 快速排查

### 检查 1：前端请求是否正确

在浏览器开发者工具（F12）中：
1. 打开 Network 标签
2. 提交问题
3. 查看 `/qa/ask` 请求：
   - 请求方法：POST
   - 请求体：`{"question": "你的问题"}`
   - 响应：`{"task_id": "xxx"}`

### 检查 2：FastAPI 是否收到请求

查看 FastAPI 日志，应该看到：
```
INFO: 收到问题提交请求...
```

如果没有，说明请求没有到达路由。

### 检查 3：任务是否发送

查看 FastAPI 日志：
```
INFO: 任务已提交，task_id: xxx
```

如果没有，说明任务提交失败。

### 检查 4：Worker 是否接收

查看 Worker 日志，应该看到：
```
[INFO] Task worker.tasks.answer_question_task[...] received
```

如果没有，说明 Worker 没有接收到任务。

---

## 🔧 常见问题

### Q: 任务 ID 返回了，但 Worker 没有日志？

**A:** 可能的原因：
1. 任务发送到了错误的队列
2. Worker 没有监听正确的队列
3. Redis 连接问题

**检查：**
```bash
# 检查 Redis 队列
redis-cli LLEN qa_queue
redis-cli LLEN celery  # 默认队列

# 如果 qa_queue 为 0 但 celery 有消息，说明路由配置未生效
```

### Q: FastAPI 日志显示任务已提交，但 Worker 没有日志？

**A:** 
1. 确认 Worker 正在运行：`ps aux | grep celery`
2. 确认 Worker 监听正确队列：查看启动命令是否包含 `-Q qa_queue`
3. 检查 Redis 连接：`redis-cli ping`

### Q: 如何验证任务是否在队列中？

**A:**
```bash
redis-cli
> LLEN qa_queue  # 查看队列长度
> LRANGE qa_queue 0 -1  # 查看队列内容
```

---

## 📝 完整的调试命令

在远程服务器上运行：

```bash
# 1. 检查 Worker 是否运行
ps aux | grep celery

# 2. 检查 Redis 连接
redis-cli ping

# 3. 检查队列消息
redis-cli LLEN qa_queue

# 4. 查看 FastAPI 日志（实时）
tail -f /path/to/app.log

# 5. 查看 Worker 日志（实时）
# 如果 Worker 在前台运行，直接看终端
# 如果后台运行，查看日志文件
```

---

## 🎯 预期行为

### 正常流程：

1. **前端发送请求** → `/qa/ask`
2. **FastAPI 接收** → 日志：`收到问题提交请求`
3. **提交任务** → 日志：`任务已提交，task_id: xxx`
4. **任务发送到 Redis** → 队列 `qa_queue` 有消息
5. **Worker 接收** → 日志：`Task ... received`
6. **Worker 执行** → 日志：`celery app Received task`

### 如果某个步骤失败：

- 步骤 2 失败 → 检查路由配置、认证
- 步骤 3 失败 → 检查 Celery 配置、Redis 连接
- 步骤 4 失败 → 检查任务路由配置
- 步骤 5 失败 → 检查 Worker 是否运行、队列配置

---

## 💡 临时测试：直接调用 API

如果前端有问题，可以直接测试 API：

```bash
# 在远程服务器上
curl -X POST http://localhost:8000/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "测试问题"}'

# 应该返回：
# {"task_id": "xxx"}
```

然后检查 Worker 日志是否有输出。

