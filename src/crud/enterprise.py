from typing import Optional
from sqlmodel import Session, select
from src.models.enterprise import Enterprise, EnterpriseCreate, EnterpriseUpdate
from .base import CRUDBase

class CRUDEnterprise(CRUDBase[Enterprise, EnterpriseCreate, EnterpriseUpdate]):
    def get_by_nit(self, session: Session, *, nit: str) -> Optional[Enterprise]:
        return session.exec(select(Enterprise).where(Enterprise.NIT == nit)).first()

enterprise = CRUDEnterprise(Enterprise)