"""
src/selector.py
===============

Finds the best-matching ideal function for each of the four noisy
training functions, using the least-squares error metric.

Reads tables `training` and `ideal` from the SQLite database, computes
Σ (y_train – y_ideal)² for each pair, picks the ideal with the smallest
error for each training column, records the max deviation, and writes
results to a new `chosen_ideals` table.

Returns a Python dict mapping training columns to ideal columns.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd
from sqlalchemy import text

from .database import DatabaseManager


def _load_tables(db: DatabaseManager) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the `training` and `ideal` tables into pandas DataFrames.

    Parameters
    ----------
    db : DatabaseManager
        The database manager with an active connection.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        A tuple of (training_df, ideal_df).
    """
    training = pd.read_sql("SELECT * FROM training", db.engine)
    ideal = pd.read_sql("SELECT * FROM ideal", db.engine)
    return training, ideal


def _least_squares(col_a: pd.Series, col_b: pd.Series) -> float:
    """
    Compute the sum of squared differences between two Series.

    Parameters
    ----------
    col_a : pd.Series
        First numeric series.
    col_b : pd.Series
        Second numeric series.

    Returns
    -------
    float
        Sum of (a - b)² across all elements.
    """
    return ((col_a - col_b) ** 2).sum()


def select_best_ideals(db: DatabaseManager) -> Dict[str, str]:
    """
    Match each noisy training column (y1–y4) to its best ideal column (y1–y50).

    Parameters
    ----------
    db : DatabaseManager
        Active database connection for reading/writing tables.

    Returns
    -------
    Dict[str, str]
        Mapping from training column name to chosen ideal column name.

    Side Effects
    ------------
    Writes a `chosen_ideals` table with columns:
    training_col, ideal_col, max_deviation.
    """
    training_df, ideal_df = _load_tables(db)

    training_cols: List[str] = [c for c in training_df.columns if c != "x"]
    ideal_cols: List[str] = [c for c in ideal_df.columns if c != "x"]

    results: List[dict] = []
    mapping: Dict[str, str] = {}

    for tcol in training_cols:
        min_error = float("inf")
        best_icol: str | None = None

        for icol in ideal_cols:
            err = _least_squares(training_df[tcol], ideal_df[icol])
            if err < min_error:
                min_error, best_icol = err, icol

        # calculate max absolute deviation for the winning pair
        max_dev = (training_df[tcol] - ideal_df[best_icol]).abs().max()

        results.append({
            "training_col": tcol,
            "ideal_col": best_icol,
            "max_deviation": max_dev,
        })
        mapping[tcol] = best_icol  # type: ignore

    # write or replace the chosen_ideals table
    pd.DataFrame(results).to_sql(
        "chosen_ideals",
        db.engine,
        if_exists="replace",
        index=False,
    )

    return mapping