# app.py (Final Rock-Solid Version using Secrets)
import streamlit as st
import requests
import threading
import uvicorn
from api import app as fastapi_app

# --- 后台线程设置 (无需改动) ---
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
st.set_page_config(page_title="稳定版猫猫API", page_icon="🚀", layout="wide")

# --- URL 获取逻辑 (全新稳定版) ---
# 内部调用的 URL 保持不变
internal_url = f"http://localhost:{PORT}/random-cat"

# 从 Secrets 读取公网 URL。
# st.secrets.get() 提供一个备用值，这让脚本在本地也能无错运行。
base_url = st.secrets.get("PUBLIC_URL", f"http://localhost:{PORT}")
public_url = f"{base_url}/random-cat"

# 在后台打印日志，方便我们确认 URL 是否正确读取
print("===================================")
print(f"APP: 从 Secrets 读取到的公网基础URL: {base_url}")
print(f"APP: 最终构建的公开API地址: {public_url}")
print("===================================")


# --- 页面内容 ---
st.title("🚀 你的 API 已准备就绪 (稳定版)")
st.markdown("---")

st.subheader("✅ 公网 API 地址")
st.write("你的 API 已在全球范围内部署，使用下面的地址即可访问。")

# --- 使用内置组件显示，确保易于复制 ---
st.text_input(
    label="API 公网地址 (点击框内即可轻松复制)",
    value=public_url,
    disabled=True,
)

st.subheader("👨‍💻 使用 `curl` 调用示例")
curl_command = f"curl -X GET \"{public_url}\""
st.text_area(
    label="cURL 命令 (点击框内即可轻松复制)",
    value=curl_command,
    disabled=True,
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
