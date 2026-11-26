"""Save and load expenses as a JSON file."""

import csv
import json
import logging  # changed
from decimal import Decimal, InvalidOperation
from pathlib import Path

from collections.abc import Iterator
from expense_tracker.exceptions import InvalidExpenseError, StorageError
from expense_tracker.models import make_expense

logger = logging.getLogger(__name__)  # changed

DATA_FILE = Path("data/expenses.json")
CSV_COLUMNS = ["id", "date", "amount", "category", "note"]


def write_csv(expenses: list[dict], path: Path) -> None:
    """Export all expenses to a CSV file."""
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(expenses)
    except OSError as exc:
        raise StorageError(f"cannot write {path}: {exc}") from exc
    logger.info("Exported %d expenses to %s", len(expenses), path)


def save_expenses(expenses: list[dict], path: Path = DATA_FILE) -> None:
    """Write all expenses to a JSON file (safely, via a temporary file)."""
    records = []
    for expense in expenses:
        record = dict(expense)  # copy, so the original keeps its Decimal
        record["amount"] = str(expense["amount"])  # JSON has no Decimal
        records.append(record)
    tmp_path = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        tmp_path.replace(path)  # swap the finished file into place
    except OSError as exc:
        raise StorageError(f"cannot save {path}: {exc}") from exc
    logger.info("Saved %d expenses to %s", len(expenses), path)


def load_expenses(path: Path = DATA_FILE) -> list[dict]:
    """Read expenses from a JSON file. Missing or corrupt file gives []."""
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
        expenses = []
        for record in records:
            expenses.append(
                {
                    "id": record["id"],
                    "date": record["date"],
                    "amount": Decimal(record["amount"]),
                    "category": record["category"],
                    "note": record["note"],
                }
            )
        logger.debug("Loaded %d expenses from %s", len(expenses), path)  # changed
        return expenses
    except FileNotFoundError:
        logger.warning(
            "Data file %s not found. Starting with no expenses.", path
        )  # changed
        return []
    except OSError as exc:
        raise StorageError(f"cannot read {path}: {exc}") from exc
    except (ValueError, KeyError, TypeError, InvalidOperation) as exc:
        logger.warning(
            "Data file %s is corrupt (%r). Starting empty.", path, exc
        )  # changed
        return []

def read_csv_expenses(path: Path) -> Iterator[dict]:
    """Generator: yield one valid expense per good CSV row, skip bad rows."""
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for column in ["date", "amount", "category", "note"]:
                if reader.fieldnames is None or column not in reader.fieldnames:
                    raise StorageError(
                        f"{path} needs the columns: date, amount, category, note"
                    )
            for row in reader:
                if None in row or None in row.values():
                    logger.warning("Skipping row with missing values: %s", row)
                    continue
                try:
                    expense = make_expense(
                        row["date"], row["amount"], row["category"], row["note"]
                    )
                except InvalidExpenseError as e:
                    logger.warning("Skipping invalid row %s: %s", row, e)
                    continue
                yield expense
    except (OSError, UnicodeDecodeError) as e:
        raise StorageError(f"cannot read {path}: {e}") from e
