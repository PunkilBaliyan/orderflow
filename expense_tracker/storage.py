import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from expense_tracker.exceptions import StorageError

DATA_FILE = Path("data/expenses.json")

def save_expenses(expenses:list[dict],path:Path=DATA_FILE)-> None:
    """Write all of the expenses to the JSON file """
    records=[]
    for expense in expenses:
        record = dict(expense)
        record["amount"] = str(expense["amount"])
        records.append(record)
    try:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(records,indent=2),encoding="utf-8")
    except OSError as e:
        raise StorageError(f"cannot save {path}:{e}") from e

def load_expenses(path:Path=DATA_FILE)-> list[dict]:
    """Read Expenses from the JSON file and return a list of dictionaries to the user"""
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
        expenses=[]
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
        return expenses
    except FileNotFoundError:
        print(f"Warinng : {path} not found. Starting with no expenses")
        return []
    except OSError as e:
        raise StorageError(f"cannot read {path}:{e}") from e
    except (ValueError,KeyError,TypeError,InvalidOperation):
        print(f"Warning: {path} is corrupted. Starting with no expenses")
        return []
