from datetime import datetime

CATEGORIES = ("food", "entertainment", "transport", "rent", "utilities", "others")


def parse_amount(raw: str) -> float | None:
    """Parse a string to a positive float, or return None if invalid."""
    value = float(raw)
    return value if value > 0 else None


def parse_date(raw: str) -> str | None:
    """Parse a string to a date in YYYY-MM-DD format, or return None if invalid."""
    try:
        return datetime.strptime(raw, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return None


def add_expense(expenses: list[dict]) -> None:
    """Prompt the user for expense details and add it to the list of expenses."""
    amount = parse_amount(input("Amount: "))
    date = parse_date(input("Date: "))
    category = input(f"Category{CATEGORIES}: ").strip().lower()
    note = input("Note: ").strip()
    if amount is None or date is None or category not in CATEGORIES:
        print("Invalid input, expense not added.")
        return
    new_id = max((e["id"] for e in expenses), default=0) + 1
    expenses.append(
        {
            "id": new_id,
            "date": date,
            "amount": amount,
            "category": category,
            "note": note,
        }
    )
    print(f"Added expense #{new_id}.")


def list_expenses(expenses: list[dict]) -> None:
    """Print a list of expenses in a formatted table."""
    if not expenses:
        print("no expenses yet.")
        return
    print(f"{'ID':<5}{'Date':<12}{'Category':<15}{'Amount':>10} Note")
    for e in sorted(expenses, key=lambda e: e["date"]):
        print(
            f"{e['id']:<5}{e['date']:<12}{e['category']:<15}{e['amount']:>10.2f} {e['note']}"
        )


def filter_by_category(expenses: list[dict], category: str) -> list[dict]:
    """Return a list of expenses filtered by the given category."""
    return [e for e in expenses if e["category"] == category]


def summarize(expenses: list[dict]) -> None:
    """Print a summary of expenses, including total, average, and largest expense."""
    if not expenses:
        print("Nothing to summarise. ")
        return
    total = sum(e["amount"] for e in expenses)
    by_category = {
        c: sum(e["amount"] for e in expenses if e["category"] == c) for c in CATEGORIES
    }
    largest = max(expenses, key=lambda e: e["amount"])
    print(f"Total: {total:.2f}  Average: {total / len(expenses):.2f}")
    for cat, amt in by_category.items():
        print(f" {cat:<15}{amt:>10.2f}")
    print(f"Largest: {largest['amount']:.2f} ({largest['note']})")


def main() -> None:
    """Main loop for the expense tracker application."""
    print("Welcome to the expense tracker!")
    expenses: list[dict] = []
    while True:
        print("\n 1) Add 2) List 3) Filter 4) Monthly summary 5) Quit")
        choice = input("Choose: ").strip()
        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            list_expenses(expenses)
        elif choice == "3":
            category = input("Category: ").strip().lower()
            list_expenses(filter_by_category(expenses, category))
        elif choice == "4":
            month = input("Month (YYYY-MM): ").strip()
            summarize([e for e in expenses if e["date"].startswith(month)])
        elif choice == "5":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
