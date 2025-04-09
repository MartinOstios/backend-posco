from typing import Optional, List
from sqlmodel import Session, select
from src.models.supplier import Supplier, SupplierCreate, SupplierUpdate
from .base import CRUDBase

class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    def get_by_nit(self, session: Session, *, nit: str) -> Optional[Supplier]:
        return session.exec(select(Supplier).where(Supplier.NIT == nit)).first()

    def get_by_email(self, session: Session, *, email: str) -> Optional[Supplier]:
        return session.exec(select(Supplier).where(Supplier.email == email)).first()

    def get_products(self, session: Session, *, supplier_id: int) -> List["Product"]:
        supplier = self.get(session=session, id=supplier_id)
        return supplier.products if supplier else []

    def get_by_nit_and_enterprise(
        self, session: Session, *, nit: str, enterprise_id: int
    ) -> Optional[Supplier]:
        return session.exec(
            select(Supplier).where(
                Supplier.NIT == nit,
                Supplier.enterprise_id == enterprise_id
            )
        ).first()

supplier = CRUDSupplier(Supplier)