from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_tokens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    token: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_used: bool = Field(default=False) 