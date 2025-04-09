from typing import Any, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from src.crud import sale as crud
from src.deps import SessionDep, get_current_active_employee
from src.models.sale import Sale, SaleCreate, SaleRead
from src.models.employee import Employee
from src.models.utils import Message

router = APIRouter()

@router.get("/", response_model=list[SaleRead])
def read_sales(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Retrieve sales.
    """
    sales = crud.get_multi(session=session, skip=skip, limit=limit)
    return sales

@router.post("/", response_model=SaleRead)
def create_sale(
    *,
    session: SessionDep,
    sale_in: SaleCreate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Create new sale.
    """
    # La creación de la venta también actualizará el stock del producto
    sale = crud.create(session=session, obj_in=sale_in)
    return sale

@router.get("/by-date-range", response_model=List[SaleRead])
def read_sales_by_date_range(
    *,
    session: SessionDep,
    start_date: date,
    end_date: date,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get sales by date range.
    """
    sales = crud.get_by_date_range(
        session=session,
        start_date=start_date,
        end_date=end_date
    )
    return sales

@router.get("/{sale_id}", response_model=SaleRead)
def read_sale(
    *,
    session: SessionDep,
    sale_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get sale by ID.
    """
    sale = crud.get(session=session, id=sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@router.delete("/{sale_id}", response_model=Message)
def delete_sale(
    *,
    session: SessionDep,
    sale_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Delete sale.
    """
    sale = crud.get(session=session, id=sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Aquí podrías agregar lógica adicional antes de eliminar la venta
    # Por ejemplo, restaurar el stock del producto
    
    crud.remove(session=session, id=sale_id)
    return Message(message="Sale deleted successfully")
