import os
from openai import AzureOpenAI

def get_azure_openai_client():
    """
    Initializes and returns the AzureOpenAI client using credentials
    from environment variables.
    """
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    return client