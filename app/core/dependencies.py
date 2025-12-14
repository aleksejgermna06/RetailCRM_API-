from functools import lru_cache

from app.clients.retailcrm import RetailCRMClient
from app.core.config import settings


@lru_cache()
def get_retailcrm_client() -> RetailCRMClient:
    return RetailCRMClient(
        api_url=settings.RETAILCRM_API_URL,
        api_key=settings.RETAILCRM_API_KEY,
    )

