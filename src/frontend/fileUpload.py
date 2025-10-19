import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(page_title="Upload Files", page_icon="💬")
st.title("Add Knowledge to the ChatBot! - :blue[Upload Files]")

# --- File Upload ---
fileUpload = st.file_uploader(
    "Choose a file",
    type=["pdf", "csv", "docx"],
    accept_multiple_files=False
)

# --- Backend Endpoint ---
fileProcessingEndpoint = "http://localhost:8000/fileProcessing"

# --- File Handling ---
if fileUpload is not None:
    # Check file size (limit = 3MB)
    file_size_mb = len(fileUpload.getvalue()) / (1024 * 1024)
    if file_size_mb > 3:
        st.error("❌ File too large! Please upload a file under 3 MB.")
    else:
        # Detect MIME type
        file_type_map = {
            "pdf": "application/pdf",
            "csv": "text/csv",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
        file_ext = fileUpload.name.split(".")[-1].lower()
        mime_type = file_type_map.get(file_ext, "application/octet-stream")

        # Prepare file for backend
        files = {
            "file": (fileUpload.name, fileUpload.getvalue(), mime_type)
        }

        # Upload to backend
        with st.spinner("Uploading and processing..."):
            try:
                response = requests.post(fileProcessingEndpoint, files=files)
                if response.status_code == 200:
                    st.success("✅ File added into the knowledge base!")
                else:
                    st.error(f"❌ Upload failed! {response.text}")
            except Exception as e:
                st.error(f"⚠️ Error connecting to server: {e}")
