from pathlib import Path
from typing import Optional

from pydantic import BaseSettings

DAGS_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    MINIO_BUCKET: Optional[str] = None
    SUCCESS_PATH: Optional[str] = None
    ERROR_PATH: Optional[str] = None
    S3_CONN_ID: Optional[str] = None
    POSTGRES_SCHEMA: Optional[str] = None
    TARGET_TABLE: Optional[str] = None
    PG_CONN_ID: Optional[str] = None
    LOCAL_PG_URL: Optional[str] = None
    AWS_ACCESS_KEY_ID: str = None
    AWS_SECRET_ACCESS_KEY: str = None
    AWS_S3_ENDPOINT_URL: str = None

    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = str(DAGS_DIR / "env" / ".env")


settings = Settings()
