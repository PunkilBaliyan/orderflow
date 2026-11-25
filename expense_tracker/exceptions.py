"""Custom exceptions for the expense tracker."""


class ExpenseTrackerError(Exception):
    """Base class for all errors raised on purpose by this project."""


class InvalidExpenseError(ExpenseTrackerError):
    """An expense failed validation (bad amount, date or category)."""


class StorageError(ExpenseTrackerError):
    """Reading or writing a data file failed."""
