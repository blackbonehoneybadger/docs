import os

# Isolated test database + deterministic key, set before app imports.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_badger_cfo.db")
os.environ.setdefault(
    "FERNET_KEY", "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
)

import pytest

from app.database import Base, engine


@pytest.fixture(autouse=True)
def fresh_db():
    from app import models  # noqa: F401

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
