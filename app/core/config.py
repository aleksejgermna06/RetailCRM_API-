from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    
    PROJECT_NAME: str = "RetailCRM Integration API"
    VERSION: str = "1.0.0"

    RETAILCRM_API_URL: str
    RETAILCRM_API_KEY: str

    ALLOWED_ORIGINS: List[str] = ["*"]

    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

