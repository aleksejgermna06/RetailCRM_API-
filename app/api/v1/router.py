from fastapi import APIRouter

from app.api.v1.endpoints import customers, orders

api_router = APIRouter()

api_router.include_router(
    customers.router,
    prefix="/customers",
    tags=["customers"],
)

api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["orders"],
)

