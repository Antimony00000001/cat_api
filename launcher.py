# launcher.py
import subprocess
import os
import time


def run():
    """
    使用一个 Python 脚本启动所有服务。
    这个脚本将作为 Streamlit Cloud 的入口点。
    """

    # 1. 启动 FastAPI 服务 (在后台运行)
    #    我们使用 subprocess.Popen，因为它不会阻塞，允许我们继续执行后续代码。
    print("🚀 开始启动 FastAPI 服务...")
    # 定义 FastAPI 的启动命令
    # 注意：在云端，端口通常由平台通过环境变量指定，但 FastAPI 可以用我们自己选的端口。
    # 这里我们用 8000，确保它不与 Streamlit 的端口冲突。
    # --host 0.0.0.0 是必须的，以便服务在容器网络中可访问。
    fastapi_command = [
        "uvicorn",
        "api:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]

    # 使用 Popen 在后台启动 FastAPI
    fastapi_process = subprocess.Popen(fastapi_command)

    # 给 FastAPI 一点时间来完全启动
    print("⏳ 等待 FastAPI 服务初始化 (5秒)...")
    time.sleep(5)
    print("✅ FastAPI 服务应该已经在后台运行。")

    # 2. 启动 Streamlit 服务 (在前台运行)
    #    我们使用 subprocess.run，因为它会阻塞，将控制权交给 Streamlit。
    #    这是我们希望的最后一个命令。
    print("\n🚀 开始启动 Streamlit 应用...")

    # 从环境变量获取 Streamlit 需要监听的端口，这是 Streamlit Cloud 的要求。
    # 如果在本地运行，默认使用 8501。
    streamlit_port = os.environ.get("PORT", "8501")

    # 定义 Streamlit 的启动命令
    streamlit_command = [
        "streamlit",
        "run",
        "app.py",
        "--server.port", streamlit_port,
        "--server.headless", "true"  # 在云环境中推荐使用
    ]

    # 使用 run 在前台启动 Streamlit
    # 这个命令会一直运行，直到你手动停止它（或容器被关闭）
    subprocess.run(streamlit_command)


if __name__ == "__main__":
    run()