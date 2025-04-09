from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class EnterpriseBase(SQLModel):
    name: str = Field(max_length=45)
    NIT: str = Field(max_length=30)
    email: str = Field(max_length=100)
    phone_number: str = Field(max_length=20)
    currency: str = Field(max_length=20)

class Enterprise(EnterpriseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employees: List["Employee"] = Relationship(back_populates="enterprise")
    products: List["Product"] = Relationship(back_populates="enterprise")
    categories: List["Category"] = Relationship(back_populates="enterprise")
    suppliers: List["Supplier"] = Relationship(back_populates="enterprise")

class EnterpriseCreate(EnterpriseBase):
    pass

class EnterpriseRead(EnterpriseBase):
    id: int

class EnterpriseUpdate(EnterpriseBase):
    pass