from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.config.config import Settings
from typing import List,Optional
from fastapi import BackgroundTasks



conf = ConnectionConfig(
    MAIL_USERNAME=Settings().MAIL_USERNAME,
    MAIL_PASSWORD=Settings().MAIL_PASSWORD,
    MAIL_FROM=Settings().MAIL_FROM,
    MAIL_PORT=Settings().MAIL_PORT,
    MAIL_SERVER=Settings().MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="app/templates/email",
)


async def send_email(
    subject: str,
    recipients: List[str],
    body: str,
    background_tasks: Optional[BackgroundTasks] = None,
    html: bool = False
):
    """
    Send an email using FastAPI-Mail utility function.

    Args:
        subject: Email subject
        recipients: List of recipient emails
        body: Email body (plain text or HTML)
        background_tasks: Optional BackgroundTasks for async sending
        html: Whether to send body as HTML
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="html" if html else "plain"
    )

    fm = FastMail(conf)

    # Send in background if provided, else directly
    if background_tasks:
        background_tasks.add_task(fm.send_message, message)
    else:
        await fm.send_message(message)

    return {"status": "sent", "recipients": recipients}

