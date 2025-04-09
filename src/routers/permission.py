from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from src.crud import permission as crud
from src.deps import SessionDep, get_current_active_superuser
from src.models.permission import Permission, PermissionCreate, PermissionRead

router = APIRouter()

@router.get(
    "/", 
    response_model=list[PermissionRead],
    dependencies=[Depends(get_current_active_superuser)]
)
def read_permissions(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve permissions.
    """
    permissions = crud.get_multi(session=session, skip=skip, limit=limit)
    return permissions

@router.post(
    "/", 
    response_model=PermissionRead,
    dependencies=[Depends(get_current_active_superuser)]
)
def create_permission(
    *,
    session: SessionDep,
    permission_in: PermissionCreate,
) -> Any:
    """
    Create new permission.
    """
    permission = crud.get_by_name(session=session, name=permission_in.name)
    if permission:
        raise HTTPException(
            status_code=400,
            detail="A permission with this name already exists.",
        )
    permission = crud.create(session=session, obj_in=permission_in)
    return permission

@router.get(
    "/{permission_id}", 
    response_model=PermissionRead,
    dependencies=[Depends(get_current_active_superuser)]
)
def read_permission(
    *,
    session: SessionDep,
    permission_id: int,
) -> Any:
    """
    Get permission by ID.
    """
    permission = crud.get(session=session, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission
