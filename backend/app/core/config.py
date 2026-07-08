from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str = ""  # set for Azure AI Foundry / OpenAI-compatible endpoints
    openai_vision_model: str = "gpt-4o-mini"

    database_url: str = "sqlite:///./storage/foodlens.db"

    upload_dir: str = "./storage/uploads"
    export_dir: str = "./storage/exports"

    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
