import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class settings(BaseSettings):
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY")

    PINECONE_API_KEY: str = os.environ.get("PINECONE_API_KEY")
    PINECONE_HOST: str = os.environ.get("PINECONE_HOST")

    MONGO_URL: str = os.environ.get("MONGO_URL") 
    DB_NAME: str = os.environ.get("DB_NAME")

config = settings()