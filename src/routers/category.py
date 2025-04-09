from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from src.crud import category as crud
from src.deps import SessionDep, get_current_active_employee
from src.models.category import Category, CategoryCreate, CategoryRead
from src.models.employee import Employee
from src.models.utils import Message

router = APIRouter()

@router.get("/", response_model=list[CategoryRead])
def read_categories(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Retrieve categories.
    """
    categories = crud.get_by_enterprise(
        session=session,
        enterprise_id=current_employee.enterprise.id,
        skip=skip,
        limit=limit
    )
    return categories

@router.post("/", response_model=CategoryRead)
def create_category(
    *,
    session: SessionDep,
    category_in: CategoryCreate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Create new category.
    """
    # Asignar la empresa del empleado actual
    category_in.enterprise_id = current_employee.enterprise.id
    
    category = crud.create(session=session, obj_in=category_in)
    return category

@router.get("/{category_id}", response_model=CategoryRead)
def read_category(
    *,
    session: SessionDep,
    category_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get category by ID.
    """
    category = crud.get(session=session, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Verificar que la categoría pertenece a la empresa del empleado
    if category.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para ver esta categoría"
        )
    
    return category

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    *,
    session: SessionDep,
    category_id: int,
    category_in: CategoryCreate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Update category.
    """
    category = crud.get(session=session, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Verificar que la categoría pertenece a la empresa del empleado
    if category.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para actualizar esta categoría"
        )
    
    category = crud.update(session=session, db_obj=category, obj_in=category_in)
    return category

@router.delete("/{category_id}", response_model=Message)
def delete_category(
    *,
    session: SessionDep,
    category_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Delete category.
    """
    category = crud.get(session=session, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Verificar que la categoría pertenece a la empresa del empleado
    if category.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para eliminar esta categoría"
        )
    
    crud.remove(session=session, id=category_id)
    return Message(message="Categoría eliminada exitosamente")

