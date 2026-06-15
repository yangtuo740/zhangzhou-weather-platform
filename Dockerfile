FROM python:3.12-slim

WORKDIR /app

# 使用阿里云镜像加速（国内部署优化）
RUN sed -i "s/deb.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i "s/deb.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list

# 安装系统依赖（EasyOCR 需要 OpenCV 库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并使用清华镜像源安装
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制后端代码（含前端静态文件 backend/static/）
COPY backend/ .

# 创建数据目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 8000

# 启动命令（首次启动时 EasyOCR 自动下载中文模型）
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]