import json
from openai import AzureOpenAI
from core.logger import get_logger

logger = get_logger(__name__)

class EntityExtractionAgent:
    def __init__(self, client: AzureOpenAI, completion_model: str):
        self.client = client
        self.model = completion_model

    def extract(self, text: str) -> dict:
        """
        Extracts key entities from the given text.
        """
        logger.info("Extracting entities...")
        try:
            system_prompt = """
            You are an expert entity extraction agent. Analyze the provided text and extract key entities.
            Entities can include people, organizations, locations, dates, and key concepts.
            Return the result as a JSON object with a single key "entities", which is a list of objects,
            each with "text" and "type" keys. Example: {"entities": [{"text": "OpenAI", "type": "Organization"}]}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            entities_json = json.loads(response.choices[0].message.content)
            logger.info("Entities extracted successfully.")
            return entities_json
        except Exception as e:
            logger.error(f"Failed to extract entities: {e}")
            return {"entities": [{"text": "Error", "type": "Could not extract entities."}]}