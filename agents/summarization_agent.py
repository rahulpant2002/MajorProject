import json
from openai import AzureOpenAI
from core.logger import get_logger

logger = get_logger(__name__)

class SummarizationAgent:
    def __init__(self, client: AzureOpenAI, completion_model: str):
        self.client = client
        self.model = completion_model

    def summarize(self, text: str) -> dict:
        """
        Generates a structured summary for the given text.
        For simplicity, this initial version does not handle chunking.
        """
        logger.info("Generating summary...")
        try:
            system_prompt = """
            You are an expert summarization agent. Your task is to create a concise and comprehensive summary of the provided text.
            The summary should capture the key points and main ideas of the document.
            Return the result as a JSON object with a single key: "summary".
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            summary_json = json.loads(response.choices[0].message.content)
            logger.info("Summary generated successfully.")
            return summary_json
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return {"summary": "Error: Could not generate summary."}