from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"


class CustomerSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)


class InvoiceItemSchema(BaseModel):
    service_id: Optional[str] = None
    service_name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=500)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    tax_rate: float = Field(..., ge=0, le=100)

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v):
        if v < 0:
            raise ValueError('Unit price cannot be negative')
        return v


class InvoiceCreateSchema(BaseModel):
    customer: CustomerSchema
    items: List[InvoiceItemSchema]
    discount: float = Field(default=0.0, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None


class InvoiceUpdateSchema(BaseModel):
    customer: Optional[CustomerSchema] = None
    items: Optional[List[InvoiceItemSchema]] = None
    discount: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[InvoiceStatus] = None


class InvoiceResponseSchema(BaseModel):
    id: str
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    customer: CustomerSchema
    items: List[InvoiceItemSchema]
    subtotal: float
    discount: float
    tax: float
    total: float
    notes: Optional[str]
    status: InvoiceStatus

    class Config:
        from_attributes = True


class ExtractRequestSchema(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class ExtractResponseSchema(BaseModel):
    customer: CustomerSchema
    items: List[InvoiceItemSchema]
    notes: Optional[str] = None
    extraction_source: str
    unmatched_services: List[str] = Field(default_factory=list)
    discount: float = 0.0


class ServiceSchema(BaseModel):
    id: str
    service_name: str
    description: str
    unit: str
    unit_price: float
    tax_rate: float

    class Config:
        from_attributes = True


class HealthResponseSchema(BaseModel):
    status: str
