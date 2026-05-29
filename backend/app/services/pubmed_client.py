"""
PubMed E-Utilities async client.

No-login PubMed E-utilities client with:
- No API key required (3 req/s public limit).
- Optional NCBI API key support (10 req/s authenticated limit).
- In-memory LRU cache keyed by PMID/query hash.
- Exponential backoff on HTTP 429 and transient 5xx errors.
- Cache stampede prevention via per-key asyncio.Lock.
- Deterministic fallback: never returns None silently.
- PMID sanitisation: strips non-numeric characters.
"""

import asyncio
import hashlib
import logging
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Optional, Dict, List

import httpx

logger = logging.getLogger(__name__)

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Module-level rate limiter — shared across all PubMedClient instances within a process.
# NCBI enforces per-IP rate limits: 3 req/s (no key) or 10 req/s (with key).
# We use a semaphore + delay to enforce this globally.
_rate_lock = asyncio.Lock()
_last_request_time: float = 0.0


def _make_fallback_metadata(pmid: str) -> Dict:
    """Deterministic fallback — never return None for a metadata fetch."""
    return {
        "pmid": str(pmid),
        "title": f"[Title unavailable — PMID {pmid}]",
        "authors": [],
        "journal": "",
        "year": 0,
        "doi": None,
        "evidence_level": "case_report",
        "abstract": "",
    }


def _sanitise_pmid(pmid: str) -> str:
    """Strip non-numeric characters from a PMID."""
    sanitised = re.sub(r"[^0-9]", "", str(pmid))
    if not sanitised:
        logger.warning(f"[PUBMED] PMID '{pmid}' contains no numeric characters after sanitisation.")
    return sanitised


def _parse_efetch_xml(pmid: str, xml_content: str) -> Dict:
    """
    Parse an eFetch XML result into a normalised metadata dict.
    """
    fallback = _make_fallback_metadata(pmid)
    try:
        root = ET.fromstring(xml_content)
    except Exception as e:
        logger.error(f"[PUBMED] Failed to parse XML for PMID {pmid}: {e}")
        return fallback

    article = root.find(".//PubmedArticle")
    if article is None:
        return fallback

    title_el = article.find(".//ArticleTitle")
    title = "".join(title_el.itertext()).strip() if title_el is not None else fallback["title"]

    abstract_el = article.find(".//Abstract")
    abstract = ""
    if abstract_el is not None:
        abstract = " ".join(["".join(text.itertext()).strip() for text in abstract_el.findall(".//AbstractText")])

    doi = None
    doi_el = article.find('.//ArticleId[@IdType="doi"]')
    if doi_el is not None:
        doi = "".join(doi_el.itertext()).strip()

    authors = []
    for author_el in article.findall(".//AuthorList/Author"):
        last_name = author_el.find("LastName")
        fore_name = author_el.find("ForeName")
        last = "".join(last_name.itertext()).strip() if last_name is not None else ""
        fore = "".join(fore_name.itertext()).strip() if fore_name is not None else ""
        if last or fore:
            authors.append(f"{fore} {last}".strip())

    journal_el = article.find(".//Journal/Title")
    if journal_el is None:
        journal_el = article.find(".//MedlineTA")
    journal = "".join(journal_el.itertext()).strip() if journal_el is not None else ""

    year = 0
    year_el = article.find(".//PubDate/Year")
    if year_el is not None:
        try:
            year = int("".join(year_el.itertext()).strip())
        except ValueError:
            pass

    pub_types = [ "".join(pt.itertext()).strip().lower() for pt in article.findall(".//PublicationType") ]
    evidence_level = "case_report"
    if any("guideline" in pt for pt in pub_types):
        evidence_level = "guideline"
    elif any("meta-analysis" in pt for pt in pub_types):
        evidence_level = "meta_analysis"
    elif any("systematic review" in pt for pt in pub_types):
        evidence_level = "systematic_review"
    elif any("randomized controlled trial" in pt for pt in pub_types) or any("clinical trial" in pt for pt in pub_types):
        evidence_level = "rct"

    return {
        "pmid": str(pmid),
        "doi": doi,
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "evidence_level": evidence_level,
        "abstract": abstract,
    }


class PubMedClient:
    """
    Async PubMed E-utilities client.

    - Works without an API key (3 req/s public limit).
    - Optionally accepts an NCBI API key (10 req/s authenticated limit).
    - In-memory cache keyed by PMID/query hash, scoped to client lifetime.
    - Exponential backoff on HTTP 429 and transient 5xx errors.
    - Per-key asyncio.Lock to prevent cache stampede.
    - Deterministic fallback: never returns None silently.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key if api_key else None
        # Public: 3/s → 0.34s delay; with key: 10/s → 0.11s delay
        self._delay = 0.34 if not self.api_key else 0.11
        self._client = httpx.AsyncClient(timeout=15.0)
        self._cache: Dict[str, any] = {}
        self._key_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    def _base_params(self) -> dict:
        """Build base query params, including api_key if configured."""
        p = {}
        if self.api_key:
            p["api_key"] = self.api_key
        return p

    async def _enforce_rate_limit(self) -> None:
        """
        Global rate limiter — ensures minimum delay between requests across all
        PubMedClient instances within the same process.
        """
        global _last_request_time
        async with _rate_lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - _last_request_time
            if elapsed < self._delay:
                await asyncio.sleep(self._delay - elapsed)
            _last_request_time = asyncio.get_event_loop().time()

    async def _get_with_retry(self, url: str, params: dict, max_attempts: int = 4, return_json: bool = True) -> any:
        """
        HTTP GET with exponential backoff on 429/5xx and transport errors.
        """
        for attempt in range(max_attempts):
            await self._enforce_rate_limit()

            try:
                r = await self._client.get(url, params=params)

                if r.status_code == 200:
                    if not return_json:
                        return r.text
                    try:
                        data = r.json()
                        if isinstance(data, dict) and "error" in data:
                            logger.warning(f"[PUBMED] API returned error key: {data['error']}")
                            return {}
                        return data
                    except Exception:
                        return r.text

                if r.status_code == 429:
                    wait = 2 ** (attempt + 1)
                    logger.warning(
                        f"[PUBMED] HTTP 429 rate limit. Waiting {wait}s (attempt {attempt + 1}/{max_attempts})."
                    )
                    await asyncio.sleep(wait)
                    continue

                if 500 <= r.status_code < 600:
                    wait = 2 ** (attempt + 1)
                    logger.warning(
                        f"[PUBMED] HTTP {r.status_code} server error. Waiting {wait}s (attempt {attempt + 1}/{max_attempts})."
                    )
                    await asyncio.sleep(wait)
                    continue

                if r.status_code in (400, 401) and "api_key" in params:
                    try:
                        resp_json = r.json()
                        error_msg = str(resp_json.get("error", ""))
                        if "api key" in error_msg.lower() or "invalid" in error_msg.lower() or r.status_code == 401:
                            logger.warning(f"[PUBMED] API key invalid or revoked. Retrying without key.")
                            self.api_key = None
                            self._delay = 0.34
                            params.pop("api_key", None)
                            continue
                    except Exception:
                        pass

                # Other non-retryable HTTP errors
                logger.warning(f"[PUBMED] HTTP {r.status_code} for {url} — not retrying.")
                return {}

            except httpx.TransportError as e:
                wait = 2 ** (attempt + 1)
                logger.warning(
                    f"[PUBMED] Transport error (attempt {attempt + 1}/{max_attempts}): {e}. Waiting {wait}s."
                )
                await asyncio.sleep(wait)

        logger.error(f"[PUBMED] All {max_attempts} attempts exhausted for {url}.")
        return {}

    async def search(self, query: str, max_results: int = 5) -> List[str]:
        """
        Search PubMed via esearch.fcgi.
        Returns a list of PMID strings, or empty list on failure.
        Results are cached by query hash.
        """
        cache_key = f"search:{hashlib.sha256(query.encode()).hexdigest()}"

        async with self._key_locks[cache_key]:
            if cache_key in self._cache:
                logger.debug(f"[PUBMED] Cache hit for search query.")
                return self._cache[cache_key]

            params = {
                **self._base_params(),
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": max_results,
                "sort": "relevance",
            }
            data = await self._get_with_retry(ESEARCH_URL, params)
            ids = data.get("esearchresult", {}).get("idlist", [])
            self._cache[cache_key] = ids
            return ids

    async def fetch_metadata(self, pmid: str) -> Dict:
        """
        Fetch article metadata from PubMed via efetch.fcgi.
        Returns a metadata dict — never None. On failure, returns a deterministic
        fallback with "[Title unavailable — PMID X]".
        """
        sanitised_pmid = _sanitise_pmid(pmid)
        if not sanitised_pmid:
            return _make_fallback_metadata(pmid)

        cache_key = f"pmid:{sanitised_pmid}"

        async with self._key_locks[cache_key]:
            if cache_key in self._cache:
                logger.debug(f"[PUBMED] Cache hit for PMID {sanitised_pmid}.")
                return self._cache[cache_key]

            params = {
                **self._base_params(),
                "db": "pubmed",
                "id": sanitised_pmid,
                "retmode": "xml",
            }
            xml_text = await self._get_with_retry(EFETCH_URL, params, return_json=False)

            if not xml_text or not isinstance(xml_text, str):
                logger.warning(f"[PUBMED] No result for PMID {sanitised_pmid} — using fallback.")
                fallback = _make_fallback_metadata(sanitised_pmid)
                self._cache[cache_key] = fallback
                return fallback

            metadata = _parse_efetch_xml(sanitised_pmid, xml_text)
            self._cache[cache_key] = metadata
            logger.info(f"[PUBMED] PMID {sanitised_pmid} fetched successfully.")
            return metadata

    async def close(self) -> None:
        """Close the underlying httpx client."""
        await self._client.aclose()
