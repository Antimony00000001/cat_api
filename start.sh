#!/bin/bash

# 启动 FastAPI 应用
# --host 0.0.0.0 允许外部访问
# --port 8000 是我们为 FastAPI 指定的端口
# & 让命令在后台运行
uvicorn api:app --host 0.0.0.0 --port 8000 &

# 启动 Streamlit 应用
# --server.port $PORT 是 Streamlit Cloud 要求的方式
# $PORT 是平台注入的环境变量，通常是 8080
# --server.headless=true 也是推荐的配置
streamlit run app.py --server.port $PORT --server.headless=true