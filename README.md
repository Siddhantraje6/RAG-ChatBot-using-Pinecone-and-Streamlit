# 🛡️ Insurance RAG Chatbot

A simple Retrieval-Augmented Generation (RAG) chatbot built with Python, using **Google Gemini** as the LLM provider and **Pinecone** for vector database storage. 
The chatbot is designed to answer insurance-related questions based on uploaded policy documents. The overall theme for the chatbot is Insurance company, but few changes
to the prompt is all required to change the behaviour of the chatbot to suite your use case

---

## 🧠 Tech Stack

- **LLM**: Google Gemini (via `google-genai`)
- **Embedding**: OpenAI Embeddings
- **Vector Store**: Pinecone
- **Framework**: Streamlit for UI, Flask for backend API
- **File Parsing**: PyPDF2
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
GEMINI_API_KEY = YOUR_API_KEY

PINECONE_API_KEY = YOUR_API_KEY

TXT_EMBEDDING_API = YOUR_API_KEY
TXT_EMBEDDING_ENDPOINT = YOUR_ENDPOINT
```

### 5. Run the app
```bash
cd src
streamlit run main.py
```

---

## 🌱 Future Aspects
