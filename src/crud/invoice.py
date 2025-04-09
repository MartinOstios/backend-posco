from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select
from src.models.invoice import Invoice, InvoiceCreate, InvoiceUpdate
from .base import CRUDBase

class CRUDInvoice(CRUDBase[Invoice, InvoiceCreate, InvoiceUpdate]):
    def get_by_date_range(
        self, 
        session: Session, 
        *, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Invoice]:
        return session.exec(
            select(Invoice)
            .where(Invoice.created_at >= start_date)
            .where(Invoice.created_at <= end_date)
        ).all()

    def get_sales(self, session: Session, *, invoice_id: int) -> List["Sale"]:
        invoice = self.get(session=session, id=invoice_id)
        return invoice.sales if invoice else []

invoice = CRUDInvoice(Invoice)