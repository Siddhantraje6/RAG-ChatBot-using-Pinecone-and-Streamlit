import requests
import streamlit as st

# ---------------------------
# Page Settings
# ---------------------------
st.set_page_config(page_title="Welcome to Chatbot", page_icon="💬")
st.title("Welcome to :blue[Diploma Help] ChatBot!")

CHAT_ENDPOINT = "http://localhost:8000/chat"


# ---------------------------
# Session State for Chat History
# ---------------------------
if "messageHistory" not in st.session_state:
    st.session_state.messageHistory = []


# ---------------------------
# Display Chat History
# ---------------------------
for message in st.session_state.messageHistory:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------------
# Chat Input
# ---------------------------
query = st.chat_input("Write your query")

if query:

    # Show user's message
    with st.chat_message("user"):
        st.markdown(query)

    # Prepare response container
    with st.chat_message("ai"):
        placeholder = st.empty()

        try:
            if len(st.session_state.messageHistory) >= 2:
                message_history = st.session_state.messageHistory[-2:]
            else: message_history = []
            with st.spinner("Thinking..."):
                response_stream = requests.post(
                    CHAT_ENDPOINT,
                    json={
                        "query": query,
                        "message_history": message_history
                    },
                    stream=True,
                    timeout=90
                )

            # Stream the response text
            result_text = ""

            for chunk in response_stream.iter_content(chunk_size=None):
                if chunk:
                    decoded = chunk.decode("utf-8", errors="ignore")
                    result_text += decoded
                    placeholder.markdown(result_text)

        except requests.exceptions.RequestException as e:
            result_text = "❌ Backend is unavailable. Please try again later."
            placeholder.error(result_text)


    # Save conversation to session state
    st.session_state.messageHistory.append(
        {"role": "user", "content": query}
    )
    st.session_state.messageHistory.append(
        {"role": "ai", "content": result_text}
    )
