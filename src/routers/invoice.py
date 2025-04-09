from typing import Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from src.crud import invoice as crud
from src.deps import SessionDep, get_current_active_employee
from src.models.invoice import Invoice, InvoiceCreate, InvoiceRead
from src.models.sale import SaleRead
from src.models.employee import Employee
from src.models.utils import Message

router = APIRouter()

@router.get("/", response_model=list[InvoiceRead])
def read_invoices(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Retrieve invoices.
    """
    invoices = crud.get_multi(session=session, skip=skip, limit=limit)
    return invoices

@router.post("/", response_model=InvoiceRead)
def create_invoice(
    *,
    session: SessionDep,
    invoice_in: InvoiceCreate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Create new invoice.
    """
    invoice = crud.create(session=session, obj_in=invoice_in)
    return invoice

@router.get("/by-date-range", response_model=List[InvoiceRead])
def read_invoices_by_date_range(
    *,
    session: SessionDep,
    start_date: datetime,
    end_date: datetime,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get invoices by date range.
    """
    invoices = crud.get_by_date_range(
        session=session,
        start_date=start_date,
        end_date=end_date
    )
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceRead)
def read_invoice(
    *,
    session: SessionDep,
    invoice_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get invoice by ID.
    """
    invoice = crud.get(session=session, id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.get("/{invoice_id}/sales", response_model=List[SaleRead])
def read_invoice_sales(
    *,
    session: SessionDep,
    invoice_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get sales for an invoice.
    """
    sales = crud.get_sales(session=session, invoice_id=invoice_id)
    return sales

@router.delete("/{invoice_id}", response_model=Message)
def delete_invoice(
    *,
    session: SessionDep,
    invoice_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Delete invoice.
    """
    invoice = crud.get(session=session, id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Verificar si la factura tiene ventas asociadas
    if invoice.sales:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete invoice with associated sales"
        )
    
    crud.remove(session=session, id=invoice_id)
    return Message(message="Invoice deleted successfully")
