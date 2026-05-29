import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.reasoning.providers.base import BaseAIProvider
from app.services.evidence_cache_service import EvidenceCacheService
from app.reasoning.prompts import format_grounding_query

logger = logging.getLogger(__name__)

class GroundingService:
    """
    Service responsible for orchestrating evidence retrieval via AI grounding,
    caching results to minimize redundant API calls, and deduplicating citations.
    """
    
    def __init__(self, provider: BaseAIProvider, cache_service: EvidenceCacheService):
        self.provider = provider
        self.cache_service = cache_service

    async def retrieve_evidence(
        self, 
        db: AsyncSession, 
        clinical_question: str, 
        context_summary: str, 
        force_refresh: bool = False
    ) -> tuple[str, list[dict]]:
        """
        Retrieves evidence for a single clinical question, checking the cache first.
        Falls back to the AI provider if not cached or if force_refresh is True.
        """
        # We pass clinical_question as a single-element list to match format_grounding_query's expected signature
        query = format_grounding_query([clinical_question], context_summary)
        
        if not force_refresh:
            cached_entry = await self.cache_service.get_cached_evidence(db, query)
            if cached_entry:
                return cached_entry.response_text, cached_entry.citations
                
        try:
            response_text, citations = await self.provider.complete_with_grounding(query)
            
            source_urls = [c.get("url") for c in citations if "url" in c]
            
            await self.cache_service.store_evidence(
                db=db,
                query_text=query,
                response_text=response_text,
                citations=citations,
                source_urls=source_urls,
                ai_provider=self.provider.provider_name
            )
            
            return response_text, citations
            
        except Exception as e:
            logger.error(f"Grounding API call failed: {e}")
            return "Evidence retrieval unavailable.", []

    async def retrieve_evidence_for_differentials(
        self, 
        db: AsyncSession, 
        diagnoses: list[str], 
        clinical_context: str, 
        force_refresh: bool = False
    ) -> list[dict]:
        """
        Retrieves and deduplicates evidence for the top differential diagnoses.
        
        Architectural Notes:
        Grounding is limited to the top-3 diagnoses. Medical literature retrieval and 
        LLM processing are computationally expensive and rate-limited. By restricting 
        grounding to the most probable differentials (top 3), we balance the need for 
        evidence-based reasoning with system performance, API constraints, and cost, 
        ensuring the reasoning pipeline remains responsive without overwhelming the provider.
        """
        top_diagnoses = diagnoses[:3]
        all_citations = []
        seen_texts = set()

        for diag in top_diagnoses:
            _, citations = await self.retrieve_evidence(
                db=db,
                clinical_question=diag,
                context_summary=clinical_context,
                force_refresh=force_refresh
            )
            
            for citation in citations:
                text = citation.get("citation_text")
                # Deduplication should match on citation_text field
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    all_citations.append(citation)

        return all_citations
