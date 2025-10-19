from fastapi import FastAPI, Body, Depends, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
import os
import uuid
import asyncio

from services.content_extraction import file_parser
from services.content_processing import getChunks, generateEmbeddings
from services.ai_init import init_genai, get_genai_client
from services.pinecone import connect_to_pinecone, upsert_records, get_pinecone, query_records

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"== Initializing services ==")
    
    await connect_to_pinecone()
    await init_genai()
    
    print(f"== All of the services initialized successfuly ==")

    yield
    print(f"== Services closed ==")

app = FastAPI(
    title = "Diploma Project API", 
    version = "1.0.0",
    lifespan = lifespan
)

@app.get("/")
async def hello():
    return {"message": "Hello from Diploma Project API!"}


@app.post("/fileProcessing")
async def file_processing(file: UploadFile = File(...)):
    """Process the uploaded file and store vectors in Pinecone DB."""
    try:
        # Save file locally
        os.makedirs("storedFiles", exist_ok = True)
        file_path = os.path.join("storedFiles", file.filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Validate file size
        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > 3:
            raise HTTPException(
                status_code = 400,
                detail = f"File too large ({file_size_mb:.2f} MB). Max allowed is 3 MB.",
            )

        # Detect file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        print(f"== file extension is: {file_extension} ==")

        # File parsing
        match file_extension:
            case ".pdf":
                extracted_content = await file_parser.using_llm(content, "pdf")
            case ".csv":
                extracted_content = await file_parser.using_llm(content, "csv")
            case ".docx":
                extracted_content = await file_parser.basic_docx(content)
            case _:
                raise HTTPException(
                    status_code = 400,
                    detail = f"Unsupported file type '{file_extension}'. Only PDF, CSV, and DOCX are supported.",
                )

        # Generate chunks and embeddings
        print("== Calculating chunks and embeddings ==")
        chunks = getChunks(extracted_content)

        batch_size = 20
        tasks = []

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]  
            tasks.append(generateEmbeddings(batch))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        embeddings = []
        for result in results:
            if isinstance(result, Exception):
                print(f"== Error generating embeddings: {result} ==")
                raise HTTPException(
                    status_code = 500,
                    detail = "Error occurred during embedding generation.",
                )
            for embedding in result:
                embeddings.append(embedding)

        if len(chunks) != len(embeddings):
            raise HTTPException(
                status_code = 500,
                detail = "Size mismatch between chunks and embeddings.",
            )

        # Prepare and upload vectors
        print("== Uploading vectors to Pinecone ==")
        upsert_batch_size = 20
        vectors = []

        for chunk, embedding in zip(chunks, embeddings):
            vector = {
                "id": str(uuid.uuid4()),
                "values": embedding,
                "metadata": {
                    "content": chunk,
                    "file_reference": file.filename,
                },
            }
            vectors.append(vector)

            if len(vectors) == upsert_batch_size:
                result = await upsert_records(vectors)
                if not result:
                    raise HTTPException(
                        status_code=500,
                        detail="Error uploading records to PineconeDB.",
                    )
                vectors = []
                await asyncio.sleep(1)

        # Upload remaining
        if vectors:
            result = await upsert_records(vectors)
            if not result:
                raise HTTPException(
                    status_code = 500,
                    detail = "Error uploading final records to PineconeDB.",
                )

        print("== File processing successful! ==")
        return {"success": True, "message": "File processed successfully!"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"== Unexpected error: {e} ==")
        return JSONResponse(
            content = {
                "success": False,
                "message": f"Unexpected error while processing file: {str(e)}",
            },
            status_code = 500,
        )


async def generate_response(
    query: str,
    genai_client
):
    try:
        # fetch context from pinecone
        embedding = await generateEmbeddings([query])
        pinecone_context = await query_records(
            vector = embedding,
            top_k = 5
        )
        print(f"context - {pinecone_context}")

        prompt = f"""
        You are a Specialized Diploma Study Bot designed to help students with academic and general Q&A.

        Instructions:
        - Use the RAG context only when it is relevant or helpful to the query. 
          If the context doesn’t apply (e.g., casual greetings, generic questions), respond naturally without forcing it.
        - If the context is partial or unclear, combine it with general academic knowledge intelligently.
        - Always provide a well-structured, clear, and detailed answer.
        - Keep the tone natural, friendly, and helpful — like a knowledgeable tutor.
        - Maintain the same language as the input (English, Hindi, etc.).
        - Organize the response logically using headings, bullet points, or steps when appropriate.

        Note: RAG context will be provided - irrespective of the nature of the query

        Student Query:
        {query}

        RAG Context:
        {pinecone_context}
        """
        response = await genai_client.aio.models.generate_content_stream(
            model = "gemini-2.0-flash",
            contents = query,
            config = {
                "system_instruction": prompt
            }
        )

        async for res in response:
            if res.candidates[0].content.parts[0].text:
                yield res.candidates[0].content.parts[0].text
                await asyncio.sleep(0.125)

    except Exception as e:
        yield f"There was an error while generating response: {e}"


@app.post("/chat")
async def send_llm_response(
    request_data = Body(...),
    genai_client = Depends(get_genai_client),
):
    return StreamingResponse(generate_response(
        query = request_data.get("query"),
        genai_client = genai_client
    ) , media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",  
        host = "0.0.0.0",  
        port = 8000,
        reload = True,
        log_level = "info"
    )

