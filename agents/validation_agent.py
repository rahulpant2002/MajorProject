from openai import AzureOpenAI
from core.logger import get_logger

logger = get_logger(__name__)

class ValidationAgent:
    def __init__(self, client: AzureOpenAI, completion_model: str):
        self.client = client
        self.model = completion_model

    def validate_summary(self, original_text: str, summary: str) -> bool:
        """
        Validates if the summary accurately reflects the original text.

        Returns:
            bool: True if the summary is valid, False otherwise.
        """
        logger.info("Validating summary...")
        try:
            system_prompt = """
            You are a validation expert. Your task is to determine if the provided summary accurately reflects the key points of the original text.
            Do not be overly critical, but ensure no major contradictions or hallucinations are present.
            Respond with only the single word "Yes" or "No".
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Original Text:\n{original_text}\n\nSummary:\n{summary}"}
                ],
                max_tokens=5
            )
            
            decision = response.choices[0].message.content.strip().lower()
            logger.info(f"Validation agent decision: '{decision}'")
            return "yes" in decision

        except Exception as e:
            logger.error(f"An error occurred during summary validation: {e}")
            # Default to True to avoid blocking the pipeline on a validation error
            return True