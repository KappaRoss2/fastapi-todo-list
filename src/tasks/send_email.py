import smtplib

from worker_config import celery_app

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@celery_app.task
def send_email(
    smtp_server: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    recipient: str,
    subject: str,
    body: str
):
    """Отправляем сообщение на email пользователя.

    Args:
        smtp_server (str): HOST SMTP сервера
        smtp_port (int): ПОРТ SMTP сервера
        smtp_username (str): Логин SMTP сервера
        smtp_password (str): Пароль SMTP сервера
        recipient (str): Кому отправляем.
        subject (str): Тема сообщения
        body (str): Тело сообщения
    """
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    msg = MIMEMultipart('alternative')
    msg['From'] = smtp_username
    msg['To'] = recipient
    msg['Subject'] = subject
    text = MIMEText(body, 'plain')
    msg.attach(text)
    server.sendmail(smtp_username, recipient, msg.as_string())
