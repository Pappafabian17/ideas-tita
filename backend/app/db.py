import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

client = None
db = None

async def connect_db():
    global client , db
    load_dotenv()
    uri = os.environ.get("MONGO_URI","mongodb://localhost:27017")
    client = AsyncIOMotorClient(uri)
    db = client[os.environ.get("MONGO_DB","ideasTita")]
    
async def close_db():
    if client:
        client.close()
        
def get_db():
    return db