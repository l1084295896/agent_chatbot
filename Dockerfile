FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p chroma_db logs data/external

# 设置 entrypoint 脚本执行权限
RUN chmod +x entrypoint.sh

# 暴露端口
EXPOSE 8501

# 启动命令 - 使用 entrypoint 脚本
CMD ["./entrypoint.sh"]
