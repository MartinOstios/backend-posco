from typing import Optional
from pydantic import BaseModel, Field


# Generic message
class Message(BaseModel):
    message: str


# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: Optional[int] = None


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)