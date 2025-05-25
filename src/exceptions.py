"""
exceptions.py
-------------
Error types used in the Ideal-Fit assignment.

- DataValidationError: CSV file is missing or empty.
- NoIdealMatchError: No test point matched within the √2 tolerance.
"""

class DataValidationError(Exception):
    """
    Raised when a CSV file is missing or contains no rows.

    This indicates that the loader could not find the file
    or that it was completely empty.
    """

class NoIdealMatchError(Exception):
    """
    Raised when no test point satisfies the √2 × max_deviation threshold.

    This occurs if every point in the test set is too far from
    its candidate ideal curves to be considered a match.
    """
