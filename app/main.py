from fastapi import FastAPI, Request, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
import time

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client.channeltalk_db
messages_collection = db.messages
conversations_collection = db.conversations


@app.post("/webhook")
async def webhook_handler(req: Request):
    try:
        data = await req.json()
        entity = data.get("entity", {})
        refers = data.get("refers", {})
        person_type = entity.get("personType")  # user, manager, bot 등

        # bot인 경우 무시
        if person_type == "bot":
            return {"status": "ignored - bot message"}

        chat_id = entity.get("chatId") or entity.get("mainKey")
        plain_text = entity.get("plainText", "")
        tags = entity.get("tags", [])
        state = entity.get("state", "").lower()
        created_at = entity.get("createdAt", int(time.time() * 1000))

        answerer_name = refers.get("manager", {}).get("name") if person_type == "manager" else None

        store_name = entity.get("name") or "알수없음"

        message_doc = {
            "chatId": chat_id,
            "type": "answer" if person_type == "manager" else "question",
            "content": plain_text,
            "personType": person_type,
            "senderName": answerer_name,
            "createdAt": created_at,
            "tags": tags,
            "storeName": store_name,
        }

        await messages_collection.insert_one(message_doc)

        if state == "closed":
            conv_update = {
                "chatId": chat_id,
                "storeName": store_name,
                "finalTags": tags,
                "state": "closed",
                "closedAt": created_at,
                "updatedAt": int(time.time() * 1000),
            }
            await conversations_collection.update_one(
                {"chatId": chat_id},
                {"$set": conv_update},
                upsert=True,
            )

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Webhook + MongoDB 연동 완료!"}
