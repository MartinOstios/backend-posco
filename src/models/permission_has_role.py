from sqlmodel import SQLModel, Field

class PermissionHasRole(SQLModel, table=True):
    permission_id: int = Field(foreign_key="permission.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)