import random
from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB 连接信息
MONGO_USERNAME = "mongo_P3ZKah"
MONGO_PASSWORD = "mongo_Kme6JJ"
MONGO_HOST = "localhost"  # 如果 MongoDB 在 Docker 里运行，且 Python 运行在宿主机，使用 localhost
MONGO_PORT = 27017
MONGO_DB = "parking_db"

# 连接 MongoDB（包含身份验证）
mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
client = MongoClient(mongo_uri)
db = client[MONGO_DB]
collection = db["parking_data"]

# 生成模拟数据
slot_ids = ["A1", "A2", "B1", "B2"]
start_date = datetime(2024, 1, 1)

for slot in slot_ids:
    for i in range(60):  # 生成 60 天的数据
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        
        # 关键修改：将整数键转换为字符串
        hours = {str(h): random.choice([0, 1]) for h in range(24)}
        
        record = {"slot_id": slot, "date": date, "hours": hours}
        collection.update_one({"slot_id": slot, "date": date}, {"$set": record}, upsert=True)

print("模拟数据生成完成！")

