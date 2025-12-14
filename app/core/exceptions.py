from fastapi import HTTPException
from typing import Optional


class RetailCRMAPIError(HTTPException):
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        headers: Optional[dict] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

