from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://korea5410:4z0z1P8TudR8SRmk@cluster0.zhripmu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URL)
db = client['channeltalk_db']  # 사용할 데이터베이스 이름 (예: 'channeltalk_db')
messages_collection = db['messages']  # 사용할 콜렉션 이름 (예: 'messages')
