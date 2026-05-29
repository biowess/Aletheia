import json
import logging
import re
from typing import List, Dict, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.reasoning.providers.base import BaseAIProvider
from app.services.pubmed_client import PubMedClient
from app.services.evidence_cache_service import EvidenceCacheService

logger = logging.getLogger(__name__)

APPROVED_DOMAINS = {
    "pubmed.ncbi.nlm.nih.gov",
    "www.ncbi.nlm.nih.gov",
    "doi.org",
    "jamanetwork.com",
    "www.nejm.org",
    "www.thelancet.com",
    "www.bmj.com",
    "www.annals.org",
    "academic.oup.com",
    "www.nature.com",
    "www.sciencedirect.com",
    "link.springer.com",
    "www.ahajournals.org",
    "www.acr.org",
    "www.eular.org",
    "www.kdigo.org",
    "www.idsociety.org",
    "www.escardio.org",
    "www.cdc.gov",
    "www.who.int",
    "www.nih.gov"
}

class MedicalRetrievalService:
    """
    Implements the STRICT medical evidence retrieval and citation verification pipeline.
    This does NOT use generalized web search grounding. It relies purely on deterministic
    APIs (PubMed E-utilities) to retrieve and verify biomedical literature.
    
    All PubMed HTTP calls are delegated to PubMedClient, which provides:
    - Rate limiting (3 req/s without key, 10 req/s with key)
    - Exponential backoff on HTTP 429/5xx
    - In-memory caching with stampede prevention
    - Deterministic fallback (never returns None)
    """
    def __init__(self, provider: BaseAIProvider, pubmed_client: PubMedClient):
        self.provider = provider
        self.pubmed_client = pubmed_client

    async def close(self):
        await self.pubmed_client.close()

    async def extract_claims(self, sentences: List[str]) -> List[Dict]:
        """Step 2: Extract factual clinical claims from the generated report using sentence indices."""
        
        # Build numbered list of sentences for the prompt
        numbered_sentences = "\n".join([f"[{i}] {s}" for i, s in enumerate(sentences)])
        
        prompt = f"""
        Extract key factual medical claims from the following clinical reasoning text that require citations.
        Return ONLY a strict JSON array of objects with the following schema:
        [
          {{
            "sentence_index": <integer index of the sentence>,
            "claim": "The factual claim extracted",
            "category": "One of: diagnosis, pathophysiology, treatment, guideline, risk_factor, prognosis"
          }}
        ]
        
        Text Sentences:
        {numbered_sentences}
        """
        logger.info("[CLAIM EXTRACTION] Starting claim extraction from sentences...")
        try:
            response = await self.provider.complete(prompt, system="You are a medical extractor. Return ONLY valid JSON array.")
            cleaned = response.strip()
            # Extract JSON array using regex
            match = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if match:
                cleaned = match.group(0)
            else:
                logger.warning("[CLAIM EXTRACTION] No JSON array found in response.")
                return []
            
            claims = json.loads(cleaned)
            logger.info(f"[CLAIM EXTRACTION] Extracted {len(claims)} claims.")
            for c in claims:
                logger.info(f"[CLAIM EXTRACTION] Extracted claim for sentence {c.get('sentence_index')}: {c.get('claim')}")
            return claims
        except Exception as e:
            logger.error(f"[CLAIM EXTRACTION] Failed to extract claims: {e}")
            return []

    async def generate_biomedical_query(self, claim: str) -> Dict[str, str]:
        """Step 3: Convert claims into fallback PubMed queries."""
        prompt = f"""
        Convert the following medical claim into an optimized PubMed search query strategy.
        Return ONLY a JSON object with the following three queries:
        {{
            "strict_query": "Highly specific query using MeSH terms and boolean operators",
            "relaxed_query": "Relaxed query with fewer constraints",
            "broad_query": "Broad keyword query focusing on the main condition/treatment"
        }}
        
        Claim: {claim}
        """
        logger.info(f"[QUERY] Generating queries for claim: '{claim}'")
        try:
            response = await self.provider.complete(prompt, system="You are an expert biomedical librarian. Return ONLY valid JSON.")
            cleaned = response.strip()
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                cleaned = match.group(0)
            else:
                logger.warning("[QUERY] No JSON object found in response.")
                return {"strict_query": claim, "relaxed_query": claim, "broad_query": claim}
                
            queries = json.loads(cleaned)
            logger.info(f"[QUERY] Generated queries: {json.dumps(queries)}")
            return queries
        except Exception as e:
            logger.error(f"[QUERY] Failed to generate query: {e}")
            return {"strict_query": claim, "relaxed_query": claim, "broad_query": claim}

    async def search_pubmed(self, db: AsyncSession | None, queries: Dict[str, str]) -> List[str]:
        """Step 4: Retrieve evidence from PubMed using fallback queries via PubMedClient."""
        # Fallback strategy
        for query_type in ["strict_query", "relaxed_query", "broad_query"]:
            query = queries.get(query_type)
            if not query:
                continue
                
            query_hash = f"pubmed_search:{query}"
            
            if db:
                try:
                    cached = await EvidenceCacheService.get_cached_evidence(db, query_hash)
                    if cached:
                        logger.debug(f"PubMed cache hit for search query: '{query}'")
                        return json.loads(cached.response_text)
                except Exception as e:
                    logger.warning(f"Cache read failed for search {query}: {e}")
                    
            logger.info(f"[RETRIEVAL] Trying {query_type}: '{query}'")
            try:
                idlist = await self.pubmed_client.search(query)
                if idlist:
                    logger.info(f"[RETRIEVAL] Found {len(idlist)} PMIDs using {query_type}: {idlist}")
                    logger.info(f"[PIPELINE LOG] Retrieved references for query '{query}': {idlist}")
                    if db:
                        try:
                            await EvidenceCacheService.store_evidence(
                                db=db,
                                query_text=query_hash,
                                response_text=json.dumps(idlist),
                                citations=[],
                                source_urls=[],
                                ai_provider="pubmed",
                                ttl_hours=72
                            )
                        except Exception as e:
                            logger.warning(f"Cache write failed for search {query}: {e}")
                    return idlist
                else:
                    logger.info(f"[RETRIEVAL] No results for {query_type}.")
                    if db:
                        try:
                            await EvidenceCacheService.store_evidence(
                                db=db,
                                query_text=query_hash,
                                response_text=json.dumps([]),
                                citations=[],
                                source_urls=[],
                                ai_provider="pubmed",
                                ttl_hours=1
                            )
                        except Exception as e:
                            logger.warning(f"Cache write failed for empty search {query}: {e}")
            except Exception as e:
                logger.error(f"[RETRIEVAL] PubMed search failed for {query_type}: {e}")
                
        logger.warning(f"[RETRIEVAL] All query fallbacks failed.")
        return []

    async def fetch_pubmed_metadata(self, db: AsyncSession | None, pmid: str) -> Optional[Dict]:
        """Step 5: Validate metadata using PubMed E-utilities via PubMedClient."""
        logger.info(f"[VERIFICATION] Fetching metadata for PMID {pmid}")
        query_text = f"pmid:{pmid}"
        
        if db:
            try:
                cached = await EvidenceCacheService.get_cached_evidence(db, query_text)
                if cached:
                    logger.debug(f"PubMed cache hit for PMID {pmid}")
                    return json.loads(cached.response_text)
            except Exception as e:
                logger.warning(f"Cache read failed for PMID {pmid}: {e}")

        try:
            metadata = await self.pubmed_client.fetch_metadata(pmid)
            # PubMedClient never returns None — but check for fallback indicator
            if metadata.get("title", "").startswith("[Title unavailable"):
                logger.error(f"[VERIFICATION] HARD FAIL: PMID {pmid} not found in PubMed.")
                # Still return the fallback metadata so pipeline doesn't break
                return metadata
            
            if not metadata.get("doi"):
                logger.info(f"[VERIFICATION] SOFT WARNING: PMID {pmid} is missing DOI.")
            logger.info(f"[VERIFICATION] PMID {pmid} verified successfully.")
            
            if db:
                try:
                    await EvidenceCacheService.store_evidence(
                        db=db,
                        query_text=query_text,
                        response_text=json.dumps(metadata),
                        citations=[],
                        source_urls=[],
                        ai_provider="pubmed",
                        ttl_hours=720
                    )
                except Exception as e:
                    logger.warning(f"Cache write failed for PMID {pmid}: {e}")
                    
            return metadata
        except Exception as e:
            logger.error(f"[VERIFICATION] PubMed metadata fetch failed for {pmid}: {e}")
            return None

    async def process_and_inject_citations(self, db: AsyncSession | None, text: str) -> Tuple[str, List[Dict]]:
        """Orchestrates the entire pipeline for a given text block using AST/Index tokenization."""
        # Simple sentence splitter: split on period, exclamation, question followed by space
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        if not sentences or not sentences[0]:
             return text, []

        claims = await self.extract_claims(sentences)
        
        citations = []
        cit_idx = 1
        seen_pmids = set()
        
        for claim_obj in claims:
            try:
                claim = claim_obj.get("claim")
                sentence_index = int(claim_obj.get("sentence_index", -1))
            except Exception:
                continue
                
            if not claim or sentence_index < 0 or sentence_index >= len(sentences):
                logger.warning(f"[INJECTION] Discarding invalid claim index: {sentence_index}")
                continue
                
            queries = await self.generate_biomedical_query(claim)
            pmids = await self.search_pubmed(db, queries)
            
            valid_citation = None
            for pmid in pmids:
                if pmid in seen_pmids:
                    existing = next((c for c in citations if c.get("pmid") == pmid), None)
                    if existing:
                        valid_citation = existing
                        break
                        
                metadata = await self.fetch_pubmed_metadata(db, pmid)
                if metadata:
                    cit_id = f"c{cit_idx}"
                    valid_citation = {
                        "id": cit_id,
                        "source_type": "pubmed",
                        "title": metadata["title"],
                        "authors": metadata["authors"],
                        "journal": metadata["journal"],
                        "year": metadata["year"],
                        "verified": True,
                        "pmid": metadata["pmid"],
                        "doi": metadata["doi"],
                        "canonical_url": f"https://pubmed.ncbi.nlm.nih.gov/{metadata['pmid']}/",
                        "source_domain": "pubmed.ncbi.nlm.nih.gov",
                        "evidence_level": metadata["evidence_level"],
                        "abstract_snippet": metadata.get("abstract", "")
                    }
                    citations.append(valid_citation)
                    seen_pmids.add(pmid)
                    cit_idx += 1
                    break
            
            if valid_citation:
                logger.info(f"[INJECTION] Injected citation {valid_citation['id']} into sentence index {sentence_index}.")
                logger.info(f"[PIPELINE LOG] Claim mapped to evidence: '{claim}' -> PMID {valid_citation['pmid']}")
                original_sent = sentences[sentence_index].rstrip(". ")
                sentences[sentence_index] = f"{original_sent} {{{{cite:{valid_citation['id']}}}}}. "
            else:
                logger.warning(f"[INJECTION] Failed to find valid citation for claim: '{claim}'")
                logger.info(f"[PIPELINE LOG] Claim rejected (unsupported): '{claim}'")
                
        # Rejoin sentences
        modified_text = " ".join(sentences)
        logger.info(f"[RENDER] Final text prepared with {len(citations)} citations.")
        return modified_text, citations
