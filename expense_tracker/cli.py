import argparse
import logging
from datetime import date
from pathlib import Path

from expense_tracker.exceptions import ExpenseTrackerError
from expense_tracker.models import CATEGORIES, make_expense, next_id
from expense_tracker.storage import load_expenses, read_csv_expenses, save_expenses, write_csv

LOG_FILE = Path("logs/app.log")
logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """File gets DEBUG and above; the console gets INFO and above."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[file_handler, console_handler],
    )


def build_parser() -> argparse.ArgumentParser:
    """Describe the commands and options the program accepts."""
    parser = argparse.ArgumentParser(
        prog="expense_tracker", description="Track your expenses."
    )
    sub_parser = parser.add_subparsers(dest="command", required=True)

    add_parser = sub_parser.add_parser("add", help="add an expense")
    add_parser.add_argument("--amount", required=True, help="e.g. 250 or 99.50")
    add_parser.add_argument("--category", required=True, choices=CATEGORIES)
    add_parser.add_argument(
        "--date", default=date.today().isoformat(), help="YYYY-MM-DD (default: today)"
    )
    add_parser.add_argument("--note", default="")

    list_parser = sub_parser.add_parser("list", help="list expenses")
    list_parser.add_argument("--category", choices=CATEGORIES)

    export_parser = sub_parser.add_parser("export-csv", help="export to a CSV file")
    export_parser.add_argument("path", type=Path)
    import_parser = sub_parser.add_parser("import-csv", help="import from a CSV file")
    import_parser.add_argument("path", type=Path)
    return parser


def add_command(args: argparse.Namespace) -> None:
    """Validate the inputs, then save one new expense."""
    expense = make_expense(args.date, args.amount, args.category, args.note)
    expenses = load_expenses()
    expense["id"] = next_id(expenses)
    expenses.append(expense)
    save_expenses(expenses)
    print(
        f"Added #{expense['id']}: {expense['amount']:.2f}"
        f"{expense['category']} on {expense['date']}"
    )


def list_command(args: argparse.Namespace) -> None:
    """Print expenses as a table, optionally for one category."""
    expenses = load_expenses()
    if args.category is not None:
        expenses = [e for e in expenses if e["category"] == args.category]
    if not expenses:
        print("No expenses found.")
        return
    print(f"{'ID':<5}{'Date':<12}{'Category':<15}{'Amount':>10}  Note")
    for e in sorted(expenses, key=lambda e: e["date"]):
        print(
            f"{e['id']:<5}{e['date']:<12}{e['category']:<15}{e['amount']:>10.2f}  {e['note']}"
        )


def export_csv_command(args: argparse.Namespace) -> None:
    """Write all saved expenses to a CSV file."""
    expenses = load_expenses()
    write_csv(expenses, args.path)
    print(f"Exported {len(expenses)} expenses to {args.path}")


def import_csv_command(args: argparse.Namespace) -> None:
    """Read a CSV file and add every good row to the saved expenses."""
    expenses = load_expenses()
    count_before = len(expenses)
    for expense in read_csv_expenses(args.path):
        expense["id"] = next_id(expenses)
        expenses.append(expense)
    save_expenses(expenses)
    print(f"Imported {len(expenses) - count_before} expenses.")


def main(argv: list[str] | None = None) -> int:
    """Run the program. Returns 0 on success, 1 on a handled error."""
    setup_logging()
    args = build_parser().parse_args(argv)
    try:
        if args.command == "add":
            add_command(args)
        elif args.command == "list":
            list_command(args)
        elif args.command == "export-csv":
            export_csv_command(args)
        elif args.command == "import-csv":
            import_csv_command(args)
    except ExpenseTrackerError as e:
        logger.error("%s", e)
        return 1
    return 0
