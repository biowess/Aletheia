from abc import ABC, abstractmethod

class BaseAIProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.2
    ) -> str:
        """
        Generate a completion for the given prompt.
        """
        pass

    @abstractmethod
    async def complete_with_grounding(
        self,
        prompt: str,
        system: str = ""
    ) -> tuple[str, list[dict]]:
        """
        Generate a completion with grounding (e.g., search retrieval).
        Returns a tuple of (response_text, citations_list).
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the AI provider."""
        pass

    @property
    @abstractmethod
    def generation_model(self) -> str:
        """Name of the model used for standard generation."""
        pass

    @property
    @abstractmethod
    def grounding_model(self) -> str:
        """Name of the model used for grounded generation."""
        pass
