from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import os
import json
from dotenv import load_dotenv

# Core imports
from core.logger import get_logger
from core.exceptions import DocumentProcessingError, ParsingError, UnsupportedFileTypeError
from core.parser import parse_document
from core.db import get_db_connection
from core.llm import get_azure_openai_client

# Agent imports
from agents.summarization_agent import SummarizationAgent
from agents.entity_extraction_agent import EntityExtractionAgent

# Vector DB import
from pgvector.psycopg2 import register_vector

# --- Initialization ---
load_dotenv()
logger = get_logger(__name__)

app = FastAPI(
    title="Intelligent Document Summarization API",
    description="API for document ingestion, summarization, and Q&A.",
)

# Initialize clients and agents
try:
    openai_client = get_azure_openai_client()
    completion_model = os.getenv("COMPLETION_DEPLOYMENT_NAME")
    embedding_model = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
    
    summarizer = SummarizationAgent(openai_client, completion_model)
    entity_extractor = EntityExtractionAgent(openai_client, completion_model)
    logger.info("Clients and agents initialized successfully.")
except Exception as e:
    logger.error(f"Fatal error during initialization: {e}")
    openai_client = None # Ensure app knows client failed

@app.on_event("startup")
async def startup_event():
    if not openai_client:
        logger.error("Azure OpenAI client not available. API will not function correctly.")
    logger.info("FastAPI application starting up.")

# --- API Endpoints ---

@app.post("/ingest/", summary="Ingest and process documents")
async def ingest_documents(files: List[UploadFile] = File(...)):
    if not openai_client:
        raise HTTPException(status_code=503, detail="AI services are unavailable.")

    processed_docs = []
    for file in files:
        try:
            logger.info(f"Processing file: {file.filename}")
            
            content = parse_document(file)
            if not content.strip():
                logger.warning(f"No content extracted from {file.filename}. Skipping.")
                continue

            summary_data = summarizer.summarize(content)
            entities_data = entity_extractor.extract(content)

            embedding_response = openai_client.embeddings.create(input=[content], model=embedding_model)
            embedding = embedding_response.data[0].embedding

            # --- Database Saving Logic ---
            conn = get_db_connection()
            if not conn:
                # If connection fails, raise an error immediately
                raise HTTPException(status_code=503, detail="Database connection could not be established.")
            
            try:
                # THIS IS THE CRITICAL FIX: Register the vector type with the connection
                register_vector(conn)
                
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO documents (filename, content, summary, entities, embedding)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id;
                        """,
                        (file.filename, content, summary_data.get('summary'), json.dumps(entities_data), embedding)
                    )
                    doc_id = cur.fetchone()['id']
                    conn.commit()
                
                processed_docs.append({"id": doc_id, "filename": file.filename})
                logger.info(f"Successfully ingested and saved document id: {doc_id}")

            finally:
                # Ensure the connection is always closed
                conn.close()

        except (ParsingError, UnsupportedFileTypeError) as e:
            logger.error(f"Document processing failed for {file.filename}: {e.message}")
            raise HTTPException(status_code=422, detail=e.message)
        except Exception as e:
            logger.error(f"An unexpected error occurred processing {file.filename}: {e}")
            # This will now catch the "Unsupported data type" if the fix fails, and other errors.
            raise HTTPException(status_code=500, detail=f"An internal server error occurred for {file.filename}: {str(e)}")

    return {"message": "Files processed successfully", "processed_documents": processed_docs}


@app.get("/documents/", summary="List processed documents")
async def get_documents():
    """Retrieves list of documents from the database."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, filename FROM documents ORDER BY created_at DESC;")
        docs = cur.fetchall()
    conn.close()
    return {"documents": docs}


@app.get("/document/{doc_id}", summary="Get all data for a document")
async def get_document_data(doc_id: int):
    """Retrieves the summary and entities for a specific document."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, filename, summary, entities FROM documents WHERE id = %s;", (doc_id,))
        data = cur.fetchone()
    conn.close()
    if not data:
        raise HTTPException(status_code=404, detail="Document not found.")
    return data


@app.put("/document/{doc_id}", summary="Update a document's summary")
async def update_summary(doc_id: int, update_data: dict):
    """Updates the summary for a given document ID."""
    summary = update_data.get('summary')
    if summary is None:
        raise HTTPException(status_code=400, detail="No summary provided in request body.")
    
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE documents SET summary = %s WHERE id = %s;", (summary, doc_id))
        conn.commit()
    conn.close()
    logger.info(f"Updated summary for document id: {doc_id}")
    return {"message": "Summary updated successfully."}