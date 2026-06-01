"""
Configuration management for the trading bot using Pydantic.
"""

import os
from typing import Optional, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from bot.exceptions import MissingCredentialError

# Load .env file explicitly
load_dotenv()

class AppConfig(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    binance_api_key: str = Field(..., alias="BINANCE_API_KEY")
    binance_api_secret: str = Field(..., alias="BINANCE_API_SECRET")
    binance_testnet: bool = Field(default=True, alias="BINANCE_TESTNET")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("binance_api_key", "binance_api_secret")
    @classmethod
    def validate_credentials(cls, v: str, info: Any) -> str:
        """
        Validates that the credentials are not empty.
        """
        if not v or v.strip() == "" or "your_api" in v.lower():
            raise MissingCredentialError(f"Required credential '{info.field_name}' is missing or is the default placeholder.")
        return v

def get_config() -> AppConfig:
    """
    Returns an instance of AppConfig after validation.
    
    Returns:
        AppConfig: Validated configuration object.
        
    Raises:
        MissingCredentialError: If required credentials are missing.
    """
    try:
        return AppConfig()
    except Exception as e:
        # Pydantic validation errors can be wrapped or re-raised
        if "BINANCE_API_KEY" in str(e) or "BINANCE_API_SECRET" in str(e):
            raise MissingCredentialError(f"Configuration validation failed: {e}") from e
        raise
