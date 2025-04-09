from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from .permission_has_role import PermissionHasRole

class PermissionBase(SQLModel):
    name: str = Field(max_length=45, unique=True)
    description: str = Field(max_length=255)

class Permission(PermissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    roles: List["Role"] = Relationship(
        back_populates="permissions",
        link_model=PermissionHasRole
    )

class PermissionCreate(PermissionBase):
    pass

class PermissionRead(PermissionBase):
    id: int

class PermissionUpdate(PermissionBase):
    pass

