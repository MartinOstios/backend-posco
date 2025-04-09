from typing import Optional, List
from sqlmodel import Session, select
from src.models.permission import Permission, PermissionCreate, PermissionUpdate
from .base import CRUDBase

class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    def get_by_name(self, session: Session, *, name: str) -> Optional[Permission]:
        return session.exec(select(Permission).where(Permission.name == name)).first()

permission = CRUDPermission(Permission)