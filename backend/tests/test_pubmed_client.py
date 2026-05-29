"""
Unit tests for PubMedClient.

Tests cover: retry logic, caching, PMID sanitisation, API key handling,
deterministic fallback, and error-key detection.
All tests use mocked HTTP — no live network calls.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.pubmed_client import (
    PubMedClient,
    _sanitise_pmid,
    _parse_esummary_result,
    _make_fallback_metadata,
)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _make_esearch_response(pmids: list[str]) -> dict:
    """Build a minimal valid esearch JSON response."""
    return {"esearchresult": {"idlist": pmids}}


def _make_esummary_response(pmid: str, title: str = "Test Article", year: str = "2024") -> dict:
    """Build a minimal valid esummary JSON response."""
    return {
        "result": {
            "uids": [str(pmid)],
            str(pmid): {
                "uid": str(pmid),
                "pubdate": f"{year} Jan",
                "title": title,
                "authors": [{"name": "Smith J"}, {"name": "Doe A"}],
                "fulljournalname": "The Lancet",
                "source": "Lancet",
                "pubtype": [{"value": "Journal Article"}],
                "articleids": [
                    {"idtype": "pubmed", "value": str(pmid)},
                    {"idtype": "doi", "value": "10.1234/test"},
                ],
            },
        }
    }


def _make_http_response(status_code: int, json_data: dict = None):
    """Build a mock httpx.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    return resp


# ──────────────────────────────────────────────
# Unit function tests
# ──────────────────────────────────────────────

class TestSanitisePmid:
    def test_pure_numeric(self):
        assert _sanitise_pmid("12345678") == "12345678"

    def test_strips_non_numeric(self):
        assert _sanitise_pmid("abc12345xyz") == "12345"

    def test_entirely_non_numeric(self):
        assert _sanitise_pmid("abcxyz") == ""

    def test_mixed_characters(self):
        assert _sanitise_pmid("PMID: 7610310") == "7610310"


class TestParseEsummaryResult:
    def test_basic_parsing(self):
        result = _make_esummary_response("12345")["result"]["12345"]
        metadata = _parse_esummary_result("12345", result)
        assert metadata["pmid"] == "12345"
        assert metadata["title"] == "Test Article"
        assert metadata["year"] == 2024
        assert metadata["doi"] == "10.1234/test"
        assert metadata["journal"] == "The Lancet"
        assert len(metadata["authors"]) == 2
        assert metadata["evidence_level"] == "case_report"  # "Journal Article" → default

    def test_guideline_evidence_level(self):
        result = _make_esummary_response("111")["result"]["111"]
        result["pubtype"] = [{"value": "Practice Guideline"}]
        metadata = _parse_esummary_result("111", result)
        assert metadata["evidence_level"] == "guideline"

    def test_rct_evidence_level(self):
        result = _make_esummary_response("222")["result"]["222"]
        result["pubtype"] = [{"value": "Randomized Controlled Trial"}]
        metadata = _parse_esummary_result("222", result)
        assert metadata["evidence_level"] == "rct"

    def test_missing_doi(self):
        result = _make_esummary_response("333")["result"]["333"]
        result["articleids"] = [{"idtype": "pubmed", "value": "333"}]
        metadata = _parse_esummary_result("333", result)
        assert metadata["doi"] is None

    def test_missing_year(self):
        result = _make_esummary_response("444")["result"]["444"]
        result["pubdate"] = "no year here"
        metadata = _parse_esummary_result("444", result)
        assert metadata["year"] == 0


class TestMakeFallbackMetadata:
    def test_fallback_structure(self):
        fb = _make_fallback_metadata("99999")
        assert fb["pmid"] == "99999"
        assert "unavailable" in fb["title"].lower()
        assert fb["authors"] == []
        assert fb["year"] == 0
        assert fb["doi"] is None
        assert fb["evidence_level"] == "case_report"


# ──────────────────────────────────────────────
# PubMedClient integration tests (mocked HTTP)
# ──────────────────────────────────────────────

@pytest.fixture
def client_no_key():
    """PubMedClient without an API key."""
    c = PubMedClient(api_key=None)
    # Zero out rate delay for fast tests
    c._delay = 0.0
    return c


@pytest.fixture
def client_with_key():
    """PubMedClient with an API key."""
    c = PubMedClient(api_key="test_key_123")
    c._delay = 0.0
    return c


class TestRetryOn429ThenSuccess:
    @pytest.mark.asyncio
    async def test_retry_on_429_then_success(self, client_no_key):
        """Mock httpx to return 429 twice then 200 — assert metadata is returned on third attempt."""
        responses = [
            _make_http_response(429),
            _make_http_response(429),
            _make_http_response(200, _make_esummary_response("7610310")),
        ]
        client_no_key._client.get = AsyncMock(side_effect=responses)

        metadata = await client_no_key.fetch_metadata("7610310")
        assert metadata["pmid"] == "7610310"
        assert metadata["title"] == "Test Article"
        assert client_no_key._client.get.call_count == 3


class TestAllRetriesExhaustedReturnsFallback:
    @pytest.mark.asyncio
    async def test_all_retries_exhausted_returns_fallback(self, client_no_key):
        """Mock get to always return 429 — assert deterministic fallback dict (not None, no exception)."""
        client_no_key._client.get = AsyncMock(
            return_value=_make_http_response(429)
        )

        metadata = await client_no_key.fetch_metadata("7610310")
        assert metadata is not None
        assert metadata["pmid"] == "7610310"
        assert "unavailable" in metadata["title"].lower()
        assert metadata["authors"] == []
        # Should have attempted max_attempts (4) times
        assert client_no_key._client.get.call_count == 4


class TestSearchReturnsPmids:
    @pytest.mark.asyncio
    async def test_search_returns_pmids(self, client_no_key):
        """Mock get to return valid esearch JSON — assert PMID list is returned."""
        client_no_key._client.get = AsyncMock(
            return_value=_make_http_response(200, _make_esearch_response(["111", "222", "333"]))
        )

        pmids = await client_no_key.search("hypertension ACE inhibitor")
        assert pmids == ["111", "222", "333"]


class TestInMemoryCachePreventsDuplicateFetch:
    @pytest.mark.asyncio
    async def test_cache_prevents_duplicate_fetch(self, client_no_key):
        """Call fetch_metadata twice with same PMID — assert get is called only once."""
        client_no_key._client.get = AsyncMock(
            return_value=_make_http_response(200, _make_esummary_response("7610310"))
        )

        metadata1 = await client_no_key.fetch_metadata("7610310")
        metadata2 = await client_no_key.fetch_metadata("7610310")

        assert metadata1 == metadata2
        assert client_no_key._client.get.call_count == 1


class TestSearchCaching:
    @pytest.mark.asyncio
    async def test_search_caching(self, client_no_key):
        """Call search twice with same query — assert get is only called once."""
        client_no_key._client.get = AsyncMock(
            return_value=_make_http_response(200, _make_esearch_response(["111"]))
        )

        result1 = await client_no_key.search("test query")
        result2 = await client_no_key.search("test query")

        assert result1 == result2 == ["111"]
        assert client_no_key._client.get.call_count == 1


class TestPmidSanitisation:
    @pytest.mark.asyncio
    async def test_pmid_sanitisation(self, client_no_key):
        """Pass 'abc12345xyz' as PMID — assert the request uses '12345'."""
        client_no_key._client.get = AsyncMock(
            return_value=_make_http_response(200, _make_esummary_response("12345"))
        )

        metadata = await client_no_key.fetch_metadata("abc12345xyz")

        assert metadata["pmid"] == "12345"
        # Verify the actual request used sanitised PMID
        call_kwargs = client_no_key._client.get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params", {})
        assert params["id"] == "12345"


class TestNoApiKeyInParamsWhenUnset:
    @pytest.mark.asyncio
    async def test_no_api_key_in_params_when_unset(self, client_no_key):
        """Construct without key — assert api_key is absent from request params."""
        client_no_key._client.get = AsyncMock(
            return_value=_make_http_response(200, _make_esearch_response(["111"]))
        )

        await client_no_key.search("test")

        call_kwargs = client_no_key._client.get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params", {})
        assert "api_key" not in params


class TestApiKeyInParamsWhenSet:
    @pytest.mark.asyncio
    async def test_api_key_in_params_when_set(self, client_with_key):
        """Construct with key 'test_key_123' — assert api_key=test_key_123 in request params."""
        client_with_key._client.get = AsyncMock(
            return_value=_make_http_response(200, _make_esearch_response(["111"]))
        )

        await client_with_key.search("test")

        call_kwargs = client_with_key._client.get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params", {})
        assert params["api_key"] == "test_key_123"


class TestErrorKeyInResponseReturnsFallback:
    @pytest.mark.asyncio
    async def test_error_key_in_response_returns_fallback(self, client_no_key):
        """Mock get to return {"error": "..."} — assert fallback is returned."""
        error_response = {"error": "API rate limit exceeded"}
        client_no_key._client.get = AsyncMock(
            return_value=_make_http_response(200, error_response)
        )

        metadata = await client_no_key.fetch_metadata("7610310")
        assert metadata is not None
        assert "unavailable" in metadata["title"].lower()


class TestTransportErrorRetry:
    @pytest.mark.asyncio
    async def test_transport_error_retries(self, client_no_key):
        """Mock get to raise transport error then succeed — assert eventual success."""
        import httpx

        responses = [
            httpx.TransportError("Connection reset"),
            _make_http_response(200, _make_esummary_response("12345")),
        ]

        call_count = 0
        async def side_effect(*args, **kwargs):
            nonlocal call_count
            r = responses[call_count]
            call_count += 1
            if isinstance(r, Exception):
                raise r
            return r

        client_no_key._client.get = AsyncMock(side_effect=side_effect)

        metadata = await client_no_key.fetch_metadata("12345")
        assert metadata["pmid"] == "12345"
        assert metadata["title"] == "Test Article"


class TestServer5xxRetry:
    @pytest.mark.asyncio
    async def test_5xx_retries_then_succeeds(self, client_no_key):
        """Mock get to return 500 once then 200 — assert success on second attempt."""
        responses = [
            _make_http_response(500),
            _make_http_response(200, _make_esummary_response("12345")),
        ]
        client_no_key._client.get = AsyncMock(side_effect=responses)

        metadata = await client_no_key.fetch_metadata("12345")
        assert metadata["pmid"] == "12345"
        assert client_no_key._client.get.call_count == 2


class TestClientClose:
    @pytest.mark.asyncio
    async def test_close(self, client_no_key):
        """Assert close() calls aclose on the underlying httpx client."""
        client_no_key._client.aclose = AsyncMock()
        await client_no_key.close()
        client_no_key._client.aclose.assert_called_once()
