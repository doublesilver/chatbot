from fastapi import FastAPI, Request
from .db import messages_collection
import json

app = FastAPI()

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))  # 전체 데이터 출력

    # 메시지 추출 (plainText 또는 blocks[0].value)
    message = None
    if 'refers' in data and 'message' in data['refers']:
        message = data['refers']['message'].get('plainText')
        if not message:
            blocks = data['refers']['message'].get('blocks', [])
            if blocks and 'value' in blocks[0]:
                message = blocks[0]['value']
    
    # 유저 정보 추출
    user_info = data.get('refers', {}).get('user', {})
    user_name = user_info.get('name')
    user_id = user_info.get('id')
    tags = user_info.get('tags', [])

    # 카테고리 지정: tags 리스트에서 첫 번째 태그 사용 (예: 이용권, 좌석 등)
    category = tags[0] if tags else "Uncategorized"

    document = {
        "original_message": message,
        "user_name": user_name,
        "user_id": user_id,
        "category": category,
        "tags": tags,
        "source": "ChannelTalk"
    }
    await messages_collection.insert_one(document)
    return {"status": "saved"}

@app.get("/")
async def root():
    return {"message": "Webhook + MongoDB 연동 완료!"}
