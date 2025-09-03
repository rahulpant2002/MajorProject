import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

# --- Page Configuration ---
st.set_page_config(
    page_title="Document Summarization UI",
    page_icon="📄",
    layout="wide"
)

st.title("Intelligent Document Summarization 🧠")
st.markdown("Upload documents to the backend for processing and interaction.")

# --- Session State Initialization ---
if 'selected_doc_id' not in st.session_state:
    st.session_state.selected_doc_id = None

# --- UI Components ---
st.sidebar.header("Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Choose files",
    type=["pdf", "docx", "html"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.sidebar.button("Process Uploaded Files"):
        files_to_upload = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
        
        with st.spinner("Sending files to backend for processing... This may take a while."):
            try:
                response = requests.post(f"{FASTAPI_URL}/ingest/", files=files_to_upload)
                if response.status_code == 200:
                    st.success("Files processed successfully by the backend!")
                    st.rerun() # Rerun the script to refresh the document list
                else:
                    st.error(f"Error from backend ({response.status_code}): {response.json().get('detail')}")
            except requests.exceptions.ConnectionError:
                st.error(f"Connection Error: Could not connect to the backend at {FASTAPI_URL}.")
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
            # Create a mapping from a display string to the document ID
            doc_options = {f"{doc['filename']} (ID: {doc['id']})": doc['id'] for doc in documents}
            
            selected_option = st.selectbox(
                "Select a document to view:",
                options=doc_options.keys(),
                index=None, # No default selection
                placeholder="Choose a document..."
            )

            if selected_option:
                st.session_state.selected_doc_id = doc_options[selected_option]

            if st.session_state.selected_doc_id:
                # Fetch full data for the selected document
                doc_id = st.session_state.selected_doc_id
                data_response = requests.get(f"{FASTAPI_URL}/document/{doc_id}")
                
                if data_response.status_code == 200:
                    doc_data = data_response.json()
                    
                    st.subheader(f"Editing: {doc_data.get('filename')}")
                    
                    # Editable Summary
                    edited_summary = st.text_area(
                        "Document Summary (Editable)",
                        value=doc_data.get('summary', 'No summary available.'),
                        height=300,
                        key=f"summary_{doc_id}" # Unique key to prevent state issues
                    )

                    if st.button("Save Changes to Summary"):
                        update_payload = {"summary": edited_summary}
                        update_response = requests.put(f"{FASTAPI_URL}/document/{doc_id}", json=update_payload)
                        if update_response.status_code == 200:
                            st.success("Summary updated successfully!")
                        else:
                            st.error("Failed to update summary.")

                    # Display Entities
                    st.subheader("Extracted Entities")
                    entities = doc_data.get('entities')
                    if entities:
                        st.json(entities)
                    else:
                        st.info("No entities were extracted.")
                else:
                    st.warning(f"Could not retrieve data for document ID {st.session_state.selected_doc_id}.")
        else:
            st.info("No documents have been processed yet. Upload some to begin.")
    else:
        st.warning("Could not fetch document list from the backend.")
except requests.exceptions.ConnectionError:
    st.error(f"Could not connect to the backend at {FASTAPI_URL}. Please ensure the backend server is running.")