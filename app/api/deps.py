"""Shared API dependencies. Single-user system for now: default user auto-created."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def get_or_create_default_user(db: Session) -> User:
    user = db.scalars(select(User).order_by(User.id).limit(1)).first()
    if user is None:
        user = User(name="Badger")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
