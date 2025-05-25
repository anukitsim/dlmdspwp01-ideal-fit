"""
src/loader.py
=============

Reusable CSV loaders for the Ideal-Fit project.

CsvLoader - base class (handles file path, DataFrame caching, DB insert)
TrainingLoader - loads training_data.csv  ->  table 'training'
IdealLoader   - loads ideal_functions.csv ->  table 'ideal'
TestLoader    - loads test_data.csv       -> not written to DB (only used in memory)
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

from .database import DatabaseManager
from .exceptions import DataValidationError


class CsvLoader:
    """
    Base loader class for CSV files. Handles file path validation,
    DataFrame caching, and optional database insertion.
    """

    # Subclasses must override this with a table name, or None
    TABLE_NAME: Final[str | None] = None

    def __init__(self, csv_path: str | Path) -> None:
        """
        Initialize CsvLoader and verify that the CSV file exists.

        Parameters
        ----------
        csv_path : str or Path
            Path to the CSV file to load.

        Raises
        ------
        DataValidationError
            If the CSV file does not exist.
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise DataValidationError(f"CSV file not found: {self.csv_path}")

        self._df: pd.DataFrame | None = None

    def to_dataframe(self) -> pd.DataFrame:
        """
        Load the CSV into a pandas DataFrame on first call and cache it.

        Returns
        -------
        pd.DataFrame
            The loaded DataFrame with CSV contents.

        Raises
        ------
        DataValidationError
            If the CSV is empty after loading.
        """
        if self._df is None:
            self._df = pd.read_csv(self.csv_path)
            if self._df.empty:
                raise DataValidationError(f"CSV file is empty: {self.csv_path}")
        return self._df

    def to_db(self, db: DatabaseManager) -> None:
        """
        Bulk-insert the DataFrame into the specified database table.

        Parameters
        ----------
        db : DatabaseManager
            Database manager instance with an active connection.
        """
        # If TABLE_NAME is None, this loader should not write to DB
        if self.TABLE_NAME is None:
            return

        # Append DataFrame to existing table
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
    """
    Loader for training_data.csv. Inserts into 'training' table.
    """
    TABLE_NAME = "training"


class IdealLoader(CsvLoader):
    """
    Loader for ideal_functions.csv. Inserts into 'ideal' table.
    """
    TABLE_NAME = "ideal"


class TestLoader(CsvLoader):
    """
    Loader for test_data.csv. Used only in memory, does not write.
    """
    TABLE_NAME = None
