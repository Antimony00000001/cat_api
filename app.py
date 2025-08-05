# app.py (The All-in-One Final Version)
import streamlit as st
import requests
import threading
import uvicorn
from fastapi.responses import JSONResponse

# 从 api.py 导入 FastAPI 的 app 实例
# 确保你的 api.py 文件与此文件在同一个目录下
from api import app as fastapi_app

# --- 后台线程设置 ---
# 定义我们 FastAPI 服务的端口
HOST = "0.0.0.0"
PORT = 8008

# 使用 Streamlit 的 session_state 来确保 Uvicorn 服务器只在一个线程中启动一次。
# 这是防止每次页面刷新都重新创建线程的关键。
if "fastapi_thread" not in st.session_state:
    # 定义一个函数，该函数将作为新线程的目标
    def run_fastapi():
        print(f"THREAD: 启动 Uvicorn 服务器在 http://{HOST}:{PORT}")
        uvicorn.run(fastapi_app, host=HOST, port=PORT)

    # 创建并启动后台线程
    # 设置为 "daemon=True" 意味着当主程序（Streamlit）退出时，这个线程也会被强制退出。
    thread = threading.Thread(target=run_fastapi, daemon=True)
    thread.start()
    
    # 将线程对象存储在 session_state 中
    st.session_state["fastapi_thread"] = thread
    print("APP: FastAPI 后台线程已创建并启动。")


# --- Streamlit 页面布局 ---
st.set_page_config(page_title="一体化猫猫 API", page_icon="🐱", layout="wide")

# 内部调用 API 的地址
internal_api_url = f"http://localhost:{PORT}/random-cat"

# 尝试获取公网URL用于展示
try:
    from streamlit.web.server.server import Server
    session_info = Server.get_current()._get_session_info()
    public_host = session_info.ws.request.host
    public_api_url = f"https://{public_host}/random-cat"
except Exception:
    public_api_url = f"http://localhost:{PORT}/random-cat (本地测试地址)"


st.title("🐱 一体化猫猫 API 服务 (稳定版)")
st.success("🎉 架构升级成功！FastAPI 现在作为后台线程稳定运行。")

st.header("✅ API 调用信息")
st.write("你的 API 已成功部署。使用以下地址和命令进行调用：")
st.code(public_api_url, language="bash")
st.code(f"curl -X GET \"{public_api_url}\"", language="bash")

st.markdown("---")

st.header("⚙️ 在线测试")
if st.button("点我从后台线程获取一只猫猫！"):
    with st.spinner("正在调用 API..."):
        try:
            response = requests.get(internal_api_url, timeout=15)
            response.raise_for_status()
            cat_data = response.json()
            st.success("API 调用成功！")
            col1, col2 = st.columns(2)
            with col1:
                st.image(cat_data["url"], caption=f"猫猫 ID: {cat_data['id']}", use_column_width=True)
            with col2:
                st.write("**返回的 JSON 数据:**")
                st.json(cat_data)
        except requests.exceptions.RequestException as e:
            st.error(f"调用 API 时出错: {e}")
            st.info("这可能是因为后台线程仍在初始化。请等待几秒钟再试一次。")
