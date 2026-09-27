from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"


@dataclass
class Customer:
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None


@dataclass
class InvoiceItem:
    service_id: Optional[str]
    service_name: str
    description: str
    quantity: int
    unit_price: float
    tax_rate: float
    amount: float = field(init=False)

    def __post_init__(self):
        self.amount = self.quantity * self.unit_price


@dataclass
class Invoice:
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    customer: Customer
    items: List[InvoiceItem]
    subtotal: float = field(init=False)
    discount: float = 0.0
    tax: float = field(init=False)
    total: float = field(init=False)
    notes: Optional[str] = None
    status: InvoiceStatus = InvoiceStatus.DRAFT

    def __post_init__(self):
        self.calculate_totals()

    def calculate_totals(self):
        self.subtotal = sum(item.amount for item in self.items)
        self.tax = sum(item.amount * (item.tax_rate / 100) for item in self.items)
        self.total = self.subtotal - self.discount + self.tax


@dataclass
class Service:
    id: str
    service_name: str
    description: str
    unit: str
    unit_price: float
    tax_rate: float
