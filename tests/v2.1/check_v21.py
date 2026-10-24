#!/usr/bin/env python3
"""Offline checks for Family Book v2.1.

These use a temporary folder as the user's computer. They do not call Excel,
and they do not read or write a real Family Book folder. Receipt files written
here start with ``TEST - ``.

    python3 tests/v2.1/check_v21.py
"""

from __future__ import annotations

import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from openpyxl import load_workbook  # noqa: E402

from bot.local.bookio import (  # noqa: E402
    advice,
    apply_receipts,
    cards_empty,
    init_local_book,
    is_locked,
    mark_statement_added,
    migrate_v21_settings,
    receipt_key,
    receipt_stats,
    record_report_sent,
    report_already_sent,
    report_totals,
    routine_gate,
    set_offer,
    short_store,
    suggest_statement,
    transactions_empty,
    week_period,
)
from bot.local.queue import LocalComputer, ReceiptQueue, drain  # noqa: E402


def _load_v2_identity():
    import importlib.util
    path = ROOT / "tests" / "v2.0" / "familybook_v2.py"
    spec = importlib.util.spec_from_file_location("familybook_v2", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["familybook_v2"] = module
    spec.loader.exec_module(module)
    return module


V2 = _load_v2_identity()


class Fail(RuntimeError):
    pass


def check(condition, detail) -> None:
    if not condition:
        raise Fail(detail)


def receipt(store="Costco", when="2026-10-03 12:00", total=12.34, **extra) -> dict:
    body = extra.pop("body", None)
    if body is None:
        body = f"{store}\n{when}\nTotal {total:.2f}\nPaid cash\n"
    item = {
        "store": store,
        "when": when,
        "total": total,
        "number": extra.pop("number", ""),
        "last4": extra.pop("last4", ""),
        "category": extra.pop("category", "Meals"),
        "source": extra.pop("source", "photo"),
        "ext": extra.pop("ext", ".txt"),
        "body": body,
    }
    item.update(extra)
    return item


def new_book(folder: Path, year: int = 2026) -> Path:
    name = "TEST - Family Book - 2026.xlsx"
    return init_local_book(ROOT / "template" / "family-book-template.xlsx", folder, year, name)


def grid_amount(path: Path, sheet: str, coord: str):
    wb = load_workbook(path)
    return wb[sheet][coord].value


def snapshot_numbers(path: Path) -> dict:
    wb = load_workbook(path)
    found = {}
    for name in wb.sheetnames:
        ws = wb[name]
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, (int, float)):
                    found[(name, cell.coordinate)] = cell.value
                elif isinstance(cell.value, str) and cell.value.startswith("="):
                    found[(name, cell.coordinate)] = cell.value
    return found


def test_keys_match_cloud() -> None:
    when = date(2026, 10, 3)
    check(short_store("Costco.ca") == "Costco", short_store("Costco.ca"))
    check(short_store("HOME DEPOT #7016") == "Home Depot", short_store("HOME DEPOT #7016"))
    blank = receipt_key("Costco Wholesale", "", when, 12.34)
    numbered = receipt_key("Costco", "#48291", when, 12.34)
    check(blank == "Costco|2026-10-03|12.34", blank)
    check(numbered == "Costco|48291", numbered)
    check(blank == V2.receipt_identity("Costco", "", when, 12.34), blank)
    check(numbered == V2.receipt_identity("Costco", "48291", when, 12.34), numbered)


def test_receipts_only_and_no_excel(tmp: Path) -> None:
    book = new_book(tmp)
    source = (ROOT / "bot" / "local" / "bookio.py").read_text(encoding="utf-8")
    check("subprocess" not in source, "book writer must not shell out")
    check("startfile" not in source and "osascript" not in source, "book writer must not launch an app")
    result = apply_receipts(
        book,
        [receipt()],
        tmp / "receipts",
        tmp / "backups",
        name_prefix="TEST - ",
        stamp="20261024-120000",
    )
    check(result["wrote"] == ["Costco|2026-10-03|12.34"], result)
    check(result["backup"], result)
    check(grid_amount(book, "Oct", "O6") == 12.34, grid_amount(book, "Oct", "O6"))
    check(transactions_empty(book), "transactions should stay empty")
    check(cards_empty(book), "cards should stay empty")
    check(routine_gate(book)["may_remind"] is False, routine_gate(book))
    check(routine_gate(book)["may_nudge"] is False, "nudge")
    check(routine_gate(book)["may_bank_income"] is False, "income")
    check(routine_gate(book)["may_bank_fixed"] is False, "fixed")
    wb = load_workbook(book)
    check(wb["Annual Summary"]["C47"].value == "off", wb["Annual Summary"]["C47"].value)
    check(wb["Annual Summary"]["C46"].value == "v2.1", wb["Annual Summary"]["C46"].value)
    names = list((tmp / "receipts").iterdir())
    check(len(names) == 1 and names[0].name.startswith("TEST - "), names)
    check(names[0].name == "TEST - 2026-10-03 1200 - Costco - 12.34.txt", names[0].name)
    # The file is a real xlsx package. Opening it does not require Excel.
    package = zipfile.ZipFile(book)
    check("[Content_Types].xml" in package.namelist() and "xl/workbook.xml" in package.namelist(), "xlsx")
    again = apply_receipts(book, [receipt()], tmp / "receipts", tmp / "backups", name_prefix="TEST - ", stamp="20261024-120100")
    check(again["skipped"] == ["Costco|2026-10-03|12.34"], again)
    check(again["backup"] == "", "a duplicate must not replace the workbook")
    check(grid_amount(book, "Oct", "O6") == 12.34, "amount was added twice")
    totals = report_totals(book, date(2026, 10, 1), date(2026, 10, 7))
    check(totals.get("Meals") == 12.34, totals)
    check("Meals" in advice(totals), advice(totals))
    check(advice({}) == "", "empty report stays quiet")


def test_split_fills_grid(tmp: Path) -> None:
    book = new_book(tmp)
    item = receipt(
        total=14.34,
        items=[
            {"name": "milk", "price": 10.00, "category": "Meals"},
            {"name": "soap", "price": 4.34, "category": "Household Goods"},
        ],
    )
    apply_receipts(book, [item], tmp / "receipts", tmp / "backups", name_prefix="TEST - ", stamp="20261024-120200")
    check(grid_amount(book, "Oct", "O6") == 10.00, grid_amount(book, "Oct", "O6"))
    check(grid_amount(book, "Oct", "O22") == 4.34, grid_amount(book, "Oct", "O22"))
    check(transactions_empty(book), "split receipt is not a statement line")


def test_suggestion_remembers_no(tmp: Path) -> None:
    book = new_book(tmp)
    today = date(2026, 10, 24)
    check(suggest_statement("off", "not yet", 1, date(2026, 10, 23), today) == "", "too soon")
    early = suggest_statement("off", "not yet", 1, date(2026, 10, 10), today)
    check("GitHub" in early and "won't ask again" in early, early)
    check("own drive" in early, early)
    check(suggest_statement("off", "declined", 40, date(2026, 1, 1), today) == "", "a no sticks")
    check(suggest_statement("off", "asked", 40, date(2026, 1, 1), today) == "", "already asked")
    check(suggest_statement("on", "not yet", 40, date(2026, 1, 1), today) == "", "features already on")
    for index in range(10):
        apply_receipts(
            book,
            [receipt(when=f"2026-10-03 12:0{index % 10}", total=10 + index, body=f"Costco\nTotal {10 + index:.2f}\n")],
            tmp / "receipts",
            tmp / "backups",
            name_prefix="TEST - ",
            stamp=f"20261024-13{index:04d}",
        )
    stats = receipt_stats(book)
    check(stats["count"] == 10, stats)
    text = suggest_statement("off", "not yet", stats["count"], stats["first"], today)
    check(text.startswith("You've been logging receipts"), text)
    before = snapshot_numbers(book)
    set_offer(book, "declined")
    check(snapshot_numbers(book) == before, "remembering a no changed a number")
    check(load_workbook(book)["Annual Summary"]["C48"].value == "declined", "offer")
    apply_receipts(
        book,
        [receipt(total=99.99, body="Costco\nTotal 99.99\n")],
        tmp / "receipts",
        tmp / "backups",
        name_prefix="TEST - ",
        stamp="20261024-140000",
    )
    later = receipt_stats(book)
    check(suggest_statement("off", "declined", later["count"], later["first"], today) == "", "must not nag")
    start, end, period = week_period(date(2026, 10, 4))
    check(period == "2026-10-04", period)
    check(start == date(2026, 9, 28) and end == date(2026, 10, 4), (start, end))
    record_report_sent(book, "weekly", period)
    check(report_already_sent(book, "weekly", period), "weekly report would be sent twice")


def test_queue_offline_lock_backup(tmp: Path) -> None:
    computer_root = tmp / "computer"
    book = new_book(computer_root)
    staging = tmp / "bot-staging"
    queue_path = tmp / "TEST - queue.json"
    queue = ReceiptQueue(queue_path)
    first = receipt()
    second_same = receipt(body="Costco\nTotal 12.34\nsecond photo\n")
    check(queue.enqueue(first)["result"] == "queued", "enqueue")
    check(queue.enqueue(second_same)["result"] == "duplicate", "same key queued twice")
    check(len(queue.items) == 1, queue.items)
    offline = LocalComputer(computer_root, online=False)
    waiting = drain(queue, offline, book.name, staging, name_prefix="TEST - ", stamp="20261024-150000")
    check(waiting["waiting"] == ["Costco|2026-10-03|12.34"], waiting)
    check(offline.approvals == 0, offline.approvals)
    check(grid_amount(book, "Oct", "O6") in (None, ""), "offline drain wrote the book")
    check(queue.items[0]["status"] == "queued", queue.items[0])
    online = LocalComputer(computer_root, online=True)
    done = drain(queue, online, book.name, staging, name_prefix="TEST - ", stamp="20261024-150000")
    check(done["wrote"] == ["Costco|2026-10-03|12.34"], done)
    check(online.approvals == 2, online.approvals)
    check(grid_amount(book, "Oct", "O6") == 12.34, grid_amount(book, "Oct", "O6"))
    backup = computer_root / "backups" / "TEST - Family Book - 2026 - 20261024-150000.xlsx"
    check(backup.exists(), "missing backup")
    check(load_workbook(backup)["Oct"]["O6"].value in (None, ""), "backup was taken after the write")
    check(load_workbook(book)["Oct"]["O6"].value == 12.34, "live book")
    quiet = drain(queue, online, book.name, staging, name_prefix="TEST - ", stamp="20261024-150100")
    check(quiet["wrote"] == [], quiet)
    check(grid_amount(book, "Oct", "O6") == 12.34, "second drain duplicated the amount")

    other = receipt(store="Shell", when="2026-10-04 09:15", total=40.00, category="Fuel", body="Shell\nTotal 40.00\n")
    queue.enqueue(other)
    lock = Path(str(book) + ".lock")
    lock.write_text("open in another app", encoding="utf-8")
    check(is_locked(book), "lock marker")
    held = drain(queue, online, book.name, staging, name_prefix="TEST - ", stamp="20261024-160000")
    check(held["locked"] is True, held)
    check(grid_amount(book, "Oct", "O6") == 12.34, "locked write changed the first receipt")
    check(grid_amount(book, "Oct", "K29") in (None, ""), grid_amount(book, "Oct", "K29"))
    check(queue.items[-1]["status"] == "retry", queue.items)
    check(len(queue.items) == 2, "lock created a second queue row")
    lock.unlink()
    released = drain(queue, online, book.name, staging, name_prefix="TEST - ", stamp="20261024-160100")
    check(released["wrote"] == ["Shell|2026-10-04|40.00"], released)
    check(grid_amount(book, "Oct", "O6") == 12.34, "retry duplicated Costco")
    # Day 4 amount column is Q (17). Fuel is row 29.
    check(grid_amount(book, "Oct", "Q29") == 40.00, grid_amount(book, "Oct", "Q29"))
    released_again = drain(queue, online, book.name, staging, name_prefix="TEST - ", stamp="20261024-160200")
    check(released_again["wrote"] == [], released_again)
    check(grid_amount(book, "Oct", "Q29") == 40.00, "retry wrote fuel twice")


def test_batch_is_two_approvals(tmp: Path) -> None:
    computer_root = tmp / "computer"
    book = new_book(computer_root)
    queue = ReceiptQueue(tmp / "TEST - batch-queue.json")
    for index in range(3):
        queue.enqueue(receipt(total=5 + index, body=f"Costco\nTotal {5 + index:.2f}\n"))
    computer = LocalComputer(computer_root, online=True)
    result = drain(queue, computer, book.name, tmp / "staging", name_prefix="TEST - ", stamp="20261024-170000")
    check(len(result["wrote"]) == 3, result)
    check(computer.approvals == 2, computer.approvals)
    wb = load_workbook(book)
    amounts = [wb["Oct"].cell(6 + index, 15).value for index in range(3)]
    check(amounts == [5, 6, 7], amounts)


def test_settings_migration_keeps_amounts(tmp: Path) -> None:
    folder = tmp / "old"
    folder.mkdir(parents=True)
    book = new_book(folder)
    wb = load_workbook(book)
    wb["Oct"]["O6"] = 12.34
    wb["Oct"]["C19"] = 80
    wb["Annual Summary"]["C46"] = "v2.0"
    wb["Annual Summary"]["C47"] = None
    wb["Annual Summary"]["B47"] = None
    wb["Annual Summary"]["C48"] = None
    wb["Annual Summary"]["B2"] = "Family Book v2.0 by SkybatanX\nKeep this line."
    wb.save(book)
    before = snapshot_numbers(book)
    result = migrate_v21_settings(book)
    check(result["changed"] is True, result)
    after = snapshot_numbers(book)
    check(before == after, "migration changed a number or a formula")
    wb = load_workbook(book)
    check(wb["Annual Summary"]["C46"].value == "v2.1", wb["Annual Summary"]["C46"].value)
    check(wb["Annual Summary"]["C47"].value == "off", wb["Annual Summary"]["C47"].value)
    check(wb["Annual Summary"]["C48"].value == "not yet", wb["Annual Summary"]["C48"].value)
    check(str(wb["Annual Summary"]["B2"].value).startswith("Family Book v2.1"), wb["Annual Summary"]["B2"].value)
    check("Keep this line." in str(wb["Annual Summary"]["B2"].value), "banner body was dropped")
    again = migrate_v21_settings(book)
    check(again["changed"] is False, again)
    check(snapshot_numbers(book) == before, "rerun changed a number")

    wb = load_workbook(book)
    wb["Annual Summary"]["C46"] = "v2.0"
    wb["Annual Summary"]["C47"] = None
    wb["Annual Summary"]["C48"] = "declined"
    wb["Jan"]["B49"] = "CIBC Visa-1001"
    wb["Jan"]["G49"] = 10
    wb.save(book)
    kept = snapshot_numbers(book)
    migrate_v21_settings(book)
    check(snapshot_numbers(book) == kept, "statement book migration changed an amount")
    wb = load_workbook(book)
    check(wb["Annual Summary"]["C47"].value == "on", "a book that already has a statement stays on")
    check(wb["Annual Summary"]["C48"].value == "declined", "a no must survive migration")
    check(wb["Jan"]["G49"].value == 10, wb["Jan"]["G49"].value)


def test_first_statement_turns_features_on(tmp: Path) -> None:
    book = new_book(tmp)
    apply_receipts(book, [receipt()], tmp / "receipts", tmp / "backups", name_prefix="TEST - ", stamp="20261024-180000")
    before = snapshot_numbers(book)
    check(routine_gate(book)["may_remind"] is False, "quiet before any statement")
    mark_statement_added(book)
    check(snapshot_numbers(book) == before, "enabling statements changed an amount")
    gate = routine_gate(book)
    check(gate["features"] == "on" and gate["may_remind"] and gate["may_nudge"] and gate["may_bank_income"], gate)
    check(grid_amount(book, "Oct", "O6") == 12.34, "receipt amount moved")


def test_v2_statement_flow_still_posts_once() -> None:
    text = (ROOT / "tests" / "v2.0" / "fixtures" / "mid-month.csv").read_text(encoding="utf-8")
    book = V2.Book()
    statement = V2.parse_statement(text, "csv")
    book.import_statement(statement, "mid-month.csv")
    book.import_statement(statement, "mid-month.csv")
    check(book.cell("Aug", "BM29") == 71.04, book.grid)
    check(len(book.txns) == 1, book.txns)


def test_template_version() -> None:
    wb = load_workbook(ROOT / "template" / "family-book-template.xlsx")
    summary = wb["Annual Summary"]
    check(summary["C46"].value == "v2.1", summary["C46"].value)
    check(summary["B47"].value == "Statement features", summary["B47"].value)
    check(summary["C47"].value == "off", summary["C47"].value)
    check(summary["C48"].value == "not yet", summary["C48"].value)
    check("v2.1" in str(summary["B2"].value), summary["B2"].value)
    check("Excel does not have to be installed" in str(summary["B2"].value), summary["B2"].value)


def main() -> None:
    test_keys_match_cloud()
    test_v2_statement_flow_still_posts_once()
    with tempfile.TemporaryDirectory(prefix="TEST - family-book-") as directory:
        root = Path(directory)
        test_receipts_only_and_no_excel(root / "plain")
        test_split_fills_grid(root / "split")
        test_suggestion_remembers_no(root / "suggest")
        test_queue_offline_lock_backup(root / "queue")
        test_batch_is_two_approvals(root / "batch")
        test_settings_migration_keeps_amounts(root / "migrate")
        test_first_statement_turns_features_on(root / "enable")
    test_template_version()
    # Reuse the v2.0 checker without regenerating its fixtures.
    import importlib.util
    path = ROOT / "tests" / "v2.0" / "generate_and_check.py"
    spec = importlib.util.spec_from_file_location("generate_and_check", path)
    checker = importlib.util.module_from_spec(spec)
    sys.modules["generate_and_check"] = checker
    spec.loader.exec_module(checker)
    checker.test_parsers()
    checker.test_book()
    checker.test_round1()
    checker.test_migration_and_crash()
    checker.test_template()
    print("v2.1 offline checks passed")


if __name__ == "__main__":
    try:
        main()
    except Fail as exc:
        print("FAIL:", exc)
        sys.exit(1)
