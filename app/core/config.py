from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str
    langchain_tracing_v2: bool = True
    langchain_project: str = "finedge-procurement"
    max_negotiation_rounds: int = 3
    database_url: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
