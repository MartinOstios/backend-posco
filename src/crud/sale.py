from typing import Optional, List
from datetime import date
from sqlmodel import Session, select
from src.models.sale import Sale, SaleCreate, SaleUpdate
from .base import CRUDBase
from . import product as product_crud

class CRUDSale(CRUDBase[Sale, SaleCreate, SaleUpdate]):
    def create(self, session: Session, *, obj_in: SaleCreate) -> Sale:
        # Crear la venta
        db_obj = Sale(
            quantity=obj_in.quantity,
            discount=obj_in.discount,
            price=obj_in.price,
            sell_date=obj_in.sell_date or date.today(),
            total_price=obj_in.total_price,
            invoice_id=obj_in.invoice_id,
            client_id=obj_in.client_id,
            product_id=obj_in.product_id
        )
        
        # Actualizar el stock del producto
        product_crud.product.update_stock(
            session=session, 
            product_id=obj_in.product_id, 
            quantity=-obj_in.quantity
        )
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_by_date_range(
        self, 
        session: Session, 
        *, 
        start_date: date, 
        end_date: date
    ) -> List[Sale]:
        return session.exec(
            select(Sale)
            .where(Sale.sell_date >= start_date)
            .where(Sale.sell_date <= end_date)
        ).all()

sale = CRUDSale(Sale)