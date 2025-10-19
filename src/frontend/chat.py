import os
import requests
import streamlit as st

# page header
st.set_page_config(page_title="Welcome to Chatbot", page_icon="💬")

# page title
st.title('Welcome to :blue[Diploma Help] chatBot!')

# chat history
if 'messageHistory' not in st.session_state:
    st.session_state.messageHistory = []

for message in st.session_state.messageHistory:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# chat input
query = st.chat_input(
    placeholder = 'Write your query',
    key = 'queryInput', # used to uniquely identify the widget
    # on_submit = 'callback'
)

if query:
    # user query
    with st.chat_message('user'):
        st.markdown(query)

    # agent response
    with st.chat_message('ai'):
        chatEndpoint = 'http://localhost:8000/chat'
        
        responseStream = requests.post(
            chatEndpoint,
            json = {
                'query': query
            }, 
            stream = True
        )
        
        # decode and stream the response
        res = ''
        placeholder = st.empty()
        for chunk in responseStream.iter_content(chunk_size = None):
            if chunk:
                decode = chunk.decode('utf-8')
                res = res + decode
                placeholder.markdown(res)


    # store the message into the state
    newMessages = [
        {
            'role': 'user',
            'content': query
        },

        {
            'role': 'ai',
            'content': res
        }
    ]

    #store the messages
    st.session_state.messageHistory.extend(newMessages)