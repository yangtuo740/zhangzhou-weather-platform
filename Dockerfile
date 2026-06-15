FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 预下载 EasyOCR 中文模型
RUN python -c "import easyocr; reader = easyocr.Reader(['ch_sim', 'en'], gpu=False); print('EasyOCR models ready')"

# 复制后端代码
COPY backend/ .

# 创建数据目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
