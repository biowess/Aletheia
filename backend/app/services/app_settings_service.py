import json
import logging
import keyring
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.app_settings import AppSettings

logger = logging.getLogger(__name__)

class AppSettingsService:
    """
    Architectural Notes:
    - This service strictly prohibits creating or deleting setting keys to maintain
      schema integrity and avoid unexpected configurations. Keys should only be added
      via migrations or initial default seeding.
    - Providing `get_typed_value` allows backend services (like AI providers and reasoning tools) 
      to read settings at runtime seamlessly without server restarts or duplicate parsing logic.
    - API keys are securely stored in the OS keyring using the `keyring` package.
    """

    @staticmethod
    async def get_all_settings(db: AsyncSession) -> list[AppSettings]:
        result = await db.execute(select(AppSettings).order_by(AppSettings.key))
        settings_list = list(result.scalars().all())
        # Note: For bulk retrieval, we don't query keyring for every key to avoid performance hits or unlocking prompts.
        # The frontend will just see the dummy "********" or empty value, which is desired.
        return settings_list

    @staticmethod
    async def get_setting(db: AsyncSession, key: str) -> AppSettings | None:
        setting = await db.get(AppSettings, key)
        return setting

    @staticmethod
    async def get_setting_value(db: AsyncSession, key: str, default: str = "") -> str:
        if key.endswith("_api_key"):
            try:
                secret = keyring.get_password("aletheia", key)
                if secret:
                    return secret
            except Exception as e:
                logger.warning(f"Failed to retrieve {key} from keyring: {e}. Falling back to database storage.")

        setting = await AppSettingsService.get_setting(db, key)
        if setting:
            return setting.value
        return default

    @staticmethod
    async def update_setting(db: AsyncSession, key: str, value: str) -> AppSettings | None:
        setting = await AppSettingsService.get_setting(db, key)
        if setting:
            if key.endswith("_api_key"):
                try:
                    # Test if we can access the keyring
                    keyring.set_password("aletheia", key, value)
                    # Verify it actually stuck, some keyrings silently fail
                    test_val = keyring.get_password("aletheia", key)
                    if test_val != value:
                        raise RuntimeError("Keyring silently failed to store the secret.")
                    setting.value = "********" # Store a dummy masked value in SQLite
                except Exception as e:
                    logger.warning(f"Keyring unavailable ({e}). WARNING: Falling back to unencrypted plaintext storage in database for {key}.")
                    setting.value = value
            else:
                setting.value = value
                
            await db.flush()
            return setting
        return None

    @staticmethod
    async def get_typed_value(db: AsyncSession, key: str) -> bool | int | str | dict | None:
        setting = await AppSettingsService.get_setting(db, key)
        if not setting:
            return None
        
        if key.endswith("_api_key"):
            secret = await AppSettingsService.get_setting_value(db, key)
            return secret

        value = setting.value
        value_type = setting.value_type

        try:
            if value_type == "boolean":
                return value.lower() == "true"
            elif value_type == "integer":
                return int(value)
            elif value_type == "json":
                return json.loads(value)
            elif value_type == "string":
                return value
        except (ValueError, json.JSONDecodeError):
            return value

        return value
