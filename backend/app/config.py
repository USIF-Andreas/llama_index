from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str
    openrouter_embedding_model: str
    google_client_secret: Path
    google_token: Path
    cors_origins: str


def get_settings() -> Settings:
    data_dir = Path(os.getenv("DATA_DIR", "/data"))
    data_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        data_dir=data_dir,
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct"),
        openrouter_embedding_model=os.getenv("OPENROUTER_EMBEDDING_MODEL", "text-embedding-3-small"),
        google_client_secret=Path(os.getenv("GOOGLE_CLIENT_SECRET", str(data_dir / "google" / "client_secret.json"))),
        google_token=Path(os.getenv("GOOGLE_TOKEN", str(data_dir / "google" / "token.json"))),
        cors_origins=os.getenv("CORS_ORIGINS", "*")
    )
