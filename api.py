# api.py
from fastapi import FastAPI
import requests
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="随机猫猫 API",
    description="一个简单的 API，用于获取随机的猫猫图片和信息。",
    version="1.0.0",
)

# 允许所有来源的请求，这对于部署后的外部调用很重要
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CAT_API_URL = "https://api.thecatapi.com/v1/images/search"


@app.get("/random-cat", summary="获取一只随机猫猫")
def get_random_cat():
    """
    调用 TheCatAPI 获取一张随机猫猫图片的信息。
    """
    try:
        response = requests.get(CAT_API_URL)
        response.raise_for_status()
        data = response.json()

        if data:
            cat_info = data[0]
            return JSONResponse(content={
                "id": cat_info.get("id"),
                "url": cat_info.get("url"),
                "width": cat_info.get("width"),
                "height": cat_info.get("height"),
                "source": "TheCatAPI"
            })
        else:
            return JSONResponse(status_code=404, content={"message": "未能获取到猫猫信息"})
    except requests.exceptions.RequestException as e:
        return JSONResponse(status_code=500, content={"message": f"请求外部 API 出错: {e}"})


@app.get("/", summary="API 健康检查")
def read_root():
    return {"status": "猫猫 API 正在运行！"}