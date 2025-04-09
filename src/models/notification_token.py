from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from .employee import Employee

# Modelo base para tokens de notificación
class NotificationTokenBase(SQLModel):
    token: str = Field(index=True)
    device_name: Optional[str] = None
    active: bool = True

# Para crear un nuevo token
class NotificationTokenCreate(NotificationTokenBase):
    user_id: int

# Para actualizar un token
class NotificationTokenUpdate(SQLModel):
    device_name: Optional[str] = None
    active: Optional[bool] = None

# Modelo de base de datos
class NotificationToken(NotificationTokenBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(foreign_key="employee.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Definir relación
    user: Optional[Employee] = Relationship(back_populates="notification_tokens")

# Modelo para respuestas API
class NotificationTokenPublic(NotificationTokenBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

# Lista de tokens para respuestas API
class NotificationTokensPublic(SQLModel):
    data: List[NotificationTokenPublic]
    count: int 