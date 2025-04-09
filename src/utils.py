import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from email.mime.text import MIMEText
import base64
import smtplib

import requests


import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from src.config.settings import settings


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    message = MIMEText(html_content, "html")
    message["from"] = settings.EMAILS_FROM_EMAIL
    message["to"] = email_to
    message["subject"] = subject

    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    server.starttls()
    server.ehlo()
    auth_string = f"user={settings.EMAILS_FROM_EMAIL}\1auth=Bearer {settings.OAUTH_ACCESS_TOKEN}\1\1"
    server.docmd("AUTH", "XOAUTH2 " +
                 base64.b64encode(auth_string.encode()).decode())

    try:
        response = server.sendmail(
            settings.EMAILS_FROM_EMAIL, email_to, message.as_string())
        logging.info(f"Send email result: {response}")
    except smtplib.SMTPSenderRefused as e:
        logging.error(f"Error sending email: {e}")
        refreshed_access_token = oauth_refresh_access_token(
            refresh_token=settings.OAUTH_REFRESH_TOKEN,
            client_id=settings.OAUTH_CLIENT_ID,
            client_secret=settings.OAUTH_SECRET,
        )
        settings.OAUTH_ACCESS_TOKEN = refreshed_access_token

        auth_string = f"user={settings.EMAILS_FROM_EMAIL}\1auth=Bearer {settings.OAUTH_ACCESS_TOKEN}\1\1"
        server.docmd("AUTH", "XOAUTH2 " +
                     base64.b64encode(auth_string.encode()).decode())
        response = server.sendmail(
            settings.EMAILS_FROM_EMAIL, email_to, message.as_string())
        logging.info(f"Send email result: {response}")

    server.quit()


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Recuperación de contraseña para {email}"
    link = f"{settings.DOMAIN}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Nueva cuenta para {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.DOMAIN,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"])
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None


def oauth_refresh_access_token(refresh_token: str, client_id: str, client_secret: str) -> str:
    """
    Refresh the Google API access token using the refresh token.
    """
    params = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }
    token_url = "https://oauth2.googleapis.com/token"
    response = requests.post(token_url, data=params)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        logging.error(f"Failed to refresh access token: {response.json()}")
