# app.py
import streamlit as st
import requests
import os

st.set_page_config(page_title="猫猫 API 测试器", page_icon="🐱", layout="wide")

def get_api_urls():
    """
    动态确定 API 的公网URL和内部调用URL。
    """
    # --- 这里是唯一的修改 ---
    # FastAPI 的内部端口已改为 8008，这里必须同步修改
    internal_request_url = "http://localhost:8008/random-cat"

    try:
        from streamlit.web.server.server import Server
        session_info = Server.get_current()._get_session_info()
        public_host = session_info.ws.request.host
        public_display_url = f"https://{public_host}/random-cat"
    except Exception:
        # 本地测试地址也同步更新
        public_display_url = "http://localhost:8008/random-cat (本地测试地址)"

    return public_display_url, internal_request_url

# --- 主应用界面 (以下部分无需修改) ---
public_url, internal_url = get_api_urls()

print("===================================")
print(f"APP: 公网API地址 (用于展示): {public_url}")
print(f"APP: 内部API请求地址 (用于调用): {internal_url}")
print("===================================")

st.title("🐱 随机猫猫 API 服务")
st.info("这是一个 FastAPI + Streamlit 的组合应用。FastAPI 在后台提供 API 服务，Streamlit 提供这个交互界面。")

st.header("✅ 你的 API 已上线！")
st.write("任何人都可以通过以下地址调用你的API来获取随机猫猫信息。")
st.subheader("API 公网地址 (Public URL)")
st.code(public_url, language="bash")
st.subheader("使用 `curl` 调用示例")
st.code(f"curl -X GET \"{public_url}\"", language="bash")

st.markdown("---")

st.header("⚙️ 在线测试 API")
if st.button("点我测试调用 API！"):
    with st.spinner("正在从后台调用 API..."):
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
            st.error(f"调用内部 API 时出错: {e}")
            st.warning("请检查应用的后台日志（Console Log）查看 FastAPI 服务是否正常运行。")
