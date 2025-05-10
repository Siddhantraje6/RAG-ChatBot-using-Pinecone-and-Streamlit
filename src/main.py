from dotenv import load_dotenv
import os
load_dotenv()

import streamlit as st

# set the navigation
chatPage = st.Page('frontend/chat.py')
fileUploadPage = st.Page('frontend/fileUpload.py')
pg = st.navigation(
    {
        'chatBot': [chatPage], # default home page
        'Upload Files': [fileUploadPage]
        
    }
)
pg.run()