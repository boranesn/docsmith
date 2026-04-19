from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DOCSMITH_", env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 8192
    chroma_path: str = "./.docsmith/chroma"
    state_path: str = "./.docsmith/state.json"
    quality_threshold: float = 0.7
    max_retries: int = 3
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1500
    chunk_overlap: int = 200

    @property
    def chroma_dir(self) -> Path:
        return Path(self.chroma_path)

    @property
    def state_file(self) -> Path:
        return Path(self.state_path)


settings = Settings()
