# 自建的 AI Agent，提供智能问答功能。

**「大模型从加载 → 微调 → 部署上线」的全过程。**

✅ 加载大模型（如 ChatGLM/Qwen）进行本地推理

✅ 使用 `transformers` + `PyTorch` 完成模型微调（如 SFT 或 LoRA）

✅ 使用 `FastAPI` 构建异步 API 接口

✅ 使用 `Celery` 分布式异步任务队列处理大模型推理请求

✅ 使用 `Docker` 容器化部署

✅ 使用 `Kubernetes` 云端部署并实现高可用 / 自动扩缩容

✅ 实现最小可用 Agent 或 AI 问答系统 Demo，可部署可上线



## 📦 所需技术栈

| 类别           | 工具/框架                                    | 用途                      |
| -------------- | -------------------------------------------- | ------------------------- |
| 模型框架       | `transformers`, `PyTorch`                    | 加载/训练/微调/部署大模型 |
| 模型类型       | ChatGLM3, Qwen1.5, LLaMA2                    | 开源大模型                |
| 推理优化       | `bitsandbytes`, `PEFT`, `accelerate`         | 量化推理、微调加速        |
| 后端           | `FastAPI`, `uvicorn`, `httpx`, `pydantic`    | 构建异步 RESTful API      |
| 分布式任务队列 | `Celery`, `Redis`/`RabbitMQ`                 | 异步调用模型              |
| 持久化         | `PostgreSQL` / `SQLite`                      | 用户管理 / 问答记录       |
| 容器化         | `Docker`, `Docker Compose`                   | 本地封装环境              |
| 云部署         | `Kubernetes`, `Helm`, `k3s`                  | 部署到云（如阿里云ECS）   |
| 向量数据库     | `FAISS`, `Chroma`, `Weaviate`                | 文档问答（RAG）扩展用     |
| 工具链         | `Makefile`, `task`, `bash`, `conda`, `pyenv` | 提高工程效率              |


## 🧱 一、基础模型运行层（推理 / 微调）

| 技术                                    | 作用                                       | 备注                            |
| --------------------------------------- | ------------------------------------------ | ------------------------------- |
| `transformers`（HuggingFace）           | 加载和使用预训练大模型（如 ChatGLM、Qwen） | HuggingFace 主力库              |
| `PyTorch`                               | 执行底层推理/训练/微调                     | ChatGLM 基于 PyTorch 实现       |
| `ChatGLM` / `Qwen` 等模型权重           | 本地推理 & RAG 问答                        | 支持 CPU/GPU 模式               |
| `CUDA` + `torch.cuda`                   | GPU 推理加速                               | 有显卡才用                      |
| `bitsandbytes` / `AutoGPTQ` / `exllama` | 量化加速                                   | 用于 INT4 推理部署              |
| `peft` + `LoRA` + `trl`                 | 微调大模型                                 | Parameter-Efficient Fine-Tuning |

------

## ⚙️ 二、向量检索 & 知识增强（RAG）

| 技术                                 | 作用                       | 推荐工具                          |
| ------------------------------------ | -------------------------- | --------------------------------- |
| `sentence-transformers`              | 文本向量化                 | 模型如 `bge-small-en`, `text2vec` |
| `FAISS` / `Milvus` / `Weaviate`      | 向量数据库                 | RAG 检索底座                      |
| `langchain`                          | 构建问答链、Agent 工具调用 | 可选（搭配 LLM 使用）             |
| `docx`, `pdfplumber`, `unstructured` | 文档解析                   | 用于知识库构建                    |

------

## 🌐 三、后端服务框架（构建 API）

| 技术                | 用途                       |
| ------------------- | -------------------------- |
| `FastAPI`（异步）   | 构建 API 服务              |
| `uvicorn[gunicorn]` | 高性能生产部署             |
| `httpx`             | 异步请求，用于模型内部调用 |
| `pydantic`          | 参数验证，模型结构         |

------

## 🧵 四、任务分发 / 异步处理

| 技术                 | 用途                           |
| -------------------- | ------------------------------ |
| `Celery`             | 大模型推理、向量更新、离线任务 |
| `RabbitMQ` / `Redis` | Celery 消息队列中间件          |
| `Flower`             | Celery 任务监控仪表盘（可选）  |

------

## 📦 五、容器化 + 云部署

| 技术                | 作用                         | 说明                         |
| ------------------- | ---------------------------- | ---------------------------- |
| `Docker`            | 打包部署你的服务 & 模型      | 多服务统一管理               |
| `docker-compose`    | 本地多容器编排               | 启动 API / Redis / Worker 等 |
| `Kubernetes`（K8s） | 云端弹性部署、调度、资源控制 | 可选轻量版：`k3s`            |
| `Helm`              | Kubernetes 的包管理器        | 部署复杂应用如向量数据库     |
| `MinIO`             | 私有对象存储（模型、文档）   | 模拟 S3                      |

------

## 📊 六、监控 & 日志 & 异常

| 技术                   | 用途           |
| ---------------------- | -------------- |
| `Prometheus + Grafana` | 性能监控       |
| `Sentry`               | 异常跟踪       |
| `loguru`               | 高级日志记录库 |

------

## 🔐 七、用户认证与权限

| 技术                    | 用途             |
| ----------------------- | ---------------- |
| `OAuth2 + JWT`          | 用户登录认证     |
| `FastAPI Users`（可选） | 快速搭建用户系统 |

------

## 🎯 八、DevOps / 运维工具链

| 技术                         | 说明                       |
| ---------------------------- | -------------------------- |
| `GitHub Actions / GitLab CI` | 自动测试 / 构建 / 部署     |
| `Nginx + HTTPS`              | 反向代理 + SSL 加密        |
| `Supervisor / PM2`           | 后台守护进程（非容器环境） |


### 测试git
