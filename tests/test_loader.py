"""
Basic checks for CsvLoader subclasses.
"""

import pandas as pd
import pytest
from src.loader import TrainingLoader
from src.exceptions import DataValidationError


def test_training_loader_returns_dataframe():
    df = TrainingLoader("data/training_data.csv").to_dataframe()
    assert isinstance(df, pd.DataFrame)
    # should contain 400 rows and 5 columns (x + y1–y4)
    assert df.shape == (400, 5)


def test_training_loader_missing_file_raises(tmp_path):
    # A dummy path that does not exist
    bogus = tmp_path / "nope.csv"
    with pytest.raises(DataValidationError):
        TrainingLoader(bogus).to_dataframe()
