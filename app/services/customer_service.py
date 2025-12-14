from typing import List, Dict, Any
from datetime import date

from app.clients.retailcrm import RetailCRMClient
from app.models.schemas import (
    CustomerCreate,
    CustomerResponse,
    CustomerListResponse,
    CustomerFilters,
)


class CustomerService:

    def __init__(self, retailcrm_client: RetailCRMClient):

        self.client = retailcrm_client
    
    async def get_customers(self, filters: CustomerFilters) -> CustomerListResponse:

        response = await self.client.get_customers(
            name=filters.name,
            email=filters.email,
            date_from=filters.date_from,
            date_to=filters.date_to,
            limit=filters.limit,
            page=filters.page,
        )
        
        customers_data = response.get("customers", [])
        customers = [
            CustomerResponse(**customer) for customer in customers_data
        ]
        
        return CustomerListResponse(
            customers=customers,
            pagination=response.get("pagination"),
        )
    
    async def create_customer(self, customer_data: CustomerCreate) -> CustomerResponse:

        customer_dict: Dict[str, Any] = {
            "firstName": str(customer_data.firstName),
            "email": str(customer_data.email),
        }

        if customer_data.lastName:
            customer_dict["lastName"] = str(customer_data.lastName)

        if customer_data.phones and len(customer_data.phones) > 0:
            formatted_phones = []
            for phone in customer_data.phones:
                phone_number = None
                if isinstance(phone, str):
                    phone_number = str(phone).strip()
                elif isinstance(phone, dict):
                    phone_number = str(phone.get("number", "")).strip() if phone.get("number") else None
                    if not phone_number and phone:
                        first_value = next(iter(phone.values()), None)
                        if first_value:
                            phone_number = str(first_value).strip()
                else:
                    if phone is not None:
                        phone_number = str(phone).strip()

                if phone_number:
                    formatted_phones.append({"number": phone_number})

            if formatted_phones:
                customer_dict["phones"] = formatted_phones

        cleaned_dict = {}
        for key, value in customer_dict.items():
            if value is not None:
                if isinstance(value, str) and value.strip():
                    cleaned_dict[key] = value
                elif isinstance(value, (list, dict)) and value:
                    cleaned_dict[key] = value
                elif not isinstance(value, str):
                    cleaned_dict[key] = value

        if not cleaned_dict.get("firstName") or not cleaned_dict.get("email"):
            raise ValueError("firstName and email are required fields")
        
        response = await self.client.create_customer(cleaned_dict)
        
        customer = response.get("customer", {})
        return CustomerResponse(**customer)

