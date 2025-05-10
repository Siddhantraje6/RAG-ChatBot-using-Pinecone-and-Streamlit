import streamlit as st
import requests
import PyPDF2

# page header
st.set_page_config(page_title="upload files", page_icon="💬")

# page title
st.title('Add knowledge to the chatBot! - :blue[Upload PDF]')

fileUpload = st.file_uploader(
    'Choose a File', 
    type = ['pdf'],   
    accept_multiple_files = False
)

if fileUpload is not None: # file has been uploaded
    # send the file to the backend for processing
    fileProcessingEndpoint = 'http://localhost:5000/fileProcessing'

    files = {
        'file': (
            fileUpload.name,
            fileUpload.getvalue(),
            'application/pdf'
        )
    }
    
    with st.spinner('Uploading and processing...'):
        response = requests.post(fileProcessingEndpoint, files=files)
    
    if response.status_code == 200:
        st.success("File added into the knowledge base")
    else:
        st.error(f"Failed to upload! {response.text}")