from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from src.crud import enterprise as crud
from src.deps import SessionDep, get_current_active_superuser
from src.models.enterprise import Enterprise, EnterpriseCreate, EnterpriseRead

router = APIRouter()

@router.get("/", response_model=list[EnterpriseRead])
def read_enterprises(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve enterprises.
    """
    enterprises = crud.get_multi(session=session, skip=skip, limit=limit)
    return enterprises

@router.post("/", response_model=EnterpriseRead)
def create_enterprise(
    *,
    session: SessionDep,
    enterprise_in: EnterpriseCreate,
) -> Any:
    """
    Create new enterprise.
    """
    enterprise = crud.get_by_nit(session=session, nit=enterprise_in.NIT)
    if enterprise:
        raise HTTPException(
            status_code=400,
            detail="An enterprise with this NIT already exists.",
        )
    enterprise = crud.create(session=session, obj_in=enterprise_in)
    return enterprise

@router.get("/{enterprise_id}", response_model=EnterpriseRead)
def read_enterprise(
    *,
    session: SessionDep,
    enterprise_id: int,
) -> Any:
    """
    Get enterprise by ID.
    """
    enterprise = crud.get(session=session, id=enterprise_id)
    if not enterprise:
        raise HTTPException(status_code=404, detail="Enterprise not found")
    return enterprise

@router.delete("/{enterprise_id}", response_model=EnterpriseRead)
def delete_enterprise(
    *,
    session: SessionDep,
    enterprise_id: int,
) -> Any:
    """
    Delete an enterprise.
    """
    enterprise = crud.get(session=session, id=enterprise_id)
    if not enterprise:
        raise HTTPException(status_code=404, detail="Enterprise not found")
    enterprise = crud.remove(session=session, id=enterprise_id)
    return enterprise
