from typing import Optional, List
from sqlmodel import Session, select
from src.models.product import Product, ProductCreate, ProductUpdate
from .base import CRUDBase

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_by_bar_code(self, session: Session, *, bar_code: str) -> Optional[Product]:
        return session.exec(select(Product).where(Product.bar_code == bar_code)).first()

    def get_by_category(
        self, 
        session: Session, 
        *, 
        category_id: int,
        enterprise_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        statement = select(Product).where(
            Product.category_id == category_id,
            Product.enterprise_id == enterprise_id
        ).offset(skip).limit(limit)
        return session.exec(statement).all()

    def get_by_supplier(
        self, 
        session: Session, 
        *, 
        supplier_id: int,
        enterprise_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        statement = select(Product).where(
            Product.supplier_id == supplier_id,
            Product.enterprise_id == enterprise_id
        ).offset(skip).limit(limit)
        return session.exec(statement).all()

    def get_by_bar_code_and_enterprise(
        self, 
        session: Session, 
        *, 
        bar_code: str, 
        enterprise_id: int
    ) -> Optional[Product]:
        return session.exec(
            select(Product).where(
                Product.bar_code == bar_code,
                Product.enterprise_id == enterprise_id
            )
        ).first()

product = CRUDProduct(Product)