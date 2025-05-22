"""
exceptions.py - error types
------------------------------------

 • DataValidationError
      If a CSV file is missing or totally empty.

 • NoIdealMatchError
      When a point in the test set can not be matched to
     any of the four selected ideal curves.
"""


class DataValidationError(Exception):
    """CSV is missing or has zero rows."""


class NoIdealMatchError(Exception):
    """Nothing in test_data.csv satisfied the √2 tolerance."""
