from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import EmailStr

class EmployeeBase(SQLModel):
    name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=100)
    code: str = Field(max_length=45)
    lastname: str = Field(max_length=100)
    telephone: str = Field(max_length=20)

class Employee(EmployeeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enterprise_id: Optional[int] = Field(default=None, foreign_key="enterprise.id")
    role_id: Optional[int] = Field(default=None, foreign_key="role.id")
    is_active: bool = Field(default=True)
    hashed_password: str = Field(max_length=255)
    
    enterprise: Optional["Enterprise"] = Relationship(back_populates="employees")
    role: Optional["Role"] = Relationship(back_populates="employees")
    notification_tokens: List["NotificationToken"] = Relationship(back_populates="user")

class EmployeeCreate(EmployeeBase):
    password: str
    enterprise_id: int
    role_id: int



class EmployeeUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    code: Optional[str] = None
    lastname: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    telephone: Optional[str] = None

class EmployeeUpdateMe(SQLModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    telephone: Optional[str] = None

class EnterpriseInfo(SQLModel):
    id: int
    name: str
    NIT: str

class PermissionInfo(SQLModel):
    id: int
    name: str
    description: str

class RoleInfo(SQLModel):
    id: int
    name: str
    description: str
    permissions: List[PermissionInfo]


class EmployeeRead(EmployeeBase):
    id: int
    is_active: bool
    enterprise: EnterpriseInfo
    role: RoleInfo
