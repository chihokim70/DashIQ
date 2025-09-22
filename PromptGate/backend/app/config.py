from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str = ""
#    rebuff_api_key: str

    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_user: str = "elastic"
    elasticsearch_password: str = "krase"
    elastic_ca_cert_path: str = ""

# PostgreSQL 설정 추가
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "your_db_name"
    db_user: str = "your_user"
    db_password: str = "your_password"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    enable_es_logging: bool = True
    log_level: str = "INFO"
    env: str = "development"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
