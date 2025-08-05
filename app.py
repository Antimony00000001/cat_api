import streamlit as st
import requests
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import io

# =========== 1. 课表生成核心逻辑 (从你的脚本移植) ===========
# 将你的脚本逻辑封装在一个函数中，使其可以被API调用

def generate_timetable_image_in_memory(style_name='cool'):
    """
    在内存中生成课表图片，并返回 Base64 编码的字符串。
    """
    # --- 全局配置 ---
    IMG_WIDTH, IMG_HEIGHT, PADDING = 1200, 1800, 50
    HEADER_HEIGHT, LEFT_AXIS_WIDTH = 80, 60
    DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    TIME_SLOTS = [f"{i}:00" for i in range(8, 22)]

    # --- 风格与调色板 ---
    STYLES = {
        'modern': {'bg_colors': ('#F0F2F5', '#E6E9EE'), 'line_color': '#D8DCE3', 'font_color': '#333740', 'text_on_course_color': '#2D3436', 'palette': ['#D4E2F4', '#F4D9D4', '#D4F4E2', '#F4F1D4', '#E2D4F4', '#D4F4F1']},
        'cute': {'bg_colors': ('#FFF0F5', '#F8E9EE'), 'line_color': '#F5E3E8', 'font_color': '#D66D93', 'text_on_course_color': '#6B2D3F', 'palette': ['#FFC3D9', '#C3E1FF', '#C3FFD9', '#FFFDC3', '#E1C3FF', '#C3F8FF']},
        'cool': {'bg_colors': ('#282C34', '#21252B'), 'line_color': '#3E444F', 'font_color': '#ABB2BF', 'text_on_course_color': '#FFFFFF', 'palette': ['#61AFEF', '#E06C75', '#98C379', '#E5C07B', '#C678DD', '#56B6C2']},
        'fresh': {'bg_colors': ('#F3F9FB', '#E8F3F6'), 'line_color': '#DAE6EB', 'font_color': '#3E667A', 'text_on_course_color': '#0B4F6C', 'palette': ['#A8DADC', '#F191A2', '#83D4A3', '#FADF98', '#B3B8E3', '#98DFF0']},
    }
    # 如果请求的风格不存在，则使用 'cool' 作为默认值
    style = STYLES.get(style_name, STYLES['cool'])
    style['font_path'] = 'SourceHanSansSC-Regular.otf' # 脚本中定义的字体路径
    style['font_bold_path'] = 'SourceHanSansSC-Bold.otf'

    # --- 示例数据 ---
    sample_courses = [("高等数学", 1, "8:00", "9:40", "教A-101"),("Python编程实践", 1, "14:00", "16:30", "实验楼302"),("大学英语", 2, "10:00", "11:40", "文科楼203"),("线性代数", 3, "8:00", "9:40", "教A-101"),("数据结构与算法", 3, "14:00", "16:30", "实验楼304"),("体育（网球）", 4, "15:00", "16:40", "体育馆"),("操作系统原理", 5, "10:00", "12:30", "实验楼501"),("电影鉴赏", 5, "19:00", "20:40", "艺术楼放映厅"),("周末自习", 6, "9:00", "17:00", "图书馆")]

    # --- 辅助函数 ---
    def create_background(w, h, colors):
        base = Image.new('RGB', (w, h), colors[0])
        top = Image.new('RGB', (w, h), colors[1])
        mask = Image.new('L', (w, h))
        mask_data = [int(255 * (y / h)) for y in range(h) for _ in range(w)]
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base

    def draw_3d_effect_shadow(img, xy, r):
        x1, y1, x2, y2 = [int(v) for v in xy]
        shadow_canvas = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow_canvas).rounded_rectangle((x1, y1 + 10, x2, y2 + 10), r, (0, 0, 0, 40))
        shadow_canvas = shadow_canvas.filter(ImageFilter.GaussianBlur(8))
        img.paste(shadow_canvas, (0, 0), shadow_canvas)

    def get_text_size(draw, text, font):
        if hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        else:
            return draw.textsize(text, font=font)

    # --- 主绘图逻辑 ---
    img = create_background(IMG_WIDTH, IMG_HEIGHT, style['bg_colors']).convert('RGBA')
    draw = ImageDraw.Draw(img)
    try:
        font_regular = ImageFont.truetype(style['font_path'], 16)
        font_bold = ImageFont.truetype(style['font_bold_path'], 22)
        font_course = ImageFont.truetype(style['font_path'], 14)
        font_course_bold = ImageFont.truetype(style['font_bold_path'], 16)
    except IOError:
        font_regular, font_bold, font_course, font_course_bold = [ImageFont.load_default()] * 4

    grid_x, grid_y = PADDING + LEFT_AXIS_WIDTH, PADDING + HEADER_HEIGHT
    grid_w, grid_h = IMG_WIDTH - grid_x - PADDING, IMG_HEIGHT - grid_y - PADDING
    col_w, row_h = grid_w / len(DAYS), grid_h / len(TIME_SLOTS)

    for i, day in enumerate(DAYS):
        text_w, text_h = get_text_size(draw, day, font_bold)
        draw.text((grid_x + i * col_w + (col_w - text_w) / 2, PADDING + (HEADER_HEIGHT - text_h) / 2), day, style['font_color'], font=font_bold)
    for i, time in enumerate(TIME_SLOTS):
        text_w, _ = get_text_size(draw, time, font_regular)
        draw.text((grid_x - text_w - 15, grid_y + i * row_h - 8), time, style['font_color'], font=font_regular)
        draw.line([(grid_x - 5, grid_y + i * row_h), (grid_x + grid_w, grid_y + i * row_h)], style['line_color'], 1)

    course_colors, palette = {}, list(style['palette'])
    random.shuffle(palette)
    for name, day_idx, start_t, end_t, loc in sample_courses:
        if name not in course_colors: course_colors[name] = palette[len(course_colors) % len(palette)]
        start_h, start_m = map(int, start_t.split(':'))
        end_h, end_m = map(int, end_t.split(':'))
        start_row, end_row = (start_h - 8) + start_m / 60.0, (end_h - 8) + end_m / 60.0
        x1, y1 = grid_x + (day_idx - 1) * col_w + 8, grid_y + start_row * row_h + 4
        x2, y2 = grid_x + day_idx * col_w - 8, grid_y + end_row * row_h - 4
        draw_3d_effect_shadow(img, (x1, y1, x2, y2), 15)
        draw.rounded_rectangle((x1, y1, x2, y2), 15, course_colors[name])
        
        text_w, _ = get_text_size(draw, name, font_course_bold)
        draw.text((x1 + (x2 - x1 - text_w) / 2, y1 + 10), name, style['text_on_course_color'], font=font_course_bold)
        loc_text = f"@{loc}"
        text_w, _ = get_text_size(draw, loc_text, font_course)
        draw.text((x1 + (x2 - x1 - text_w) / 2, y1 + 35), loc_text, style['text_on_course_color'], font=font_course)

    # --- 将图片保存到内存并编码 ---
    final_img = img.convert('RGB')
    img_buffer = io.BytesIO()
    final_img.save(img_buffer, format="PNG")
    img_bytes = img_buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return {"filename": f"timetable_{style_name}.png", "filedata_base64": img_base64}

# =========== 2. 主程序逻辑 ===========
query_params = st.query_params.to_dict()
endpoint = query_params.get("endpoint")

if endpoint == "generate-timetable":
    # 如果是 API 请求，则执行 API 逻辑
    style = query_params.get("style", "cool")
    image_data = generate_timetable_image_in_memory(style)
    st.json(image_data)
else:
    # --- 如果不是 API 请求，则正常显示网页界面 ---
    st.set_page_config(page_title="课表图片生成API", page_icon="🎨", layout="wide")
    st.title("🎨 课表图片生成 API")
    st.success("应用已更新！现在提供一个API端点，用于生成精美的课程表图片。")
    st.markdown("---")

    base_url = st.secrets.get("PUBLIC_URL", "https://your-app-name.streamlit.app")
    api_url = f"{base_url}?endpoint=generate-timetable&style=cool"
    
    st.subheader("🚀 API 调用信息")
    st.text_input("API 地址 (可修改 `style` 参数)", api_url, disabled=True)
    st.info("支持的风格参数 `style`: `modern`, `cute`, `cool`, `fresh`。")
    st.warning("注意：云端服务器缺少中文字体，生成的图片将使用默认英文字体。")

    st.subheader("👨‍💻 Python 调用脚本")
    st.write("将以下完整代码复制到你的本地 Python 环境中运行，即可调用 API 并在当前目录生成图片。")

    client_code = f"""
import requests
import base64

# API 的公网地址
API_URL = "{api_url}"

print(f"🚀 正在调用 API: {{API_URL}}")

try:
    # 发送 GET 请求
    response = requests.get(API_URL, timeout=45) # 生成图片可能需要更长的时间
    response.raise_for_status()

    # 解析返回的 JSON 数据
    data = response.json()
    filename = data.get("filename")
    filedata_base64 = data.get("filedata_base64")

    if filename and filedata_base64:
        # 解码 Base64 数据
        image_data = base64.b64decode(filedata_base64)
        
        # 将解码后的数据写入文件
        with open(filename, "wb") as f:
            f.write(image_data)
        
        print(f"✅ 图片已成功生成并保存为: {{filename}}")
    else:
        print("❌ API 返回的数据格式不正确或缺少内容。")
        print("返回内容:", data)

except requests.exceptions.RequestException as e:
    print(f"❌ 请求失败: {{e}}")

"""
    st.code(client_code, language="python")

