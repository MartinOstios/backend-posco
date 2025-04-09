from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import date

class SaleBase(SQLModel):
    quantity: int
    discount: float
    price: float
    sell_date: date
    total_price: float

class Sale(SaleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: Optional[int] = Field(default=None, foreign_key="invoice.id")
    client_id: Optional[int] = Field(default=None, foreign_key="client.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    
    invoice: Optional["Invoice"] = Relationship(back_populates="sales")
    client: Optional["Client"] = Relationship(back_populates="sales")
    product: Optional["Product"] = Relationship(back_populates="sales")

class SaleCreate(SaleBase):
    invoice_id: int
    client_id: int
    product_id: int

class SaleRead(SaleBase):
    id: int
    invoice_id: int
    client_id: int
    product_id: int

class SaleUpdate(SaleBase):
    pass