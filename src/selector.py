"""
src/selector.py
===============

Finds the best-matching ideal function for each of the four noisy
training functions, using the least-squares error metric.

Reads tables training and ideal from db/idealfit.db
Calculates  Σ (y_train - y_ideal)²  for every combination
Picks the ideal column with the smallest error for each training column
Also records the maximum absolute deviation for that winning pair
Writes the 4 results into a new SQLite table named chosen_ideals
  (training_col | ideal_col | max_deviation)
  
Returns a Python dict →  {'y1':'y17', 'y2':'y03', ...}


"""

from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd
from sqlalchemy import text

from .database import DatabaseManager


def _load_tables(db: DatabaseManager) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Pull training and ideal as pandas DataFrames."""
    training = pd.read_sql("SELECT * FROM training", db.engine)
    ideal = pd.read_sql("SELECT * FROM ideal", db.engine)
    return training, ideal


def _least_squares(col_a: pd.Series, col_b: pd.Series) -> float:
    """Σ (a - b)² without normalising by N (only compare magnitudes)."""
    return ((col_a - col_b) ** 2).sum()


def select_best_ideals(db: DatabaseManager) -> Dict[str, str]:
    """
    Match each noisy training column (y1‥y4) to one ideal column (y1‥y50).

    Parameters
    ----------
    db : DatabaseManager
        Open (or new) connection to db/idealfit.db.

    Returns
    -------
    dict
        Mapping e.g. {'y1': 'y17', 'y2': 'y03', 'y3': 'y29', 'y4': 'y42'}
    """
    training_df, ideal_df = _load_tables(db)

    training_cols: List[str] = [c for c in training_df.columns if c != "x"]
    ideal_cols: List[str] = [c for c in ideal_df.columns if c != "x"]

    results = []          # list of dicts → will become DataFrame
    mapping: Dict[str, str] = {}

    for tcol in training_cols:
        min_error = float("inf")
        best_icol = None

        for icol in ideal_cols:
            err = _least_squares(training_df[tcol], ideal_df[icol])
            if err < min_error:
                min_error, best_icol = err, icol

        # calculate max absolute deviation for the winning pair
        max_dev = (training_df[tcol] - ideal_df[best_icol]).abs().max()

        results.append(
            {"training_col": tcol,
             "ideal_col": best_icol,
             "max_deviation": max_dev}
        )
        mapping[tcol] = best_icol

    # write/replace SQLite table
    pd.DataFrame(results).to_sql(
        "chosen_ideals", db.engine, if_exists="replace", index=False
    )

    return mapping
