# 🤖 RAG Chatbot

A simple Retrieval-Augmented Generation (RAG) chatbot built with Python, using **Google Gemini** as the LLM provider and **Pinecone** for vector database storage. 

The chatbot is designed to answer questions based on your uploaded documents. With minimal changes to the prompt, you can customize the chatbot's behavior to suit any use case.

---

## 🧠 Tech Stack

- **LLM**: Google Gemini (via `google-genai`)
- **Embedding**: via google-genai
- **Vector Store**: Pinecone
- **Framework**: Streamlit for UI, FastAPI for backend API
- **File Parsing**: 
  - PDF & CSV: LLM-based parsing
  - DOCX: `python-docx` library
- **Text Splitting**: LangChain

---

## 🚀 Getting Started Locally

Follow these steps to set up and run the project locally:

### 1. Clone the Repo
```bash
git clone https://github.com/Siddhantraje6/RAG-ChatBot-using-Pinecone-and-Streamlit.git
cd RAG-ChatBot-using-Pinecone-and-Streamlit
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set the .env variables
```bash
GEMINI_API_KEY=YOUR_API_KEY
PINECONE_API_KEY=YOUR_API_KEY
PINECONE_HOST=YOUR_PINECONE_HOST
```

### 5. Run the app
for frontend server
```bash
cd src
streamlit run main.py
```
for backend server
```bash
cd src/backend
python server.py
```

---

## 🌱 Recent Updates

- **FastAPI Backend**: Migrated from Flask to FastAPI for improved async support and better performance
- **Enhanced File Parsing**:
  - PDF and CSV files now use LLM-based parsing for better accuracy
  - DOCX parsing using `python-docx` library
- **Performance Improvements**: Better async support for faster response times
- **Simplified Configuration**: Streamlined environment variables with `PINECONE_HOST` support

---

## 🔮 Future Enhancements

- Multi-language support
- Advanced conversation memory
- Custom embedding models
- Document versioning support
- Enhanced error handling and logging
- Support for additional file formats
