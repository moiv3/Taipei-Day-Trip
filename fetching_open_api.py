import requests
import json
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def index():
    return {"index": True}

@app.get("/openapi")
async def get_taipei_open_api():
    api_1 = "http://www.travel.taipei/open-api/zh-tw/Attractions/All"
    api_1_headers = {'Accept': 'application/json'}
    res = requests.get(api_1,headers=api_1_headers)
    response = json.loads(res.text)

    return response