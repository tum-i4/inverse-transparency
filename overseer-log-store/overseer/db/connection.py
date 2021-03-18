#!/usr/bin/env python3
""" Database connection """

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm import sessionmaker

from overseer.db.models import Base
from overseer.settings import settings


class Session(_Session):
    """ Helper for adding context manager semantics to Session """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # code inside with block raised an error, rollback
            self.rollback()
            return

        try:
            self.commit()
        except Exception:
            # commit failed, rollback and reraise exception
            self.rollback()
            raise


# `check_same_thread: False` required for SQLite
engine = create_engine(settings.DATABASE_URI, connect_args={"check_same_thread": False})

# enforce foreign key constraints in SQLite
event.listen(engine, "connect", lambda db, _: db.execute("pragma foreign_keys=ON"))

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=Session
)


def init_db():
    """ Import models """
    Base.metadata.create_all(bind=engine)


def close_db():
    """ Close the database connection. """
    SessionLocal.close_all()
    engine.dispose()


def get_db():
    """ Dependency for managing a database transaction """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
