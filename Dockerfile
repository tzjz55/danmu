<<<<<<< HEAD
FROM python:3.11-slim
=======
FROM python:3.9-slim
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

<<<<<<< HEAD
=======
# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p data logs

<<<<<<< HEAD
=======
# 设置文件权限
RUN chmod +x bot.py

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=10)" || exit 1

# 暴露端口（如果需要）
EXPOSE 8000

>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
# 运行应用
CMD ["python", "bot.py"]