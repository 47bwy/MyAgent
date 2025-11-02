# 🔧 CUDA 错误修复指南

## ❌ 错误信息

```
ValueError: libcublas.so.*[0-9] not found in the system path
```

## 🔍 问题原因

这个错误通常发生在以下情况：

1. **安装了支持 CUDA 的 PyTorch**，但系统没有 NVIDIA GPU
2. **CUDA 驱动未安装**或版本不匹配
3. **PyTorch 在导入时就尝试加载 CUDA 库**

## ✅ 解决方案

### 方案 1：使用 CPU 版本的 PyTorch（推荐）

如果你**没有 NVIDIA GPU**，应该安装 CPU 版本的 PyTorch：

```bash
# 卸载现有的 PyTorch
pipenv uninstall torch

# 安装 CPU 版本的 PyTorch
pipenv install torch --index-url https://download.pytorch.org/whl/cpu
```

### 方案 2：设置环境变量强制使用 CPU

在启动应用前设置环境变量：

```bash
# 方法1：在命令行设置
export CUDA_VISIBLE_DEVICES=""
export PYTORCH_CUDA_ALLOC_CONF=""
python -m uvicorn app.main:app

# 方法2：在 .env 文件中添加
CUDA_VISIBLE_DEVICES=
```

### 方案 3：代码已自动处理（已修复）

我已经更新了 `app/services/llm_services.py`，现在会：
- ✅ 自动检测 CUDA 可用性
- ✅ 如果没有 CUDA，自动使用 CPU
- ✅ 延迟加载模型，避免导入时出错
- ✅ 更好的错误处理和日志

## 🔍 检查你的系统

### 检查是否有 GPU

```bash
# 检查 NVIDIA GPU（Linux）
nvidia-smi

# macOS（通常没有 NVIDIA GPU）
system_profiler SPDisplaysDataType
```

### 检查 PyTorch 版本

```python
import torch
print(torch.__version__)
print(torch.cuda.is_available())
```

### 检查当前安装的 PyTorch

```bash
pipenv run python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

## 📝 推荐的安装方式

### 如果**没有 GPU**（大多数 macOS 和部分 Linux 服务器）：

```bash
# 在 Pipfile 中明确指定 CPU 版本
# 或者使用：
pipenv install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 如果有 GPU：

```bash
# 根据你的 CUDA 版本安装对应的 PyTorch
# CUDA 11.8:
pipenv install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1:
pipenv install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 🚀 快速修复步骤

### 步骤 1：检查系统

```bash
# 检查是否有 GPU
nvidia-smi  # 如果没有输出，说明没有 NVIDIA GPU
```

### 步骤 2：重新安装 PyTorch（CPU 版本）

```bash
# 激活虚拟环境
pipenv shell

# 卸载现有 PyTorch
pip uninstall torch torchvision torchaudio

# 安装 CPU 版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 验证安装
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
```

### 步骤 3：更新 Pipfile.lock

```bash
pipenv lock
```

### 步骤 4：测试应用

```bash
# 启动应用
uvicorn app.main:app --reload

# 应该不再出现 CUDA 错误
```

## 💡 代码改进说明

我已经更新了 `app/services/llm_services.py`：

1. **延迟加载模型**：模型只在需要时才加载，避免导入时出错
2. **自动 CPU 回退**：如果没有 CUDA，自动使用 CPU
3. **更好的错误处理**：提供清晰的错误信息和日志
4. **环境变量支持**：可以通过环境变量控制行为

## ⚠️ 注意事项

1. **性能影响**：CPU 模式比 GPU 模式慢很多，但足够用于开发和测试
2. **模型大小**：某些大模型在 CPU 上可能运行很慢
3. **内存**：确保有足够的内存加载模型

## 📚 相关资源

- [PyTorch 官方安装指南](https://pytorch.org/get-started/locally/)
- [CUDA 兼容性](https://pytorch.org/get-started/previous-versions/)
- [Transformers 文档](https://huggingface.co/docs/transformers/)

## 🔄 如果问题仍然存在

1. 检查 `.env` 文件，确保 `CUDA_VISIBLE_DEVICES=""` 已设置
2. 删除虚拟环境并重新创建：`pipenv --rm && pipenv install`
3. 查看日志文件，了解具体的错误信息

