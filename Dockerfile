FROM python:3.11

WORKDIR /app

# 安装 pipenv
RUN pip install --upgrade pip && pip install pipenv

# 复制 Pipfile 和 Pipfile.lock
COPY Pipfile Pipfile.lock ./

# 安装依赖（--deploy 保证和 Pipfile.lock 一致，--system 安装到全局环境）
RUN pipenv install --deploy --system

# 复制项目代码
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]