"""
src/mapper.py
=============

Assign every (x, y) pair in test_data.csv to one of the four chosen
ideal curves—if it is close enough.

Rule:
    | y_test - y_ideal |  ≤  max_deviation x √2

 Reads:
    - chosen_ideals  (training_col | ideal_col | max_deviation)
    - ideal          (x | y1‥y50)
    - test_data.csv  via TestLoader
 For each test row chooses the ideal curve with the smallest deviation that still satisfies the rule.
 Inserts the accepted points into SQLite table mapping
  (x | y | ideal_id | deviation).

Returns number of inserted rows.
"""

from __future__ import annotations

import math
from typing import List, Tuple

import pandas as pd
from sqlalchemy import text

from .database import DatabaseManager
from .loader import TestLoader


def _load_helpers(
    db: DatabaseManager,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fetch chosen_ideals + ideal table + test DataFrame."""
    chosen = pd.read_sql("SELECT * FROM chosen_ideals", db.engine)
    ideal = pd.read_sql("SELECT * FROM ideal", db.engine)
    test = TestLoader("data/test_data.csv").to_dataframe()
    return chosen, ideal, test


def map_test_points(db: DatabaseManager) -> int:
    """
    Classify test points and write accepted ones to mapping table.

    Returns
    -------
    int;
        Number of rows inserted.
    """
    chosen_df, ideal_df, test_df = _load_helpers(db)

    accepted_rows: List[dict] = []

    # Build a quick lookup dict: ideal_col -> max_deviation
    tol = {
        row["ideal_col"]: row["max_deviation"] * math.sqrt(2)
        for _, row in chosen_df.iterrows()
    }
    ideal_cols = list(tol.keys())

    for _, test_row in test_df.iterrows():
        x_val, y_val = test_row["x"], test_row["y"]

        # Sub-select the row in ideal_df where x matches
        ideal_row = ideal_df[ideal_df["x"] == x_val]
        if ideal_row.empty:
            continue  # should not happen; skip

        best_match = None
        best_dev = float("inf")

        for icol in ideal_cols:
            deviation = abs(y_val - ideal_row.iloc[0][icol])
            if deviation <= tol[icol] and deviation < best_dev:
                best_match, best_dev = icol, deviation

        if best_match:
            accepted_rows.append(
                {
                    "x": x_val,
                    "y": y_val,
                    "ideal_id": best_match,
                    "deviation": best_dev,
                }
            )

    # Create DataFrame → append to mapping table
    if accepted_rows:
        pd.DataFrame(accepted_rows).to_sql(
            "mapping", db.engine, if_exists="append", index=False
        )

        # Create DataFrame → append to mapping table
    if accepted_rows:
        pd.DataFrame(accepted_rows).to_sql(
            "mapping", db.engine, if_exists="append", index=False
        )
    else:  # <── nothing matched
        from .exceptions import NoIdealMatchError

        raise NoIdealMatchError(
            "No test point matched any ideal curve (tolerance √2 × max_dev)."
        )

    return len(accepted_rows)
