# app.py
import streamlit as st
import requests
import os

# 在 Streamlit Cloud 上，应用通常运行在 8080 端口
# 我们需要构建动态的 API URL
# Streamlit Cloud 会设置 `SERVER_PORT` 环境变量
# st.experimental_get_query_params() 可以获取 URL 信息
# 但最简单可靠的方式是直接构建，因为服务在同一容器
# 我们假设 Streamlit 应用的 URL 是 [app-name].streamlit.app
# 那么 API 的 URL 就是 [app-name].streamlit.app:8080 (或者直接是[app-name].streamlit.app，取决于内部网络)
# 为了简单起见，我们直接假定 Streamlit 和 FastAPI 在同一个 host 上，端口是 8080
# 动态获取当前应用的主机名
# st.get_option 在较新版本可用，或者用一个技巧
try:
    # 尝试从会话状态获取服务器地址，这在 Streamlit Cloud 上比较可靠
    from streamlit.web.server.server import Server

    session_info = Server.get_current()._get_session_info()
    app_host = session_info.ws.request.host
    API_BASE_URL = f"https://{app_host}"  # Streamlit Cloud 默认使用 HTTPS
except Exception:
    # 如果本地运行或获取失败，则回退到本地地址
    API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="猫猫 API 测试器", page_icon="🐱")

st.title("🐱 随机猫猫信息获取器")
st.write("这是一个运行在 Streamlit Cloud 上的 FastAPI + Streamlit 应用。")

# --- API 调用和测试 ---
st.header("API 调用测试")

if st.button("从我的 API 获取一只新猫猫！"):
    with st.spinner("正在调用 API..."):
        try:
            # 调用我们自己的 FastAPI 端点
            api_url = f"{API_BASE_URL}/random-cat"
            st.info(f"正在请求: {api_url}")  # 打印出请求地址，方便调试
            response = requests.get(api_url)
            response.raise_for_status()

            cat_data = response.json()

            st.success("成功从 API 获取数据！")
            st.image(cat_data["url"], caption=f"猫猫 ID: {cat_data['id']}", use_column_width=True)
            st.subheader("API 返回的 JSON 数据:")
            st.json(cat_data)

        except requests.exceptions.RequestException as e:
            st.error(f"调用 API 时出错: {e}")
            st.warning(f"请检查 API 服务是否正常。请求地址: {api_url}")

st.markdown("---")

# --- 如何调用 API 的说明 ---
st.header("如何调用这个已发布的 API？")
st.write(f"你可以使用任何 HTTP 客户端来调用这个部署在云端的 API。API 的基地址是: `{API_BASE_URL}`")

st.subheader("使用 `curl` (命令行)")
st.code(f"curl -X GET {API_BASE_URL}/random-cat", language="bash")

st.subheader("使用 Python `requests` 库")
st.code(f"""
import requests

# URL 就是你当前浏览器地址栏的地址
url = "{API_BASE_URL}/random-cat"
response = requests.get(url)

if response.status_code == 200:
    cat_data = response.json()
    print(cat_data)
else:
    print(f"请求失败，状态码: {{response.status_code}}")
    print(f"错误信息: {{response.text}}")
""", language="python")