"""
src/loader.py
=============

Reusable CSV loaders for the Ideal-Fit project.

CsvLoader - base class (handles file path, DataFrame caching, DB insert)
TrainingLoader - loads training_data.csv  ->  table 'training'
IdealLoader - loads ideal_functions.csv ->  table 'ideal'
TestLoader - loads test_data.csv      ->  not written to DB (is only kept in RAM)

"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

from .database import DatabaseManager
from .exceptions import DataValidationError


class CsvLoader:
    """Parent class that any  loader can inherit from."""

    # subclasses must override this
    TABLE_NAME: Final[str | None] = None

    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise DataValidationError(f"CSV file not found: {self.csv_path}")

        self._df: pd.DataFrame | None = None

    # ------------------------------------------------------------------ #
    # Public helpers
    # ------------------------------------------------------------------ #
    def to_dataframe(self) -> pd.DataFrame:
        """Load the CSV once and cache the DataFrame."""
        if self._df is None:
            self._df = pd.read_csv(self.csv_path)

            # ===== safety-net ======================================
        if self._df.empty:
            from .exceptions import DataValidationError

            raise DataValidationError(f"CSV file is empty: {self.csv_path}")
        # =============================================================

        return self._df

    def to_db(self, db: DatabaseManager) -> None:
        """
        Bulk-insert the DataFrame into SQLite.

        Parameters
        ----------
        db : DatabaseManager
            Instance that already opened (or will open) db/idealfit.db.
        """
        if self.TABLE_NAME is None:
            # TestLoader will call parent but should not write
            return

        # pandas' to_sql will create the table if missing,
        # but we *already* created empty tables, so just append.
        self.to_dataframe().to_sql(
            name=self.TABLE_NAME,
            con=db.engine,
            if_exists="append",
            index=False,
        )


# ---------------------------------------------------------------------- #
# Concrete subclasses
# ---------------------------------------------------------------------- #
class TrainingLoader(CsvLoader):
    TABLE_NAME = "training"


class IdealLoader(CsvLoader):
    TABLE_NAME = "ideal"


class TestLoader(CsvLoader):
    # we have None here because test points are not here at load time
    #    They will be written later by the Mapper.
    TABLE_NAME = None
