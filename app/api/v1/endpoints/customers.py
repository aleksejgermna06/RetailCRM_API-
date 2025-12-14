from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date

from app.core.dependencies import get_retailcrm_client
from app.clients.retailcrm import RetailCRMClient
from app.services.customer_service import CustomerService
from app.models.schemas import (
    CustomerCreate,
    CustomerResponse,
    CustomerListResponse,
    CustomerFilters,
)

router = APIRouter()


@router.get("/", response_model=CustomerListResponse)
async def get_customers(
    name: Optional[str] = Query(None, description="Filter by customer name"),
    email: Optional[str] = Query(None, description="Filter by customer email"),
    date_from: Optional[date] = Query(None, alias="dateFrom", description="Filter by registration date from"),
    date_to: Optional[date] = Query(None, alias="dateTo", description="Filter by registration date to"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    page: int = Query(1, ge=1, description="Page number"),
    client: RetailCRMClient = Depends(get_retailcrm_client),
):

    service = CustomerService(client)
    filters = CustomerFilters(
        name=name,
        email=email,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        page=page,
    )
    return await service.get_customers(filters)


@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(
    customer: CustomerCreate,
    client: RetailCRMClient = Depends(get_retailcrm_client),
):

    service = CustomerService(client)
    return await service.create_customer(customer)





