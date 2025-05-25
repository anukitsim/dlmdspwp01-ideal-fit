"""
src/database.py
================

SQLite helper for the *Ideal-Fit* assignment.

It does **one** job: create (or open) ``db/idealfit.db`` and make sure the
three required tables exist:

1. training -  x + y1‥y4        (raw noisy curves)
2. ideal    -  x + y1‥y50       (perfect reference curves)
3. mapping  -  id + x, y, ideal_id, deviation (test-point assignments)
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import Column, Float, Integer, MetaData, String, Table, create_engine
from sqlalchemy.engine import Engine


class DatabaseManager:
    """
    Small wrapper around SQLAlchemy to handle database setup and access.

    Parameters
    ----------
    db_path : str, optional
        Path to the SQLite file. Defaults to "db/idealfit.db".
    """

    def __init__(self, db_path: str = "db/idealfit.db") -> None:
        """
        Initialize DatabaseManager and ensure the database directory exists.

        Creates the parent folder for the database file if it is missing.
        """
        self.db_path: str = db_path
        self._engine: Engine | None = None
        self._meta: MetaData = MetaData()

        # Make sure the folder exists (useful in fresh clones)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Public helpers
    # ------------------------------------------------------------------ #

    def create_engine(self) -> Engine:
        """
        Create or reuse a SQLAlchemy Engine connected to the SQLite database.

        Returns
        -------
        Engine
            The SQLAlchemy Engine for database operations.
        """
        if self._engine is None:
            self._engine = create_engine(f"sqlite:///{self.db_path}")
        return self._engine

    def create_tables(self) -> None:
        """
        Define and create the required tables if they do not already exist.

        Tables created:
        - training: x (primary key), y1–y4
        - ideal: x (primary key), y1–y50
        - mapping: id (primary key), x, y, ideal_id, deviation
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

        # Actually create the tables in SQLite
        self._meta.create_all(self._engine)

    # ------------------------------------------------------------------ #
    # Convenience property
    # ------------------------------------------------------------------ #

    @property
    def engine(self) -> Engine:
        """
        Provide the SQLAlchemy Engine for database access.

        Returns
        -------
        Engine
            The active SQLAlchemy Engine instance.
        """
        return self.create_engine()
