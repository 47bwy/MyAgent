# 🐛 调试指南 - Cursor/VSCode

## 📦 安装调试依赖

是的，**需要使用 `debugpy`** 进行 Python 调试！

```bash
pipenv install --dev debugpy
```

或者直接添加到 `Pipfile` 的 `[dev-packages]` 部分。

---

## 🔧 Cursor/VSCode 调试配置

### 1. 创建 `.vscode/launch.json`

我已经为你创建了调试配置文件，包含以下配置：

- **FastAPI 调试**：启动 API 服务器并支持断点调试
- **Celery Worker 调试**：调试异步任务
- **Python 测试调试**：运行和调试测试

### 2. 使用调试功能

#### 方法一：使用启动配置

1. 按 `F5` 或点击左侧调试图标（🐛）
2. 选择调试配置：
   - `Python: FastAPI` - 调试 API 服务器
   - `Python: Celery Worker` - 调试 Celery 任务
   - `Python: Current File` - 调试当前文件
3. 点击绿色的运行按钮或按 `F5`

#### 方法二：附加到进程

如果你已经在运行服务，可以使用"附加到进程"配置来连接调试器。

---

## 🎯 调试技巧

### 1. 设置断点

- 点击行号左侧添加断点（红点）
- 或按 `F9` 切换断点
- 使用条件断点：右键断点 → "编辑断点" → 设置条件

### 2. 调试控制

- **F5**: 继续执行（Continue）
- **F10**: 单步跳过（Step Over）
- **F11**: 单步进入（Step Into）
- **Shift+F11**: 单步跳出（Step Out）
- **Shift+F5**: 停止调试

### 3. 查看变量

- **变量面板**：查看当前作用域的变量
- **监视面板**：添加要监视的表达式
- **调用堆栈**：查看函数调用链
- **悬停**：鼠标悬停在变量上查看值

### 4. 调试控制台

在调试控制台中可以执行 Python 代码：
```python
# 例如：查看当前请求数据
print(user_data.username)
```

---

## 🧪 调试示例场景

### 场景 1：调试 Pydantic 验证

在 `app/routers/auth.py` 的 `register_user` 函数中设置断点：

```python
def register_user(
    user_data: UserCreate,  # 在这里打断点，查看验证后的数据
    db: Session = Depends(db.get_db)
):
    # 断点：可以查看 user_data 的所有字段
    db_user = auth.get_user(db, username=user_data.username)
```

**测试步骤：**
1. 在 `register_user` 函数开始处设置断点
2. 启动调试（F5）
3. 发送注册请求（使用 curl 或前端页面）
4. 调试器会在断点处暂停
5. 查看 `user_data` 对象，验证 Pydantic 是否正常工作

### 场景 2：调试 Celery 任务

在 `worker/tasks.py` 中设置断点：

```python
@celery_app.task
def answer_question_task(question: str, user_id: str) -> str:
    logger.info(f"celery app Received task for question: {question}")
    # 在这里设置断点
    time.sleep(1)
    return process_question(question, user_id)
```

**注意**：调试 Celery Worker 需要使用 `celery worker --pool=solo` 选项，因为多进程模式不支持调试。

### 场景 3：调试 Pydantic 验证器

在 `app/schemas/user.py` 中设置断点：

```python
@field_validator('username')
@classmethod
def validate_username(cls, v: str) -> str:
    # 在这里设置断点，查看传入的值
    if not all(c.isalnum() or c == '_' for c in v):
        raise ValueError('用户名只能包含字母、数字和下划线')
    return v
```

---

## 🔍 常用调试命令

### 查看请求数据

```python
# 在路由函数中
print(f"Request data: {user_data.dict()}")
print(f"Username: {user_data.username}")
```

### 查看数据库查询

```python
# 查看 SQL 查询
from sqlalchemy import event
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 查看 Pydantic 验证错误

```python
from pydantic import ValidationError

try:
    user_data = UserCreate(**request_data)
except ValidationError as e:
    print(e.errors())  # 查看所有验证错误
```

---

## ⚠️ 调试注意事项

1. **Celery Worker 调试**：必须使用 `--pool=solo`，否则多进程无法调试
2. **断点位置**：确保断点设置在可执行的代码行上（不是空行或注释）
3. **异步代码**：FastAPI 的异步函数可以正常调试，但注意异步上下文
4. **环境变量**：确保 `.env` 文件配置正确，调试时会加载环境变量

---

## 🛠️ 高级调试技巧

### 1. 条件断点

右键断点 → "编辑断点" → 设置条件，例如：
```python
username == "testuser"  # 只在特定用户名时暂停
```

### 2. 日志断点

右键断点 → "编辑断点" → "日志断点"，不需要暂停执行，只记录日志

### 3. 远程调试

如果需要调试远程服务器，可以配置远程调试：
```python
import debugpy
debugpy.listen(('0.0.0.0', 5678))
debugpy.wait_for_client()
```

---

## 📚 相关资源

- [debugpy 文档](https://github.com/microsoft/debugpy)
- [VSCode Python 调试](https://code.visualstudio.com/docs/python/debugging)
- [FastAPI 调试指南](https://fastapi.tiangolo.com/tutorial/debugging/)

