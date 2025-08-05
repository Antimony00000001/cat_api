import requests
import json
import base64

# API 的公网地址
API_URL = "https://catapi-eu9nw8xikcg8qgqduwcamn.streamlit.app?endpoint=generate-timetable&style=cool"

def test_cloud_api():
    """
    调用部署在云端的 API，并提供详细的调试信息。
    """
    print(f"🚀 正在调用云端 API: {API_URL}")
    
    try:
        # --- 关键修正：伪装成浏览器发送请求 ---
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 发送带有浏览器头的 GET 请求
        response = requests.get(API_URL, timeout=45, headers=headers)

        print(f"✅ HTTP 请求完成！状态码: {response.status_code}")
        
        # 尝试解析 JSON 数据
        data = response.json()
        
        filename = data.get("filename")
        filedata_base64 = data.get("filedata_base64")

        if filename and filedata_base64:
            # 解码 Base64 数据
            image_data = base64.b64decode(filedata_base64)
            
            # 将解码后的数据写入文件
            with open(filename, "wb") as f:
                f.write(image_data)
            
            print(f"\n🎉🎉🎉 图片已成功生成并保存为: {filename} 🎉🎉🎉")
        else:
            print("\n❌ API 返回了 JSON，但内容不符合预期。")
            print("返回内容:", data)

    except json.JSONDecodeError:
        print("\n❌ JSON 解析失败！服务器返回的不是有效的 JSON。")
        print("   这通常意味着服务器返回了 HTML 页面。")
        print("   以下是服务器返回的完整内容：")
        print("---------------------------------")
        print(response.text) # 打印完整的返回内容
        print("---------------------------------")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {e}")


if __name__ == "__main__":
    test_cloud_api()
