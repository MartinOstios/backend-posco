from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
import requests
from requests.exceptions import ConnectionError, HTTPError
import os
from src.config.settings import settings
from src.models.notification_token import NotificationToken
from sqlmodel import Session
import logging

logger = logging.getLogger(__name__)

# Configurar la sesión para las solicitudes con el token de autenticación
session = requests.Session()
session.headers.update(
    {
        "Authorization": f"Bearer {settings.EXPO_TOKEN}",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)

def send_push_message(token: str, title: str, message: str, extra: dict = None) -> bool:
    """
    Envía un mensaje push a un dispositivo específico.
    
    Args:
        token: Token del dispositivo.
        title: Título de la notificación.
        message: Mensaje de la notificación.
        extra: Datos adicionales para enviar con la notificación.
        
    Returns:
        bool: True si el mensaje se envió correctamente, False en caso contrario.
    """
    try:
        response = PushClient(session=session).publish(
            PushMessage(
                to=token,
                title=title,
                body=message,
                data=extra
            )
        )
    except PushServerError as exc:
        # Error de formato o validación
        logger.error(
            f"Error al enviar notificación push: {exc}",
            extra={
                'token': token,
                'title': title,
                'message': message,
                'extra': extra,
                'errors': exc.errors,
                'response_data': exc.response_data,
            }
        )
        return False
    except (ConnectionError, HTTPError) as exc:
        # Error de conexión o HTTP
        logger.error(
            f"Error de conexión al enviar notificación push: {exc}",
            extra={'token': token, 'title': title, 'message': message, 'extra': extra}
        )
        return False

    try:
        # Validar la respuesta
        response.validate_response()
        return True
    except DeviceNotRegisteredError:
        # El token ya no es válido
        logger.warning(f"Token de dispositivo no registrado: {token}")
        return False
    except PushTicketError as exc:
        # Otro error por notificación
        logger.error(
            f"Error de ticket al enviar notificación push: {exc}",
            extra={
                'token': token,
                'title': title,
                'message': message,
                'extra': extra,
                'push_response': exc.push_response._asdict(),
            }
        )
        return False

def send_notification_to_user(db: Session, user_id: int, title: str, message: str, extra: dict = None) -> dict:
    """
    Envía una notificación a todos los dispositivos registrados de un usuario.
    
    Args:
        db: Sesión de base de datos.
        user_id: ID del usuario.
        title: Título de la notificación.
        message: Mensaje de la notificación.
        extra: Datos adicionales para enviar con la notificación.
        
    Returns:
        dict: Resumen de resultados de envío.
    """
    # Obtener todos los tokens activos del usuario
    tokens = db.query(NotificationToken).filter(
        NotificationToken.user_id == user_id,
        NotificationToken.active == True
    ).all()
    
    results = {
        'total': len(tokens),
        'successful': 0,
        'failed': 0,
        'tokens_to_deactivate': []
    }
    
    if not tokens:
        return results
    
    for token in tokens:
        success = send_push_message(token.token, title, message, extra)
        if success:
            results['successful'] += 1
        else:
            results['failed'] += 1
            # Marcar para desactivar los tokens que fallaron
            results['tokens_to_deactivate'].append(token.id)
    
    # Desactivar los tokens que fallaron
    if results['tokens_to_deactivate']:
        db.query(NotificationToken).filter(
            NotificationToken.id.in_(results['tokens_to_deactivate'])
        ).update({NotificationToken.active: False}, synchronize_session=False)
        db.commit()
    
    return results 