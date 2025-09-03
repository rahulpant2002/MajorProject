import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

# --- Page Configuration ---
st.set_page_config(
    page_title="Document Summarization UI",
    page_icon="📄",
    layout="wide"
)

st.title("Intelligent Document Summarization 🧠")
st.markdown("Upload documents to the backend for processing.")

# --- UI Components ---
st.sidebar.header("Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Choose files",
    type=["pdf", "docx", "html"],
    accept_multiple_files=True
)

if uploaded_files:
    st.sidebar.info(f"{len(uploaded_files)} file(s) selected.")
    if st.sidebar.button("Process Uploaded Files"):
        files_to_upload = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
        
        with st.spinner("Sending files to backend for processing..."):
            try:
                response = requests.post(f"{FASTAPI_URL}/ingest/", files=files_to_upload)
                
                if response.status_code == 200:
                    st.success("Files processed successfully by the backend!")
                    st.json(response.json())
                else:
                    # Show error from backend in a red block
                    st.error(f"Error from backend: {response.status_code}")
                    st.error(response.json().get("detail", "No detail provided."))

            except requests.exceptions.ConnectionError:
                st.error(f"Connection Error: Could not connect to the backend at {FASTAPI_URL}. Is the backend server running?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# --- Document Interaction Area ---
st.header("Document Interaction")
st.markdown("---")

try:
    doc_response = requests.get(f"{FASTAPI_URL}/documents/")
    if doc_response.status_code == 200:
        documents = doc_response.json().get("documents", [])
        if documents:
            selected_doc = st.selectbox("Select a document to view its summary:", options=documents)
            if selected_doc:
                summary_response = requests.get(f"{FASTAPI_URL}/summary/{selected_doc}")
                if summary_response.status_code == 200:
                    summary = summary_response.json().get("summary", "No summary available.")
                    st.text_area("Document Summary", value=summary, height=300)
                else:
                    st.warning(f"Could not retrieve summary for {selected_doc}.")
        else:
            st.info("No documents have been processed yet.")
    else:
        st.warning("Could not fetch document list from the backend.")
except requests.exceptions.ConnectionError:
    st.error(f"Could not connect to the backend at {FASTAPI_URL}. Please ensure the backend server is running.")
