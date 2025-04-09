from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from src.models.notification_token import (
    NotificationToken,
    NotificationTokenCreate,
    NotificationTokenUpdate,
)


def get_by_id(db: Session, token_id: int) -> Optional[NotificationToken]:
    """
    Obtiene un token de notificación por su ID.
    """
    return db.get(NotificationToken, token_id)


def get_by_token(db: Session, token: str) -> Optional[NotificationToken]:
    """
    Obtiene un token de notificación por su valor.
    """
    statement = select(NotificationToken).where(NotificationToken.token == token)
    return db.exec(statement).first()


def get_by_user_id(db: Session, user_id: int, active_only: bool = True) -> List[NotificationToken]:
    """
    Obtiene todos los tokens de notificación de un usuario.
    """
    statement = select(NotificationToken).where(NotificationToken.user_id == user_id)
    
    if active_only:
        statement = statement.where(NotificationToken.active == True)
        
    return db.exec(statement).all()


def create(db: Session, obj_in: NotificationTokenCreate) -> NotificationToken:
    """
    Crea un nuevo token de notificación. Si el token ya existe, lo actualiza a activo.
    """
    # Verificar si el token ya existe
    existing_token = get_by_token(db, obj_in.token)
    
    if existing_token:
        # Si existe pero pertenece a otro usuario, crear uno nuevo
        if existing_token.user_id != obj_in.user_id:
            # Desactivar el existente
            existing_token.active = False
            existing_token.updated_at = datetime.utcnow()
            db.add(existing_token)
            
            # Crear uno nuevo
            db_obj = NotificationToken(
                token=obj_in.token,
                device_name=obj_in.device_name,
                user_id=obj_in.user_id,
                active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(db_obj)
        else:
            # Si pertenece al mismo usuario, actualizarlo
            existing_token.active = True
            existing_token.device_name = obj_in.device_name
            existing_token.updated_at = datetime.utcnow()
            db.add(existing_token)
            db_obj = existing_token
    else:
        # Si no existe, crear uno nuevo
        db_obj = NotificationToken(
            token=obj_in.token,
            device_name=obj_in.device_name,
            user_id=obj_in.user_id,
            active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_obj)
    
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: NotificationToken, obj_in: NotificationTokenUpdate) -> NotificationToken:
    """
    Actualiza un token de notificación existente.
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    
    # Actualizar los campos
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db_obj.updated_at = datetime.utcnow()
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, token_id: int) -> bool:
    """
    Elimina un token de notificación.
    """
    db_obj = get_by_id(db, token_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return True
    return False


def deactivate(db: Session, token_id: int) -> Optional[NotificationToken]:
    """
    Desactiva un token de notificación.
    """
    db_obj = get_by_id(db, token_id)
    if db_obj:
        db_obj.active = False
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    return None


def deactivate_all_user_tokens(db: Session, user_id: int) -> int:
    """
    Desactiva todos los tokens de un usuario.
    """
    tokens = get_by_user_id(db, user_id)
    count = 0
    
    for token in tokens:
        if token.active:
            token.active = False
            token.updated_at = datetime.utcnow()
            db.add(token)
            count += 1
    
    db.commit()
    return count 