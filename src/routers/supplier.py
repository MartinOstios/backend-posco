from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from src.crud import supplier as crud
from src.deps import SessionDep, get_current_active_employee
from src.models.supplier import Supplier, SupplierCreate, SupplierRead
from src.models.employee import Employee
from src.models.utils import Message

router = APIRouter()

@router.get("/", response_model=list[SupplierRead])
def read_suppliers(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Retrieve suppliers.
    """
    suppliers = crud.get_by_enterprise(
        session=session,
        enterprise_id=current_employee.enterprise.id,
        skip=skip,
        limit=limit
    )
    return suppliers

@router.post("/", response_model=SupplierRead)
def create_supplier(
    *,
    session: SessionDep,
    supplier_in: SupplierCreate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Create new supplier.
    """
    # Asignar la empresa del empleado actual
    supplier_in.enterprise_id = current_employee.enterprise.id
    
    # Verificar si ya existe un proveedor con el mismo NIT en la misma empresa
    existing_supplier = crud.get_by_nit_and_enterprise(
        session=session,
        nit=supplier_in.NIT,
        enterprise_id=current_employee.enterprise.id
    )
    if existing_supplier:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un proveedor con este NIT en tu empresa"
        )
    
    supplier = crud.create(session=session, obj_in=supplier_in)
    return supplier

@router.get("/{supplier_id}", response_model=SupplierRead)
def read_supplier(
    *,
    session: SessionDep,
    supplier_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get supplier by ID.
    """
    supplier = crud.get(session=session, id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Verificar que el proveedor pertenece a la empresa del empleado
    if supplier.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para ver este proveedor"
        )
    
    return supplier

@router.put("/{supplier_id}", response_model=SupplierRead)
def update_supplier(
    *,
    session: SessionDep,
    supplier_id: int,
    supplier_in: SupplierCreate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Update supplier.
    """
    supplier = crud.get(session=session, id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Verificar que el proveedor pertenece a la empresa del empleado
    if supplier.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para actualizar este proveedor"
        )
    
    supplier = crud.update(session=session, db_obj=supplier, obj_in=supplier_in)
    return supplier

@router.delete("/{supplier_id}", response_model=Message)
def delete_supplier(
    *,
    session: SessionDep,
    supplier_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Delete supplier.
    """
    supplier = crud.get(session=session, id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Verificar que el proveedor pertenece a la empresa del empleado
    if supplier.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para eliminar este proveedor"
        )
    
    crud.remove(session=session, id=supplier_id)
    return Message(message="Proveedor eliminado exitosamente")
