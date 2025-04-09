from typing import Optional, List
from sqlmodel import Session, select
from src.models.client import Client, ClientCreate, ClientUpdate
from .base import CRUDBase

class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    def get_by_name(self, session: Session, *, name: str) -> Optional[Client]:
        return session.exec(select(Client).where(Client.name == name)).first()

    def get_sales(self, session: Session, *, client_id: int) -> List["Sale"]:
        client = self.get(session=session, id=client_id)
        return client.sales if client else []

client = CRUDClient(Client)