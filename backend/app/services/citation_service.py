import re
from typing import List, Dict, Optional, Any


class CitationFormattingService:
    """
    Utility service for citation management.
    
    Schema v2: Works with structured Citation objects (id, label, source_type, url, title, etc.)
    instead of the old flat {citation_text, source, url} format.
    """

    def deduplicate_citations(self, citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Removes duplicate citations by PMID (primary), DOI, URL, and title (fallback).
        Preserves the order of the first occurrence.
        """
        if not citations:
            return []

        seen = set()
        unique = []
        for cit in citations:
            if not isinstance(cit, dict):
                continue
            key = cit.get("pmid") or cit.get("doi") or cit.get("canonical_url") or cit.get("url") or cit.get("title", "").lower()
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            unique.append(cit)
        return unique

    def merge_grounding_into_citations(
        self,
        existing_citations: List[Dict[str, Any]],
        grounding_chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Converts raw grounding chunks from the AI provider into structured
        Citation objects and merges them with existing LLM-generated citations.
        Assigns unique IDs to avoid collisions.
        """
        existing_ids = {c.get("id") for c in existing_citations if isinstance(c, dict)}
        merged = list(existing_citations)

        for i, gc in enumerate(grounding_chunks):
            if not isinstance(gc, dict):
                continue

            # Generate unique ID
            cid = f"g{i + 1}"
            while cid in existing_ids:
                cid = f"g{i + 1}_{len(existing_ids)}"
            existing_ids.add(cid)

            url = gc.get("url", "")
            citation_text = gc.get("citation_text", "")

            merged.append({
                "id": cid,
                "label": (citation_text or "Source")[:40],
                "source_type": "web",
                "url": url or "",
                "title": citation_text or "",
                "journal": None,
                "year": None,
                "authors": None,
            })

        return self.deduplicate_citations(merged)

    def format_vancouver(self, citation: Optional[Dict[str, Any]], index: int) -> str:
        """
        Formats a structured Citation dict into a Vancouver-style reference string.
        Used by the PDF export pipeline.
        """
        if not citation:
            return f"[{index}] [Missing citation data]"
        parts = []
        authors = citation.get("authors") or []
        if authors:
            # Vancouver: Last FM, Last FM, Last FM. Up to 6, then et al.
            fmt_authors = [a for a in authors[:6]]
            suffix = " et al." if len(authors) > 6 else "."
            parts.append(", ".join(fmt_authors) + suffix)
        title = (citation.get("title") or citation.get("label") or "[Untitled]").rstrip(".")
        parts.append(title + ".")
        journal = citation.get("journal") or ""
        year = citation.get("year")
        if year == 0 or str(year) == "0":
            year = ""
        else:
            year = str(year) if year else ""
            
        if journal:
            parts.append(f"{journal}. {year};" if year else f"{journal}.")
        elif year:
            parts.append(f"{year}.")
        doi = citation.get("doi")
        if doi:
            parts.append(f"doi:{doi}")
        pmid = citation.get("pmid")
        url = citation.get("canonical_url") or citation.get("url") or ""
        if url:
            parts.append(f"Available: {url}")
        return f"[{index}] " + " ".join(parts)

    def format_citation_list(self, citations: List[Dict[str, Any]]) -> List[str]:
        """
        Formats a list of Citation dicts into Vancouver-style strings.
        Used by the PDF export pipeline.
        """
        if not citations:
            return []
        return [self.format_vancouver(cit, i + 1) for i, cit in enumerate(citations)]
