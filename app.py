import streamlit as st
import os
from dotenv import load_dotenv
from core.llm import get_azure_openai_client
from core.db import get_db_connection

# Load environment variables from .env file at the very beginning
# This ensures that all subsequent modules can access them.
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Intelligent Document Summarization",
    page_icon="📄",
    layout="wide"
)

# --- Initialize Connections ---
@st.cache_resource
def init_openai_client():
    # Check if the key was loaded correctly
    if not os.getenv("AZURE_OPENAI_KEY"):
        raise ValueError("AZURE_OPENAI_KEY not found in environment variables. Check your .env file.")
    return get_azure_openai_client()

@st.cache_resource
def init_db_conn():
    return get_db_connection()

# --- UI Components ---
st.title("Intelligent Document Summarization 🧠")
st.markdown("""
Upload your documents (PDF, DOCX, HTML) and interact with them.
- Generate summaries
- Edit and save final versions
- Ask questions about the content
""")

# --- Main Application Logic ---
# Use a try-except block to gracefully handle initialization errors
try:
    openai_client = init_openai_client()
    db_conn = init_db_conn()

    if not db_conn:
        # The error for db_conn is already handled inside get_db_connection
        st.stop()

    st.sidebar.header("Upload Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Choose files",
        type=["pdf", "docx", "html"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.sidebar.info(f"{len(uploaded_files)} file(s) selected.")
        if st.sidebar.button("Process Uploaded Files"):
            with st.spinner("Processing documents... This may take a moment."):
                st.success("Placeholder: Document processing would happen here.")
                st.info("Next steps will involve parsing, agent workflows, and database storage.")

    st.header("Document Interaction")
    st.markdown("---")
    st.write("Interaction area will be built here.")

except ValueError as e:
    st.error(f"Initialization Failed: {e}")
    st.warning("Please ensure your `.env` file is in the root directory and correctly configured.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
