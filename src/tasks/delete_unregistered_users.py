from datetime import datetime, timedelta, timezone

from db.database import sync_session

from sqlalchemy.orm import Session
from sqlalchemy import delete

from celery import shared_task

from models import User


@shared_task
def delete_unregistered_users():
    """Удаляем незарегистрированных пользователей."""
    session: Session = sync_session()
    try:
        deleted_datetime = datetime.now(tz=timezone.utc) - timedelta(days=1)
        stmt = delete(User).where(User.is_register.is_(False), User.created_at <= deleted_datetime)
        session.execute(stmt)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()
