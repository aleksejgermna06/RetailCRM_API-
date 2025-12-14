from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import List, Optional
from datetime import date, datetime


class CustomerBase(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    phones: Optional[List[dict]] = None
    
    class Config:
        populate_by_name = True


class CustomerCreate(CustomerBase):
    firstName: str = Field(..., min_length=1, description="Customer first name")
    email: EmailStr = Field(..., description="Customer email")
    phones: List[dict] = Field(default_factory=list, description="Customer phones")


class CustomerResponse(CustomerBase):
    id: int
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]
    pagination: Optional[dict] = None


# Order Schemas
class OrderItem(BaseModel):
    productName: str = Field(..., description="Product name")
    quantity: int = Field(..., gt=0, description="Product quantity")
    price: float = Field(..., ge=0, description="Product price")
    comment: Optional[str] = None


class OrderCreate(BaseModel):
    orderNumber: str = Field(..., description="Order number")
    customerId: Optional[int] = Field(None, description="Existing customer ID")
    customer: Optional[dict] = Field(None, description="New customer data (if customerId not provided)")
    items: List[OrderItem] = Field(..., min_length=1, description="Order items")
    status: Optional[str] = "new"
    
    @model_validator(mode="after")
    def validate_customer_or_id(self):
        if not self.customerId and not self.customer:
            raise ValueError("Either customerId or customer data must be provided")
        return self


class OrderResponse(BaseModel):
    id: int
    number: str
    customerId: Optional[int] = None
    status: Optional[str] = None
    items: Optional[List[dict]] = None
    createdAt: Optional[datetime] = None
    totalSumm: Optional[float] = None
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    pagination: Optional[dict] = None


# Payment Schemas
class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount")
    type: str = Field(default="cash", description="Payment type")
    status: str = Field(default="paid", description="Payment status")
    comment: Optional[str] = None
    paidAt: Optional[datetime] = Field(default_factory=datetime.now, description="Payment date")


class PaymentResponse(BaseModel):
    id: Optional[int] = None
    amount: float
    type: str
    status: str
    comment: Optional[str] = None
    paidAt: Optional[datetime] = None


class CustomerFilters(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    date_from: Optional[date] = Field(None, alias="dateFrom")
    date_to: Optional[date] = Field(None, alias="dateTo")
    limit: int = Field(20, ge=1, le=100)
    page: int = Field(1, ge=1)
    
    class Config:
        populate_by_name = True

