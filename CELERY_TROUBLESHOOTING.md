# 🔧 Celery Worker 接收不到消息排查

## ❌ 问题：Worker 没有日志输出，接收不到消息

### 🔍 可能的原因

1. **队列不匹配**（最常见）
2. Redis 连接失败
3. Worker 未正确启动
4. 任务路由配置错误

---

## 🎯 诊断步骤

### 步骤 1：检查队列配置是否匹配

**问题根源：**

在 `worker/celery_config.py` 中，队列路由被注释了：
```python
# task_default_queue = 'qa_queue'
# task_routes = {'worker.tasks.answer_question_task': {'queue': 'qa_queue'}}
```

但 Worker 启动时使用了 `-Q qa_queue`：
```bash
celery -A worker.celery_app worker -Q qa_queue
```

**结果：**
- FastAPI 发送任务到默认队列（`celery`）
- Worker 只监听 `qa_queue` 队列
- ❌ **消息不匹配，Worker 收不到！**

---

## ✅ 解决方案

### 方案 1：启用任务路由（推荐）

取消注释 `worker/celery_config.py` 中的路由配置：

```python
task_default_queue = 'qa_queue'
task_routes = {'worker.tasks.answer_question_task': {'queue': 'qa_queue'}}
```

### 方案 2：Worker 监听默认队列

启动 Worker 时不指定队列，监听所有队列：
```bash
celery -A worker.celery_app worker --loglevel=info
```

---

## 🔍 完整诊断流程

### 1. 检查 Redis 连接

**在远程服务器上：**
```bash
# 检查 Redis 是否运行
redis-cli ping
# 应该返回：PONG

# 检查 Redis 连接配置
redis-cli -h localhost -p 6379 ping
```

### 2. 检查 Worker 是否运行

```bash
# 查看 Worker 进程
ps aux | grep celery

# 查看 Worker 日志（如果在前台运行）
# 应该看到类似：
# celery@hostname v5.x.x (darwin)
# [tasks]
#   . worker.tasks.answer_question_task
```

### 3. 检查队列消息

```bash
# 查看 Redis 中的队列
redis-cli
> KEYS celery*
> LLEN celery  # 默认队列
> LLEN qa_queue  # 自定义队列

# 查看队列中的消息
> LRANGE celery 0 -1
> LRANGE qa_queue 0 -1
```

### 4. 测试任务发送

```python
# 在 Python 中测试
from worker.tasks import answer_question_task
result = answer_question_task.delay("测试问题", "testuser")
print(f"Task ID: {result.id}")
print(f"Task State: {result.state}")
```

---

## 🛠️ 快速修复

让我为你修复配置！

