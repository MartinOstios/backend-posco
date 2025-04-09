from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from src.crud import client as crud
from src.deps import SessionDep, get_current_active_employee
from src.models.client import Client, ClientCreate, ClientRead
from src.models.sale import SaleRead
from src.models.employee import Employee
from src.models.utils import Message

router = APIRouter()

@router.get("/", response_model=list[ClientRead])
def read_clients(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Retrieve clients.
    """
    clients = crud.get_multi(session=session, skip=skip, limit=limit)
    return clients

@router.post("/", response_model=ClientRead)
def create_client(
    *,
    session: SessionDep,
    client_in: ClientCreate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Create new client.
    """
    client = crud.create(session=session, obj_in=client_in)
    return client

@router.get("/{client_id}", response_model=ClientRead)
def read_client(
    *,
    session: SessionDep,
    client_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get client by ID.
    """
    client = crud.get(session=session, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/{client_id}/sales", response_model=List[SaleRead])
def read_client_sales(
    *,
    session: SessionDep,
    client_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get sales for a client.
    """
    sales = crud.get_sales(session=session, client_id=client_id)
    return sales

@router.delete("/{client_id}", response_model=Message)
def delete_client(
    *,
    session: SessionDep,
    client_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Delete client.
    """
    client = crud.get(session=session, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Verificar si el cliente tiene ventas asociadas
    if client.sales:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete client with associated sales"
        )
    
    crud.remove(session=session, id=client_id)
    return Message(message="Client deleted successfully")
