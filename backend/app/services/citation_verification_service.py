import logging
from typing import List, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.reasoning.providers.base import BaseAIProvider
from app.services.medical_retrieval_service import MedicalRetrievalService
from app.services.pubmed_client import PubMedClient

logger = logging.getLogger(__name__)

class CitationVerificationService:
    """
    Acts as a wrapper for the new strict MedicalRetrievalService.

    IMPORTANT: The PubMedClient is shared with the owner (ReasoningOrchestrationService)
    and must NOT be closed between inject_citations calls. The owner is responsible for
    closing the client when the full pipeline is complete.
    """
    def __init__(self, provider: BaseAIProvider, pubmed_client: PubMedClient):
        self.provider = provider
        self.retrieval_service = MedicalRetrievalService(provider, pubmed_client)

    async def inject_citations(self, db: AsyncSession | None, text: str) -> Tuple[str, List[Dict]]:
        """
        Orchestrates the strict deterministic medical retrieval pipeline.

        NOTE: Does NOT close the underlying PubMedClient. The client is shared
        across multiple inject_citations calls within a single report generation,
        so its lifecycle is managed by the owning service.
        """
        modified_text, citations = await self.retrieval_service.process_and_inject_citations(db, text)
        return modified_text, citations
