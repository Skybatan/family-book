#!/usr/bin/env python3
"""Read and write a Family Book .xlsx without Microsoft Excel.

The bot runs this on its own computer after copying the workbook off the
user's computer. Nothing here starts the Excel application. A locked file
is left untouched. A receipt key that is already in the book is not written
again. A backup is taken before a workbook is replaced.

Receipt key, categories, and the month-sheet layout match the cloud books.
"""

from __future__ import annotations

import hashlib
import re
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Daily Record rows. These match the family-book skill and the template.
CATEGORIES = {
    "Meals": (6, 16),
    "Snacks & Groceries": (17, 19),
    "Dining Out": (20, 20),
    "Household Goods": (22, 27),
    "Education & Enrichment": (28, 28),
    "Fuel": (29, 29),
    "Clothing": (30, 31),
    "Medical": (32, 32),
    "Hair & Cosmetics": (33, 33),
    "Transportation": (34, 34),
    "Entertainment": (35, 35),
    "Gifts & Social": (36, 36),
    "Other": (37, 40),
    "Temporary Income": (43, 43),
}

OFFER_VALUES = ("not yet", "asked", "declined", "accepted")
FEATURE_VALUES = ("off", "on")

SUGGESTION_TEXT = (
    "You've been logging receipts for a while. If you want, you can also add a "
    "card or bank statement. That catches purchases you didn't photograph, "
    "reminds you before a card is due, and can fill in income and fixed bills. "
    "The original file stays in your own drive. Nothing is uploaded to GitHub. "
    "Say yes and send a statement, or say no and I won't ask again."
)

BANNER_V21 = (
    "Family Book v2.1 by SkybatanX: a yearly family income & expense book run by your personal Grok Bot.\n"
    "The bot logs spending from receipts. Card and bank statements are optional, and the book works with none.\n"
    "Each month keeps the number grid, then a Transactions section and a Receipts section. The same purchase is never added twice.\n"
    "The book can live in Google Sheets, Excel Online, or an Excel file on your computer. Excel does not have to be installed.\n"
    "Follow @SkyXFunNext on X for more templates and fun!"
)


def short_store(name: str) -> str:
    """Short merchant name used in the Store column, the file name, and the receipt key."""
    text = (name or "").strip()
    folded = text.lower().replace("&", " and ")
    folded = re.sub(r"#\s*\d+", " ", folded)
    folded = re.sub(r"\b(no\.?|store)\s*\d+\b", " ", folded)
    folded = re.sub(r"\.(com|ca|co\.uk|net|org)\b", " ", folded)
    folded = re.sub(r"\b(wholesale|online|the)\b", " ", folded)
    folded = re.sub(r"[^a-z0-9\s]", " ", folded)
    folded = re.sub(r"\s+", " ", folded).strip()
    brands = (
        ("costco", "Costco"),
        ("home depot", "Home Depot"),
        ("shell", "Shell"),
        ("walmart", "Walmart"),
        ("canadian tire", "Canadian Tire"),
        ("sport chek", "Sport Chek"),
        ("tim hortons", "Tim Hortons"),
        ("t and t", "T&T"),
    )
    for needle, pretty in brands:
        if needle in folded:
            return pretty
    if not folded:
        return "Receipt"
    return " ".join(part.capitalize() for part in folded.split()[:3])


def normalize_number(number: str) -> str:
    text = (number or "").strip()
    if text.startswith("#"):
        text = text[1:].strip()
    return text.casefold()


def receipt_key(store: str, number: str, when, total) -> str:
    """Same key as the cloud books.

    A receipt number at that store is the key. With no number, the key is the
    short store name, the transaction date, and the total to the cent.
    """
    merchant = short_store(store)
    normalized = normalize_number(number)
    if normalized:
        return f"{merchant}|{normalized}"
    day = _as_date(when)
    day_text = day.isoformat() if day else ""
    return f"{merchant}|{day_text}|{float(total):.2f}"


def _as_date(when) -> date | None:
    if when is None or when == "":
        return None
    if isinstance(when, datetime):
        return when.date()
    if isinstance(when, date):
        return when
    text = str(when).strip()
    if not text:
        return None
    return date.fromisoformat(text[:10])


def _as_hhmm(when) -> str:
    if isinstance(when, datetime):
        return when.strftime("%H%M")
    text = str(when or "")
    match = re.search(r"(\d{2}):(\d{2})", text)
    if match:
        return match.group(1) + match.group(2)
    match = re.search(r"\b(\d{4})\b", text[10:])
    if match:
        return match.group(1)
    return ""


def file_name(when, store: str, total: float, ext: str, prefix: str = "") -> str:
    """YYYY-MM-DD HHMM - Store - TOTAL.ext, with an optional test prefix."""
    day = _as_date(when)
    day_text = day.isoformat() if day else "0000-00-00"
    hhmm = _as_hhmm(when)
    stamp = f"{day_text} {hhmm}" if hhmm else day_text
    suffix = ext if ext.startswith(".") else f".{ext}"
    total_text = f"{float(total):.2f}"
    base = f"{stamp} - {short_store(store)} - {total_text}{suffix}"
    safe = re.sub(r'[\\/:*?"<>|]', "", base)
    return f"{prefix}{safe}" if prefix else safe


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_locked(path: Path) -> bool:
    """True when another app has the workbook open, or a tester lock marker is present.

    Excel's owner file is ``~$<name>``. A ``.lock`` file beside the workbook is
    the stand-in a tester uses when Excel is not installed. A lock means the
    caller must not replace the file.
    """
    path = Path(path)
    if not path.exists():
        return False
    if path.with_name("~$" + path.name).exists():
        return True
    if Path(str(path) + ".lock").exists():
        return True
    try:
        import fcntl
        import os
        fd = os.open(path, os.O_RDWR)
    except OSError:
        return True
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    finally:
        os.close(fd)


def backup_workbook(path: Path, backups_dir: Path, stamp: str | None = None) -> Path:
    """Copy the workbook into backups before it is replaced. Never overwrite a backup."""
    path = Path(path)
    backups_dir = Path(backups_dir)
    backups_dir.mkdir(parents=True, exist_ok=True)
    when = stamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = backups_dir / f"{path.stem} - {when}{path.suffix}"
    number = 2
    while dest.exists():
        dest = backups_dir / f"{path.stem} - {when} - {number}{path.suffix}"
        number += 1
    shutil.copy2(path, dest)
    if dest.stat().st_size <= 0:
        raise RuntimeError(f"backup is empty: {dest}")
    return dest


def _atomic_save(wb, path: Path) -> None:
    partial = Path(str(path) + ".partial")
    wb.save(partial)
    partial.replace(path)


def init_local_book(template: Path, folder: Path, year: int, workbook_name: str) -> Path:
    """Create a year folder, a receipts folder, and a year workbook. Excel is not used."""
    folder = Path(folder)
    receipts = folder / "receipts"
    backups = folder / "backups"
    receipts.mkdir(parents=True, exist_ok=True)
    backups.mkdir(parents=True, exist_ok=True)
    dest = folder / workbook_name
    if dest.exists():
        return dest
    shutil.copy2(template, dest)
    wb = load_workbook(dest)
    summary = wb["Annual Summary"]
    summary["F5"] = int(year)
    if summary["C46"].value in (None, ""):
        summary["C46"] = "v2.1"
    if summary["C47"].value not in FEATURE_VALUES:
        summary["B47"] = "Statement features"
        summary["C47"] = "off"
    if summary["C48"].value not in OFFER_VALUES:
        summary["B48"] = "Statement offer"
        summary["C48"] = "not yet"
    summary["B49"] = "Last weekly report"
    summary["B50"] = "Last monthly report"
    summary["B51"] = "Last yearly report"
    _atomic_save(wb, dest)
    return dest


def _summary(wb):
    return wb["Annual Summary"]


def read_settings(wb) -> dict:
    summary = _summary(wb)
    features = summary["C47"].value if summary["C47"].value in FEATURE_VALUES else "off"
    offer = summary["C48"].value if summary["C48"].value in OFFER_VALUES else "not yet"
    return {
        "version": summary["C46"].value or "",
        "features": features,
        "offer": offer,
        "weekly": summary["C49"].value or "",
        "monthly": summary["C50"].value or "",
        "yearly": summary["C51"].value or "",
    }


def _sheet_for(when) -> tuple[str, date, int]:
    day = _as_date(when)
    if day is None:
        raise ValueError("receipt has no transaction date")
    return MONTHS[day.month - 1], day, day.day


def _day_columns(day_number: int) -> tuple[int, int]:
    item = 10 + 2 * (day_number - 1)
    return item, item + 1


def _items_of(receipt: dict) -> list[dict]:
    items = receipt.get("items") or []
    if items:
        return items
    category = receipt.get("category") or "Meals"
    if category not in CATEGORIES:
        raise ValueError(f"unknown category: {category}")
    return [{"name": short_store(receipt.get("store", "")), "price": float(receipt["total"]), "category": category}]


def _check_split(receipt: dict) -> list[dict]:
    items = _items_of(receipt)
    for item in items:
        if item.get("category") not in CATEGORIES:
            raise ValueError(f"unknown category: {item.get('category')}")
    total = round(sum(float(item["price"]) for item in items), 2)
    if abs(total - round(float(receipt["total"]), 2)) > 0.001:
        raise ValueError("item prices do not add up to the receipt total")
    return items


def _iter_receipt_rows(wb):
    for name in MONTHS:
        ws = wb[name]
        for row in range(152, 302):
            store = ws.cell(row, 3).value
            key = ws.cell(row, 79).value
            if store or key:
                yield ws, row


def _next_receipt_row(wb, sheet: str) -> int:
    ws = wb[sheet]
    for row in range(152, 302):
        if not ws.cell(row, 3).value and not ws.cell(row, 79).value:
            return row
    raise RuntimeError(f"no empty receipt row on {sheet}")


def _next_log_row(wb) -> int:
    log = wb["Log"]
    for row in range(2, 5000):
        if not log.cell(row, 3).value and not log.cell(row, 14).value:
            return row
    raise RuntimeError("no empty log row")


def _first_empty(ws, day_number: int, category: str, reserved: set[tuple]) -> tuple[int, int]:
    start, end = CATEGORIES[category]
    _item_col, amount_col = _day_columns(day_number)
    for row in range(start, end + 1):
        if (ws.title, row, amount_col) in reserved:
            continue
        value = ws.cell(row, amount_col).value
        if value is None or value == "":
            return row, amount_col
    raise RuntimeError(f"no empty {category} cell on day {day_number}")


def _amount_cells(ws, day_number: int, items: list[dict], reserved: set[tuple] | None = None) -> list[tuple[str, int, int, float]]:
    """Pick the first empty amount cell in each category. Do not write yet."""
    reserved = reserved if reserved is not None else set()
    grouped: dict[str, float] = {}
    for item in items:
        grouped[item["category"]] = round(grouped.get(item["category"], 0) + float(item["price"]), 2)
    chosen = []
    for category, amount in grouped.items():
        row, col = _first_empty(ws, day_number, category, reserved)
        reserved.add((ws.title, row, col))
        chosen.append((category, row, col, amount))
    return chosen


def _where_text(sheet: str, cells: list[tuple[str, int, int, float]]) -> str:
    parts = []
    for _category, row, col, _amount in cells:
        parts.append(f"{sheet}!{get_column_letter(col)}{row}")
    return "+".join(parts)


def _grid_snapshot(wb) -> dict:
    """Numbers and formulas in the grid. Migration and a skipped receipt must leave these alone."""
    found = {}
    for name in MONTHS:
        ws = wb[name]
        for row in list(range(8, 12)) + list(range(18, 40)) + list(range(6, 44)):
            for col in range(1, 72):
                value = ws.cell(row, col).value
                if isinstance(value, (int, float)) or (isinstance(value, str) and value.startswith("=")):
                    found[(name, row, col)] = value
    return found


def _body_bytes(receipt: dict) -> bytes:
    body = receipt.get("body", b"")
    if isinstance(body, str):
        body = body.encode("utf-8")
    return body or b""


def _place_file(receipts_dir: Path, name: str, data: bytes) -> str:
    receipts_dir.mkdir(parents=True, exist_ok=True)
    digest = sha256_bytes(data) if data else ""
    candidate = receipts_dir / name
    if candidate.exists() and digest and sha256_bytes(candidate.read_bytes()) == digest:
        return candidate.name
    if candidate.exists():
        stem = candidate.stem
        suffix = candidate.suffix
        number = 2
        while candidate.exists():
            candidate = receipts_dir / f"{stem} - {number}{suffix}"
            number += 1
    if data:
        candidate.write_bytes(data)
    return candidate.name


def _find_log_row(wb, key: str):
    log = wb["Log"]
    for row in range(2, max(log.max_row, 2) + 1):
        merchant = log.cell(row, 3).value
        if not merchant:
            continue
        built = receipt_key(
            str(merchant),
            str(log.cell(row, 9).value or ""),
            log.cell(row, 2).value,
            log.cell(row, 4).value or 0,
        )
        if built == key:
            return row
    return None


def _find_receipt_row(wb, key: str):
    for ws, row in _iter_receipt_rows(wb):
        if ws.cell(row, 79).value == key:
            return ws, row
    return None, None


def apply_receipts(workbook_path, receipts: list[dict], receipts_dir, backups_dir, name_prefix: str = "", stamp: str | None = None) -> dict:
    """Write receipts into a local workbook.

    A finished receipt key does not get a second amount. A Log row still
    marked ``pending`` is resumed: the amount cell is written only when it is
    empty. The workbook is not replaced when it is locked. A backup is taken
    before the file is replaced, and only when this call will change it.
    """
    workbook_path = Path(workbook_path)
    receipts_dir = Path(receipts_dir)
    backups_dir = Path(backups_dir)
    if is_locked(workbook_path):
        return {"locked": True, "wrote": [], "skipped": [], "resumed": [], "backup": ""}
    wb = load_workbook(workbook_path)
    before = _grid_snapshot(wb)
    wrote: list[str] = []
    skipped: list[str] = []
    resumed: list[str] = []
    planned = []
    touched: set[tuple] = set()
    seen: set[str] = set()
    reserved: set[tuple] = set()
    for receipt in receipts:
        items = _check_split(receipt)
        key = receipt_key(receipt.get("store", ""), receipt.get("number", ""), receipt.get("when"), receipt.get("total"))
        if key in seen:
            skipped.append(key)
            continue
        seen.add(key)
        sheet, day, day_number = _sheet_for(receipt.get("when"))
        log_row = _find_log_row(wb, key)
        if log_row is not None:
            status = wb["Log"].cell(log_row, 14).value or ""
            if status != "pending":
                skipped.append(key)
                continue
            where = str(wb["Log"].cell(log_row, 5).value or "")
            _resume_pending(wb, log_row, receipt, items, key, sheet, day, day_number, where, receipts_dir, name_prefix, touched)
            resumed.append(key)
            continue
        cells = _amount_cells(wb[sheet], day_number, items, reserved)
        where = _where_text(sheet, cells)
        for _category, row, col, _amount in cells:
            touched.add((sheet, row, col))
        planned.append((receipt, items, key, sheet, day, day_number, cells, where))

    if not planned and not resumed:
        return {"locked": False, "wrote": [], "skipped": skipped, "resumed": [], "backup": ""}

    backup_path = backup_workbook(workbook_path, backups_dir, stamp=stamp)
    for receipt, items, key, sheet, day, day_number, cells, where in planned:
        _write_new_receipt(wb, receipt, items, key, sheet, day, day_number, cells, where, receipts_dir, name_prefix)
        wrote.append(key)
    after = _grid_snapshot(wb)
    for coord, value in before.items():
        if coord in touched:
            continue
        if after.get(coord) != value:
            raise RuntimeError(f"unrelated cell changed: {coord}")
    _atomic_save(wb, workbook_path)
    return {"locked": False, "wrote": wrote, "skipped": skipped, "resumed": resumed, "backup": str(backup_path)}


def _write_new_receipt(wb, receipt, items, key, sheet, day, day_number, cells, where, receipts_dir, name_prefix) -> None:
    ws = wb[sheet]
    for _category, row, col, amount in cells:
        if ws.cell(row, col).value not in (None, ""):
            raise RuntimeError(f"refusing to overwrite {sheet}!{get_column_letter(col)}{row}")
        label = short_store(receipt.get("store", ""))
        note = receipt.get("note") or ""
        ws.cell(row, col - 1).value = f"{label} {note}".strip() if note else label
        ws.cell(row, col).value = amount
        ws.cell(row, col).number_format = "#,##0.00"
    log_row = _next_log_row(wb)
    receipt_row = _next_receipt_row(wb, sheet)
    _write_log(wb, log_row, receipt, where, day, sheet, receipt_row)
    _write_receipt_row(ws, receipt_row, receipt, items, key, where, day)
    saved_name = _store_body(receipt, receipts_dir, name_prefix)
    if saved_name:
        _mark_file(wb, log_row, ws, receipt_row, saved_name, _body_bytes(receipt), finished=True, cash=_is_cash(receipt))


def _resume_pending(wb, log_row, receipt, items, key, sheet, day, day_number, where, receipts_dir, name_prefix, touched) -> None:
    """Finish a pending row. Write an amount only into a cell that is still empty."""
    ws = wb[sheet]
    if where:
        for part in where.split("+"):
            cell_ref = part.split("!", 1)[-1]
            match = re.fullmatch(r"([A-Z]+)(\d+)", cell_ref)
            if not match:
                continue
            col = 0
            for letter in match.group(1):
                col = col * 26 + (ord(letter) - 64)
            row = int(match.group(2))
            current = ws.cell(row, col).value
            if current in (None, ""):
                ws.cell(row, col).value = round(float(receipt["total"]), 2) if "+" not in where else current
                touched.add((sheet, row, col))
            elif isinstance(current, (int, float)) and abs(float(current) - float(receipt["total"])) > 0.001 and "+" not in where:
                raise RuntimeError("pending cell holds a different amount")
    receipt_ws, receipt_row = _find_receipt_row(wb, key)
    if receipt_ws is None:
        if not where:
            cells = _amount_cells(ws, day_number, items, touched)
            where = _where_text(sheet, cells)
            wb["Log"].cell(log_row, 5).value = where
            for _category, row, col, amount in cells:
                ws.cell(row, col).value = amount
                touched.add((sheet, row, col))
        receipt_row = _next_receipt_row(wb, sheet)
        _write_receipt_row(ws, receipt_row, receipt, items, key, where, day)
        wb["Log"].cell(log_row, 13).value = f"{sheet}!B{receipt_row}"
        receipt_ws = ws
    saved_name = _store_body(receipt, receipts_dir, name_prefix)
    if saved_name:
        _mark_file(wb, log_row, receipt_ws, receipt_row, saved_name, _body_bytes(receipt), finished=True, cash=_is_cash(receipt))


def _is_cash(receipt: dict) -> bool:
    return not str(receipt.get("last4") or "").strip()


def _write_log(wb, row: int, receipt: dict, where: str, day: date, sheet: str, receipt_row: int) -> None:
    log = wb["Log"]
    source = receipt.get("source") or "photo"
    log.cell(row, 1).value = source
    log.cell(row, 2).value = day.isoformat()
    log.cell(row, 3).value = short_store(receipt.get("store", ""))
    log.cell(row, 4).value = round(float(receipt["total"]), 2)
    log.cell(row, 4).number_format = "#,##0.00"
    log.cell(row, 5).value = where
    log.cell(row, 9).value = normalize_number(receipt.get("number", ""))
    hhmm = _as_hhmm(receipt.get("when"))
    log.cell(row, 10).value = f"{day.isoformat()} {hhmm[:2]}:{hhmm[2:]}" if hhmm else day.isoformat()
    items = _items_of(receipt)
    log.cell(row, 11).value = "; ".join(f"{item['name']}: {float(item['price']):.2f}" for item in items)
    log.cell(row, 12).value = str(receipt.get("last4") or "")
    log.cell(row, 13).value = f"{sheet}!B{receipt_row}"
    log.cell(row, 14).value = "pending"
    # Column P stays blank until a statement line exists. The receipt key lives on the Receipts row.


def _write_receipt_row(ws, row: int, receipt: dict, items: list[dict], key: str, where: str, day: date) -> None:
    ws.cell(row, 2).value = normalize_number(receipt.get("number", ""))
    ws.cell(row, 3).value = short_store(receipt.get("store", ""))
    hhmm = _as_hhmm(receipt.get("when"))
    ws.cell(row, 4).value = f"{day.isoformat()} {hhmm[:2]}:{hhmm[2:]}" if hhmm else day.isoformat()
    ws.cell(row, 6).value = round(float(receipt["total"]), 2)
    ws.cell(row, 6).number_format = "#,##0.00"
    ws.cell(row, 7).value = str(receipt.get("last4") or "") or "cash"
    ws.cell(row, 7).number_format = "@"
    for index, item in enumerate(items[:6]):
        start = 9 + index * 3
        ws.cell(row, start).value = item["name"]
        ws.cell(row, start + 1).value = round(float(item["price"]), 2)
        ws.cell(row, start + 1).number_format = "#,##0.00"
        ws.cell(row, start + 2).value = item["category"]
    ws.cell(row, 79).value = key
    ws.cell(row, 82).value = "pending"
    ws.cell(row, 83).value = where


def _store_body(receipt: dict, receipts_dir: Path, name_prefix: str) -> str:
    data = _body_bytes(receipt)
    if not data:
        return ""
    ext = receipt.get("ext") or ".txt"
    name = file_name(receipt.get("when"), receipt.get("store", ""), float(receipt["total"]), ext, prefix=name_prefix)
    return _place_file(receipts_dir, name, data)


def _mark_file(wb, log_row: int, ws, receipt_row: int, saved_name: str, data: bytes, finished: bool, cash: bool) -> None:
    label = "text" if saved_name.endswith(".txt") else "photo"
    pointer = f"1 {label}: {saved_name}"
    digest = sha256_bytes(data) if data else ""
    log = wb["Log"]
    log.cell(log_row, 6).value = pointer
    if digest:
        log.cell(log_row, 15).value = f"1 {digest}"
    if finished:
        log.cell(log_row, 14).value = "cash" if cash else "awaiting statement"
    ws.cell(receipt_row, 27).value = label
    ws.cell(receipt_row, 82).value = "cash" if cash else "pending"


def _has_statement_data(wb) -> bool:
    statements = wb["Statements"] if "Statements" in wb.sheetnames else None
    if statements is not None:
        for row in range(3, statements.max_row + 1):
            if statements.cell(row, 1).value:
                return True
    if "Cards" in wb.sheetnames:
        cards = wb["Cards"]
        for row in range(3, 31):
            if cards.cell(row, 3).value:
                return True
    for name in MONTHS:
        ws = wb[name]
        for row in range(49, 149):
            if ws.cell(row, 2).value or ws.cell(row, 6).value or ws.cell(row, 7).value:
                return True
    return False


def migrate_v21_settings(workbook_path) -> dict:
    """Bring a v2.0 book to v2.1 by filling settings cells only.

    Amounts, formulas, receipt rows, and transaction rows are not edited.
    Safe to run twice. A declined offer stays declined.
    """
    workbook_path = Path(workbook_path)
    if is_locked(workbook_path):
        return {"locked": True, "changed": False}
    wb = load_workbook(workbook_path)
    before = _grid_snapshot(wb)
    summary = _summary(wb)
    version = str(summary["C46"].value or "")
    if version not in {"v2.0", "v2.1"}:
        raise ValueError(f"v2.1 settings step only runs after v2.0 sections exist, not on {version!r}")
    changed = False
    if summary["C47"].value not in FEATURE_VALUES:
        summary["B47"] = "Statement features"
        summary["C47"] = "on" if _has_statement_data(wb) else "off"
        changed = True
    elif summary["B47"].value != "Statement features":
        summary["B47"] = "Statement features"
        changed = True
    if summary["C48"].value not in OFFER_VALUES:
        summary["B48"] = "Statement offer"
        summary["C48"] = "accepted" if summary["C47"].value == "on" else "not yet"
        changed = True
    elif summary["B48"].value != "Statement offer":
        summary["B48"] = "Statement offer"
        changed = True
    for row, label in ((49, "Last weekly report"), (50, "Last monthly report"), (51, "Last yearly report")):
        if summary.cell(row, 2).value != label:
            summary.cell(row, 2).value = label
            changed = True
    banner = str(summary["B2"].value or "")
    if banner.startswith("Family Book v2.0"):
        summary["B2"] = "Family Book v2.1" + banner[len("Family Book v2.0"):]
        changed = True
    if version == "v2.0":
        summary["C46"] = "v2.1"
        changed = True
    after = _grid_snapshot(wb)
    if before != after:
        raise RuntimeError("v2.1 settings changed a number or a formula")
    if changed:
        _atomic_save(wb, workbook_path)
    return {"locked": False, "changed": changed, "version": _summary(load_workbook(workbook_path))["C46"].value if changed else version}


def mark_statement_added(workbook_path) -> dict:
    """The first imported statement turns statement features on. Amounts stay as they are."""
    workbook_path = Path(workbook_path)
    if is_locked(workbook_path):
        return {"locked": True}
    wb = load_workbook(workbook_path)
    before = _grid_snapshot(wb)
    summary = _summary(wb)
    summary["B47"] = "Statement features"
    summary["C47"] = "on"
    summary["B48"] = "Statement offer"
    summary["C48"] = "accepted"
    if before != _grid_snapshot(wb):
        raise RuntimeError("turning statement features on changed a number")
    _atomic_save(wb, workbook_path)
    return {"locked": False, "features": "on"}


def routine_gate(workbook_path) -> dict:
    """What the routines are allowed to do. Off until the first statement."""
    wb = load_workbook(workbook_path)
    settings = read_settings(wb)
    on = settings["features"] == "on"
    return {
        "features": settings["features"],
        "offer": settings["offer"],
        "may_remind": on,
        "may_nudge": on,
        "may_bank_income": on,
        "may_bank_fixed": on,
    }


def receipt_stats(workbook_path) -> dict:
    wb = load_workbook(workbook_path)
    count = 0
    first = None
    for ws, row in _iter_receipt_rows(wb):
        status = ws.cell(row, 82).value or ""
        if status in {"question", "superseded"}:
            continue
        count += 1
        day = _as_date(ws.cell(row, 4).value)
        if day and (first is None or day < first):
            first = day
    return {"count": count, "first": first}


def suggest_statement(features: str, offer: str, count: int, first: date | None, today: date) -> str:
    """One suggestion, or an empty string. A no, a yes, or an earlier ask returns nothing."""
    if features == "on":
        return ""
    if offer != "not yet":
        return ""
    days = (today - first).days if first else 0
    if count >= 10 or days >= 14:
        return SUGGESTION_TEXT
    return ""


def set_offer(workbook_path, offer: str) -> None:
    if offer not in OFFER_VALUES:
        raise ValueError(offer)
    workbook_path = Path(workbook_path)
    if is_locked(workbook_path):
        raise RuntimeError("workbook is locked")
    wb = load_workbook(workbook_path)
    before = _grid_snapshot(wb)
    summary = _summary(wb)
    summary["B48"] = "Statement offer"
    summary["C48"] = offer
    if before != _grid_snapshot(wb):
        raise RuntimeError("offer update changed a number")
    _atomic_save(wb, workbook_path)


def report_totals(workbook_path, start: date, end: date) -> dict:
    """Category sums for a date range, read from amount cells. Excel is not asked to calculate."""
    wb = load_workbook(workbook_path)
    year = _summary(wb)["F5"].value
    if not isinstance(year, int):
        raise ValueError("Annual Summary F5 has no year")
    totals = {name: 0.0 for name in CATEGORIES}
    for month_index, name in enumerate(MONTHS, 1):
        ws = wb[name]
        for day_number in range(1, 32):
            try:
                current = date(year, month_index, day_number)
            except ValueError:
                continue
            if current < start or current > end:
                continue
            _item_col, amount_col = _day_columns(day_number)
            for category, (row_start, row_end) in CATEGORIES.items():
                for row in range(row_start, row_end + 1):
                    value = ws.cell(row, amount_col).value
                    if isinstance(value, (int, float)):
                        totals[category] += float(value)
    return {key: round(value, 2) for key, value in totals.items() if value}


def advice(totals: dict) -> str:
    spent = {key: value for key, value in totals.items() if value}
    if not spent:
        return ""
    top = max(spent, key=spent.get)
    total = round(sum(spent.values()), 2)
    share = spent[top] / total if total else 0
    return f"{top} is the largest category, {spent[top]:.2f} of {total:.2f} ({share:.0%})."


def report_already_sent(workbook_path, kind: str, period: str) -> bool:
    wb = load_workbook(workbook_path)
    settings = read_settings(wb)
    return str(settings.get(kind) or "") == period


def record_report_sent(workbook_path, kind: str, period: str) -> None:
    cell = {"weekly": "C49", "monthly": "C50", "yearly": "C51"}[kind]
    workbook_path = Path(workbook_path)
    if is_locked(workbook_path):
        raise RuntimeError("workbook is locked")
    wb = load_workbook(workbook_path)
    before = _grid_snapshot(wb)
    _summary(wb)[cell] = period
    if before != _grid_snapshot(wb):
        raise RuntimeError("report marker changed a number")
    _atomic_save(wb, workbook_path)


def week_period(today: date) -> tuple[date, date, str]:
    """Monday-to-Sunday week ending on the most recent Sunday, including today.

    The id is that Sunday. A later run with the same id does not send again.
    """
    days_since_sunday = (today.weekday() + 1) % 7
    end = today - timedelta(days=days_since_sunday)
    start = end - timedelta(days=6)
    return start, end, end.isoformat()


def transactions_empty(workbook_path) -> bool:
    wb = load_workbook(workbook_path)
    for name in MONTHS:
        ws = wb[name]
        for row in range(49, 149):
            if any(ws.cell(row, col).value not in (None, "") for col in (2, 3, 4, 6, 7, 9, 10)):
                return False
    return True


def cards_empty(workbook_path) -> bool:
    wb = load_workbook(workbook_path)
    if "Cards" not in wb.sheetnames:
        return True
    cards = wb["Cards"]
    for row in range(3, 31):
        if cards.cell(row, 1).value or cards.cell(row, 3).value:
            return False
    return True
