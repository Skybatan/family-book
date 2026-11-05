#!/usr/bin/env python3
"""Offline checks for Family Book v2.2 reconnect and migration.

These use a temporary folder and synthetic names. They do not call Excel,
do not read a real Family Book, and do not talk to a bot.

    python3 tests/v2.2/check_v22.py

Excel is not required. openpyxl is.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from openpyxl import Workbook, load_workbook  # noqa: E402

from bot.local.bookio import (  # noqa: E402
    BOT_STATE_SHEET,
    choose_book_sets,
    detect_version,
    group_book_sets,
    guarded_write,
    init_local_book,
    is_real_book,
    memory_from_book,
    message_already_logged,
    migrate_book,
    missing_routines,
    name_is_skipped,
    path_is_skipped,
    read_bot_state,
    scan_not_before,
    snapshot_amount_block,
    write_inbox_scan,
)

TEMPLATE = ROOT / "template" / "family-book-template.xlsx"


def check(condition, detail) -> None:
    if not condition:
        raise SystemExit(f"FAIL {detail}")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_book(folder: Path) -> Path:
    return init_local_book(TEMPLATE, folder, 2026, "Family Book - 2026.xlsx")


def test_template_has_bot_state() -> None:
    wb = load_workbook(TEMPLATE)
    check(wb["Annual Summary"]["C46"].value == "v2.2", wb["Annual Summary"]["C46"].value)
    check("v2.2" in str(wb["Annual Summary"]["B2"].value), "banner")
    check(BOT_STATE_SHEET in wb.sheetnames, wb.sheetnames)
    state = wb[BOT_STATE_SHEET]
    check(state.sheet_state == "hidden", state.sheet_state)
    check(str(state["A1"].value).startswith("Managed by Family Book bot"), state["A1"].value)
    check(state["A4"].value == "Book version" and state["B4"].value == "v2.2", (state["A4"].value, state["B4"].value))
    check(state["A30"].value == "Inbox" and state["B30"].value == "Last scan", "inbox header")
    check(is_real_book(wb) is False, "a blank F5 is not a year book")
    wb["Annual Summary"]["F5"] = 2026
    check(is_real_book(wb), "B46 and F5")


def test_lookalike_is_not_a_book() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Annual Summary"
    ws["F5"] = 2026
    ws["B46"] = "Notes"
    ws["B2"] = "Household budget"
    check(is_real_book(wb) is False, "a year cell alone is not a Family Book")
    ws["B2"] = "Family Book v1.0 by SkybatanX"
    wb.create_sheet("Jan")
    check(is_real_book(wb), "a v1.0 banner still counts")
    check(name_is_skipped("TEST - Family Book - 2026"), "tester prefix")
    check(name_is_skipped("Copy of Family Book - 2026.xlsx"), "drive copy")
    check(name_is_skipped("Family Book - 2026") is False, "real name")
    check(path_is_skipped("Family Book/Family Book - Backups/Family Book - 2026.xlsx"), "backup folder")
    check(path_is_skipped("Family Book/TEST - Family Book - 2026/book.xlsx"), "tester folder")


def test_one_set_reconnects_and_lookalikes_do_not() -> None:
    records = [
        {"name": "Family Book - 2026", "path": "Family Book/Family Book - 2026/Family Book - 2026",
         "storage": "google", "owned": True, "trashed": False, "container": "root-1", "year": 2026, "real": True},
        {"name": "TEST - Family Book - 2026", "path": "Family Book/TEST - Family Book - 2026/TEST - Family Book - 2026",
         "storage": "google", "owned": True, "trashed": False, "container": "root-1", "year": 2026, "real": True},
        {"name": "Copy of Family Book - 2026", "path": "Family Book/Copy of Family Book - 2026",
         "storage": "google", "owned": True, "trashed": False, "container": "root-1", "year": 2026, "real": True},
        {"name": "Family Book - 2026", "path": "Trash/Family Book - 2026",
         "storage": "google", "owned": True, "trashed": True, "container": "root-1", "year": 2026, "real": True},
        {"name": "Budget", "path": "Family Book/Budget",
         "storage": "google", "owned": True, "trashed": False, "container": "root-1", "year": 2026, "real": False},
    ]
    choice = choose_book_sets(group_book_sets(records))
    check(choice["action"] == "reconnect", choice)
    check(choice["role"] == "owner", choice)
    check(choice["book"]["years"] == [2026], choice)
    check(choice["book"]["names"] == ["Family Book - 2026"], choice["book"]["names"])


def test_last_year_only_is_one_set() -> None:
    records = [
        {"name": "Family Book - 2025", "path": "Family Book/Family Book - 2025/Family Book - 2025",
         "storage": "google", "owned": True, "trashed": False, "container": "root-1", "year": 2025, "real": True},
    ]
    choice = choose_book_sets(group_book_sets(records))
    check(choice["action"] == "reconnect" and choice["book"]["years"] == [2025], choice)


def test_two_roots_and_a_shared_book_ask() -> None:
    records = [
        {"name": "Family Book - 2026", "path": "Family Book/Family Book - 2026/Family Book - 2026",
         "storage": "google", "owned": True, "trashed": False, "container": "root-1", "year": 2026, "real": True},
        {"name": "Family Book - 2026", "path": "Other/Family Book - 2026/Family Book - 2026",
         "storage": "google", "owned": True, "trashed": False, "container": "root-2", "year": 2026, "real": True},
    ]
    choice = choose_book_sets(group_book_sets(records))
    check(choice["action"] == "ask" and len(choice["sets"]) == 2, choice)
    shared = [
        {"name": "Family Book - 2026", "path": "shared/Family Book - 2026",
         "storage": "google", "owned": False, "trashed": False, "container": "root-9",
         "owner_id": "owner-alex", "year": 2026, "real": True},
    ]
    joined = choose_book_sets(group_book_sets(shared))
    check(joined["action"] == "reconnect" and joined["role"] == "member", joined)
    check(choose_book_sets(group_book_sets([]))["action"] == "setup", "empty")


def test_blank_marker_uses_structure(tmp: Path) -> None:
    book = new_book(tmp)
    wb = load_workbook(book)
    wb["Annual Summary"]["C46"] = None
    wb["Oct"]["O6"] = 12.34
    if BOT_STATE_SHEET in wb.sheetnames:
        del wb[BOT_STATE_SHEET]
    wb.save(book)
    info = detect_version(load_workbook(book))
    check(info["effective"] == "v2.1", info)
    check(info["steps"] == ["v2.2"], info)
    check("v1.2.3" not in info["steps"] and "v2.0" not in info["steps"], info)
    result = migrate_book(book, tmp / "Family Book - Backups", stamp="20261105-090000")
    check(result["action"] == "migrate" and result["changed"] is True, result)
    wb = load_workbook(book)
    check(wb["Annual Summary"]["C46"].value == "v2.2", wb["Annual Summary"]["C46"].value)
    check(wb["Oct"]["O6"].value == 12.34, wb["Oct"]["O6"].value)
    check(read_bot_state(wb)["present"] is True, "Bot State was not added")

    bare = Workbook()
    summary = bare.active
    summary.title = "Annual Summary"
    summary["F5"] = 2024
    summary["B2"] = "Family Book v1.0"
    bare.create_sheet("Jan")
    info = detect_version(bare)
    check(info["effective"] == "v1.0", info)
    check(info["steps"][0] == "v1.2.3", info)
    check(info["action"] == "skill", info)


def test_v123_is_not_rewritten_here(tmp: Path) -> None:
    book = new_book(tmp / "made")
    wb = load_workbook(book)
    wb["Annual Summary"]["C46"] = "v1.2.3"
    wb["Annual Summary"]["C47"] = None
    wb["Annual Summary"]["B47"] = None
    wb["Log"]["N1"] = None
    wb["Log"]["O1"] = None
    if BOT_STATE_SHEET in wb.sheetnames:
        del wb[BOT_STATE_SHEET]
    for name in wb.sheetnames:
        if name in {"Annual Summary", "Holidays", "Cards", "Log", "Merchant Map", "Statements"}:
            continue
        wb[name]["B47"] = "Receipts this month\nOne row per receipt."
        wb[name]["B48"] = "Date & time"
    wb["Jan"]["K6"] = 12.34
    wb.save(book)
    before = file_hash(book)
    info = detect_version(load_workbook(book))
    check(info["effective"] == "v1.2.3", info)
    check(info["steps"] == ["v2.0", "v2.1", "v2.2"], info)
    result = migrate_book(book, tmp / "Family Book - Backups", stamp="20261105-090100")
    check(result["action"] == "skill" and result["changed"] is False, result)
    check(file_hash(book) == before, "v1.2.3 book was edited by the local chain")
    check(load_workbook(book)["Jan"]["K6"].value == 12.34, "amount moved")


def test_v21_to_v22_backup_and_rerun(tmp: Path) -> None:
    book = new_book(tmp)
    wb = load_workbook(book)
    wb["Annual Summary"]["C46"] = "v2.1"
    wb["Annual Summary"]["B2"] = "Family Book v2.1 by SkybatanX\nKeep this line."
    wb["Oct"]["O6"] = 12.34
    wb["Oct"]["C19"] = 80
    if BOT_STATE_SHEET in wb.sheetnames:
        del wb[BOT_STATE_SHEET]
    wb.save(book)
    before = snapshot_amount_block(load_workbook(book))
    backups = tmp / "Family Book - Backups"
    result = migrate_book(book, backups, {"storage": "local", "holiday_region": "Canada / Ontario"}, stamp="20261105-100000")
    check(result["action"] == "migrate", result)
    wb = load_workbook(book)
    check(wb["Annual Summary"]["C46"].value == "v2.2", wb["Annual Summary"]["C46"].value)
    check(str(wb["Annual Summary"]["B2"].value).startswith("Family Book v2.2"), wb["Annual Summary"]["B2"].value)
    check("Keep this line." in str(wb["Annual Summary"]["B2"].value), "banner body dropped")
    check(wb["Oct"]["O6"].value == 12.34 and wb["Oct"]["C19"].value == 80, "amounts changed")
    check(snapshot_amount_block(wb) == before, "rows 1-44 changed")
    state = read_bot_state(wb)
    check(state["fields"]["book_version"] == "v2.2", state["fields"])
    check(state["fields"]["holiday_region"] == "Canada / Ontario", state["fields"])
    check(wb[BOT_STATE_SHEET].sheet_state == "hidden", "local Bot State stays hidden")
    names = list(backups.iterdir())
    check(len(names) == 1 and "before-v2.2" in names[0].name, names)
    again = migrate_book(book, backups, stamp="20261105-100100")
    check(again["action"] == "noop" and again["changed"] is False, again)
    check(len(list(backups.iterdir())) == 1, "a rerun took another backup")
    check(snapshot_amount_block(load_workbook(book)) == before, "rerun changed an amount")


def test_failed_step_restores(tmp: Path) -> None:
    book = new_book(tmp)
    wb = load_workbook(book)
    wb["Oct"]["O6"] = 12.34
    wb.save(book)
    backups = tmp / "Family Book - Backups"

    def break_amount(workbook):
        workbook["Oct"]["O6"] = 99

    result = guarded_write(book, backups, "v2.2", break_amount, stamp="20261105-110000")
    check(result["ok"] is False and result["restored"] is True, result)
    check(load_workbook(book)["Oct"]["O6"].value == 12.34, "live book kept the bad amount")
    check(load_workbook(book)["Annual Summary"]["C46"].value == "v2.2", "restore replaced the whole file")
    saved = list(backups.iterdir())
    check(len(saved) == 1, saved)
    check(load_workbook(saved[0])["Oct"]["O6"].value == 12.34, "backup should be the pre-step file")


def test_newer_book_is_read_only(tmp: Path) -> None:
    book = new_book(tmp)
    wb = load_workbook(book)
    wb["Annual Summary"]["C46"] = "v2.3"
    wb["Oct"]["O6"] = 12.34
    wb.save(book)
    before = file_hash(book)
    result = migrate_book(book, tmp / "Family Book - Backups", stamp="20261105-120000")
    check(result["action"] == "read-only" and result["changed"] is False, result)
    check(result["effective"] == "v2.3", result)
    check(file_hash(book) == before, "a newer book was written")
    check(not (tmp / "Family Book - Backups").exists(), "read-only still took a backup")


def test_scan_window_and_message_backstop(tmp: Path) -> None:
    book = new_book(tmp)
    inbox = "gmail/family@example.com"
    other = "outlook/alex@example.com"
    wb = load_workbook(book)
    state = wb[BOT_STATE_SHEET]
    state["A31"] = inbox
    state["B31"] = "2026-11-03T20:00:00Z"
    state["C31"] = inbox
    state["A32"] = other
    state["B32"] = "2026-10-01T20:00:00Z"
    state["C32"] = other
    wb["Log"]["A2"] = f"email {inbox} 18c3fab"
    wb["Log"]["B2"] = "2026-10-20"
    wb["Log"]["C2"] = "Costco"
    wb.save(book)
    window = scan_not_before(load_workbook(book), inbox, today=date(2026, 11, 5))
    check(window["source"] == "watermark", window)
    check(window["not_before"] == datetime(2026, 11, 1, 20, 0, 0), window["not_before"])
    check(message_already_logged(load_workbook(book), inbox, "18c3fab"), "known message")
    check(message_already_logged(load_workbook(book), inbox, "ffff") is False, "new message")

    wb = load_workbook(book)
    wb[BOT_STATE_SHEET]["B31"] = None
    wb.save(book)
    from_log = scan_not_before(load_workbook(book), inbox, today=date(2026, 11, 5))
    check(from_log["source"] == "log", from_log)
    check(from_log["not_before"] == datetime(2026, 10, 13, 0, 0, 0), from_log["not_before"])

    wb = load_workbook(book)
    wb["Log"]["A2"] = None
    wb["Log"]["B2"] = None
    wb["Log"]["C2"] = None
    wb["Annual Summary"]["C52"] = "2026-01-15"
    wb.save(book)
    from_start = scan_not_before(load_workbook(book), inbox, today=date(2026, 11, 5))
    check(from_start["source"] == "book-started", from_start)
    check(from_start["not_before"] == datetime(2026, 1, 15, 0, 0, 0), from_start["not_before"])

    wb = load_workbook(book)
    wb["Annual Summary"]["C52"] = None
    wb.save(book)
    fresh = scan_not_before(load_workbook(book), inbox, today=date(2026, 11, 5))
    check(fresh["source"] == "new-book", fresh)
    check(fresh["not_before"] == datetime(2026, 10, 6, 0, 0, 0), fresh["not_before"])


def test_member_writes_only_its_inbox(tmp: Path) -> None:
    book = new_book(tmp)
    owner = "gmail/family@example.com"
    member = "outlook/alex@example.com"
    wb = load_workbook(book)
    state = wb[BOT_STATE_SHEET]
    state["B5"] = "google"
    state["A31"] = owner
    state["B31"] = "2026-11-01T20:00:00Z"
    state["C31"] = owner
    state["A18"] = "Alex"
    state["B18"] = "member"
    wb.save(book)
    try:
        write_inbox_scan(book, owner, datetime(2026, 11, 5, 20, 0, 0), [member])
    except PermissionError:
        pass
    else:
        raise SystemExit("FAIL member wrote the owner's inbox")
    wb = load_workbook(book)
    check(wb[BOT_STATE_SHEET]["B31"].value == "2026-11-01T20:00:00Z", "owner scan time changed")
    check(wb[BOT_STATE_SHEET]["B5"].value == "google", "storage changed")
    write_inbox_scan(book, member, datetime(2026, 11, 5, 20, 0, 0), [member])
    wb = load_workbook(book)
    check(wb[BOT_STATE_SHEET]["A32"].value == member, "member inbox was not appended")
    check(wb[BOT_STATE_SHEET]["B32"].value == "2026-11-05T20:00:00Z", wb[BOT_STATE_SHEET]["B32"].value)
    check(wb[BOT_STATE_SHEET]["B31"].value == "2026-11-01T20:00:00Z", "owner row changed")
    check(wb[BOT_STATE_SHEET]["B5"].value == "google", "member rewrote storage")
    check(wb[BOT_STATE_SHEET]["A18"].value == "Alex", "member row changed")
    remembered = memory_from_book(wb)
    check(remembered["storage"] == "google", remembered)
    check(remembered["inboxes"][member] == "2026-11-05T20:00:00Z", remembered["inboxes"])
    check(remembered["members"][0]["name"] == "Alex", remembered["members"])


def test_routines_are_created_once() -> None:
    missing = missing_routines([], role="owner", features_on=False, inbox_ready=True)
    check(missing == ["Daily receipt scan", "Spending report", "New year's book"], missing)
    again = missing_routines(missing, role="owner", features_on=False, inbox_ready=True)
    check(again == [], again)
    member = missing_routines([], role="member", features_on=True, inbox_ready=False)
    check(member == ["Spending report", "Card due reminder"], member)
    check("New year's book" not in member and "Statement ready" not in member, member)


def test_v20_chain_keeps_amounts(tmp: Path) -> None:
    book = new_book(tmp)
    wb = load_workbook(book)
    wb["Annual Summary"]["C46"] = "v2.0"
    wb["Annual Summary"]["C47"] = None
    wb["Annual Summary"]["B47"] = None
    wb["Annual Summary"]["C48"] = "declined"
    wb["Annual Summary"]["B2"] = "Family Book v2.0 by SkybatanX\nKeep this line."
    wb["Oct"]["O6"] = 12.34
    if BOT_STATE_SHEET in wb.sheetnames:
        del wb[BOT_STATE_SHEET]
    wb.save(book)
    before = snapshot_amount_block(load_workbook(book))
    result = migrate_book(book, tmp / "Family Book - Backups", stamp="20261105-130000")
    check(result["changed"] is True, result)
    wb = load_workbook(book)
    check(wb["Annual Summary"]["C46"].value == "v2.2", wb["Annual Summary"]["C46"].value)
    check(wb["Annual Summary"]["C47"].value == "off", wb["Annual Summary"]["C47"].value)
    check(wb["Annual Summary"]["C48"].value == "declined", "a no was forgotten")
    check(wb["Oct"]["O6"].value == 12.34, "v2.0 chain changed an amount")
    check(snapshot_amount_block(wb) == before, "rows 1-44 changed on the v2.0 chain")
    names = sorted(path.name for path in (tmp / "Family Book - Backups").iterdir())
    check(names == [
        "Family Book - 2026 - before-v2.1 - 20261105-130000.xlsx",
        "Family Book - 2026 - before-v2.2 - 20261105-130000.xlsx",
    ], names)


def main() -> None:
    test_template_has_bot_state()
    test_lookalike_is_not_a_book()
    test_one_set_reconnects_and_lookalikes_do_not()
    test_last_year_only_is_one_set()
    test_two_roots_and_a_shared_book_ask()
    test_routines_are_created_once()
    with tempfile.TemporaryDirectory(prefix="TEST - family-book-v22-") as directory:
        root = Path(directory)
        test_blank_marker_uses_structure(root / "blank")
        test_v123_is_not_rewritten_here(root / "v123")
        test_v21_to_v22_backup_and_rerun(root / "v22")
        test_failed_step_restores(root / "restore")
        test_newer_book_is_read_only(root / "newer")
        test_scan_window_and_message_backstop(root / "scan")
        test_member_writes_only_its_inbox(root / "member")
        test_v20_chain_keeps_amounts(root / "chain")
    print("v2.2 offline checks passed")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"FAIL {error}") from error
