from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"

class ProductBase(SQLModel):
    name: str = Field(max_length=45)
    description: str = Field(max_length=255)
    status: ProductStatus
    stock: int
    supplier_price: float
    public_price: float
    thumbnail: str = Field(max_length=45)
    bar_code: str = Field(max_length=45)
    minimal_safe_stock: int
    discount: float

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enterprise_id: Optional[int] = Field(default=None, foreign_key="enterprise.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.id")
    
    enterprise: Optional["Enterprise"] = Relationship(back_populates="products")
    category: Optional["Category"] = Relationship(back_populates="products")
    supplier: Optional["Supplier"] = Relationship(back_populates="products")
    sales: List["Sale"] = Relationship(back_populates="product")

class ProductCreate(ProductBase):
    enterprise_id: int
    category_id: int
    supplier_id: int

class ProductRead(ProductBase):
    id: int
    enterprise_id: int
    category_id: int
    supplier_id: int

class ProductUpdate(ProductBase):
    pass