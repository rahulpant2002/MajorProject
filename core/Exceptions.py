"""Defines custom exceptions for the application."""

class DocumentProcessingError(Exception):
    """Base exception for errors during document processing."""
    pass

class ParsingError(DocumentProcessingError):
    """Raised when text extraction from a file fails."""
    def __init__(self, filename, message="Failed to parse content"):
        self.filename = filename
        self.message = f"[{filename}] {message}"
        super().__init__(self.message)

class UnsupportedFileTypeError(DocumentProcessingError):
    """Raised when an unsupported file type is uploaded."""
    def __init__(self, filename, file_type):
        self.filename = filename
        self.file_type = file_type
        self.message = f"[{filename}] Unsupported file type: '{file_type}'"
        super().__init__(self.message)