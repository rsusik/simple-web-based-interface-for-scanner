from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    API_HOSTNAME: str
    API_PORT: str
    DOMAIN_URL_API: str
    DOMAIN_URL_CLIENT: str
    SCANS_DESTINATION: str
    LOG_LEVEL: str
    BUFFER_SIZE: int

    class Config:
        env_file = ".env"
    
@lru_cache()
def get_settings():
    return Settings()