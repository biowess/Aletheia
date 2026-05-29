"""
Configuration management for the FastAPI backend.

Architectural Notes:
We use `pydantic-settings` over plain `os.environ` for the following reasons:
1. Type Safety & Validation: Automatically casts environment variables to correct types (e.g., bools, ints, lists) and fails fast on invalid data.
2. Default Values: Allows cleanly specifying fallbacks and defaults directly in the schema without littering the codebase with `.get("VAR", default)`.
3. Centralized Schema: Provides a single source of truth for all configuration options, improving discoverability and making it easy to see all available settings.
4. Auto-documentation: Provides `description` fields which can be exported and used in documentation.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union, Any

import os
from pathlib import Path

# Create data directory respecting XDG Base Directory Specification
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "aletheia"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Runtime check for read-only filesystem
if not os.access(DATA_DIR, os.W_OK):
    raise RuntimeError(f"FATAL: The data directory {DATA_DIR} is read-only. Aletheia requires a writable directory to store the database and exports.")

class Settings(BaseSettings):
    app_name: str = Field(default="Clinical Reasoning Workstation", description="The name of the application")
    app_version: str = Field(default="0.1.0", description="The version of the application")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    database_url: str = Field(default=f"sqlite+aiosqlite:///{DATA_DIR}/clinical_workstation.db", description="Database connection URL")
    
    # Defaults to empty string to ensure the app does not crash on startup if not provided
    gemini_api_key: str = Field(default="", description="API key for Gemini provider")
    gemini_model: str = Field(default="gemini-3.1-flash-lite", description="Gemini generation model to use")
    gemini_grounding_enabled: bool = Field(default=True, description="Enable grounding for Gemini")
    
    max_evidence_cache_age_hours: int = Field(default=72, description="Maximum age of cached evidence in hours")
    pdf_output_dir: str = Field(default=str(DATA_DIR / "exports"), description="Directory to output generated PDFs")
    
    backend_host: str = Field(default="127.0.0.1", description="Host to bind the backend server to (loopback-only for local-first security)")
    backend_port: int = Field(default=8000, description="Port to bind the backend server to")
    
    cors_origins: List[str] = Field(default=["http://localhost:5173"], description="List of allowed CORS origins")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
