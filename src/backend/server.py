from dotenv import load_dotenv
import os
load_dotenv('./.env')

from flask import Flask, request, Response, jsonify 
from google import genai
from google.genai import types
from pinecone import Pinecone
import uuid
import requests
import PyPDF2
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List


app = Flask(__name__)


def preProcessDocument(rawContent: str) -> str:
    lines = rawContent.splitlines()

    cleanedLines = []
    for line in lines:
        if line.strip() == '':
            continue
        cleanedLines.append(line.strip())

    cleanContent = ''.join(cleanedLines)
    return cleanContent


def splitDocument(PDFcontent: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_text(PDFcontent)
    return chunks


def embedChunks(chunk: str) -> List[float]:
    txt_embedding_endpoint = os.getenv('TXT_EMBEDDING_ENDPOINT') 
    txt_embedding_api_key = os.getenv('TXT_EMBEDDING_API')

    try:
        response = requests.post(
            txt_embedding_endpoint,
            json = {
                'input': [chunk]
            },
            headers = {
                'Content-Type': 'application/json',
                'api-key': txt_embedding_api_key
            }
        )

        result = response.json()
        embedding = result['data'][0]['embedding']
        
        return embedding

    except Exception as e:
        print(e)
        return []


def PineconeInsert(chunks: List[str], embeddings: List[List[float]]) -> bool:
    pc = Pinecone(api_key = os.getenv('PINECONE_API_KEY'))
    index = pc.Index('ragtest-1')
    
    if len(chunks) != len(embeddings):
        return False
    
    for chunk, embedding in zip(chunks, embeddings):
        try:
            id = str(uuid.uuid4())
            index.upsert(
                vectors = [
                    {
                        'id': id,
                        'values': embedding,
                        'metadata': {
                            'text': chunk
                        }
                    }
                ],
                namespace = 'PDFdocs'
            )
            
        except Exception as e:
            print(e)
            return False

    return True




@app.route('/fileProcessing', methods = ['POST'])
def fileProcessing():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']

    # save the file
    with open(f'storedFiles/{file.filename}', 'wb') as f:
        f.write(file.getbuffer())
    f.close()

    document = PyPDF2.PdfReader( file ) #extract the text
    fileContent = ''
    for page in document.pages:
        fileContent += page.extract_text()

    cleanContent = preProcessDocument( fileContent ) #preprocess the raw content

    chunks = splitDocument( cleanContent ) #get the chunks
    
    embeddings = []
    for chunk in chunks: 
        embed = embedChunks( chunk ) #get embedding for each chunk
        if embed == []:
            return 'Embeddings falid for the document!', 400
        embeddings.append( embed )
    
    PineconeInsert(chunks, embeddings) #insert the chunks into the database

    return jsonify({'text': fileContent})


def queryPinecone(query: str) -> str:
    print('<--Pinecone DB call-->')
    pc = Pinecone(api_key = os.getenv('PINECONE_API_KEY'))
    index = pc.Index('ragtest-1')

    vector = embedChunks( query )

    result = index.query(
        namespace = 'PDFdocs',
        vector = vector,
        include_metadata = True,
        top_k = 5
    )

    # process the result to only get the text
    data = ''
    for match in result['matches']:
        data = data + match['metadata']['text']
    
    return data # return the data


getDataFromPinecone = {
    'name': 'getDataFromPinecone',
    'description': 'Retrieves relevant information from the Pinecone vector database based on a semantic Retrieval-Augmented Generation search.',
    'parameters': {
        'type': 'object',
        'properties': {
            'query': {
                'type': 'string',
                'description': 'A natural language description of the information the user is seeking.'
            }
        },
        'required': ['query']
    }
}


def generateResponse(query: str):
    client = genai.Client(api_key = os.getenv('GEMINI_API_KEY'))

    tools = types.Tool(
        function_declarations = [getDataFromPinecone]
    )

    system_instruction = """
        Role: You are a helpful **insurance assistant** that guides users with information about 
        insurance policies (**car**, **health**, and **full life**) and also handles general 
        insurance-related or conversational queries.

        Tasks: 
        - Use the `getDataFromPinecone` tool to retrieve relevant information from a Pinecone-based 
          knowledge base (e.g., policy terms, benefits, exclusions).
        - Answer general questions about insurance or assist with common queries when retrieval is not required.

        Tool Access:
        - `getDataFromPinecone(query: string)`  
           Use this to semantically search the document database when the query may relate to stored policy content.
        
        When to Use Retrieval
        Use the tool when:
        - The user asks about specific policy details.
        - When asked about insurance company
        - The query likely references uploaded or indexed documents.

        When to Answer Directly
        Respond directly when:
        - The question is general (e.g., “What is life insurance?”).
        - It’s conversational or doesn’t need document-based lookup.

        Behavior Guidelines
        - Clearly mention when an answer is based on retrieved information.
        - Provide helpful, and easy-to-understand responses.
        - Give Detailed responses
        - Beautify the outputs (make use of emojis, give responses point - wise, etc)   
        """

    config = types.GenerateContentConfig(
        system_instruction = system_instruction,
        tools = [tools]
    )

    response = client.models.generate_content_stream(
        model='gemini-2.0-flash',
        contents=[query],
        config = config
    )

    for chunk in response:
        if chunk.candidates[0].content.parts[0].text:
            yield chunk.candidates[0].content.parts[0].text
            time.sleep(0.125)
        if chunk.candidates[0].content.parts[0].function_call:
            toolCall = chunk.candidates[0].content.parts[0].function_call
            toolName = toolCall.name
            args = toolCall.args
            arg = args['query']

            if toolName == 'getDataFromPinecone':
                context = queryPinecone( **toolCall.args )

                function_response_part = types.Part.from_function_response(
                    name=toolName,
                    response={"result": context},
                )

                contents = []
                contents.append(
                    types.Content(
                        role = 'model',
                        parts = [
                            types.Part(
                                function_call = toolCall
                            )
                        ]
                    )
                )

                contents.append(
                    types.Content(
                        role = 'user',
                        parts = [ function_response_part ]
                    )
                )

                finalResponse = client.models.generate_content_stream(
                    model = 'gemini-2.0-flash',
                    config = config,
                    contents = contents
                )

                #stream the final response
                for res in finalResponse:
                    if res.candidates[0].content.parts[0].text:
                        yield res.candidates[0].content.parts[0].text
                        time.sleep(0.125)
                


@app.route('/chat', methods = ['POST'])
def chat():
    query = request.json.get('query')

    return Response(generateResponse(query), mimetype='text/plain')

if __name__ == "__main__":
    app.run(debug=True)

