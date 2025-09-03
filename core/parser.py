from fastapi import UploadFile
import pypdf
import docx
from bs4 import BeautifulSoup
import io

from .exceptions import ParsingError, UnsupportedFileTypeError

def parse_document(file: UploadFile) -> str:
    """
    Parses the content of an uploaded file based on its content type.

    Args:
        file (UploadFile): The file uploaded by the user.

    Returns:
        str: The extracted text content of the document.
    
    Raises:
        ParsingError: If text extraction fails.
        UnsupportedFileTypeError: If the file type is not supported.
    """
    content_type = file.content_type
    filename = file.filename
    file_content = file.file.read()
    
    try:
        if content_type == "application/pdf":
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
            
        elif content_type == "text/html":
            soup = BeautifulSoup(file_content, "lxml")
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            text = soup.get_text(separator='\n', strip=True)
            return text
            
        else:
            raise UnsupportedFileTypeError(filename=filename, file_type=content_type)

    except Exception as e:
        raise ParsingError(filename=filename, message=f"An error occurred during parsing: {e}")
