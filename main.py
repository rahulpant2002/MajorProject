from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import os
from dotenv import load_dotenv

from core.logger import get_logger
from core.exceptions import DocumentProcessingError

# Load environment variables and initialize logger
load_dotenv()
logger = get_logger(__name__)

app = FastAPI(
    title="Intelligent Document Summarization API",
    description="API for document ingestion, summarization, and Q&A.",
)

# --- In-memory storage for uploaded file paths (for simplicity) ---
# In a real app, you might use a temporary storage service or a DB entry
processed_files = {}

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application starting up.")
    # Here you would initialize DB connections, etc.
    # For now, we just log.

@app.post("/ingest/", summary="Ingest and process documents")
async def ingest_documents(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload and trigger the processing of multiple documents.
    """
    filenames = [file.filename for file in files]
    logger.info(f"Received {len(filenames)} files for ingestion: {', '.join(filenames)}")

    # --- Placeholder for Agent Workflow ---
    # This is where the full agent workflow from Milestone 2/3 will be called.
    # For now, we simulate processing and handle potential errors.
    try:
        for file in files:
            # Simulate processing
            logger.info(f"Processing file: {file.filename}")
            # In a real scenario, you would save the file temporarily
            # and then pass it to the parsing/summarization agents.
            
            # Example of using custom exceptions
            if file.filename.endswith(".txt"):
                 raise DocumentProcessingError(f"Simulating a processing error for {file.filename}")

            processed_files[file.filename] = {"status": "processed", "summary": f"This is a summary for {file.filename}."}
        
        return {"message": "Files processed successfully", "processed_files": list(processed_files.keys())}

    except DocumentProcessingError as e:
        logger.error(f"A processing error occurred: {e.message}")
        # HTTP 422: Unprocessable Entity
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.error(f"An unexpected error occurred during ingestion: {e}")
        # HTTP 500: Internal Server Error
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


@app.get("/documents/", summary="List processed documents")
async def get_documents():
    """
    Endpoint to retrieve the list of successfully processed documents.
    """
    return {"documents": list(processed_files.keys())}


@app.get("/summary/{filename}", summary="Get summary of a document")
async def get_summary(filename: str):
    """
    Endpoint to retrieve the summary for a specific document.
    """
    if filename not in processed_files:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    summary_data = processed_files.get(filename, {})
    return {"filename": filename, "summary": summary_data.get("summary")}

# Add other endpoints for Q&A, etc. as you build them.