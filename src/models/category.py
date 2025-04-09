from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class CategoryBase(SQLModel):
    name: str = Field(max_length=45)
    description: str = Field(max_length=255)

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enterprise_id: Optional[int] = Field(default=None, foreign_key="enterprise.id")
    products: List["Product"] = Relationship(back_populates="category")
    enterprise: Optional["Enterprise"] = Relationship(back_populates="categories")

class CategoryCreate(CategoryBase):
    enterprise_id: int

class CategoryRead(CategoryBase):
    id: int
    enterprise_id: int

class CategoryUpdate(CategoryBase):
    pass

