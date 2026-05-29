from urllib.parse import urlparse
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import BaseAIProvider

class GeminiProvider(BaseAIProvider):
    def __init__(
        self,
        api_key: str,
        generation_model: str = "gemini-3.1-flash-lite",
        grounding_model: str = "gemini-2.5-flash",
        grounding_enabled: bool = True
    ):
        if not api_key:
            raise ValueError("AI provider API key is not configured")
        
        self._client = genai.Client(api_key=api_key)
        self._generation_model = generation_model
        self._grounding_model = grounding_model
        self._grounding_enabled = grounding_enabled

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def generation_model(self) -> str:
        return self._generation_model

    @property
    def grounding_model(self) -> str:
        return self._grounding_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.2
    ) -> str:
        response = await self._client.aio.models.generate_content(
            model=self.generation_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system if system else None
            )
        )
        return response.text

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def complete_with_grounding(
        self,
        prompt: str,
        system: str = ""
    ) -> tuple[str, list[dict]]:
        # Use Google Search tool if grounding is enabled
        tools = [types.Tool(google_search=types.GoogleSearch())] if self._grounding_enabled else None
        
        response = await self._client.aio.models.generate_content(
            model=self.grounding_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system if system else None,
                tools=tools
            )
        )
        
        citations = []
        try:
            if response.candidates and hasattr(response.candidates[0], "grounding_metadata"):
                metadata = response.candidates[0].grounding_metadata
                if hasattr(metadata, "grounding_chunks") and metadata.grounding_chunks:
                    for chunk in metadata.grounding_chunks:
                        if hasattr(chunk, "web") and chunk.web:
                            uri = getattr(chunk.web, "uri", "") or ""
                            title = getattr(chunk.web, "title", "") or ""
                            citations.append({
                                "citation_text": title or "Untitled Source",
                                "source": GeminiProvider._extract_domain(uri),
                                "url": uri or None,
                            })
        except Exception:
            # Fallback to returning empty citations if parsing fails
            pass
            
        return response.text, citations

    @staticmethod
    def _extract_domain(uri: str) -> str:
        """
        Parses a URI and returns the netloc (e.g. 'pubmed.ncbi.nlm.nih.gov')
        as the human-readable source name. Returns 'Unknown Source' if the URI
        is empty or cannot be parsed into a valid netloc.
        """
        if not uri:
            return "Unknown Source"
        try:
            parsed = urlparse(uri)
            return parsed.netloc or "Unknown Source"
        except Exception:
            return "Unknown Source"
