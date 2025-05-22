"""
Unit test for the least-squares selector.
"""

from sqlalchemy import text
from src.selector import select_best_ideals


def test_selector_picks_four_unique_ideals(db):
    mapping = select_best_ideals(db)
    assert set(mapping.keys()) == {"y1", "y2", "y3", "y4"}
    assert len(set(mapping.values())) == 4

    with db.engine.connect() as conn:
        rows = conn.scalar(text("SELECT COUNT(*) FROM chosen_ideals"))
    assert rows == 4
