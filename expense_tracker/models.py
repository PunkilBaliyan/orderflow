from datetime import datetime
from decimal import Decimal, InvalidOperation

from expense_tracker.exceptions import InvalidExpenseError

CATEGORIES = ("food", "entertaiment", "transport", "rent", "utilities", "other")
CENTS = Decimal("0.01")


def parse_amount(raw: str) -> Decimal:
    """Convert a string to a Decimal, raising InvalidExpenseError if invalid."""
    try:
        amount = Decimal(raw).quantize(CENTS)
    except InvalidOperation as e:
        raise InvalidExpenseError(f"Invalid amount: {raw!r}") from e
    if not amount.is_finite() or amount < 0:
        raise InvalidExpenseError(f"Amount must be a positive number: {raw!r}")
    return amount


def parse_date(raw: str) -> str:
    """return the date as YYYY-MM-DD, or raise a InvalidExpenseError."""
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date().isoformat()
    except ValueError as e:
        raise InvalidExpenseError(f"invalid date (use YYYY-MM-DD):{raw!r}") from e


def make_expense(raw_date: str, raw_amount: str, category: str, note: str) -> dict:
    """Validate the inputs and return a new dictionary of new expense"""
    category = category.strip().lower()
    if category not in CATEGORIES:
        raise InvalidExpenseError(f"unknown category {category!r}")
    return {
        "date": parse_date(raw_date),
        "amount": parse_amount(raw_amount),
        "category": category,
        "note": note.strip(),
    }

def next_id(expenses: list[dict]) -> int:
    """Return the next unused expense id."""
    highest = 0
    for expense in expenses:
        highest = max(highest, expense["id"])
    return highest + 1
