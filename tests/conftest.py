"""
conftest.py — shared pytest fixtures
"""

from __future__ import annotations

import sys
from pathlib import Path
from sqlalchemy import text
import pytest  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from src.database import DatabaseManager  # noqa: E402
from src.loader import TrainingLoader, IdealLoader  # noqa: E402


@pytest.fixture(scope="session")
def db():
    """Shared SQLite handle, pre-loaded with training & ideal data."""
    db = DatabaseManager()
    db.create_tables()

    with db.engine.connect() as conn:
        if conn.scalar(text("SELECT COUNT(*) FROM training")) == 0:
            TrainingLoader("data/training_data.csv").to_db(db)
            IdealLoader("data/ideal_functions.csv").to_db(db)

    return db
