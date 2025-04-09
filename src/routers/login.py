from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from src.crud import employee as crud
from src.deps import CurrentUser, SessionDep, get_current_active_superuser
from src.config import security
from src.config.settings import settings
from src.config.security import get_password_hash
from src.models.utils import Message, NewPassword, Token
from src.models.employee import Employee, EmployeeRead
from src.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    employee = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not employee:
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")
    elif not employee.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            employee.id, expires_delta=access_token_expires
        )
    )


@router.post("/login/test-token", response_model=EmployeeRead)
def test_token(current_employee: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_employee


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    employee = crud.get_by_email(session=session, email=email)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="El empleado con este correo no existe en el sistema.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=employee.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=employee.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Correo de recuperación de contraseña enviado")


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido")
    employee = crud.get_by_email(session=session, email=email)
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="El empleado con este correo no existe en el sistema.",
        )
    elif not employee.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    hashed_password = get_password_hash(password=body.new_password)
    employee.hashed_password = hashed_password
    session.add(employee)
    session.commit()
    return Message(message="Contraseña actualizada exitosamente")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    employee = crud.get_by_email(session=session, email=email)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=employee.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )