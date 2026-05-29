import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.reasoning import ReasoningRequest, PreprocessingResult
from app.schemas.case import (
    AnamnesisSchema,
    PhysicalExamSchema,
    LaboratoryDataSchema,
    MorphologicalDataSchema,
)
from app.services.reasoning_service import ReasoningOrchestrationService
from app.models.report_version import ReportVersion

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.complete = AsyncMock(return_value="mocked ai response")
    provider.provider_name = "test_provider"
    provider.generation_model = "test_model"
    return provider

@pytest.fixture
def mock_grounding_service():
    return MagicMock()

@pytest.fixture
def mock_citation_service():
    service = MagicMock()
    service.deduplicate_citations.side_effect = lambda x: x
    return service

@pytest.fixture
def mock_parser():
    parser = MagicMock()
    parser.parse_reasoning_response = MagicMock(return_value={
        "summary": {
            "overview": "Original overview text",
            "severity": "moderate"
        },
        "citations": []
    })
    return parser

@pytest.fixture
def mock_preprocessing_engine():
    engine = MagicMock()
    engine.run = MagicMock(return_value=PreprocessingResult())
    return engine

@pytest.fixture
def orchestration_service(
    mock_provider,
    mock_grounding_service,
    mock_citation_service,
    mock_parser,
    mock_preprocessing_engine
):
    service = ReasoningOrchestrationService(
        provider=mock_provider,
        grounding_service=mock_grounding_service,
        citation_service=mock_citation_service,
        parser=mock_parser,
        preprocessing_engine=mock_preprocessing_engine
    )
    service.citation_verification_service = AsyncMock()
    service.citation_verification_service.inject_citations = AsyncMock(
        return_value=("Modified overview text {{cite:c1}}", [{"id": "c1", "text": "Citation 1"}])
    )
    return service

@pytest.fixture
def base_request():
    return ReasoningRequest(
        case_id="123e4567-e89b-12d3-a456-426614174000",
        anamnesis=AnamnesisSchema(),
        physical_exam=PhysicalExamSchema(),
        laboratory_data=LaboratoryDataSchema(),
        morphological_data=MorphologicalDataSchema(),
        use_grounding=True
    )

@pytest.mark.asyncio
@patch("app.services.reasoning_service.CaseService.get_case")
@patch("app.services.reasoning_service.ReportVersionService.get_latest_report_version")
@patch("app.services.reasoning_service.ReportVersionService.create_report_version")
async def test_generate_report_use_grounding_true(
    mock_create_report,
    mock_get_latest,
    mock_get_case,
    orchestration_service,
    mock_db,
    base_request
):
    mock_get_case.return_value = MagicMock()
    mock_get_latest.return_value = None
    mock_create_report.return_value = ReportVersion(version_number=1)

    report = await orchestration_service.generate_report(mock_db, base_request)

    # Assert inject_citations was called
    orchestration_service.citation_verification_service.inject_citations.assert_called_once_with(mock_db, "Original overview text")
    
    # Assert correct parameters were passed to create_report_version
    called_report_data = mock_create_report.call_args[1]["report_data"]
    assert called_report_data["summary"]["overview"] == "Modified overview text {{cite:c1}}"
    assert called_report_data["citations"] == [{"id": "c1", "text": "Citation 1"}]

@pytest.mark.asyncio
@patch("app.services.reasoning_service.CaseService.get_case")
@patch("app.services.reasoning_service.ReportVersionService.get_latest_report_version")
@patch("app.services.reasoning_service.ReportVersionService.create_report_version")
async def test_generate_report_use_grounding_false(
    mock_create_report,
    mock_get_latest,
    mock_get_case,
    orchestration_service,
    mock_db,
    base_request
):
    mock_get_case.return_value = MagicMock()
    mock_get_latest.return_value = None
    mock_create_report.return_value = ReportVersion(version_number=1)
    
    base_request.use_grounding = False

    report = await orchestration_service.generate_report(mock_db, base_request)

    # Assert inject_citations was STILL called despite use_grounding=False
    orchestration_service.citation_verification_service.inject_citations.assert_called_once_with(mock_db, "Original overview text")
    
    # Assert correct parameters were passed to create_report_version
    called_report_data = mock_create_report.call_args[1]["report_data"]
    assert called_report_data["summary"]["overview"] == "Modified overview text {{cite:c1}}"
    assert called_report_data["citations"] == [{"id": "c1", "text": "Citation 1"}]
    assert called_report_data["grounding_used"] is False

@pytest.mark.asyncio
@patch("app.services.reasoning_service.CaseService.get_case")
@patch("app.services.reasoning_service.ReportVersionService.get_latest_report_version")
@patch("app.services.reasoning_service.ReportVersionService.create_report_version")
async def test_generate_report_citation_injection_fails(
    mock_create_report,
    mock_get_latest,
    mock_get_case,
    orchestration_service,
    mock_db,
    base_request
):
    mock_get_case.return_value = MagicMock()
    mock_get_latest.return_value = None
    mock_create_report.return_value = ReportVersion(version_number=1)
    
    # Mock inject_citations to raise an exception
    orchestration_service.citation_verification_service.inject_citations.side_effect = Exception("API error")

    # Should not raise exception
    report = await orchestration_service.generate_report(mock_db, base_request)

    # Assert inject_citations was called
    orchestration_service.citation_verification_service.inject_citations.assert_called_once_with(mock_db, "Original overview text")
    
    # Assert citations array is empty
    called_report_data = mock_create_report.call_args[1]["report_data"]
    assert called_report_data["summary"]["overview"] == "Original overview text"
    assert called_report_data["citations"] == []
