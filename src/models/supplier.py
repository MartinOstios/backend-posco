from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import EmailStr

class SupplierBase(SQLModel):
    name: str = Field(max_length=45)
    email: EmailStr = Field(max_length=255)
    phone_number: str = Field(max_length=45)
    NIT: str = Field(max_length=45)

class Supplier(SupplierBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enterprise_id: Optional[int] = Field(default=None, foreign_key="enterprise.id")
    products: List["Product"] = Relationship(back_populates="supplier")
    enterprise: Optional["Enterprise"] = Relationship(back_populates="suppliers")

class SupplierCreate(SupplierBase):
    enterprise_id: int

class SupplierRead(SupplierBase):
    id: int
    enterprise_id: int

class SupplierUpdate(SupplierBase):
    pass