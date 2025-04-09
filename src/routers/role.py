from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from src.crud import role as crud
from src.deps import SessionDep, get_current_active_superuser
from src.models.role import Role, RoleCreate, RoleRead
from src.models.permission import PermissionRead

router = APIRouter()

@router.get("/", response_model=list[RoleRead])
def read_roles(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve roles.
    """
    roles = crud.get_multi(session=session, skip=skip, limit=limit)
    return roles

@router.post("/", response_model=RoleRead)
def create_role(
    *,
    session: SessionDep,
    role_in: RoleCreate,
) -> Any:
    """
    Create new role.
    """
    role = crud.get_by_name(session=session, name=role_in.name)
    if role:
        raise HTTPException(
            status_code=400,
            detail="A role with this name already exists.",
        )
    role = crud.create(session=session, obj_in=role_in)
    return role

@router.get("/{role_id}", response_model=RoleRead)
def read_role(
    *,
    session: SessionDep,
    role_id: int,
) -> Any:
    """
    Get role by ID.
    """
    role = crud.get(session=session, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.get("/{role_id}/permissions", response_model=List[PermissionRead])
def read_role_permissions(
    *,
    session: SessionDep,
    role_id: int,
) -> Any:
    """
    Get permissions for a role.
    """
    permissions = crud.get_permissions(session=session, role_id=role_id)
    return permissions
