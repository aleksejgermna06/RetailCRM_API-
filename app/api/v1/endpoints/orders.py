from fastapi import APIRouter, Depends, Query, Path

from app.core.dependencies import get_retailcrm_client
from app.clients.retailcrm import RetailCRMClient
from app.services.order_service import OrderService
from app.models.schemas import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    PaymentCreate,
    PaymentResponse,
)

router = APIRouter()


@router.get("/customer/{customer_id}", response_model=OrderListResponse)
async def get_customer_orders(
    customer_id: int = Path(..., description="Customer ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    page: int = Query(1, ge=1, description="Page number"),
    client: RetailCRMClient = Depends(get_retailcrm_client),
):

    service = OrderService(client)
    return await service.get_customer_orders(
        customer_id=customer_id,
        limit=limit,
        page=page,
    )


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    order: OrderCreate,
    client: RetailCRMClient = Depends(get_retailcrm_client),
):

    service = OrderService(client)
    return await service.create_order(order)


@router.post("/{order_id}/payments", response_model=PaymentResponse, status_code=201)
async def create_payment(
    order_id: int = Path(..., description="Order ID"),
    payment: PaymentCreate = ...,
    client: RetailCRMClient = Depends(get_retailcrm_client),
):

    service = OrderService(client)
    return await service.create_payment(order_id, payment)

