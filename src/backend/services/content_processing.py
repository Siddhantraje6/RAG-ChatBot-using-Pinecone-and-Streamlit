from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

from google.genai import types
from services.ai_init import get_genai_client

def getChunks(
    content: str, 
    chunkSize: int = 800, # default values
    chunkOverlap: int = 80
) -> List[str]:
    
    """Split the content into chunks"""

    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunkSize,
            chunk_overlap = chunkOverlap,
        )
        chunks = splitter.split_text( content )
        
        return chunks

    except Exception as e:
        print(f"== Chunking failed: {e} ==")
        return []
    

async def generateEmbeddings(chunks: List[str]) -> List[List[float]]:
    """Find embeddings for all the text chunks"""
    try:
        print("== generate embedding called ==")
        genai_client = get_genai_client()
        
        result = await genai_client.aio.models.embed_content(
            model = "text-embedding-004",
            contents = chunks,
            config = types.EmbedContentConfig(
                task_type = "SEMANTIC_SIMILARITY",
            )
        )
        
        # extract the embeddings
        embeddings = []
        for em in result.embeddings:
            embeddings.append(em.values)

        return embeddings
    
    except Exception as e:
        print(f"== Error while generating embeddings : {e} ==")
        raise Exception(f"Error while generating embeddings : {e}")