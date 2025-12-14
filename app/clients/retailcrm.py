
import httpx
from typing import Dict, List, Optional, Any
from datetime import date
from app.core.exceptions import RetailCRMAPIError


class RetailCRMClient:

    
    def __init__(self, api_url: str, api_key: str):

        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.base_url = f"{self.api_url}/api/v5"
        
    def _get_headers(self) -> Dict[str, str]:

        return {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

    async def _request(
            self,
            method: str,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    params=params,
                    json=json_data,
                )

                response.raise_for_status()
                result = response.json()

                if not result.get("success", False):
                    error_msg = result.get("errorMsg", "Unknown error")
                    if "errors" in result:
                        error_msg += f" Errors: {result['errors']}"
                    raise RetailCRMAPIError(
                        f"RetailCRM API error: {error_msg}",
                        status_code=response.status_code,
                    )

                return result

            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                try:
                    error_json = e.response.json()
                    if "errorMsg" in error_json:
                        error_detail = error_json["errorMsg"]
                    elif "errors" in error_json:
                        error_detail = str(error_json["errors"])
                except:
                    pass
                raise RetailCRMAPIError(
                    f"HTTP error {e.response.status_code}: {error_detail}",
                    status_code=e.response.status_code,
                )
            except httpx.RequestError as e:
                raise RetailCRMAPIError(
                    f"Request error: {str(e)}",
                    status_code=500,
                )
    
    async def get_customers(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:

        params = {
            "limit": limit,
            "page": page,
        }
        
        # Add filters
        if name:
            params["name"] = name
        if email:
            params["email"] = email
        if date_from:
            params["createdAtFrom"] = date_from.isoformat()
        if date_to:
            params["createdAtTo"] = date_to.isoformat()
        
        return await self._request("GET", "customers", params=params)
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:

        if "phones" in customer_data and customer_data["phones"]:
            formatted_phones = []
            for phone in customer_data["phones"]:
                if isinstance(phone, dict) and "number" in phone:
                    formatted_phones.append({"number": str(phone["number"])})
                elif isinstance(phone, str):
                    formatted_phones.append({"number": str(phone)})
            if formatted_phones:
                customer_data["phones"] = formatted_phones
            else:
                customer_data.pop("phones", None)
        
        return await self._request(
            "POST",
            "customers/create",
            json_data={"customer": customer_data},
        )
    
    async def get_customer_orders(
        self,
        customer_id: int,
        limit: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:

        params = {
            "filter[customerId]": customer_id,
            "limit": limit,
            "page": page,
        }
        
        return await self._request("GET", "orders", params=params)
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:

        return await self._request(
            "POST",
            "orders/create",
            json_data={"order": order_data},
        )
    
    async def create_payment(
        self,
        order_id: int,
        payment_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        order_response = await self._request(
            "GET",
            f"orders/{order_id}",
        )
        
        order = order_response.get("order", {})

        payments = order.get("payments", [])
        if not payments:
            payments = []

        payments.append(payment_data)

        update_data = {
            "id": order_id,
            "payments": payments,
        }
        
        return await self._request(
            "POST",
            "orders/edit",
            json_data={"order": update_data},
        )

