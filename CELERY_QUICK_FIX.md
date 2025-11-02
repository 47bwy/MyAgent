# ⚡ Celery 队列问题快速修复

## ❌ 问题原因

**队列不匹配！**

- FastAPI 发送任务到默认队列（`celery`）
- Worker 只监听 `qa_queue` 队列
- ❌ 消息不匹配，Worker 收不到！

---

## ✅ 已修复

我已经修复了 `worker/celery_config.py`，取消注释了任务路由配置。

**修改内容：**
```python
# 之前（被注释）：
# task_default_queue = 'qa_queue'
# task_routes = {'worker.tasks.answer_question_task': {'queue': 'qa_queue'}}

# 现在（已启用）：
task_default_queue = 'qa_queue'
task_routes = {
    'worker.tasks.answer_question_task': {'queue': 'qa_queue'}
}
```

---

## 🚀 修复步骤

### 步骤 1：上传修复后的文件到远程服务器

使用 SFTP 上传以下文件：
- `worker/celery_config.py` （已修复）
- `worker_debug.py` （增强版，显示配置信息）
- `test_celery.py` （测试脚本）
- `check_celery.sh` （诊断脚本）

### 步骤 2：在远程服务器上重启 Worker

```bash
# SSH 到远程服务器
ssh root@192.168.189.246 -p 20022
cd /root/MyAgent

# 停止旧的 Worker（如果正在运行）
pkill -f "celery.*worker"

# 启动新的 Worker
celery -A worker.celery_app worker --loglevel=info -Q qa_queue

# 或使用调试模式
export ENABLE_REMOTE_DEBUG=1
export DEBUG_PORT=5679
python worker_debug.py
```

**你应该看到：**
```
[tasks]
  . worker.tasks.answer_question_task

 -------------- celery@hostname v5.x.x
```

### 步骤 3：测试任务发送

**方法 1：使用测试脚本**
```bash
cd /root/MyAgent
python test_celery.py
```

**方法 2：发送真实请求**
```bash
# 通过 API
curl -X POST http://localhost:8000/qa/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question": "测试问题"}'
```

**如果修复成功，Worker 应该输出：**
```
[INFO] Task worker.tasks.answer_question_task[...] received
celery app Received task for question: 测试问题
[INFO] Task worker.tasks.answer_question_task[...] succeeded
```

---

## 🔍 如果还是不行，运行诊断

```bash
# 在远程服务器上
cd /root/MyAgent
./check_celery.sh
```

诊断脚本会检查：
- ✅ Redis 连接
- ✅ Worker 进程
- ✅ 队列配置
- ✅ Redis 队列消息
- ✅ 环境变量

---

## 📋 验证清单

- [ ] `worker/celery_config.py` 中 `task_default_queue = 'qa_queue'` 已取消注释
- [ ] `worker/celery_config.py` 中 `task_routes` 已取消注释
- [ ] Worker 已重启
- [ ] Worker 启动时显示 `[tasks]` 列表
- [ ] 发送任务后，Worker 有日志输出

---

## 🎯 常见问题

### Q: Worker 启动但没有任务日志？

**A:** 检查：
1. Worker 启动时是否显示 `[tasks]` 列表
2. 队列配置是否正确
3. 运行 `test_celery.py` 测试

### Q: 任务状态一直是 PENDING？

**A:** 说明 Worker 没有接收到任务，检查：
1. Redis 连接
2. 队列配置
3. Worker 是否监听正确的队列

### Q: 如何确认任务已发送？

**A:** 使用 Redis 客户端：
```bash
redis-cli
> LLEN celery
> LLEN qa_queue
> LRANGE qa_queue 0 -1
```

