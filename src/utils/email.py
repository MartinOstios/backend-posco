import smtplib
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
import jwt
from datetime import datetime, timedelta
from sqlmodel import Session, select
from src.config.settings import settings
from src.models.reset_token import PasswordResetToken

def send_email(to_email: str, subject: str, html_content: str):
    # Verificar que la configuración de correo esté completa
    if not settings.SMTP_HOST or not settings.EMAILS_FROM_EMAIL or not settings.SMTP_PASSWORD:
        print("ERROR: Configuración de correo incompleta. Verifique las variables de entorno SMTP_HOST, EMAILS_FROM_EMAIL y SMTP_PASSWORD.")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        # Asegurar que los encabezados tengan codificación UTF-8 para caracteres especiales
        msg['Subject'] = subject
        msg['From'] = settings.EMAILS_FROM_EMAIL
        msg['To'] = to_email
        
        # Crear la parte HTML asegurando codificación UTF-8
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        print(f"Configuración SMTP: Host={settings.SMTP_HOST}, Port={settings.SMTP_PORT}, SSL={settings.SMTP_SSL}, TLS={settings.SMTP_TLS}")
        
        if settings.SMTP_SSL:
            print("Usando conexión SSL...")
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            print("Usando conexión normal...")
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            if settings.SMTP_TLS:
                print("Iniciando TLS...")
                server.starttls()
        
        print(f"Intentando conectar a servidor SMTP: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        server.login(settings.EMAILS_FROM_EMAIL, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAILS_FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"Correo enviado con éxito a {to_email}")
        return True
    except Exception as e:
        print(f"ERROR detallado al enviar correo: {str(e)}")
        import traceback
        print("Traceback completo:")
        print(traceback.format_exc())
        return False

def generate_email_verification_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=48)
    return jwt.encode(
        {"exp": expire, "email": email, "type": "email_verification"},
        settings.SECRET_KEY,
        algorithm="HS256"
    )

def verify_email_token(token: str) -> str:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if decoded_token["type"] != "email_verification":
            raise ValueError("Invalid token type")
        return decoded_token["email"]
    except jwt.PyJWTError:
        raise ValueError("Invalid token")

# Funciones para manejo de tokens de restablecimiento de contraseña
def generate_reset_code() -> str:
    """
    Genera un código numérico aleatorio de 4 dígitos
    """
    return str(random.randint(1000, 9999))

def save_reset_token(db: Session, email: str, token: str) -> PasswordResetToken:
    """
    Guarda un token de restablecimiento en la base de datos
    """
    reset_token = PasswordResetToken(
        email=email,
        token=token,
        created_at=datetime.utcnow()
    )
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    return reset_token

def verify_reset_token(db: Session, email: str, token: str) -> bool:
    """
    Verifica si un token de restablecimiento es válido:
    - Debe existir en la base de datos
    - Debe pertenecer al email especificado
    - No debe estar usado
    - No debe haber expirado (15 minutos)
    """
    # Obtener el token más reciente para el email dado
    statement = (
        select(PasswordResetToken)
        .where(PasswordResetToken.email == email)
        .where(PasswordResetToken.token == token)
        .where(PasswordResetToken.is_used == False)
        .order_by(PasswordResetToken.created_at.desc())
    )
    result = db.exec(statement).first()
    
    if not result:
        return False
    
    # Verificar que no haya expirado (15 minutos)
    expiration_time = result.created_at + timedelta(minutes=15)
    if datetime.utcnow() > expiration_time:
        return False
    
    # Marcar el token como usado
    result.is_used = True
    db.add(result)
    db.commit()
    
    return True

def generate_reset_password_email(email_to: str, email: str, token: str) -> dict:
    """
    Genera el contenido del correo de restablecimiento de contraseña
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Recuperación de contraseña para {email}"
    
    # Leer la plantilla HTML
    template_path = Path(__file__).parent.parent / "email-templates" / "build" / "reset_password.html"
    
    # Si la plantilla no existe, usar un mensaje simple
    if not template_path.exists():
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>{project_name} - Recuperación de contraseña</h1>
            <p>Hola {email},</p>
            <p>Tu código de recuperación de contraseña es: <strong>{token}</strong></p>
            <p>Este código caducará en 15 minutos.</p>
        </body>
        </html>
        """
    else:
        # Leer la plantilla y reemplazar las variables
        html_content = template_path.read_text(encoding='utf-8')
        html_content = html_content.replace("{{ project_name }}", project_name)
        html_content = html_content.replace("{{ username }}", email)
        html_content = html_content.replace("{{ token }}", token)
    
    return {
        "html_content": html_content,
        "subject": subject
    } 