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
from openpyxl.styles import Alignment
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

# This bot writes v2.2. A higher marker is opened read-only.
BOT_VERSION = "v2.2"
BOT_VERSION_TUPLE = (2, 2)
BOT_STATE_SHEET = "Bot State"
BOT_STATE_NOTE = (
    "Managed by Family Book bot, please don't edit. "
    "This sheet remembers the book so a reinstalled bot can reconnect. "
    "It is not part of your totals."
)
BACKUPS_FOLDER = "Family Book - Backups"

# Fixed rows on Bot State. Column A is the label, column B is the value.
BOT_FIELDS = (
    (4, "Book version", "book_version"),
    (5, "Storage", "storage"),
    (6, "Currency", "currency"),
    (7, "Holiday region", "holiday_region"),
    (8, "Root folder id", "root_folder_id"),
    (9, "Root path", "root_path"),
    (10, "Year folder id", "year_folder_id"),
    (11, "Workbook id", "workbook_id"),
    (12, "Receipts folder id", "receipts_folder_id"),
    (13, "Year", "year"),
    (14, "Statements folder id", "statements_folder_id"),
)
MEMBERS_HEADER_ROW = 17
MEMBERS_FIRST = 18
MEMBERS_LAST = 27
INBOX_HEADER_ROW = 30
INBOX_FIRST = 31
INBOX_LAST = 50

# Completed versions, oldest to newest. A book sits on the last step whose
# sheets are actually present. The next step is the first one after that.
CHAIN = ((1, 2, 3), (2, 0), (2, 1), (2, 2))
STEP_NAME = {(1, 2, 3): "v1.2.3", (2, 0): "v2.0", (2, 1): "v2.1", (2, 2): "v2.2"}
ROUTINE_TITLES = (
    "Daily receipt scan",
    "Spending report",
    "New year's book",
    "Card due reminder",
    "Statement ready",
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
        summary["C46"] = BOT_VERSION
    if summary["C47"].value not in FEATURE_VALUES:
        summary["B47"] = "Statement features"
        summary["C47"] = "off"
    if summary["C48"].value not in OFFER_VALUES:
        summary["B48"] = "Statement offer"
        summary["C48"] = "not yet"
    summary["B49"] = "Last weekly report"
    summary["B50"] = "Last monthly report"
    summary["B51"] = "Last yearly report"
    summary["B52"] = "Book started"
    if not summary["C52"].value:
        summary["C52"] = date.today().isoformat()
    _ensure_bot_state(wb, {
        "book_version": BOT_VERSION,
        "storage": "local",
        "currency": str(summary["C11"].value or ""),
        "year": str(int(year)),
    })
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
        "started": _started_text(summary["C52"].value),
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


def _placed_amount(ws, day_number: int, category: str, amount: float, store: str, reserved: set[tuple]):
    """A cell in this day's category block that already holds this amount and names the store."""
    start, end = CATEGORIES[category]
    item_col, amount_col = _day_columns(day_number)
    needle = short_store(store).casefold()
    for row in range(start, end + 1):
        if (ws.title, row, amount_col) in reserved:
            continue
        value = ws.cell(row, amount_col).value
        text = str(ws.cell(row, item_col).value or "")
        if isinstance(value, (int, float)) and abs(float(value) - amount) < 0.001 and needle in text.casefold():
            return row, amount_col
    return None


def _amount_cells(ws, day_number: int, items: list[dict], reserved: set[tuple] | None = None, store: str = "") -> tuple[list[tuple[str, int, int, float]], bool]:
    """Choose amount cells. Reuse a cell that already holds this amount, otherwise the first empty one.

    The bool is true when at least one cell is still empty and will be written.
    """
    reserved = reserved if reserved is not None else set()
    grouped: dict[str, float] = {}
    for item in items:
        grouped[item["category"]] = round(grouped.get(item["category"], 0) + float(item["price"]), 2)
    chosen = []
    fresh = False
    for category, amount in grouped.items():
        placed = _placed_amount(ws, day_number, category, amount, store, reserved) if store else None
        if placed:
            row, col = placed
        else:
            row, col = _first_empty(ws, day_number, category, reserved)
            fresh = True
        reserved.add((ws.title, row, col))
        chosen.append((category, row, col, amount))
    return chosen, fresh


def _where_text(sheet: str, cells: list[tuple[str, int, int, float]]) -> str:
    parts = []
    for _category, row, col, _amount in cells:
        parts.append(f"{sheet}!{get_column_letter(col)}{row}")
    return "+".join(parts)


def _assert_grid(before: dict, after: dict, touched: set) -> None:
    for coord, value in before.items():
        if coord in touched:
            continue
        if after.get(coord) != value:
            raise RuntimeError(f"unrelated cell changed: {coord}")
    for coord in after:
        if coord in touched or coord in before:
            continue
        raise RuntimeError(f"new amount: {coord}")


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


def merchant_match(left: str, right: str) -> str:
    """Return ``full``, ``partial``, or ``""`` using the same name rules as the cloud book."""

    def norm(value: str) -> str:
        text = (value or "").lower().replace("&", " and ")
        text = re.sub(r"#\s*\d+", " ", text)
        text = text.replace("*", " ")
        text = re.sub(r"\b(no\.?|store)\s*\d+\b", " ", text)
        text = re.sub(r"\.(com|ca|co\.uk|net|org)\b", " ", text)
        text = re.sub(r"\b(wholesale|online)\b", " ", text)
        text = re.sub(r"^\s*the\s+", " ", text)
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    na, nb = norm(left), norm(right)
    if not na or not nb:
        return ""
    if na in nb or nb in na:
        return "full"
    words_a, words_b = na.split(), nb.split()
    shorter, longer = (words_a, words_b) if len(words_a) <= len(words_b) else (words_b, words_a)
    if shorter and all(word in longer for word in shorter):
        return "full"
    if any(len(word) >= 4 and word in words_b and word in words_a for word in words_a):
        return "partial"
    if abs(len(na) - len(nb)) <= 2 and _edits(na, nb) <= 2:
        return "partial"
    return ""


def _edits(left: str, right: str) -> int:
    if abs(len(left) - len(right)) > 2:
        return 99
    prev = list(range(len(right) + 1))
    for i, ca in enumerate(left, 1):
        cur = [i]
        for j, cb in enumerate(right, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _merchant_unclear(store: str) -> bool:
    text = (store or "").strip().casefold()
    return text in {"", "unknown", "store", "merchant", "receipt", "?"}


def _spoken_date(day: date) -> str:
    return f"{MONTHS[day.month - 1]} {day.day}"


def _money(amount) -> str:
    return f"{float(amount):.2f}"


def _log_rows(wb) -> list[dict]:
    log = wb["Log"]
    rows = []
    for row in range(2, max(log.max_row, 2) + 1):
        merchant = log.cell(row, 3).value
        status = log.cell(row, 14).value
        if not merchant and not status:
            continue
        total = log.cell(row, 4).value
        rows.append({
            "row": row,
            "source": str(log.cell(row, 1).value or ""),
            "date": _as_date(log.cell(row, 2).value),
            "merchant": str(merchant or ""),
            "total": float(total) if isinstance(total, (int, float)) else 0.0,
            "where": str(log.cell(row, 5).value or ""),
            "number": str(log.cell(row, 9).value or ""),
            "status": str(status or ""),
            "notes": str(log.cell(row, 8).value or ""),
            "hash": str(log.cell(row, 15).value or ""),
        })
    return rows


def _hash_seen(rows: list[dict], digest: str) -> bool:
    if not digest:
        return False
    return any(digest in row["hash"] for row in rows)


def _question_dates(row: dict) -> list[date]:
    found = []
    for text in (row["notes"], row["source"]):
        for match in re.findall(r"\d{4}-\d{2}-\d{2}", text):
            day = date.fromisoformat(match)
            if day not in found:
                found.append(day)
    if row["date"] and row["date"] not in found:
        found.append(row["date"])
    return found


def _near_limit(left: float, right: float) -> float:
    return max(5.0, 0.15 * max(abs(left), abs(right)))


def _gather_candidates(rows: list[dict], receipt: dict) -> list[dict]:
    """Every Log row that fits rule 1, 2, or 3. Question and superseded rows are not candidates."""
    store = receipt.get("store", "")
    number = normalize_number(receipt.get("number", ""))
    total = round(float(receipt["total"]), 2)
    day = _as_date(receipt.get("when"))
    found = []
    for row in rows:
        if row["status"] in {"superseded", "pending", "question", "refused"}:
            continue
        other_number = normalize_number(row["number"])
        if number and other_number and number != other_number:
            continue
        kind = merchant_match(row["merchant"], store)
        if not row["date"] or not day:
            continue
        gap = abs((row["date"] - day).days)
        same_total = abs(row["total"] - total) < 0.001
        one_blank = not number or not other_number
        rule = 0
        reason = ""
        if number and other_number == number and kind == "full":
            rule, reason = 1, "same receipt number"
        elif kind == "full" and same_total and gap <= 1 and one_blank:
            rule, reason = 2, "one day apart" if gap == 1 else "same day"
        elif kind == "full" and same_total and 1 < gap <= 7:
            rule, reason = 3, f"{gap} days apart"
        elif kind == "full" and gap <= 1 and not same_total:
            diff = abs(row["total"] - total)
            if 0 < diff <= _near_limit(row["total"], total) + 1e-9:
                rule, reason = 3, "close total"
        elif same_total and kind == "" and _merchant_unclear(store):
            rule, reason = 3, "unclear merchant"
        elif same_total and gap == 0 and kind == "partial":
            rule, reason = 3, "partial merchant"
        if rule:
            found.append({**row, "rule": rule, "reason": reason, "gap": gap})
    return found


def _covering_question(rows: list[dict], receipt: dict) -> dict | None:
    store = receipt.get("store", "")
    total = round(float(receipt["total"]), 2)
    day = _as_date(receipt.get("when"))
    if day is None:
        return None
    for row in rows:
        if row["status"] != "question":
            continue
        if merchant_match(row["merchant"], store) != "full":
            continue
        if abs(row["total"] - total) >= 0.001:
            continue
        if any(abs((listed - day).days) <= 7 for listed in _question_dates(row)):
            return row
    return None


def _candidate_label(candidate: dict) -> str:
    store = short_store(str(candidate.get("merchant") or ""))
    total = _money(candidate.get("total") or 0)
    day = candidate.get("date")
    spoken = _spoken_date(day) if day else "that day"
    return f"{store} ${total} on {spoken}"


def _question_text(receipt: dict, candidates: list[dict]) -> str:
    if len(candidates) == 1:
        return f"Same purchase as {_candidate_label(candidates[0])}? Reply no if it's new."
    labels = [_candidate_label(item) for item in candidates]
    if len(labels) == 2:
        listed = f"{labels[0]} or {labels[1]}"
    else:
        listed = ", ".join(labels[:-1]) + f", or {labels[-1]}"
    return f"Which date does it match: {listed}? Reply no if it's new."


def _started_text(value) -> str:
    if value is None or value == "":
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()[:10]
    return str(value)[:10]


_MONTH_WORDS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sept": 9, "sep": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}
_MONTH_PATTERN = "|".join(sorted(_MONTH_WORDS, key=len, reverse=True))
_NEGATIVE_REPLIES = {
    "no",
    "nope",
    "nah",
    "no its new",
    "no it is new",
    "new",
    "different",
}
_AFFIRMATIVE_REPLIES = {
    "yes",
    "y",
    "yes same purchase",
    "yes it matches",
    "same",
    "same purchase",
    "that one",
    "correct",
}


def _reply_phrase(answer: str) -> str:
    """The reply as words, so ``Nov`` and ``note`` are not the word ``no``."""
    text = answer.strip().casefold().replace("’", "'").replace("‘", "'").replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _reply_dates(text: str) -> list[tuple[int, int, date | None]]:
    """Dates named in the reply. A full ISO date keeps its year; a month and day do not."""
    found: list[tuple[int, int, date | None]] = []
    lowered = text.casefold()
    for match in re.finditer(r"\b(\d{4})-(\d{2})-(\d{2})\b", lowered):
        try:
            day = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            continue
        found.append((day.month, day.day, day))
    for match in re.finditer(rf"\b({_MONTH_PATTERN})\.?\s+(\d{{1,2}})\b", lowered):
        day_number = int(match.group(2))
        if 1 <= day_number <= 31:
            found.append((_MONTH_WORDS[match.group(1)], day_number, None))
    for match in re.finditer(rf"\b(\d{{1,2}})\s+({_MONTH_PATTERN})\b", lowered):
        day_number = int(match.group(1))
        if 1 <= day_number <= 31:
            found.append((_MONTH_WORDS[match.group(2)], day_number, None))
    return found


def _parse_reply(answer: str) -> tuple[str, date | tuple[int, int] | None]:
    """Read a raw reply. Dates win, then a whole-reply no, then a whole-reply yes.

    ``Nov 3`` and ``November 3`` are dates. ``nope`` is a no. ``note: same purchase``
    is neither, so the caller asks again and writes nothing.
    """
    seen: dict[tuple[int, int], date | None] = {}
    for month, day_number, full in _reply_dates(answer):
        key = (month, day_number)
        if key not in seen:
            seen[key] = full
            continue
        if full is not None and seen[key] is not None and full != seen[key]:
            raise ValueError(f"ambiguous date: {answer}")
        if seen[key] is None and full is not None:
            seen[key] = full
    if len(seen) > 1:
        raise ValueError(f"ambiguous date: {answer}")
    if len(seen) == 1:
        (month, day_number), full = next(iter(seen.items()))
        if full is not None:
            return "date", full
        return "monthday", (month, day_number)
    phrase = _reply_phrase(answer)
    if phrase in _NEGATIVE_REPLIES:
        return "no", None
    if phrase in _AFFIRMATIVE_REPLIES:
        return "yes", None
    raise ValueError(f"unrecognized answer: {answer}")


def _pick_candidate(candidates: list[dict], kind: str, when) -> dict | None:
    if kind == "yes":
        return candidates[0] if len(candidates) == 1 else None
    if kind == "date":
        hits = [item for item in candidates if item.get("date") == when]
        return hits[0] if len(hits) == 1 else None
    if kind == "monthday":
        month, day_number = when
        hits = [
            item for item in candidates
            if item.get("date") and item["date"].month == month and item["date"].day == day_number
        ]
        return hits[0] if len(hits) == 1 else None
    return None


def _source_label(receipt: dict) -> str:
    source = str(receipt.get("source") or "").strip()
    if source:
        return source
    ext = str(receipt.get("ext") or "")
    if ext == ".txt" or receipt.get("pasted"):
        return "text"
    return "photo"


def _file_label(saved_name: str, receipt: dict) -> str:
    source = _source_label(receipt)
    if source.startswith("email"):
        return "email"
    if source == "statement":
        return "statement"
    if saved_name.endswith(".txt") or source == "text":
        return "text"
    return "photo"


def apply_receipts(workbook_path, receipts: list[dict], receipts_dir, backups_dir, name_prefix: str = "", stamp: str | None = None) -> dict:
    """Write receipts into a local workbook.

    Matching follows the cloud book. Gather every candidate. Auto-attach only
    when there is exactly one rule 1 or rule 2 candidate. A near match asks and
    does not write an amount. A finished receipt key does not get a second
    amount. A Log row still marked ``pending`` is resumed. The workbook is not
    replaced when it is locked. A backup is taken before the file is replaced,
    and only when this call will change it.
    """
    workbook_path = Path(workbook_path)
    receipts_dir = Path(receipts_dir)
    backups_dir = Path(backups_dir)
    empty = {"locked": True, "wrote": [], "skipped": [], "resumed": [], "attached": [], "questions": [], "backup": ""}
    if is_locked(workbook_path):
        return empty
    wb = load_workbook(workbook_path)
    before = _grid_snapshot(wb)
    wrote: list[str] = []
    skipped: list[str] = []
    resumed: list[str] = []
    attached: list[str] = []
    questions: list[dict] = []
    touched: set[tuple] = set()
    seen: set[str] = set()
    reserved: set[tuple] = set()
    changed = False
    for receipt in receipts:
        items = _check_split(receipt)
        key = receipt_key(receipt.get("store", ""), receipt.get("number", ""), receipt.get("when"), receipt.get("total"))
        if key in seen:
            skipped.append(key)
            continue
        seen.add(key)
        outcome = _apply_one(wb, receipt, items, key, receipts_dir, name_prefix, reserved, touched)
        kind = outcome["action"]
        if kind == "skip":
            skipped.append(key)
        elif kind == "resume":
            resumed.append(key)
            changed = True
        elif kind == "attach":
            attached.append(key)
            changed = True
        elif kind == "question":
            questions.append({"key": key, "text": outcome["text"]})
            changed = True
        elif kind == "write":
            wrote.append(key)
            changed = True
        else:
            raise RuntimeError(f"unknown receipt action {kind}")

    if not changed:
        return {"locked": False, "wrote": [], "skipped": skipped, "resumed": [], "attached": [], "questions": [], "backup": ""}

    backup_path = backup_workbook(workbook_path, backups_dir, stamp=stamp)
    after = _grid_snapshot(wb)
    for coord, value in before.items():
        if coord in touched:
            continue
        if after.get(coord) != value:
            raise RuntimeError(f"unrelated cell changed: {coord}")
    _atomic_save(wb, workbook_path)
    return {
        "locked": False,
        "wrote": wrote,
        "skipped": skipped,
        "resumed": resumed,
        "attached": attached,
        "questions": questions,
        "backup": str(backup_path),
    }


def _apply_one(wb, receipt, items, key, receipts_dir, name_prefix, reserved, touched) -> dict:
    rows = _log_rows(wb)
    digest = sha256_bytes(_body_bytes(receipt)) if _body_bytes(receipt) else ""
    if _hash_seen(rows, digest):
        return {"action": "skip"}
    sheet, day, day_number = _sheet_for(receipt.get("when"))
    log_row = _find_log_row(wb, key)
    if log_row is not None:
        status = str(wb["Log"].cell(log_row, 14).value or "")
        if status == "pending":
            where = str(wb["Log"].cell(log_row, 5).value or "")
            _resume_pending(wb, log_row, receipt, items, key, sheet, day, day_number, where, receipts_dir, name_prefix, touched)
            return {"action": "resume"}
        if status == "question":
            text = _join_question(wb, log_row, receipt, receipts_dir, name_prefix)
            return {"action": "question", "text": text}
        if status == "superseded":
            return {"action": "skip"}
        _attach_to_log(wb, log_row, receipt, day, receipts_dir, name_prefix, touched)
        return {"action": "attach"}
    covering = _covering_question(rows, receipt)
    if covering is not None:
        text = _join_question(wb, covering["row"], receipt, receipts_dir, name_prefix)
        return {"action": "question", "text": text}
    candidates = _gather_candidates(_log_rows(wb), receipt)
    if len(candidates) == 1 and candidates[0]["rule"] in {1, 2}:
        _attach_to_log(wb, candidates[0]["row"], receipt, day, receipts_dir, name_prefix, touched)
        return {"action": "attach"}
    if candidates:
        text = _question_text(receipt, candidates)
        _write_question(wb, receipt, items, key, sheet, day, text, candidates, receipts_dir, name_prefix)
        return {"action": "question", "text": text}
    cells, fresh = _amount_cells(wb[sheet], day_number, items, reserved, store=receipt.get("store", ""))
    if not fresh:
        return {"action": "skip"}
    where = _where_text(sheet, cells)
    for _category, row, col, _amount in cells:
        touched.add((sheet, row, col))
    _write_new_receipt(wb, receipt, items, key, sheet, day, cells, where, receipts_dir, name_prefix)
    return {"action": "write"}


def _write_new_receipt(wb, receipt, items, key, sheet, day, cells, where, receipts_dir, name_prefix) -> None:
    ws = wb[sheet]
    label = short_store(receipt.get("store", ""))
    note = receipt.get("note") or ""
    for _category, row, col, amount in cells:
        current = ws.cell(row, col).value
        if isinstance(current, (int, float)) and abs(float(current) - amount) < 0.001:
            continue
        if current not in (None, ""):
            raise RuntimeError(f"refusing to overwrite {sheet}!{get_column_letter(col)}{row}")
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
            cells, _fresh = _amount_cells(ws, day_number, items, touched, store=receipt.get("store", ""))
            where = _where_text(sheet, cells)
            wb["Log"].cell(log_row, 5).value = where
            for _category, row, col, amount in cells:
                current = ws.cell(row, col).value
                if isinstance(current, (int, float)) and abs(float(current) - amount) < 0.001:
                    continue
                if current not in (None, ""):
                    raise RuntimeError(f"refusing to overwrite {sheet}!{get_column_letter(col)}{row}")
                ws.cell(row, col).value = amount
                touched.add((sheet, row, col))
        receipt_row = _next_receipt_row(wb, sheet)
        _write_receipt_row(ws, receipt_row, receipt, items, key, where, day)
        wb["Log"].cell(log_row, 13).value = f"{sheet}!B{receipt_row}"
        receipt_ws = ws
    saved_name = _store_body(receipt, receipts_dir, name_prefix)
    if saved_name:
        _mark_file(wb, log_row, receipt_ws, receipt_row, saved_name, _body_bytes(receipt), finished=True, cash=_is_cash(receipt))


def _attach_to_log(wb, log_row: int, receipt: dict, new_day: date, receipts_dir, name_prefix: str, touched: set) -> None:
    """Add a file to an existing purchase. Do not add the amount. An earlier date keeps the amount."""
    log = wb["Log"]
    old_key = receipt_key(
        str(log.cell(log_row, 3).value or ""),
        str(log.cell(log_row, 9).value or ""),
        log.cell(log_row, 2).value,
        log.cell(log_row, 4).value or 0,
    )
    receipt_ws, receipt_row = _find_receipt_row(wb, old_key)
    old_day = _as_date(log.cell(log_row, 2).value)
    if old_day and new_day < old_day:
        _shift_amount_earlier(wb, log_row, receipt, new_day, touched)
        if receipt_ws is not None:
            hhmm = _as_hhmm(receipt.get("when"))
            receipt_ws.cell(receipt_row, 4).value = f"{new_day.isoformat()} {hhmm[:2]}:{hhmm[2:]}" if hhmm else new_day.isoformat()
            receipt_ws.cell(receipt_row, 79).value = receipt_key(
                str(log.cell(log_row, 3).value or ""),
                str(log.cell(log_row, 9).value or ""),
                new_day,
                log.cell(log_row, 4).value or 0,
            )
    source = _source_label(receipt)
    current = str(log.cell(log_row, 1).value or "")
    parts = [part.strip() for part in current.split(",")] if current else []
    if source and source not in parts:
        log.cell(log_row, 1).value = f"{current}, {source}" if current else source
    number = normalize_number(receipt.get("number", ""))
    if number and not str(log.cell(log_row, 9).value or "").strip():
        log.cell(log_row, 9).value = number
        if receipt_ws is not None and not str(receipt_ws.cell(receipt_row, 2).value or "").strip():
            receipt_ws.cell(receipt_row, 2).value = number
    saved_name = _store_body(receipt, receipts_dir, name_prefix)
    if saved_name:
        _append_file(wb, log_row, receipt_ws if receipt_ws is not None else wb[MONTHS[new_day.month - 1]], receipt_row, saved_name, _body_bytes(receipt), receipt)


def _shift_amount_earlier(wb, log_row: int, receipt: dict, new_day: date, touched: set) -> None:
    """Move the same amount onto the earlier day, on the same category row."""
    log = wb["Log"]
    where = str(log.cell(log_row, 5).value or "")
    if not where or "was =" in where:
        log.cell(log_row, 2).value = new_day.isoformat()
        return
    new_sheet = MONTHS[new_day.month - 1]
    _item_col, new_col = _day_columns(new_day.day)
    parts = []
    for piece in where.split("+"):
        piece = piece.strip()
        if "!" not in piece:
            parts.append(piece)
            continue
        sheet, ref = piece.split("!", 1)
        match = re.fullmatch(r"([A-Z]+)(\d+)", ref)
        if not match or sheet not in wb.sheetnames:
            parts.append(piece)
            continue
        col = 0
        for letter in match.group(1):
            col = col * 26 + (ord(letter) - 64)
        row = int(match.group(2))
        value = wb[sheet].cell(row, col).value
        target = wb[new_sheet].cell(row, new_col)
        if not isinstance(value, (int, float)):
            parts.append(piece)
            continue
        if target.value not in (None, "") and not (isinstance(target.value, (int, float)) and abs(float(target.value) - float(value)) < 0.001):
            parts.append(piece)
            continue
        target.value = float(value)
        target.number_format = "#,##0.00"
        if wb[new_sheet].cell(row, new_col - 1).value in (None, ""):
            wb[new_sheet].cell(row, new_col - 1).value = wb[sheet].cell(row, col - 1).value
        if not (sheet == new_sheet and col == new_col):
            wb[sheet].cell(row, col).value = None
            wb[sheet].cell(row, col - 1).value = None
        touched.add((sheet, row, col))
        touched.add((new_sheet, row, new_col))
        parts.append(f"{new_sheet}!{get_column_letter(new_col)}{row}")
    log.cell(log_row, 5).value = "+".join(parts)
    log.cell(log_row, 2).value = new_day.isoformat()
    hhmm = _as_hhmm(receipt.get("when"))
    log.cell(log_row, 10).value = f"{new_day.isoformat()} {hhmm[:2]}:{hhmm[2:]}" if hhmm else new_day.isoformat()


def _append_file(wb, log_row: int, ws, receipt_row: int | None, saved_name: str, data: bytes, receipt: dict) -> None:
    log = wb["Log"]
    label = _file_label(saved_name, receipt)
    current = str(log.cell(log_row, 6).value or "")
    count = current.count(": ") + 1 if current else 1
    pointer = f"{count} {label}: {saved_name}"
    log.cell(log_row, 6).value = f"{current}, {pointer}" if current else pointer
    digest = sha256_bytes(data) if data else ""
    if digest:
        hashes = str(log.cell(log_row, 15).value or "")
        log.cell(log_row, 15).value = f"{hashes}, {count} {digest}" if hashes else f"1 {digest}"
    if receipt_row is not None:
        existing = str(ws.cell(receipt_row, 27).value or "")
        if not existing:
            ws.cell(receipt_row, 27).value = label
        elif existing == label or existing.startswith(label + " +"):
            extra = 1
            match = re.search(r"\+(\d+)$", existing)
            if match:
                extra = int(match.group(1)) + 1
            ws.cell(receipt_row, 27).value = f"{label} +{extra}" if not match else f"{label} +{extra}"
        else:
            ws.cell(receipt_row, 27).value = f"{existing.split(' +')[0]} +1"


def _write_question(wb, receipt, items, key, sheet, day, text, candidates, receipts_dir, name_prefix) -> None:
    """One open question. No category amount is written."""
    log_row = _next_log_row(wb)
    log = wb["Log"]
    dates = ", ".join(item["date"].isoformat() for item in candidates if item["date"])
    source = _source_label(receipt)
    log.cell(log_row, 1).value = f"open question: candidates {dates}; {source}"
    log.cell(log_row, 2).value = day.isoformat()
    log.cell(log_row, 3).value = short_store(receipt.get("store", ""))
    log.cell(log_row, 4).value = round(float(receipt["total"]), 2)
    log.cell(log_row, 4).number_format = "#,##0.00"
    log.cell(log_row, 8).value = f"{day.isoformat()}; candidates {dates}"
    log.cell(log_row, 9).value = normalize_number(receipt.get("number", ""))
    hhmm = _as_hhmm(receipt.get("when"))
    log.cell(log_row, 10).value = f"{day.isoformat()} {hhmm[:2]}:{hhmm[2:]}" if hhmm else day.isoformat()
    log.cell(log_row, 11).value = "; ".join(f"{item['name']}: {float(item['price']):.2f}" for item in items)
    log.cell(log_row, 12).value = str(receipt.get("last4") or "")
    log.cell(log_row, 14).value = "question"
    ws = wb[sheet]
    receipt_row = _next_receipt_row(wb, sheet)
    _write_receipt_row(ws, receipt_row, receipt, items, key, "", day)
    ws.cell(receipt_row, 81).value = text
    ws.cell(receipt_row, 82).value = "question"
    saved_name = _store_body(receipt, receipts_dir, name_prefix)
    if saved_name:
        _append_file(wb, log_row, ws, receipt_row, saved_name, _body_bytes(receipt), receipt)


def _question_sheet_row(wb, log_row: int):
    merchant = wb["Log"].cell(log_row, 3).value
    total = wb["Log"].cell(log_row, 4).value or 0
    for ws, row in _iter_receipt_rows(wb):
        if ws.cell(row, 82).value != "question":
            continue
        if ws.cell(row, 3).value != merchant:
            continue
        amount = ws.cell(row, 6).value or 0
        if isinstance(amount, (int, float)) and abs(float(amount) - float(total)) < 0.001:
            return ws, row
    return None, None


def _join_question(wb, log_row: int, receipt: dict, receipts_dir, name_prefix: str) -> str:
    log = wb["Log"]
    day = _as_date(receipt.get("when"))
    notes = str(log.cell(log_row, 8).value or "")
    source = str(log.cell(log_row, 1).value or "")
    if day and day.isoformat() not in notes:
        if "candidates " in notes:
            notes = notes + f", {day.isoformat()}"
        else:
            notes = f"{day.isoformat()}; candidates {day.isoformat()}"
        log.cell(log_row, 8).value = notes
        prefix, sep, tail = source.partition(";")
        if "candidates " in prefix:
            log.cell(log_row, 1).value = prefix + f", {day.isoformat()}" + (sep + tail if sep else "")
    label = _source_label(receipt)
    source = str(log.cell(log_row, 1).value or "")
    if label and label not in source:
        log.cell(log_row, 1).value = f"{source}, {label}" if source else label
    ws, receipt_row = _question_sheet_row(wb, log_row)
    saved_name = _store_body(receipt, receipts_dir, name_prefix)
    if saved_name:
        _append_file(wb, log_row, ws if ws is not None else wb[MONTHS[0]], receipt_row, saved_name, _body_bytes(receipt), receipt)
    if ws is not None and receipt_row is not None and ws.cell(receipt_row, 81).value:
        return str(ws.cell(receipt_row, 81).value)
    return "Which date does it match? Reply no if it's new."


def _finished_source(source: str) -> str:
    text = (source or "").strip()
    if text.startswith("open question:"):
        _head, sep, tail = text.partition(";")
        tail = tail.strip()
        return tail or "text"
    return text


def _items_from_receipt_row(ws, row: int) -> list[dict]:
    items = []
    for index in range(6):
        start = 9 + index * 3
        name = ws.cell(row, start).value
        price = ws.cell(row, start + 1).value
        category = ws.cell(row, start + 2).value
        if name in (None, "") and price in (None, ""):
            continue
        items.append({
            "name": str(name or ""),
            "price": float(price or 0),
            "category": str(category or "Meals"),
        })
    return items


def _receipt_from_question(wb, log_row: int) -> dict:
    log = wb["Log"]
    day = _as_date(log.cell(log_row, 2).value)
    return {
        "store": str(log.cell(log_row, 3).value or ""),
        "number": str(log.cell(log_row, 9).value or ""),
        "when": day,
        "total": float(log.cell(log_row, 4).value or 0),
        "last4": str(log.cell(log_row, 12).value or ""),
        "source": _finished_source(str(log.cell(log_row, 1).value or "")),
    }


def _merge_saved_files(wb, source_row: int, target_row: int, receipt: dict) -> None:
    """Copy file pointers from the question onto the purchase. Do not add an amount."""
    log = wb["Log"]
    incoming = [part.strip() for part in str(log.cell(source_row, 6).value or "").split(",") if part.strip()]
    current = str(log.cell(target_row, 6).value or "")
    hashes = [part.strip() for part in str(log.cell(source_row, 15).value or "").split(",") if part.strip()]
    target_hashes = str(log.cell(target_row, 15).value or "")
    for piece in incoming:
        name = piece.split(": ", 1)[-1].strip() if ": " in piece else piece
        if not name or name in current:
            continue
        label = piece.split(": ", 1)[0]
        label = label.split(" ", 1)[-1] if label[:1].isdigit() else label
        count = current.count(": ") + 1 if current else 1
        pointer = f"{count} {label}: {name}"
        current = f"{current}, {pointer}" if current else pointer
    if current:
        log.cell(target_row, 6).value = current
    for piece in hashes:
        digest = piece.split(" ", 1)[-1]
        if not digest or digest in target_hashes:
            continue
        count = target_hashes.count(" ") + 1 if target_hashes else 1
        target_hashes = f"{target_hashes}, {count} {digest}" if target_hashes else f"1 {digest}"
    if target_hashes:
        log.cell(target_row, 15).value = target_hashes
    source = _finished_source(str(log.cell(source_row, 1).value or "")) or _source_label(receipt)
    kept = str(log.cell(target_row, 1).value or "")
    if source and source not in kept:
        log.cell(target_row, 1).value = f"{kept}, {source}" if kept else source


def _clear_question_row(wb, log_row: int, status: str, linked: str = "") -> None:
    log = wb["Log"]
    log.cell(log_row, 14).value = status
    if linked:
        log.cell(log_row, 20).value = linked
    ws, receipt_row = _question_sheet_row(wb, log_row)
    if ws is None:
        return
    ws.cell(receipt_row, 81).value = None
    ws.cell(receipt_row, 82).value = status


def answer_question(workbook_path, key: str, answer: str, receipts_dir, backups_dir, name_prefix: str = "", stamp: str | None = None) -> dict:
    """Record the reply to one near-match question.

    Pass the user's raw reply. Dates are read first (``Nov 3``, ``November 3``,
    ``2026-11-03``). A whole reply of ``no``, ``nope``, ``nah``, ``no, it's new``,
    ``new``, or ``different`` writes that question as its own purchase, once.
    A whole reply of ``yes``, ``yes, same purchase``, ``yes it matches``, ``same``,
    ``that one``, or ``correct`` attaches when there is exactly one candidate.
    Anything else asks again and writes nothing. A later apply of the same receipt
    does not write the amount again. After a no, a changed body of that key attaches
    the file and adds no amount. A bare yes with two or more candidates leaves the
    question open.
    """
    workbook_path = Path(workbook_path)
    receipts_dir = Path(receipts_dir)
    backups_dir = Path(backups_dir)
    idle = {"locked": False, "action": "skip", "key": key, "text": "", "backup": ""}
    if is_locked(workbook_path):
        return {"locked": True, "action": "skip", "key": key, "text": "", "backup": ""}
    wb = load_workbook(workbook_path)
    log_row = _find_log_row(wb, key)
    if log_row is None or str(wb["Log"].cell(log_row, 14).value or "") != "question":
        return idle
    try:
        kind, when = _parse_reply(answer)
    except ValueError:
        ws, receipt_row = _question_sheet_row(wb, log_row)
        stored = str(ws.cell(receipt_row, 81).value) if ws is not None and receipt_row else ""
        return {"locked": False, "action": "ask", "key": key, "text": stored, "backup": ""}
    if kind == "no":
        return _answer_no(wb, workbook_path, log_row, key, receipts_dir, backups_dir, stamp)
    receipt = _receipt_from_question(wb, log_row)
    candidates = _gather_candidates(_log_rows(wb), receipt)
    chosen = _pick_candidate(candidates, kind, when)
    if chosen is None:
        text = _question_text(receipt, candidates) if candidates else "Which date does it match? Reply no if it's new."
        return {"locked": False, "action": "ask", "key": key, "text": text, "backup": ""}
    return _answer_yes(wb, workbook_path, log_row, key, chosen, receipt, receipts_dir, backups_dir, stamp)


def _answer_no(wb, workbook_path, log_row: int, key: str, receipts_dir, backups_dir, stamp) -> dict:
    log = wb["Log"]
    day = _as_date(log.cell(log_row, 2).value)
    if day is None:
        raise ValueError("question row has no date")
    sheet = MONTHS[day.month - 1]
    ws, receipt_row = _question_sheet_row(wb, log_row)
    if ws is None:
        raise RuntimeError("question has no receipt row")
    items = _items_from_receipt_row(ws, receipt_row)
    if not items:
        items = _items_of(_receipt_from_question(wb, log_row))
    before = _grid_snapshot(wb)
    touched: set[tuple] = set()
    cells, _fresh = _amount_cells(wb[sheet], day.day, items, store=str(log.cell(log_row, 3).value or ""))
    where = _where_text(sheet, cells)
    label = short_store(str(log.cell(log_row, 3).value or ""))
    for category, row, col, amount in cells:
        current = wb[sheet].cell(row, col).value
        if isinstance(current, (int, float)) and abs(float(current) - amount) < 0.001:
            touched.add((sheet, row, col))
            continue
        if current not in (None, ""):
            raise RuntimeError(f"refusing to overwrite {sheet}!{get_column_letter(col)}{row}")
        names = [item["name"] for item in items if item["category"] == category and item.get("name")]
        wb[sheet].cell(row, col - 1).value = f"{label} {' '.join(names)}".strip()
        wb[sheet].cell(row, col).value = amount
        wb[sheet].cell(row, col).number_format = "#,##0.00"
        touched.add((sheet, row, col))
    cash = not str(log.cell(log_row, 12).value or "").strip()
    log.cell(log_row, 1).value = _finished_source(str(log.cell(log_row, 1).value or ""))
    log.cell(log_row, 5).value = where
    log.cell(log_row, 13).value = f"{sheet}!B{receipt_row}"
    log.cell(log_row, 14).value = "cash" if cash else "awaiting statement"
    ws.cell(receipt_row, 81).value = None
    ws.cell(receipt_row, 82).value = "cash" if cash else "pending"
    ws.cell(receipt_row, 83).value = where
    ws.cell(receipt_row, 7).number_format = "@"
    _assert_grid(before, _grid_snapshot(wb), touched)
    backup_path = backup_workbook(workbook_path, backups_dir, stamp=stamp)
    _atomic_save(wb, workbook_path)
    return {"locked": False, "action": "wrote", "key": key, "text": "", "backup": str(backup_path)}


def _answer_yes(wb, workbook_path, log_row: int, key: str, chosen: dict, receipt: dict, receipts_dir, backups_dir, stamp) -> dict:
    before = _grid_snapshot(wb)
    touched: set[tuple] = set()
    new_day = _as_date(receipt.get("when")) or chosen["date"]
    _attach_to_log(wb, chosen["row"], receipt, new_day, receipts_dir, "", touched)
    _merge_saved_files(wb, log_row, chosen["row"], receipt)
    kept_key = receipt_key(chosen["merchant"], chosen["number"], chosen["date"], chosen["total"])
    _clear_question_row(wb, log_row, "superseded", linked=kept_key)
    _assert_grid(before, _grid_snapshot(wb), touched)
    backup_path = backup_workbook(workbook_path, backups_dir, stamp=stamp)
    _atomic_save(wb, workbook_path)
    return {"locked": False, "action": "attached", "key": key, "text": "", "backup": str(backup_path)}


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


def _parse_version(value) -> tuple | str | None:
    """A version tuple, the word ``migrating``, or None when the cell is blank."""
    text = str(value or "").strip()
    if not text:
        return None
    if text == "migrating":
        return "migrating"
    match = re.fullmatch(r"v(\d+(?:\.\d+)*)", text)
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def _format_version(version: tuple) -> str:
    return "v" + ".".join(str(part) for part in version)


def _column_has_prefix(wb, prefix: str) -> bool:
    for name in MONTHS:
        if name not in wb.sheetnames:
            continue
        ws = wb[name]
        for row in range(1, min(ws.max_row or 1, 400) + 1):
            value = ws.cell(row, 2).value
            if isinstance(value, str) and value.startswith(prefix):
                return True
    return False


def _has_old_receipt_list(wb) -> bool:
    """The v1.2.3 list: title in column B, and ``Date & time`` on the next row."""
    for name in MONTHS:
        if name not in wb.sheetnames:
            continue
        ws = wb[name]
        for row in range(1, min(ws.max_row or 1, 400) + 1):
            value = ws.cell(row, 2).value
            if isinstance(value, str) and value.startswith("Receipts this month"):
                header = ws.cell(row + 1, 2).value
                if header == "Date & time":
                    return True
    return False


def _has_log(wb) -> bool:
    return "Log" in wb.sheetnames


def _has_log_status(wb) -> bool:
    if "Log" not in wb.sheetnames:
        return False
    log = wb["Log"]
    return log.cell(1, 14).value == "Status" and log.cell(1, 15).value == "Content hash"


def _has_statement_settings(wb) -> bool:
    if "Annual Summary" not in wb.sheetnames:
        return False
    summary = wb["Annual Summary"]
    if summary["B47"].value == "Statement features":
        return True
    return summary["C47"].value in FEATURE_VALUES


def _has_current_bot_state(wb) -> bool:
    if BOT_STATE_SHEET not in wb.sheetnames:
        return False
    ws = wb[BOT_STATE_SHEET]
    note = str(ws["A1"].value or "")
    if "Managed by Family Book bot" not in note:
        return False
    parsed = _parse_version(ws["B4"].value)
    return isinstance(parsed, tuple) and parsed >= BOT_VERSION_TUPLE


def structure_version(wb) -> tuple:
    """Highest version the sheets actually have. A blank C46 is not consulted.

    Each later check requires the earlier layout, so a v2 book is not left at
    v1.2.3 just because it still has a Book version label.
    """
    level = (1, 0)
    if _has_log(wb):
        level = (1, 2)
    if _has_old_receipt_list(wb) or (
        "Annual Summary" in wb.sheetnames and str(wb["Annual Summary"]["B46"].value or "").strip() == "Book version"
    ):
        level = (1, 2, 3)
    if _has_old_receipt_list(wb) and _has_log_status(wb):
        level = (1, 2, 4)
    if _column_has_prefix(wb, "Transactions this month"):
        level = (2, 0)
    if level >= (2, 0) and _has_statement_settings(wb):
        level = (2, 1)
    if level >= (2, 1) and _has_current_bot_state(wb):
        level = (2, 2)
    return level


def steps_after(effective: tuple) -> list[str]:
    """Steps still to run, in order. A finished v2.2 book returns an empty list."""
    return [STEP_NAME[step] for step in CHAIN if step > effective]


def detect_version(wb) -> dict:
    """C46 plus a structure check.

    A blank C46 uses the sheets. It is not treated as v1.0 when the book
    already has later sections. A marker newer than this bot is read-only.
    When the marker and the sheets disagree, the sheets win: a stale low
    marker does not rebuild finished work, and a high marker does not skip a
    step whose sheet is missing.
    """
    marker_cell = ""
    if "Annual Summary" in wb.sheetnames:
        marker_cell = wb["Annual Summary"]["C46"].value
    parsed = _parse_version(marker_cell)
    structure = structure_version(wb)
    marker_text = str(marker_cell or "").strip()
    if isinstance(parsed, tuple) and parsed > BOT_VERSION_TUPLE:
        return {
            "marker": marker_text,
            "structure": _format_version(structure),
            "effective": _format_version(parsed),
            "newer": True,
            "steps": [],
            "action": "read-only",
        }
    # Sheets win over a blank, a stale marker, and a marker that claims
    # work the sheets do not have. ``migrating`` resumes from the sheets.
    effective = structure
    steps = steps_after(effective)
    marker_is_current = isinstance(parsed, tuple) and parsed == BOT_VERSION_TUPLE
    if structure >= BOT_VERSION_TUPLE and not marker_is_current:
        if "v2.2" not in steps:
            steps.append("v2.2")
    if not steps:
        action = "noop"
    elif any(step in steps for step in ("v1.2.3", "v2.0")):
        action = "skill"
    else:
        action = "migrate"
    return {
        "marker": marker_text,
        "structure": _format_version(structure),
        "effective": _format_version(effective),
        "newer": False,
        "steps": steps,
        "action": action,
    }


def book_year(value) -> int | None:
    if isinstance(value, bool) or value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.year if 1900 <= value.year <= 2999 else None
    if isinstance(value, date):
        return value.year if 1900 <= value.year <= 2999 else None
    if isinstance(value, (int, float)) and float(value) == int(value):
        year = int(value)
        return year if 1900 <= year <= 2999 else None
    if isinstance(value, str) and re.fullmatch(r"\d{4}", value.strip()):
        year = int(value.strip())
        return year if 1900 <= year <= 2999 else None
    return None


def is_real_book(wb) -> bool:
    """A year book, not a look-alike spreadsheet.

    v1.2.3 and later have the ``Book version`` label in B46 and a year in F5.
    v1.0 through v1.2.2 never got that label. Those still count when the
    banner starts with ``Family Book``, F5 is a year, and a Jan sheet exists.
    A file with neither the label nor that banner is not a book.
    """
    if "Annual Summary" not in wb.sheetnames:
        return False
    summary = wb["Annual Summary"]
    if book_year(summary["F5"].value) is None:
        return False
    if str(summary["B46"].value or "").strip() == "Book version":
        return True
    banner = str(summary["B2"].value or "")
    return banner.startswith("Family Book") and "Jan" in wb.sheetnames


def _leaf_name(name: str) -> str:
    leaf = name.replace("\\", "/").rstrip("/").split("/")[-1]
    if leaf.lower().endswith(".xlsx"):
        leaf = leaf[:-5]
    return leaf.strip()


def name_is_skipped(name: str) -> bool:
    """Tester copies and Drive's ``Copy of`` duplicates are not candidates."""
    leaf = _leaf_name(name).lower()
    return leaf.startswith("test -") or leaf.startswith("copy of")


def path_is_skipped(path: str) -> bool:
    """Trash is filtered by the caller. Backups, templates, and tester copies are not books."""
    parts = [part for part in path.replace("\\", "/").split("/") if part]
    reserved = {"family book - backups", "family book - templates", "backups"}
    for part in parts:
        if name_is_skipped(part) or part.lower() in reserved:
            return True
    return False


def group_book_sets(records: list[dict]) -> list[dict]:
    """Group real books into household sets. One set reconnects. Several ask.

    ``records`` use name, path, storage, owned, trashed, container, owner_id,
    year, and real. ``container`` is the root folder id when the parent is
    ``Family Book``. Use ``legacy`` when the year folder still sits at the
    top of that drive. Trashed rows are ignored.
    """
    kept = []
    for record in records:
        if record.get("trashed") or not record.get("real"):
            continue
        if name_is_skipped(str(record.get("name") or "")):
            continue
        if path_is_skipped(str(record.get("path") or record.get("name") or "")):
            continue
        kept.append(record)

    owned = [record for record in kept if record.get("owned")]
    shared = [record for record in kept if not record.get("owned")]
    sets = []

    by_container: dict[tuple, list] = {}
    legacy_by_storage: dict[str, list] = {}
    for record in owned:
        storage = record.get("storage") or ""
        container = record.get("container") or ""
        if container == "legacy":
            legacy_by_storage.setdefault(storage, []).append(record)
        else:
            by_container.setdefault((storage, container), []).append(record)

    root_sets = []
    for key, rows in by_container.items():
        root_sets.append((key, rows))
    if len(root_sets) == 1:
        storage, _container = root_sets[0][0]
        root_sets[0][1].extend(legacy_by_storage.pop(storage, []))
    for storage, rows in legacy_by_storage.items():
        root_sets.append(((storage, "legacy"), rows))

    for (storage, container), rows in root_sets:
        years = sorted({int(row["year"]) for row in rows if row.get("year")})
        sets.append({
            "role": "owner",
            "storage": storage,
            "container": container,
            "years": years,
            "names": [row.get("name") for row in rows],
        })

    shared_groups: dict[tuple, list] = {}
    alone = []
    for record in shared:
        owner_id = record.get("owner_id") or ""
        if owner_id:
            shared_groups.setdefault((record.get("storage") or "", owner_id), []).append(record)
        else:
            alone.append(record)
    for (storage, owner_id), rows in shared_groups.items():
        years = sorted({int(row["year"]) for row in rows if row.get("year")})
        sets.append({
            "role": "member",
            "storage": storage,
            "container": owner_id,
            "years": years,
            "names": [row.get("name") for row in rows],
        })
    for record in alone:
        year = record.get("year")
        sets.append({
            "role": "member",
            "storage": record.get("storage") or "",
            "container": record.get("path") or record.get("name"),
            "years": [int(year)] if year else [],
            "names": [record.get("name")],
        })
    return sets


def choose_book_sets(sets: list[dict]) -> dict:
    """One set reconnects. Several always ask. None is a new setup."""
    if not sets:
        return {"action": "setup", "sets": []}
    if len(sets) == 1:
        return {"action": "reconnect", "role": sets[0]["role"], "book": sets[0], "sets": sets}
    return {"action": "ask", "sets": sets}


def missing_routines(existing_titles, *, role: str, features_on: bool, inbox_ready: bool) -> list[str]:
    """Routine titles that are not on the bot yet. An existing title is not created again."""
    have = {str(title).strip().lower() for title in existing_titles}
    wanted = ["Spending report"]
    if inbox_ready:
        wanted.insert(0, "Daily receipt scan")
    if role == "owner":
        wanted.append("New year's book")
    if features_on:
        wanted.append("Card due reminder")
        if role == "owner":
            wanted.append("Statement ready")
    return [title for title in wanted if title.lower() not in have]


def _bot_state_sheet(wb):
    if BOT_STATE_SHEET in wb.sheetnames:
        return wb[BOT_STATE_SHEET]
    ws = wb.create_sheet(BOT_STATE_SHEET)
    ws["A1"] = BOT_STATE_NOTE
    ws.merge_cells("A1:F1")
    ws["A1"].alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[1].height = 32
    ws["A3"] = "Key"
    ws["B3"] = "Value"
    for row, label, _key in BOT_FIELDS:
        ws.cell(row, 1).value = label
    ws["A16"] = "Family members"
    ws.cell(MEMBERS_HEADER_ROW, 1).value = "Display name"
    ws.cell(MEMBERS_HEADER_ROW, 2).value = "Role"
    ws.cell(MEMBERS_HEADER_ROW, 3).value = "Inboxes"
    ws["A29"] = "Inbox scans"
    ws.cell(INBOX_HEADER_ROW, 1).value = "Inbox"
    ws.cell(INBOX_HEADER_ROW, 2).value = "Last scan"
    ws.cell(INBOX_HEADER_ROW, 3).value = "Updated by"
    ws.sheet_state = "hidden"
    return ws


def _ensure_bot_state(wb, updates: dict | None = None, members: list | None = None) -> None:
    """Create or fill Bot State. Values are text. Existing inbox rows are kept."""
    ws = _bot_state_sheet(wb)
    if not str(ws["A1"].value or "").startswith("Managed by Family Book bot"):
        ws["A1"] = BOT_STATE_NOTE
    for row, label, key in BOT_FIELDS:
        if ws.cell(row, 1).value != label:
            ws.cell(row, 1).value = label
        if updates and key in updates and updates[key] is not None:
            ws.cell(row, 2).value = str(updates[key])
    if members is not None:
        for index, member in enumerate(members[: MEMBERS_LAST - MEMBERS_FIRST + 1]):
            row = MEMBERS_FIRST + index
            ws.cell(row, 1).value = str(member.get("name") or "")
            ws.cell(row, 2).value = str(member.get("role") or "")
            ws.cell(row, 3).value = str(member.get("inboxes") or "")
    # Excel and OneDrive can hide the sheet. Google Sheets often cannot.
    # The note stays either way. Local files hide it.
    ws.sheet_state = "hidden"


def _parse_stamp(value) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1]
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def read_bot_state(wb) -> dict:
    if BOT_STATE_SHEET not in wb.sheetnames:
        return {
            "present": False,
            "fields": {},
            "members": [],
            "inboxes": {},
        }
    ws = wb[BOT_STATE_SHEET]
    fields = {}
    for row, _label, key in BOT_FIELDS:
        fields[key] = str(ws.cell(row, 2).value or "")
    members = []
    for row in range(MEMBERS_FIRST, MEMBERS_LAST + 1):
        name = str(ws.cell(row, 1).value or "").strip()
        if not name:
            continue
        members.append({
            "name": name,
            "role": str(ws.cell(row, 2).value or "").strip(),
            "inboxes": str(ws.cell(row, 3).value or "").strip(),
        })
    inboxes = {}
    for row in range(INBOX_FIRST, INBOX_LAST + 1):
        inbox = str(ws.cell(row, 1).value or "").strip()
        if not inbox:
            continue
        inboxes[inbox] = {
            "last_scan": str(ws.cell(row, 2).value or "").strip(),
            "updated_by": str(ws.cell(row, 3).value or "").strip(),
            "row": row,
        }
    return {"present": True, "fields": fields, "members": members, "inboxes": inboxes}


def memory_from_book(wb) -> dict:
    """Facts a reinstalled bot copies into memory. Role still follows file ownership."""
    summary = wb["Annual Summary"] if "Annual Summary" in wb.sheetnames else None
    settings = read_settings(wb) if summary is not None else {}
    state = read_bot_state(wb)
    fields = state["fields"]
    currency = fields.get("currency") or ""
    if not currency and summary is not None:
        currency = str(summary["C11"].value or "")
    version = ""
    if summary is not None:
        version = str(summary["C46"].value or "")
    if not version:
        version = fields.get("book_version") or ""
    return {
        "version": version,
        "storage": fields.get("storage") or "",
        "currency": currency,
        "holiday_region": fields.get("holiday_region") or "",
        "root_folder_id": fields.get("root_folder_id") or "",
        "root_path": fields.get("root_path") or "",
        "year_folder_id": fields.get("year_folder_id") or "",
        "workbook_id": fields.get("workbook_id") or "",
        "receipts_folder_id": fields.get("receipts_folder_id") or "",
        "statements_folder_id": fields.get("statements_folder_id") or "",
        "year": fields.get("year") or (str(book_year(summary["F5"].value)) if summary is not None and book_year(summary["F5"].value) else ""),
        "statement_features": settings.get("features", "off"),
        "statement_offer": settings.get("offer", "not yet"),
        "book_started": settings.get("started", ""),
        "members": state["members"],
        "inboxes": {key: value["last_scan"] for key, value in state["inboxes"].items()},
    }


def _newest_log_date(wb) -> date | None:
    if "Log" not in wb.sheetnames:
        return None
    log = wb["Log"]
    newest = None
    for row in range(2, min(log.max_row or 1, 5000) + 1):
        for column in (2, 10):
            parsed = _parse_stamp(log.cell(row, column).value)
            if parsed is None:
                continue
            found = parsed.date()
            if newest is None or found > newest:
                newest = found
    return newest


def message_already_logged(wb, inbox: str, message_id: str) -> bool:
    """True when Log column A already names this inbox and message id.

    That row is the duplicate backstop for the two-day overlap. The scan
    attaches or skips. It does not add the amount again.
    """
    if "Log" not in wb.sheetnames or not inbox or not message_id:
        return False
    needle = f"email {inbox} {message_id}"
    log = wb["Log"]
    for row in range(2, min(log.max_row or 1, 5000) + 1):
        source = str(log.cell(row, 1).value or "")
        if needle in source:
            return True
    return False


def scan_not_before(wb, inbox: str, today: date | None = None) -> dict:
    """When this inbox's search starts. Never the beginning of the mailbox.

    Saved last-scan minus 2 days. Otherwise the newest Log date minus 7 days.
    Otherwise Book started (C52). A book with none of those is new: the last
    30 days only, and older mail can be backfilled on request.
    """
    today = today or date.today()
    state = read_bot_state(wb)
    stamp = _parse_stamp(state["inboxes"].get(inbox, {}).get("last_scan"))
    if stamp is not None:
        return {"not_before": stamp - timedelta(days=2), "source": "watermark", "inbox": inbox}
    newest = _newest_log_date(wb)
    if newest is not None:
        return {
            "not_before": datetime.combine(newest - timedelta(days=7), datetime.min.time()),
            "source": "log",
            "inbox": inbox,
        }
    started = None
    if "Annual Summary" in wb.sheetnames:
        started = _parse_stamp(wb["Annual Summary"]["C52"].value)
    if started is not None:
        return {"not_before": datetime.combine(started.date(), datetime.min.time()), "source": "book-started", "inbox": inbox}
    return {
        "not_before": datetime.combine(today - timedelta(days=30), datetime.min.time()),
        "source": "new-book",
        "inbox": inbox,
    }


def write_inbox_scan(workbook_path, inbox: str, when: datetime, allowed_inboxes) -> dict:
    """Write one inbox's last-scan time. Other inboxes and the key block stay put.

    A member passes only that member's own inbox in ``allowed_inboxes``.
    The call refuses, and does not save, when ``inbox`` is not allowed.
    """
    allowed = set(allowed_inboxes)
    if inbox not in allowed:
        raise PermissionError(f"this bot may not write the scan time for {inbox}")
    workbook_path = Path(workbook_path)
    if is_locked(workbook_path):
        return {"locked": True, "changed": False}
    wb = load_workbook(workbook_path)
    before = read_bot_state(wb)
    if not before["present"]:
        raise RuntimeError("Bot State is missing. The owner's bot adds it. A member does not.")
    ws = wb[BOT_STATE_SHEET]
    field_before = {row: ws.cell(row, 2).value for row, _label, _key in BOT_FIELDS}
    other_before = {
        key: (ws.cell(value["row"], 2).value, ws.cell(value["row"], 3).value)
        for key, value in before["inboxes"].items()
        if key != inbox
    }
    stamp = when.strftime("%Y-%m-%dT%H:%M:%SZ")
    if inbox in before["inboxes"]:
        row = before["inboxes"][inbox]["row"]
    else:
        row = None
        for candidate in range(INBOX_FIRST, INBOX_LAST + 1):
            if not str(ws.cell(candidate, 1).value or "").strip():
                row = candidate
                break
        if row is None:
            raise RuntimeError("Bot State has no empty inbox row")
        ws.cell(row, 1).value = inbox
    ws.cell(row, 2).value = stamp
    ws.cell(row, 3).value = inbox
    for key, pair in other_before.items():
        other_row = before["inboxes"][key]["row"]
        if (ws.cell(other_row, 2).value, ws.cell(other_row, 3).value) != pair:
            raise RuntimeError(f"refusing to change another inbox: {key}")
    for field_row, value in field_before.items():
        if ws.cell(field_row, 2).value != value:
            raise RuntimeError("refusing to change Bot State book fields during a scan-time write")
    _atomic_save(wb, workbook_path)
    return {"locked": False, "changed": True, "inbox": inbox, "last_scan": stamp}


def snapshot_amount_block(wb) -> dict:
    """Typed numbers in rows 1–44 of Annual Summary and each month. Not formulas."""
    found = {}
    names = ["Annual Summary", *MONTHS]
    for name in names:
        if name not in wb.sheetnames:
            continue
        ws = wb[name]
        for row in range(1, 45):
            for col in range(1, 72):
                value = ws.cell(row, col).value
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    continue
                found[(name, get_column_letter(col) + str(row))] = value
    return found


def snapshot_formula_block(wb) -> dict:
    found = {}
    names = ["Annual Summary", *MONTHS]
    for name in names:
        if name not in wb.sheetnames:
            continue
        ws = wb[name]
        for row in range(1, 45):
            for col in range(1, 72):
                value = ws.cell(row, col).value
                if isinstance(value, str) and value.startswith("="):
                    found[(name, get_column_letter(col) + str(row))] = value
    return found


def migration_backup(path: Path, backups_dir: Path, step_name: str, stamp: str | None = None) -> Path:
    """Copy the workbook into ``Family Book - Backups`` before one migration step."""
    path = Path(path)
    backups_dir = Path(backups_dir)
    backups_dir.mkdir(parents=True, exist_ok=True)
    when = stamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = backups_dir / f"{path.stem} - before-{step_name} - {when}{path.suffix}"
    number = 2
    while dest.exists():
        dest = backups_dir / f"{path.stem} - before-{step_name} - {when} - {number}{path.suffix}"
        number += 1
    shutil.copy2(path, dest)
    if dest.stat().st_size <= 0:
        raise RuntimeError(f"backup is empty: {dest}")
    return dest


def restore_workbook(path: Path, backup: Path) -> None:
    """Put the backup bytes back. The backup file itself stays."""
    shutil.copy2(backup, path)


def guarded_write(workbook_path, backups_dir, step_name: str, mutate, stamp: str | None = None) -> dict:
    """Run one step. Any number or formula change in rows 1–44 restores and stops.

    ``mutate`` receives the workbook and must not save it. A restore leaves the
    backup in place and does not retry.
    """
    workbook_path = Path(workbook_path)
    if is_locked(workbook_path):
        return {"ok": False, "locked": True, "restored": False, "changed": False, "step": step_name}
    backup = migration_backup(workbook_path, backups_dir, step_name, stamp=stamp)
    wb = load_workbook(workbook_path)
    before_numbers = snapshot_amount_block(wb)
    before_formulas = snapshot_formula_block(wb)
    try:
        extra = mutate(wb) or {}
    except Exception:
        restore_workbook(workbook_path, backup)
        raise
    if snapshot_amount_block(wb) != before_numbers or snapshot_formula_block(wb) != before_formulas:
        restore_workbook(workbook_path, backup)
        return {
            "ok": False,
            "locked": False,
            "restored": True,
            "changed": False,
            "backup": str(backup),
            "step": step_name,
        }
    _atomic_save(wb, workbook_path)
    if not isinstance(extra, dict):
        extra = {"detail": extra}
    return {
        "ok": True,
        "locked": False,
        "restored": False,
        "changed": True,
        "backup": str(backup),
        "step": step_name,
        **extra,
    }


def _apply_v22_state(wb, updates: dict | None = None) -> dict:
    """The v2.1 → v2.2 step. Settings cells and amount cells stay as they are."""
    summary = _summary(wb)
    version = str(summary["C46"].value or "")
    parsed = _parse_version(version)
    if isinstance(parsed, tuple) and parsed > BOT_VERSION_TUPLE:
        raise RuntimeError(f"refusing to write a newer book ({version})")
    fields = {
        "book_version": BOT_VERSION,
        "currency": str(summary["C11"].value or ""),
        "year": str(book_year(summary["F5"].value) or ""),
    }
    if updates:
        for key, value in updates.items():
            if value is not None:
                fields[key] = value
    _ensure_bot_state(wb, fields)
    banner = str(summary["B2"].value or "")
    if banner.startswith("Family Book v2.1"):
        summary["B2"] = "Family Book v2.2" + banner[len("Family Book v2.1"):]
    elif banner.startswith("Family Book v2.0"):
        summary["B2"] = "Family Book v2.2" + banner[len("Family Book v2.0"):]
    summary["B46"] = "Book version"
    summary["C46"] = BOT_VERSION
    return {"version": BOT_VERSION}


def migrate_book(workbook_path, backups_dir, updates: dict | None = None, stamp: str | None = None) -> dict:
    """Run the steps this file can finish: v2.1 settings, then v2.2 Bot State.

    v1.x through v2.0 stay in the family-book-migrate skill, which uses the
    same backup and the same rows 1–44 check. This function does not start
    those steps and does not change the file while they are still pending.
    A second call on a finished v2.2 book writes nothing and takes no backup.
    A newer book is not written.
    """
    workbook_path = Path(workbook_path)
    if is_locked(workbook_path):
        return {"locked": True, "changed": False, "action": "locked"}
    wb = load_workbook(workbook_path)
    info = detect_version(wb)
    if info["action"] == "read-only":
        return {"locked": False, "changed": False, "action": "read-only", **info}
    if info["action"] == "noop":
        return {"locked": False, "changed": False, "action": "noop", **info}
    if info["action"] == "skill":
        return {"locked": False, "changed": False, "action": "skill", **info}
    backups_dir = Path(backups_dir)
    results = []
    if "v2.1" in info["steps"]:
        def apply_v21(book):
            summary = _summary(book)
            if str(summary["C46"].value or "") not in {"v2.0", "v2.1"}:
                summary["C46"] = "v2.0"
            return _apply_v21_cells(book)
        results.append(guarded_write(workbook_path, backups_dir, "v2.1", apply_v21, stamp=stamp))
        if not results[-1]["ok"]:
            return {"locked": False, "changed": False, "action": "restored", "steps_run": results, **{k: v for k, v in info.items() if k != "action"}}
    def apply_v22(book):
        return _apply_v22_state(book, updates)
    results.append(guarded_write(workbook_path, backups_dir, "v2.2", apply_v22, stamp=stamp))
    if not results[-1]["ok"]:
        after = detect_version(load_workbook(workbook_path))
        after.pop("action", None)
        return {"locked": False, "changed": False, "action": "restored", "steps_run": results, **after}
    done = detect_version(load_workbook(workbook_path))
    done.pop("action", None)
    return {"locked": False, "changed": True, "action": "migrate", "steps_run": results, **done}


def _apply_v21_cells(wb) -> dict:
    """Settings cells only. Shared by migrate_v21_settings and the v2.2 chain."""
    summary = _summary(wb)
    version = str(summary["C46"].value or "")
    if summary["C47"].value not in FEATURE_VALUES:
        summary["B47"] = "Statement features"
        summary["C47"] = "on" if _has_statement_data(wb) else "off"
    elif summary["B47"].value != "Statement features":
        summary["B47"] = "Statement features"
    if summary["C48"].value not in OFFER_VALUES:
        summary["B48"] = "Statement offer"
        summary["C48"] = "accepted" if summary["C47"].value == "on" else "not yet"
    elif summary["B48"].value != "Statement offer":
        summary["B48"] = "Statement offer"
    for row, label in ((49, "Last weekly report"), (50, "Last monthly report"), (51, "Last yearly report")):
        if summary.cell(row, 2).value != label:
            summary.cell(row, 2).value = label
    if summary["B52"].value != "Book started":
        summary["B52"] = "Book started"
    if not summary["C52"].value:
        summary["C52"] = date.today().isoformat()
    banner = str(summary["B2"].value or "")
    if banner.startswith("Family Book v2.0"):
        summary["B2"] = "Family Book v2.1" + banner[len("Family Book v2.0"):]
    if version == "v2.0":
        summary["C46"] = "v2.1"
    return {"version": str(summary["C46"].value or "")}


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
    if summary["B52"].value != "Book started":
        summary["B52"] = "Book started"
        changed = True
    if not summary["C52"].value:
        # The day clock starts when this step runs. It does not use a receipt date.
        summary["C52"] = date.today().isoformat()
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


def suggest_statement(features: str, offer: str, count: int, started: date | None, today: date) -> str:
    """One suggestion, or an empty string.

    ``started`` is Annual Summary ``C52`` (the day the book was set up), not
    the date on a receipt. A no, a yes, or an earlier ask returns nothing.
    """
    if features == "on":
        return ""
    if offer != "not yet":
        return ""
    days = (today - started).days if started else 0
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
