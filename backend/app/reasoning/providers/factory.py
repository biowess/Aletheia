from .base import BaseAIProvider
from .gemini import GeminiProvider

def get_ai_provider(api_key: str, grounding: bool) -> BaseAIProvider:
    """
    Factory function to get the configured AI provider.
    Currently always returns the Gemini provider, but provides architectural
    separation for future extensibility.
    """
    return GeminiProvider(api_key=api_key, grounding_enabled=grounding)
