from typing import Annotated, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from src.config.security import ALGORITHM
from src.config.settings import settings
from src.config.db import engine
from src.models.employee import Employee, EmployeeRead, PermissionInfo, RoleInfo, EnterpriseInfo
from src.crud import employee as employee_crud
from src.models.utils import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_session() -> Generator:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[Employee, Depends(reusable_oauth2)]

def get_current_employee(
    session: SessionDep,
    token: str = Depends(reusable_oauth2)
) -> EmployeeRead:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    employee = employee_crud.get(session=session, id=token_data.sub)
    if not employee:
        raise HTTPException(
            status_code=404, 
            detail="Employee not found"
        )
    
    # Construir el objeto EmployeeAuth con la información de la empresa
    employee_auth = EmployeeRead(
        id=employee.id,
        name=employee.name,
        lastname=employee.lastname,
        email=employee.email,
        code=employee.code,
        telephone=employee.telephone,
        enterprise_id=employee.enterprise_id,
        is_active=employee.is_active,
        role=RoleInfo(
            id=employee.role.id,
            name=employee.role.name,
            description=employee.role.description,
            permissions=[
                PermissionInfo(
                    id=permission.id,
                    name=permission.name,
                    description=permission.description
                )
                for permission in employee.role.permissions
            ]
        ),
        enterprise=EnterpriseInfo(
            id=employee.enterprise.id,
            name=employee.enterprise.name,
            NIT=employee.enterprise.NIT
        )
    )
    
    return employee_auth

def get_current_active_employee(
    current_employee: Employee = Depends(get_current_employee),
) -> EmployeeRead:
    if not current_employee.is_active:
        raise HTTPException(
            status_code=400, 
            detail="Inactive employee"
        )
    return current_employee

def get_current_active_superuser(
    current_employee: Employee = Depends(get_current_active_employee),
) -> EmployeeRead:
    if current_employee.role.name != "ADMIN":
        raise HTTPException(
            status_code=400, 
            detail="The employee doesn't have enough privileges"
        )
    return current_employee