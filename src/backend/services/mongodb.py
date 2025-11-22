from motor.motor_asyncio import AsyncIOMotorClient
from config import config

mongodb_client: AsyncIOMotorClient = None
mongodb_instance = None

async def connect_to_mongodb():
    """Establishes the MongoDB connection"""
    global mongodb_client, mongodb_instance
    try:
        mongodb_client = AsyncIOMotorClient(config.MONGO_URL)
        mongodb_instance = mongodb_client[config.DB_NAME]

    except Exception as e:
        print(f"== Failed to connect to mongodb: {e} ==")
        raise Exception(f"Failed to connect to mongodb: {e}")
    
def get_mongodb():
    """Dependency function to get the mongodb client instance"""
    if mongodb_instance is None:
        print("== mongodb connection not initiated ==")
        raise Exception("mongodb connection not initiated")
    
    return mongodb_instance
    
async def close_mongodb_connection():
    """Closes the MongoDB connection"""
    global mongodb_client
    try:
        if mongodb_client:
            mongodb_client.close()
            
    except Exception as e:
        print(f"== Failed to close mongodb connection: {e} ==")
        raise Exception(f"Failed to close mongodb connection: {e}")