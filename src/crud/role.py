from typing import Optional, List
from sqlmodel import Session, select
from src.models.role import Role, RoleCreate, RoleUpdate
from src.models.permission import Permission
from .base import CRUDBase

class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def get_by_name(self, session: Session, *, name: str) -> Optional[Role]:
        return session.exec(select(Role).where(Role.name == name)).first()

    def get_permissions(self, session: Session, *, role_id: int) -> List[Permission]:
        role = self.get(session=session, id=role_id)
        return role.permissions if role else []

role = CRUDRole(Role)