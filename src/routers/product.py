from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from src.crud import product as crud
from src.crud import category as category_crud
from src.deps import SessionDep, get_current_active_employee
from src.models.product import Product, ProductCreate, ProductRead
from src.models.employee import Employee
from src.models.utils import Message

router = APIRouter()

@router.get("/", response_model=list[ProductRead])
def read_products(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Retrieve products.
    """
    products = crud.get_by_enterprise(
        session=session,
        enterprise_id=current_employee.enterprise.id,
        skip=skip,
        limit=limit
    )
    return products

@router.get("/category/{category_id}", response_model=list[ProductRead])
def read_products_by_category(
    *,
    session: SessionDep,
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Retrieve products by category.
    """
    # Verificar que la categoría existe y pertenece a la empresa del empleado
    category = category_crud.get(session=session, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para ver los productos de esta categoría"
        )
    
    products = crud.get_by_category(
        session=session,
        category_id=category_id,
        enterprise_id=current_employee.enterprise.id,
        skip=skip,
        limit=limit
    )
    return products

@router.post("/", response_model=ProductRead)
def create_product(
    *,
    session: SessionDep,
    product_in: ProductCreate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Create new product.
    """
    # Verificar que la categoría pertenece a la empresa del empleado
    category = category_crud.get(session=session, id=product_in.category_id)
    if not category or category.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=400,
            detail="Invalid category"
        )
    
    # Verificar que no exista otro producto con el mismo código de barras en la empresa
    existing_product = crud.get_by_bar_code_and_enterprise(
        session=session,
        bar_code=product_in.bar_code,
        enterprise_id=current_employee.enterprise.id
    )
    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un producto con este código de barras"
        )
    
    # Asignar la empresa del empleado actual
    product_in.enterprise_id = current_employee.enterprise.id
    
    product = crud.create(session=session, obj_in=product_in)
    return product

@router.get("/{product_id}", response_model=ProductRead)
def read_product(
    *,
    session: SessionDep,
    product_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get product by ID.
    """
    product = crud.get(session=session, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verificar que el producto pertenece a la empresa del empleado
    if product.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para ver este producto"
        )
    
    return product

@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    *,
    session: SessionDep,
    product_id: int,
    product_in: ProductCreate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Update product.
    """
    product = crud.get(session=session, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verificar que el producto pertenece a la empresa del empleado
    if product.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para actualizar este producto"
        )
    
    # Verificar que la categoría pertenece a la empresa del empleado
    category = category_crud.get(session=session, id=product_in.category_id)
    if not category or category.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=400,
            detail="Invalid category"
        )
    
    product = crud.update(session=session, db_obj=product, obj_in=product_in)
    return product

@router.delete("/{product_id}", response_model=Message)
def delete_product(
    *,
    session: SessionDep,
    product_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Delete product.
    """
    product = crud.get(session=session, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verificar que el producto pertenece a la empresa del empleado
    if product.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para eliminar este producto"
        )
    
    crud.remove(session=session, id=product_id)
    return Message(message="Producto eliminado exitosamente")
