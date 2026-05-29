import pytest
import json
import re
from unittest.mock import AsyncMock, patch, MagicMock

# 1. Unit test: RichText-compatible token parsing
def test_cite_token_parsing():
    text = "The patient has hypertension {{cite:c1}}. Treatment includes ACE inhibitors {{cite:c2}}."
    tokens = re.findall(r'\{\{cite:(\w+)\}\}', text)
    assert tokens == ["c1", "c2"]

# 2. Unit test: Vancouver formatting
def test_format_vancouver_full():
    from app.services.citation_service import CitationFormattingService
    svc = CitationFormattingService()
    cit = {"id": "c1", "title": "ACE inhibitors in hypertension", "authors": ["Smith AB", "Jones CD"],
           "journal": "N Engl J Med", "year": 2022, "pmid": "12345678",
           "doi": "10.1056/test", "canonical_url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"}
    result = svc.format_vancouver(cit, 1)
    assert result.startswith("[1]")
    assert "Smith AB" in result
    assert "N Engl J Med" in result
    assert "2022" in result

# 3. Unit test: deduplication by PMID
def test_dedup_by_pmid():
    from app.services.citation_service import CitationFormattingService
    svc = CitationFormattingService()
    cits = [{"id": "c1", "pmid": "111", "title": "A", "canonical_url": ""},
            {"id": "c2", "pmid": "111", "title": "A duplicate", "canonical_url": ""}]
    result = svc.deduplicate_citations(cits)
    assert len(result) == 1

# 4. Integration test: mock PubMed, assert full pipeline output
@pytest.mark.asyncio
async def test_injection_with_mocked_pubmed():
    from app.services.medical_retrieval_service import MedicalRetrievalService
    mock_provider = AsyncMock()
    mock_provider.complete.side_effect = [
        json.dumps([{"sentence_index": 0, "claim": "ACE inhibitors for hypertension", "category": "treatment"}]),
        json.dumps({"strict_query": "ACE inhibitors hypertension", "relaxed_query": "ACE hypertension", "broad_query": "hypertension treatment"})
    ]
    mock_pubmed = AsyncMock()
    svc = MedicalRetrievalService(mock_provider, mock_pubmed)
    with patch.object(svc, 'search_pubmed', new=AsyncMock(return_value=["7610310"])), \
         patch.object(svc, 'fetch_pubmed_metadata', new=AsyncMock(return_value={
             "pmid": "7610310", "title": "The ALLHAT trial", "authors": ["ALLHAT Officers"],
             "journal": "JAMA", "year": 2002, "doi": None, "evidence_level": "rct"
         })):
        text = "ACE inhibitors reduce cardiovascular risk in hypertension."
        modified, citations = await svc.process_and_inject_citations(None, text)
    assert "{{cite:c1}}" in modified
    assert len(citations) == 1
    assert citations[0]["pmid"] == "7610310"

# 5. Snapshot test: Vancouver list stability
def test_vancouver_list_stable():
    from app.services.citation_service import CitationFormattingService
    svc = CitationFormattingService()
    cits = [
        {"title": "Study A", "authors": ["Alpha A"], "journal": "JAMA", "year": 2020, "pmid": "1", "canonical_url": "https://pubmed.ncbi.nlm.nih.gov/1/", "doi": None},
        {"title": "Study B", "authors": ["Beta B"], "journal": "Lancet", "year": 2021, "pmid": "2", "canonical_url": "https://pubmed.ncbi.nlm.nih.gov/2/", "doi": None},
    ]
    result = svc.format_citation_list(cits)
    assert result[0] == "[1] Alpha A. Study A. JAMA. 2020; Available: https://pubmed.ncbi.nlm.nih.gov/1/"
    assert result[1] == "[2] Beta B. Study B. Lancet. 2021; Available: https://pubmed.ncbi.nlm.nih.gov/2/"

# 6. PDF token-replacement test
def test_pdf_replace_not_strip():
    from app.export.pdf_service import PDFExportService
    svc = PDFExportService.__new__(PDFExportService)
    id_map = {"c1": 1, "c2": 2}
    text = "Hypertension is common {{cite:c1}}. ACE inhibitors are first-line {{cite:c2}}."
    result = svc._replace_cite_tokens(text, id_map)
    assert "[1]" in result
    assert "[2]" in result
    assert "{{cite:" not in result

# Edge case: empty input to process_and_inject_citations
@pytest.mark.asyncio
async def test_empty_input():
    from app.services.medical_retrieval_service import MedicalRetrievalService
    mock_provider = AsyncMock()
    mock_pubmed = AsyncMock()
    svc = MedicalRetrievalService(mock_provider, mock_pubmed)
    modified, citations = await svc.process_and_inject_citations(None, "")
    assert modified == ""
    assert citations == []

# Edge case: malformed LLM claim extraction JSON
@pytest.mark.asyncio
async def test_malformed_llm_json():
    from app.services.medical_retrieval_service import MedicalRetrievalService
    mock_provider = AsyncMock()
    mock_provider.complete.return_value = "This is not json"
    mock_pubmed = AsyncMock()
    svc = MedicalRetrievalService(mock_provider, mock_pubmed)
    modified, citations = await svc.process_and_inject_citations(None, "Some medical text.")
    assert modified == "Some medical text."
    assert citations == []
