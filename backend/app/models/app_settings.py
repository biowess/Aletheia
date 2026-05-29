from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class AppSettings(Base):
    """
    Key-value store for application settings that are dynamically editable at runtime.
    
    Architectural Notes:
    We use a key-value store rather than a single JSON column or dedicated typed columns to allow
    adding new settings dynamically without requiring database migrations (Alembic). It also 
    simplifies the frontend UI by allowing it to map over a list of generic settings.
    Model selection is deliberately excluded here because the application architecture uses
    fixed internal models, ensuring deterministic inference behavior across deployments and
    simplifying the user experience.
    """
    __tablename__ = "app_settings"
    
    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]
    value_type: Mapped[str]
    label: Mapped[str]
    description: Mapped[Optional[str]]
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    @classmethod
    def default_settings(cls) -> list[dict]:
        return [
            {"key": "gemini_api_key", "value": "", "value_type": "string", "label": "Gemini API Key"},
            {"key": "grounding_enabled", "value": "true", "value_type": "boolean", "label": "Enable Search Grounding"},
            {"key": "cache_ttl_hours", "value": "72", "value_type": "integer", "label": "Evidence Cache TTL (hours)"},
            {"key": "pdf_include_timeline", "value": "true", "value_type": "boolean", "label": "Include Timeline in PDF"},
            {"key": "ncbi_api_key", "value": "", "value_type": "string", "label": "NCBI API Key", "description": "Optional. Register at https://www.ncbi.nlm.nih.gov/account/ to increase PubMed rate limits from 3 to 10 requests/second. Leave blank to use the public (no-login) limit."}
        ]
