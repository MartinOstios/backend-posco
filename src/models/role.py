from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from .permission_has_role import PermissionHasRole

class RoleBase(SQLModel):
    name: str = Field(max_length=45, unique=True)
    description: str = Field(max_length=255)

class Role(RoleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=PermissionHasRole
    )
    employees: List["Employee"] = Relationship(back_populates="role")

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int

class RoleUpdate(RoleBase):
    pass