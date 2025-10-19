from pinecone import Pinecone

from config import config

pinecone_client: Pinecone = None
pinecone_index = None

async def connect_to_pinecone():
    """Establishes the Pinecone connection"""
    global pinecone_client, pinecone_index

    try:
        pinecone_client = Pinecone(api_key = config.PINECONE_API_KEY)
        pinecone_index = pinecone_client.IndexAsyncio(host = config.PINECONE_HOST)
    
    except Exception as e:
        print(f"== Failed to connect to Pinecone: {e} ==")
        raise RuntimeError(f"Failed to connect to Pinecone: {e}")

def get_pinecone():
    """Dependency function to get the Pinecone client instance"""
    if pinecone_index is None:
        print(f"== Pinecone connection not initiated ==")
        raise RuntimeError("Pinecone connection not initiated")
    
    return pinecone_index

async def query_records(
    vector: list,
    top_k: int,
    namespace: str = "diploma_studies_project"
):
    """Fetch context from Pinecone DB"""
    try:
        print(f"== Pinecone query record called ==")

        if pinecone_index is None:
            print(f"== Pinecone connection not initiated ==")
            raise RuntimeError("Pinecone connection not initiated")
        
        result = await pinecone_index.query(
            namespace = namespace,
            vector = vector,
            top_k = top_k,
            include_metadata = True
        )

        embedding_context = ""
        for match in result['matches']:
            embedding_context = embedding_context + match['metadata']['content']

        return embedding_context

    except Exception as e:
        print(f"== An error while fetching context from pinecone: {e} ==")
        raise Exception(f"An error while fetching context from pinecone: {e}")

async def upsert_records(
    vector: list,
    namespace: str = "diploma_studies_project"   
) -> bool:
    try:
        print(f"== Pinecone upsert called ==")
        
        if pinecone_index is None:
            print(f"== Pinecone connection not initiated ==")
            raise RuntimeError("Pinecone connection not initiated")

        await pinecone_index.upsert(
            vectors = vector,
            namespace = namespace
        )

        return True

    except Exception as e:
        print(f"== An error occured while upserting vectors to pineconeDB: {e} ==")
        return False