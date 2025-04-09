from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from src.crud import employee as crud
from src.deps import SessionDep, get_current_active_superuser, get_current_active_employee
from src.models.employee import Employee, EmployeeCreate, EmployeeRead, EmployeeUpdate, RoleInfo, PermissionInfo, EnterpriseInfo, EmployeeUpdateMe
from src.models.utils import Message

router = APIRouter()


@router.get("/", response_model=list[EmployeeRead])
def read_employees(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_employee: EmployeeRead = Depends(get_current_active_employee)
) -> Any:
    """
    Retrieve employees.
    """
    # Si es superusuario, puede ver todos los empleados
    # if current_employee.role.name == "ADMIN":
    # employees = crud.get_multi(session=session, skip=skip, limit=limit)
    # else:
    # Si no es superusuario, solo ve los empleados de su empresa
    employees = crud.get_by_enterprise(
        session=session,
        enterprise_id=current_employee.enterprise.id,
        skip=skip,
        limit=limit
    )
    for employee in employees:
        employee = EmployeeRead(
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
        
    return employees


@router.post("/", response_model=EmployeeRead)
def create_employee(
    *,
    session: SessionDep,
    employee_in: EmployeeCreate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Create new employee.
    """
    # Verificar si el email ya existe
    employee = crud.get_by_email(session=session, email=employee_in.email)
    if employee:
        raise HTTPException(
            status_code=400,
            detail="An employee with this email already exists.",
        )
    
    employee_in.enterprise_id = current_employee.enterprise.id

    employee = crud.create(session=session, obj_in=employee_in)
    return employee


@router.get("/me", response_model=EmployeeRead)
def read_employee_me(
    current_employee: EmployeeRead = Depends(get_current_active_employee)
) -> Any:
    """
    Get current employee.
    """
    return current_employee


@router.get("/{employee_id}", response_model=EmployeeRead)
def read_employee(
    *,
    session: SessionDep,
    employee_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Get employee by ID.
    """
    employee = crud.get(session=session, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee_new = EmployeeRead(
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
    return employee_new


@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(
    *,
    session: SessionDep,
    employee_id: int,
    employee_in: EmployeeUpdate,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Update employee.
    """
    employee = crud.get(session=session, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    # Verificar si el empleado pertenece a la misma empresa
    if employee.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para actualizar empleados de otra empresa"
        )
    
    # Verificar si el email ya existe (si se está actualizando)
    if employee_in.email and employee_in.email != employee.email:
        existing_employee = crud.get_by_email(session=session, email=employee_in.email)
        if existing_employee:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un empleado con este email"
            )

    employee = crud.update(session=session, db_obj=employee, obj_in=employee_in)
    
    return EmployeeRead(
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


@router.patch("/{employee_id}/activate", response_model=Message)
def activate_employee(
    *,
    session: SessionDep,
    employee_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Activate employee.
    """
    employee = crud.get(session=session, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    if employee.enterprise_id != current_employee.enterprise_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para activar empleados de otra empresa"
        )
    
    employee = crud.update(session=session, db_obj=employee, obj_in={"is_active": True})
    return Message(message="Empleado activado exitosamente")


@router.patch("/{employee_id}/deactivate", response_model=Message)
def deactivate_employee(
    *,
    session: SessionDep,
    employee_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Deactivate employee.
    """
    employee = crud.get(session=session, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    if employee.enterprise_id != current_employee.enterprise_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para desactivar empleados de otra empresa"
        )
    
    employee = crud.update(session=session, db_obj=employee, obj_in={"is_active": False})
    return Message(message="Empleado desactivado exitosamente")


@router.delete("/{employee_id}", response_model=Message)
def delete_employee(
    *,
    session: SessionDep,
    employee_id: int,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Delete employee.
    """
    employee = crud.get(session=session, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    # Verificar si el empleado pertenece a la misma empresa
    if employee.enterprise_id != current_employee.enterprise.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para eliminar empleados de otra empresa"
        )
    
    # Evitar que un empleado se elimine a sí mismo
    if employee.id == current_employee.id:
        raise HTTPException(
            status_code=400,
            detail="No puedes eliminarte a ti mismo"
        )
    
    # Verificar si el empleado tiene el rol de administrador
    if employee.role.name == "ADMIN":
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar un empleado con rol de administrador"
        )
    
    crud.remove(session=session, id=employee_id)
    return Message(message="Empleado eliminado exitosamente")


@router.patch("/me", response_model=EmployeeRead)
def update_employee_me(
    *,
    session: SessionDep,
    employee_in: EmployeeUpdateMe,
    current_employee: Employee = Depends(get_current_active_employee)
) -> Any:
    """
    Update current employee profile.
    """
    employee_bd = crud.get(session=session, id=current_employee.id)
    employee = crud.update(session=session, db_obj=employee_bd, obj_in=employee_in)
    
    return EmployeeRead(
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
