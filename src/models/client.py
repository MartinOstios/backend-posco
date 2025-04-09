from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class ClientBase(SQLModel):
    name: str = Field(max_length=45)
    # Puedes agregar más campos según necesites, como:
    # email: str = Field(max_length=100)
    # phone: str = Field(max_length=20)
    # address: str = Field(max_length=255)

class Client(ClientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sales: List["Sale"] = Relationship(back_populates="client")

class ClientCreate(ClientBase):
    pass

class ClientRead(ClientBase):
    id: int

class ClientsRead(SQLModel):
    data: List[ClientRead]
    count: int

class ClientUpdate(ClientBase):
    pass

