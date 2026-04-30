from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from app.models import User, Organization, Membership, Project, Task

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


def get_session():
    with Session(engine) as session:
        yield session
        