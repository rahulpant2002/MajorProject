import json
from openai import AzureOpenAI
from core.logger import get_logger

logger = get_logger(__name__)

class SummarizationAgent:
    def __init__(self, client: AzureOpenAI, completion_model: str):
        self.client = client
        self.model = completion_model

    def _chunk_text(self, text: str, max_chars: int = 4000) -> list[str]:
        """Simple text chunker based on character count."""
        return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

    def summarize(self, text: str) -> dict:
        """
        Generates a structured summary for the given text, using chunking for long documents.
        """
        logger.info("Generating summary...")
        
        # If text is short, summarize directly
        if len(text) < 4500:
            logger.info("Text is short. Performing direct summarization.")
            return self._summarize_text(text)

        # If text is long, use map-reduce strategy
        logger.info("Text is long. Using map-reduce summarization strategy.")
        chunks = self._chunk_text(text)
        chunk_summaries = [self._summarize_text(chunk).get("summary", "") for chunk in chunks]
        
        combined_summaries = "\n".join(chunk_summaries)
        logger.info("Generating final summary from chunk summaries.")
        return self._summarize_text(combined_summaries, is_final_summary=True)

    def _summarize_text(self, text_to_summarize: str, is_final_summary: bool = False) -> dict:
        """Helper function to call the OpenAI API for summarization."""
        try:
            if is_final_summary:
                system_prompt = """
                You are an expert summarization agent. The following text consists of several section summaries from a single document.
                Your task is to synthesize these into one single, final, coherent summary.
                Return the result as a JSON object with a single key: "summary".
                """
            else:
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
                    {"role": "user", "content": text_to_summarize}
                ]
            )
            summary_json = json.loads(response.choices[0].message.content)
            return summary_json
        except Exception as e:
            logger.error(f"Failed to generate summary part: {e}")
            return {"summary": f"Error: Could not generate summary part. Details: {e}"}