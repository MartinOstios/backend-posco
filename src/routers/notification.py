from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Any, List

from src.deps import get_current_employee, get_session
from src.models.employee import Employee
from src.models.notification_token import (
    NotificationToken,
    NotificationTokenCreate,
    NotificationTokenPublic,
    NotificationTokensPublic,
    NotificationTokenUpdate,
)
from src.crud import notification_token as crud
from src.utils.notification import send_notification_to_user

router = APIRouter()


class NotificationRequest(NotificationTokenCreate):
    pass


class NotificationSendRequest(NotificationTokenCreate):
    title: str
    message: str
    data: dict = None


@router.post("/register-token", response_model=NotificationTokenPublic)
def register_notification_token(
    request: NotificationRequest,
    db: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_employee),
) -> Any:
    """
    Registra un token de notificación para el usuario actual.
    """
    # Asegurarse de que el usuario actual es el dueño del token
    token_data = NotificationTokenCreate(
        token=request.token,
        device_name=request.device_name,
        user_id=current_user.id
    )
    return crud.create(db, token_data)


@router.get("/my-tokens", response_model=NotificationTokensPublic)
def get_my_tokens(
    active_only: bool = True,
    db: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_employee),
) -> Any:
    """
    Obtiene todos los tokens de notificación del usuario actual.
    """
    tokens = crud.get_by_user_id(db, current_user.id, active_only)
    return {
        "data": tokens,
        "count": len(tokens)
    }


@router.put("/tokens/{token_id}", response_model=NotificationTokenPublic)
def update_token(
    token_id: int,
    token_update: NotificationTokenUpdate,
    db: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_employee),
) -> Any:
    """
    Actualiza un token de notificación.
    """
    db_token = crud.get_by_id(db, token_id)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de notificación no encontrado",
        )
    if db_token.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este token",
        )
    return crud.update(db, db_token, token_update)


@router.delete("/tokens/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_token(
    token_id: int,
    db: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_employee),
) -> None:
    """
    Elimina un token de notificación.
    """
    db_token = crud.get_by_id(db, token_id)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de notificación no encontrado",
        )
    if db_token.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este token",
        )
    crud.delete(db, token_id)


@router.post("/send-test", status_code=status.HTTP_200_OK)
def send_test_notification(
    db: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_employee),
) -> dict:
    """
    Envía una notificación de prueba a todos los dispositivos del usuario actual.
    """
    title = "Notificación de prueba"
    message = f"Hola {current_user.name} {current_user.lastname}, esta es una notificación de prueba."
    
    results = send_notification_to_user(db, current_user.id, title, message)
    return {
        "message": "Notificación de prueba enviada",
        "results": results
    }


@router.post("/send-to-user/{user_id}", status_code=status.HTTP_200_OK)
def send_notification_to_specific_user(
    user_id: int,
    title: str,
    message: str,
    data: dict = None,
    db: Session = Depends(get_session),
    current_user: Employee = Depends(get_current_employee),
) -> dict:
    """
    Envía una notificación a un usuario específico.
    Solo accesible para administradores.
    """
    if current_user.role.name != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para enviar notificaciones a otros usuarios",
        )
    
    results = send_notification_to_user(db, user_id, title, message, data)
    return {
        "message": f"Notificación enviada al usuario {user_id}",
        "results": results
    } 