from typing import Optional, List
from sqlmodel import Session, select
from src.models.category import Category, CategoryCreate, CategoryUpdate
from .base import CRUDBase

class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, session: Session, *, name: str) -> Optional[Category]:
        return session.exec(select(Category).where(Category.name == name)).first()

    def get_products(self, session: Session, *, category_id: int) -> List["Product"]:
        category = self.get(session=session, id=category_id)
        return category.products if category else []

category = CRUDCategory(Category)