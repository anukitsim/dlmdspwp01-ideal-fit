"""
Tests for the √2 mapper (src/mapper.py)
"""

from sqlalchemy import text
import pytest
import pandas as pd
from src.mapper import map_test_points
from src.exceptions import NoIdealMatchError


def test_mapper_inserts_rows(db):
    """start from an empty mapping table, mapper should insert ≥ 1 row."""
    with db.engine.begin() as conn:
        conn.execute(text("DELETE FROM mapping"))

    inserted = map_test_points(db)
    assert inserted > 0

    with db.engine.connect() as conn:
        rows = conn.scalar(text("SELECT COUNT(*) FROM mapping"))
    assert rows >= inserted  # allow duplicates


def test_mapper_raises_custom_if_nothing(tmp_path, db):
    """Feed an empty CSV - expect NoIdealMatchError."""
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("x,y\n")  # header only

    # patch TestLoader everywhere mapper might have cached it
    from src import loader
    import src.mapper as mapper

    OriginalLoader = loader.TestLoader

    class _EmptyLoader(OriginalLoader):
        def __init__(self, *_a, **_kw):
            # skip parent __init__ entirely, just store the path
            self.csv_path = empty_csv
            self._df = None

        def to_dataframe(self):  # override to return an EMPTY df without raising
            if self._df is None:
                self._df = pd.DataFrame(columns=["x", "y"])
            return self._df

    loader.TestLoader = _EmptyLoader
    mapper.TestLoader = _EmptyLoader  # make sure mapper re-uses it

    with pytest.raises(NoIdealMatchError):
        map_test_points(db)

    # restore
    loader.TestLoader = OriginalLoader
    mapper.TestLoader = OriginalLoader
