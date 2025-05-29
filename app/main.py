from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json

app = FastAPI()

# MongoDB 연결 (환경변수 MONGO_URL 사용)
MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client['channeltalk_db']
messages_collection = db['messages']

@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))  # 수신 데이터 로그 출력

    person_type = data.get("entity", {}).get("personType")
    
    # 문의하는 고객 메시지 처리
    if person_type == "user":
        question = data.get("refers", {}).get("message", {}).get("plainText") \
                   or data.get("refers", {}).get("message", {}).get("blocks", [{}])[0].get("value")
        store_name = data.get("refers", {}).get("user", {}).get("name") \
                     or data.get("entity", {}).get("name")
        tags = data.get("entity", {}).get("tags") \
               or data.get("refers", {}).get("userChat", {}).get("tags", [])
        
        document = {
            "type": "question",
            "content": question,
            "store_name": store_name,
            "tags": tags,
            "created_at": data.get("entity", {}).get("createdAt")
        }
        await messages_collection.insert_one(document)

    # 상담사가 답변하는 메시지 처리
    elif person_type == "manager":
        answer = data.get("entity", {}).get("plainText") \
                 or data.get("entity", {}).get("blocks", [{}])[0].get("value")
        answerer = data.get("refers", {}).get("manager", {})
        store_name = data.get("refers", {}).get("user", {}).get("name") \
                     or data.get("entity", {}).get("name")
        tags = data.get("refers", {}).get("userChat", {}).get("tags", [])
        
        document = {
            "type": "answer",
            "content": answer,
            "answerer_name": answerer.get("name"),
            "store_name": store_name,
            "tags": tags,
            "created_at": data.get("entity", {}).get("createdAt")
        }
        await messages_collection.insert_one(document)

    else:
        # personType이 user, manager 외일 경우(필요시 로그 또는 처리)
        print(f"Unhandled personType: {person_type}")

    return {"status": "saved"}

@app.get("/")
async def root():
    return {"message": "Webhook + MongoDB 연동 완료!"}
