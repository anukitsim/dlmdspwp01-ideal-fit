"""
src/database.py
================

SQLite helper for the *Ideal-Fit* assignment.

It does **one** job: create (or open) ``db/idealfit.db`` and make sure the
three required tables exist:

1. training -  x + y1‥y4        (raw noisy curves)
2. ideal   - x + y1‥y50       (perfect reference curves)
3. mapping - id + x, y, ideal_id, deviation (test-point assignments)


"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import Column, Float, Integer, MetaData, String, Table, create_engine
from sqlalchemy.engine import Engine


class DatabaseManager:
    """
    small wrapper around SQLAlchemy so the rest of the codebase never has to
    think about SQL—or paths on disk.

    Parameters
    ----------
    db_path : str, optional
        Relative (or absolute) location of the SQLite file.
        Defaults to ``"db/idealfit.db"``

    """

    def __init__(self, db_path: str = "db/idealfit.db") -> None:
        self.db_path: str = db_path
        self._engine: Engine | None = None
        self._meta: MetaData = MetaData()

        # Make sure the folder exists (useful in fresh clones)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Public helpers
    # ------------------------------------------------------------------ #
    def create_engine(self) -> Engine:
        """Create (or reuse) the SQLAlchemy engine that talks to SQLite."""
        if self._engine is None:
            self._engine = create_engine(f"sqlite:///{self.db_path}")
        return self._engine

    def create_tables(self) -> None:
        """
        Define all three tables only once and issue ``CREATE TABLE IF NOT EXISTS``
        so running the script twice does not brak anything.
        """
        if self._engine is None:
            self.create_engine()

        # --- 1) training -------------------------------------------------
        Table(
            "training",
            self._meta,
            Column("x", Float, primary_key=True),
            *[Column(f"y{i}", Float) for i in range(1, 5)],
        )

        # --- 2) ideal (50 y-columns) ------------------------------------
        Table(
            "ideal",
            self._meta,
            Column("x", Float, primary_key=True),
            *[Column(f"y{i}", Float) for i in range(1, 51)],
        )

        # --- 3) mapping --------------------------------------------------
        Table(
            "mapping",
            self._meta,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("x", Float),
            Column("y", Float),
            Column("ideal_id", String),  # e.g. "y17"
            Column("deviation", Float),  # |y_test – y_ideal|
        )

        # Actually create them in SQLite
        self._meta.create_all(self._engine)

    # ------------------------------------------------------------------ #
    # Convenience property
    # ------------------------------------------------------------------ #
    @property
    def engine(self) -> Engine:
        """Expose the underlying engine (read-only)."""
        return self.create_engine()
