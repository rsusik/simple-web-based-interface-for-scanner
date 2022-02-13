from typing import Optional
from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    ROOT_FOLDER: str
    IP_ADDRESS: str
    PORT: str
    SCANS_FOLDER: str
    SCANS_ADDRESS: str
    APP_FOLDER: str
    APP_ADDRESS: str
    LOG_LEVEL: str
    BUFFER_SIZE: int
    USER: Optional[str]
    GROUP: Optional[str]
    
    class Config:
        env_file = '.env'
    
@lru_cache()
def get_settings(**args):
    return Settings(**args)
