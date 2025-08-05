# app.py (Final Pure Streamlit Version)
import streamlit as st
import requests
import threading
import uvicorn
from api import app as fastapi_app

# --- 后台线程设置 (这部分无需改动) ---
HOST = "0.0.0.0"
PORT = 8008

if "fastapi_thread" not in st.session_state:
    def run_fastapi():
        print(f"THREAD: 启动 Uvicorn 服务器在 http://{HOST}:{PORT}")
        uvicorn.run(fastapi_app, host=HOST, port=PORT)

    thread = threading.Thread(target=run_fastapi, daemon=True)
    thread.start()
    st.session_state["fastapi_thread"] = thread
    print("APP: FastAPI 后台线程已创建并启动。")


# --- Streamlit 页面 ---
st.set_page_config(page_title="纯净版猫猫API", page_icon="✅", layout="wide")

# --- URL 获取逻辑 (无需改动) ---
def get_api_urls():
    internal_request_url = f"http://localhost:{PORT}/random-cat"
    public_api_url = f"http://localhost:{PORT}/random-cat"
    try:
        from streamlit.web.server.server import Server
        session_info = Server.get_current()._get_session_info()
        public_host = session_info.ws.request.host
        public_api_url = f"https://{public_host}/random-cat"
    except Exception:
        print("APP: 未能获取公网主机名，将使用本地测试URL。")
    return public_api_url, internal_request_url

public_url, internal_url = get_api_urls()

# --- 页面内容 ---
st.title("✅ 你的 API 已准备就绪 (纯净版)")
st.markdown("---")

st.subheader("🚀 公网 API 地址")
st.write("你的 API 已在全球范围内部署，使用下面的地址即可访问。")

# --- 使用内置组件实现清晰的显示和复制 ---
st.text_input(
    label="API 公网地址 (点击框内即可轻松复制)",
    value=public_url,
    disabled=True, # 设置为只读
)

st.subheader("👨‍💻 使用 `curl` 调用示例")
curl_command = f"curl -X GET \"{public_url}\""
st.text_area(
    label="cURL 命令 (点击框内即可轻松复制)",
    value=curl_command,
    disabled=True, # 设置为只读
    height=50,
)

st.markdown("---")

# --- 在线测试部分 (无需改动) ---
st.header("⚙️ 在线测试")
if st.button("点我立即测试！"):
    with st.spinner("正在调用 API..."):
        try:
            response = requests.get(internal_url, timeout=15)
            response.raise_for_status()
            cat_data = response.json()
            st.success("API 调用成功！")
            col1, col2 = st.columns(2)
            with col1:
                st.image(cat_data["url"], caption=f"猫猫 ID: {cat_data['id']}", use_column_width=True)
            with col2:
                st.write("**API 返回的 JSON 数据:**")
                st.json(cat_data)
        except requests.exceptions.RequestException as e:
            st.error(f"调用 API 时出错: {e}")
            st.info("这可能是因为后台服务仍在初始化。请等待几秒钟再试一次。")
