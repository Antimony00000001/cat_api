# launcher.py
import subprocess
import os
import time

def run():
    """
    使用一个 Python 脚本启动所有服务。
    这个脚本将作为 Streamlit Cloud 的入口点。
    """
    print("=================================================")
    print("🚀 LAUNCHER: 开始执行启动脚本...")
    print("=================================================")
    
    # 1. 启动 FastAPI 服务 (在后台运行)
    fastapi_port = "8000"
    print(f"LAUNCHER: 准备在后台启动 FastAPI 服务于端口 {fastapi_port}...")
    
    fastapi_command = [
        "uvicorn", 
        "api:app", 
        "--host", "0.0.0.0", 
        "--port", fastapi_port
    ]
    
    # 使用 Popen 在后台启动 FastAPI
    fastapi_process = subprocess.Popen(fastapi_command)
    print(f"LAUNCHER: FastAPI 进程已启动 (PID: {fastapi_process.pid}).")
    
    # 给 FastAPI 一点时间来完全启动
    print("LAUNCHER: 等待 5 秒让 FastAPI 初始化...")
    time.sleep(5)

    # 2. 启动 Streamlit 服务 (在前台运行)
    # 从环境变量获取 Streamlit 需要监听的端口，这是 Streamlit Cloud 的要求
    # 如果在本地运行，我们回退到一个不容易冲突的端口，例如 8505
    streamlit_port = os.environ.get("PORT", "8505")
    
    print(f"\nLAUNCHER: 准备在前台启动 Streamlit 应用于端口 {streamlit_port}...")
    
    streamlit_command = [
        "streamlit", 
        "run", 
        "app.py", 
        "--server.port", streamlit_port, 
        "--server.headless", "true"
    ]

    # 这个命令会占据当前进程，直到应用被关闭
    subprocess.run(streamlit_command)

if __name__ == "__main__":
    run()
