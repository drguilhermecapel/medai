import pytest
from app.database import get_db, engine, SessionLocal

def test_database_setup():
    assert engine is not None
    assert SessionLocal is not None

def test_get_db():
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    # Cleanup
    try:
        next(db_gen)
    except StopIteration:
        pass
