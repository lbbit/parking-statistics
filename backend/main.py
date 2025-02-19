from fastapi import FastAPI, Query
from pymongo import MongoClient
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

# MongoDB 连接信息
MONGO_USERNAME = "your_username"
MONGO_PASSWORD = "your_password"
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "parking_db"

# 连接 MongoDB（包含身份验证）
mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
client = MongoClient(mongo_uri)
db = client[MONGO_DB]
collection = db["parking_data"]

# 创建 FastAPI 应用
app = FastAPI()

# 允许跨域访问（解决前端请求问题）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class ParkingRecord:
    def __init__(self, slot_id: str, date: str, hours: Dict[int, int]):
        self.slot_id = slot_id
        self.date = date
        self.hours = hours  # {0: 1, 1: 0, ..., 23: 1}

# 存储停车数据
@app.post("/store_data/")
async def store_data(slot_id: str, date: str, hours: Dict[int, int]):
    """
    存储停车数据
    """
    record = {
        "slot_id": slot_id,
        "date": date,
        "hours": hours
    }
    collection.update_one({"slot_id": slot_id, "date": date}, {"$set": record}, upsert=True)
    return {"message": "Data stored successfully"}

# 查询停车数据
@app.get("/get_data/")
async def get_data(slot_id: str, view: str, year: int, month: int):
    """
    根据视图类型（Day, Month）查询某个月的数据
    """
    start_date = datetime(year, month, 1)
    _, last_day = divmod((start_date.replace(month=month % 12 + 1) - timedelta(days=1)).day, 31)
    last_day = last_day or 31  # 处理 31 天的情况

    results = []

    for day in range(1, last_day + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        data = collection.find_one({"slot_id": slot_id, "date": date_str})

        if view == "day":
            # 日视图：返回 24 小时数据
            if data:
                hours = {int(k): v for k, v in data["hours"].items()}
            else:
                hours = {h: 0 for h in range(24)}
            results.append({"date": date_str, "hours": hours})

        elif view == "month":
            # 月视图：返回当天的停车小时数
            if data:
                total_hours = sum(int(v) for v in data["hours"].values())
            else:
                total_hours = 0
            results.append({"date": date_str, "total_hours": total_hours})

    return {"slot_id": slot_id, "view": view, "data": results}

# **查询所有车位 ID**
@app.get("/get_slots/")
async def get_slots():
    slots = collection.distinct("slot_id")
    return {"slots": slots}
# 运行服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

