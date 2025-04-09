from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from src.models.reset_token import PasswordResetToken


def create(db: Session, email: str, token: str) -> PasswordResetToken:
    """
    Crea un nuevo token de restablecimiento de contraseña
    """
    reset_token = PasswordResetToken(
        email=email,
        token=token,
        created_at=datetime.utcnow(),
        is_used=False
    )
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    return reset_token


def get_latest_for_email(db: Session, email: str) -> Optional[PasswordResetToken]:
    """
    Obtiene el token más reciente para un correo electrónico
    """
    statement = (
        select(PasswordResetToken)
        .where(PasswordResetToken.email == email)
        .where(PasswordResetToken.is_used == False)
        .order_by(PasswordResetToken.created_at.desc())
    )
    return db.exec(statement).first()


def get_by_token(db: Session, token: str) -> Optional[PasswordResetToken]:
    """
    Obtiene un token por su valor
    """
    statement = (
        select(PasswordResetToken)
        .where(PasswordResetToken.token == token)
        .where(PasswordResetToken.is_used == False)
    )
    return db.exec(statement).first()


def verify_token(db: Session, email: str, token: str) -> bool:
    """
    Verifica si un token es válido y lo marca como usado
    """
    statement = (
        select(PasswordResetToken)
        .where(PasswordResetToken.email == email)
        .where(PasswordResetToken.token == token)
        .where(PasswordResetToken.is_used == False)
        .order_by(PasswordResetToken.created_at.desc())
    )
    reset_token = db.exec(statement).first()
    
    if not reset_token:
        return False
    
    # Verificar que no haya expirado (15 minutos)
    expiration_time = reset_token.created_at + datetime.timedelta(minutes=15)
    if datetime.utcnow() > expiration_time:
        return False
    
    # Marcar el token como usado
    reset_token.is_used = True
    db.add(reset_token)
    db.commit()
    
    return True 