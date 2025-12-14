from typing import List, Dict, Any
from datetime import datetime

from app.clients.retailcrm import RetailCRMClient
from app.models.schemas import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    PaymentCreate,
    PaymentResponse,
)


class OrderService:

    
    def __init__(self, retailcrm_client: RetailCRMClient):
        self.client = retailcrm_client
    
    async def get_customer_orders(
        self,
        customer_id: int,
        limit: int = 20,
        page: int = 1,
    ) -> OrderListResponse:
        response = await self.client.get_customer_orders(
            customer_id=customer_id,
            limit=limit,
            page=page,
        )
        
        orders_data = response.get("orders", [])
        orders = [
            OrderResponse(**order) for order in orders_data
        ]
        
        return OrderListResponse(
            orders=orders,
            pagination=response.get("pagination"),
        )
    
    async def create_order(self, order_data: OrderCreate) -> OrderResponse:

        order_dict: Dict[str, Any] = {
            "number": str(order_data.orderNumber),
            "status": str(order_data.status or "new"),
        }

        if order_data.customerId:
            order_dict["customerId"] = int(order_data.customerId)
        elif order_data.customer:
            customer_dict = order_data.customer
            formatted_customer = {}
            if isinstance(customer_dict, dict):
                if "firstName" in customer_dict:
                    formatted_customer["firstName"] = str(customer_dict["firstName"])
                if "lastName" in customer_dict:
                    formatted_customer["lastName"] = str(customer_dict["lastName"])
                if "email" in customer_dict:
                    formatted_customer["email"] = str(customer_dict["email"])
                if "phones" in customer_dict:
                    phones = customer_dict["phones"]
                    if isinstance(phones, list):
                        formatted_customer["phones"] = [
                            {"number": str(phone.get("number", phone) if isinstance(phone, dict) else phone)}
                            for phone in phones
                        ]
            order_dict["customer"] = formatted_customer

        order_dict["items"] = []
        for item in order_data.items:
            item_dict = {
                "productName": str(item.productName),
                "quantity": int(item.quantity),
                "initialPrice": float(item.price),
            }
            if item.comment:
                item_dict["comment"] = str(item.comment)
            order_dict["items"].append(item_dict)
        
        response = await self.client.create_order(order_dict)
        
        order = response.get("order", {})
        return OrderResponse(**order)
    
    async def create_payment(
        self,
        order_id: int,
        payment_data: PaymentCreate,
    ) -> PaymentResponse:

        payment_dict = payment_data.model_dump(exclude_none=True)

        payment_dict["amount"] = float(payment_dict["amount"])

        if payment_dict.get("paidAt"):
            if isinstance(payment_dict["paidAt"], datetime):
                payment_dict["paidAt"] = payment_dict["paidAt"].isoformat()
        else:
            payment_dict["paidAt"] = datetime.now().isoformat()
        
        response = await self.client.create_payment(
            order_id=order_id,
            payment_data=payment_dict,
        )

        order = response.get("order", {})
        payments = order.get("payments", [])
        
        if payments:
            last_payment = payments[-1]
            return PaymentResponse(**last_payment)

        return PaymentResponse(**payment_dict)

