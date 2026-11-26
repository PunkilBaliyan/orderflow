"""Summaries of expenses."""

import functools
import logging
import time
from decimal import Decimal

from expense_tracker.models import CENTS

logger = logging.getLogger(__name__)


def timed(func):
    """Decorator: log how long the decorated function took."""

    @functools.wraps(func)  # keeps the original __name__ and __doc__
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug("%s took %.4fs", func.__name__, elapsed)
        return result

    return wrapper


@timed
def build_report(expenses: list[dict]) -> dict:
    """Work out count, total, average, per-category totals and largest expense."""
    total = Decimal("0.00")
    by_category = {}
    for expense in expenses:
        total += expense["amount"]
        category = expense["category"]
        so_far = by_category.get(category, Decimal("0.00"))
        by_category[category] = so_far + expense["amount"]

    count = len(expenses)
    average = Decimal("0.00")
    largest = None
    if count > 0:
        average = (total / count).quantize(CENTS)
        largest = max(expenses, key=lambda e: e["amount"])

    return {
        "count": count,
        "total": total,
        "average": average,
        "by_category": by_category,
        "largest": largest,
    }


def format_report(report: dict) -> str:
    """Turn a report dict into text that is ready to print."""
    if report["count"] == 0:
        return "No expenses found."
    header = (
        f"Expenses: {report['count']}   Total: {report['total']:.2f}   "
        f"Average: {report['average']:.2f}"
    )
    lines = [header, "By category:"]
    for category, amount in report["by_category"].items():
        lines.append(f"  {category:<15}{amount:>10.2f}")
    big = report["largest"]
    lines.append(
        f"Largest: {big['amount']:.2f} on {big['date']} "
        f"({big['category']}) {big['note']}"
    )
    return "\n".join(lines)
