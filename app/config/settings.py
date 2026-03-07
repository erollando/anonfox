from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "anonfox"
    app_version: str = "0.1.0"
    enable_spacy_ner: bool = False
    spacy_model_en: str = "en_core_web_sm"
    spacy_model_nl: str = "nl_core_news_sm"

    model_config = SettingsConfigDict(env_prefix="ANONFOX_", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
