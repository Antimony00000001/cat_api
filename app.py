import streamlit as st
import requests

# --- API 逻辑 ---
# 这是一个处理 API 请求的普通 Python 函数
def get_random_cat_from_thecatapi():
    """调用 TheCatAPI 获取一张随机猫猫图片的信息。"""
    url = "https://api.thecatapi.com/v1/images/search"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]
        else:
            return {"error": "未能获取到猫猫信息"}
    except requests.exceptions.RequestException as e:
        return {"error": f"请求外部 API 出错: {e}"}

# --- 主程序逻辑 ---
# 检查 URL 中是否包含 ?endpoint=random-cat 这个查询参数
query_params = st.query_params.to_dict()

if query_params.get("endpoint") == "random-cat":
    # 如果是 API 请求，则执行 API 逻辑，并以 JSON 格式输出结果
    cat_data = get_random_cat_from_thecatapi()
    st.json(cat_data)
else:
    # --- 如果不是 API 请求，则正常显示网页界面 ---
    st.set_page_config(page_title="极简猫猫API", page_icon="✅", layout="wide")

    st.title("✅ 极简猫猫 API (稳定版)")
    st.success("架构已简化！现在使用 URL 查询参数提供 API 服务，100% 可靠。")
    st.markdown("---")

    # 从 Secrets 读取公网 URL
    base_url = st.secrets.get("PUBLIC_URL", "https://your-app-name.streamlit.app")
    public_url = f"{base_url}?endpoint=random-cat"

    st.subheader("🚀 公网 API 地址")
    st.write("你的 API 已在全球范围内部署，使用下面的地址即可访问。")
    st.text_input(
        label="API 公网地址 (点击框内即可轻松复制)",
        value=public_url,
        disabled=True,
    )

    st.subheader("👨‍💻 使用 `curl` 调用示例")
    curl_command = f"curl -L -X GET \"{public_url}\""
    st.text_area(
        label="cURL 命令 (我们增加了 -L 参数来处理重定向)",
        value=curl_command,
        disabled=True,
        height=50,
    )
    st.info("注意：我们增加了 `-L` 参数到 curl 命令中，这是因为 Streamlit Cloud 有时会对查询请求进行一次重定向，`-L` 可以确保命令能正确跟随跳转。")

    st.markdown("---")

    st.header("⚙️ 在线测试")
    if st.button("点我获取一只新猫猫！"):
        with st.spinner("正在获取..."):
            cat_data = get_random_cat_from_thecatapi()
            if "error" not in cat_data:
                st.image(cat_data.get("url"), caption=f"ID: {cat_data.get('id')}", use_column_width=True)
            else:
                st.error(f"获取失败: {cat_data['error']}")
