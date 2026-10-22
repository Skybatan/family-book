"""Offline rules for Family Book v2.0.

This module is the checker behind tests/v2.0. The bot skills describe the
same rules in prose for a connector-only bot. Nothing here reads a real
statement or a real card number.

A statement line has no issuer transaction id. The key is:

    last4|YYYY-MM-DD|amount|NORMALIZED DESCRIPTION|occurrence

The date in the key is the post date. Occurrence numbers identical lines
in statement order, starting at 1.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional


MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}
MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Leading markers issuers print on a line (CIBC uses Y-acute).
MARKERS = ("Ý", "Ý", "\u00dd", "\u00fd", "•", "·")

ISSUER_CATEGORIES = [
    "Personal and Household Expenses",
    "Professional and Financial Services",
    "Hotel, Entertainment and Recreation",
    "Home and Office Improvement",
    "Retail and Grocery",
    "Health and Education",
    "Other Transactions",
    "Transportation",
    "Restaurants",
]

PAYMENT_RE = re.compile(
    r"(PAYMENT\s+THANK\s+YOU|PAIEMENT\s+MERCI|BANK\s+PAYMENT|"
    r"PAIEMENT\s+BANQUE|PAYMENT\s+RECEIVED|ONLINE\s+PAYMENT|"
    r"THANK\s+YOU\s*/\s*PAIEMENT)",
    re.I,
)
FX_RE = re.compile(
    r"FOREIGN\s+CURRENCY\s+([A-Z]{3})\s+([\d,]+\.\d+)\s*@\s*([\d.]+)",
    re.I,
)
AMOUNT_RE = re.compile(r"^-?\$?\(?\d{1,3}(?:,\d{3})*\.\d{2}\)?$")
LAST4_RE = re.compile(r"(?:XXXX(?:\s+XXXX){2}\s+|ending with\s+)(\d{4})", re.I)
CARD_HEADER_RE = re.compile(
    r"(?:Card\s+number|Card\s*#|Purchases\s*-\s*Card\s*#|Account\s+number)"
    r"[^\d]{0,40}(\d{4})",
    re.I,
)

BIG_CHARGE = 75.00  # book currency; ask once at or above this

# Sheet rows. Fuel is a single row, so a second fuel purchase on the same
# day becomes a formula on that cell. The number grid itself is unchanged.
CATEGORY_ROWS = {
    "Meals": (6, 16),
    "Snacks": (17, 19),
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
    "Bank fees": (37, 40),
    "Temporary Income": (43, 43),
}
FIXED_ROWS = {
    "Income offset": 18,
    "GAS": 19,
    "Electricity & Water": 20,
    "RESP": 21,
    "Mobile Phone": 22,
    "Daycare": 23,
    "Rent / Mortgage": 24,
    "Internet": 25,
    "Car Insurance": 26,
    "Property Tax": 27,
    "Fuel / Maintenance": 28,
    "Home Insurance": 29,
    "Car Loan Payment": 30,
    "Housing Management Fee": 31,
    "Term Deposit": 32,
    "Pocket Money": 33,
    "Savings": 34,
}

# Return windows in days. Unknown stores stay None.
RETURN_WINDOWS = {
    "sport chek": 30,
    "costco": 90,
    "home depot": 90,
    "walmart": 90,
    "canadian tire": 90,
}


def col_letter(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def day_amount_col(day: int) -> str:
    """Amount column for day 1..31. Day 1 is K, day 31 is BS."""
    if not 1 <= day <= 31:
        raise ValueError(day)
    return col_letter(11 + 2 * (day - 1))


def day_item_col(day: int) -> str:
    return col_letter(10 + 2 * (day - 1))


def month_name(month: int) -> str:
    return MONTH_ABBR[month - 1]


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_amount(token: str) -> Optional[float]:
    raw = token.strip().replace("$", "").replace(",", "")
    neg = False
    if raw.startswith("(") and raw.endswith(")"):
        neg = True
        raw = raw[1:-1]
    if raw.endswith("-") and raw[:-1].replace(".", "", 1).isdigit():
        neg = True
        raw = raw[:-1]
    if not re.fullmatch(r"-?\d+\.\d{2}", raw):
        return None
    value = float(raw)
    if neg and value > 0:
        value = -value
    return value


def format_amount(value: float) -> str:
    return f"{value:.2f}"


def strip_markers(text: str) -> str:
    text = text.replace("\u00dd", " ").replace("\u00fd", " ")
    for mark in MARKERS:
        text = text.replace(mark, " ")
    # A lone leading marker sometimes survives as the letter Y before the merchant.
    text = re.sub(r"(^|\s)[ÝY](?=\s+[A-Z])", " ", text)
    return text


def normalize_description(text: str) -> str:
    """Stored description and key text. Keeps '&' (T&T stays T&T)."""
    text = strip_markers(text)
    text = text.upper()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def match_fold(text: str) -> str:
    """Matching form only. '&' folds to AND. Do not write this into a cell."""
    text = normalize_description(text).replace("&", " AND ")
    return re.sub(r"\s+", " ", text).strip()


def grid_day(line: "StatementLine") -> date:
    """Day column in the post-date year's book.

    Same year: the purchase date, so an Aug 28 purchase that posts Aug 31
    stays on August 28. A year change uses the post date, because that day
    is the one that exists in the post-date year's book.
    """
    if line.trans_date.year == line.post_date.year:
        return line.trans_date
    return line.post_date


def transaction_key(last4: str, post: date, amount: float, description: str, occurrence: int) -> str:
    return "|".join([
        str(last4),
        post.isoformat(),
        format_amount(amount),
        normalize_description(description),
        str(occurrence),
    ])


def short_merchant(name: str) -> str:
    """The name used in the Store column and in file names."""
    text = match_fold(name).lower()
    text = re.sub(r"#\d+", " ", text)
    text = text.replace("*", " ")
    text = re.sub(r"\b(no\.?|store)\s*\d+\b", " ", text)
    text = re.sub(r"\.(com|ca|co\.uk|net|org)\b", " ", text)
    for word in ("wholesale", "online"):
        text = re.sub(rf"\b{word}\b", " ", text)
    text = re.sub(r"\bthe\b", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # Drop a trailing city/province-ish tail by keeping the brand words
    # only when a known brand is present. Otherwise keep the first 3 words.
    brands = (
        "costco", "shell", "petro canada", "esso", "tim hortons", "mcdonalds",
        "sport chek", "home depot", "netflix", "walmart", "whole foods",
        "canadian tire", "subway", "starbucks", "t and t",
    )
    for brand in brands:
        if brand in text:
            pretty = {
                "costco": "Costco",
                "shell": "Shell",
                "petro canada": "Petro-Canada",
                "esso": "Esso",
                "tim hortons": "Tim Hortons",
                "mcdonalds": "McDonalds",
                "sport chek": "Sport Chek",
                "home depot": "Home Depot",
                "netflix": "Netflix",
                "walmart": "Walmart",
                "whole foods": "Whole Foods",
                "canadian tire": "Canadian Tire",
                "subway": "Subway",
                "starbucks": "Starbucks",
                "t and t": "T&T",
            }[brand]
            return pretty
    words = [w for w in text.split() if w not in PROVINCES and not w.isdigit()]
    if not words:
        return name.strip() or "Store"
    kept = words[:3]
    return " ".join(w.capitalize() for w in kept)


PROVINCES = {
    "on", "qc", "bc", "ab", "mb", "sk", "ns", "nb", "pe", "nl", "yt", "nt", "nu",
    "tx", "ny", "ca", "fl", "wa", "or", "me",
}


def merchant_match(a: str, b: str) -> str:
    """Return 'full', 'partial', or '' using the v1.2.4 name rules."""
    def norm(value: str) -> str:
        text = strip_markers(value).lower().replace("&", " and ")
        text = re.sub(r"#\d+", " ", text)
        text = text.replace("*", " ")
        text = re.sub(r"\b(no\.?|store)\s*\d+\b", " ", text)
        text = re.sub(r"\.(com|ca|co\.uk|net|org)\b", " ", text)
        text = re.sub(r"\b(wholesale|online)\b", " ", text)
        text = re.sub(r"^\s*the\s+", " ", text)
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    na, nb = norm(a), norm(b)
    if not na or not nb:
        return ""
    if na in nb or nb in na:
        return "full"
    wa, wb = na.split(), nb.split()
    shorter, longer = (wa, wb) if len(wa) <= len(wb) else (wb, wa)
    if shorter and all(word in longer for word in shorter):
        return "full"
    if any(len(word) >= 4 and word in nb.split() and word in na.split() for word in na.split()):
        return "partial"
    # within 2 single-character edits
    if abs(len(na) - len(nb)) <= 2 and _edits(na, nb) <= 2:
        return "partial"
    return ""


def _edits(a: str, b: str) -> int:
    if abs(len(a) - len(b)) > 2:
        return 99
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(
                cur[-1] + 1,
                prev[j] + 1,
                prev[j - 1] + (ca != cb),
            ))
        prev = cur
    return prev[-1]


def _parse_human_date(text: str) -> Optional[date]:
    text = text.strip().replace(",", "")
    for fmt in ("%B %d %Y", "%b %d %Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _find_period(text: str) -> tuple[Optional[date], Optional[date], Optional[date]]:
    statement_date = None
    for pattern in (
        r"Statement\s+date:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"Statement\s+Date\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
    ):
        match = re.search(pattern, text, re.I)
        if match:
            statement_date = _parse_human_date(match.group(1))
            break
    period = re.search(
        r"(?:For the period:|statement period|Statement\s+Period)\s*"
        r"([A-Za-z]+\s+\d{1,2},?\s+\d{4})\s*(?:to|–|-)\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        text, re.I,
    )
    if not period:
        period = re.search(
            r"([A-Za-z]+\s+\d{1,2},?\s+\d{4})\s+to\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            text, re.I,
        )
    if not period:
        period = re.search(
            r"([A-Za-z]+\s+\d{1,2})\s+to\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            text, re.I,
        )
        if period and statement_date:
            start = _parse_human_date(period.group(1) + f" {statement_date.year}")
            end = _parse_human_date(period.group(2))
            if start and end and start > end:
                start = _parse_human_date(period.group(1) + f" {statement_date.year - 1}")
            return start, end, statement_date
    if period:
        return _parse_human_date(period.group(1)), _parse_human_date(period.group(2)), statement_date
    return None, None, statement_date


def _find_due(text: str) -> Optional[date]:
    patterns = (
        r"Payment\s+due\s+date\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"(?:due by|pay this amount by|Minimum Payment due by)\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"due\s+date\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            found = _parse_human_date(match.group(1))
            if found:
                return found
    return None


def _find_money(text: str, labels: tuple[str, ...]) -> Optional[float]:
    for label in labels:
        match = re.search(label + r"\s*\$?\s*([\d,]+\.\d{2})", text, re.I)
        if match:
            return parse_amount(match.group(1))
    return None


def detect_product(text: str) -> tuple[str, str]:
    low = text.lower()
    if "costco" in low and "mastercard" in low:
        return "CIBC", "Costco MC"
    if "dividend" in low and "visa" in low:
        return "CIBC", "Visa"
    if "triangle" in low and "mastercard" in low:
        return "Triangle", "MC"
    if "rogers" in low and ("mastercard" in low or "rogers bank" in low):
        return "Rogers", "MC"
    if "visa" in low and "cibc" in low:
        return "CIBC", "Visa"
    if "mastercard" in low and "cibc" in low:
        return "CIBC", "MC"
    return "Card", "Card"


def card_label(issuer: str, product: str, last4: str) -> str:
    return f"{issuer} {product}-{last4}"


def statement_identity(statement: "Statement") -> str:
    """Statement id is `{Issuer Product}-{first card last4}-{statement date}`."""
    if statement.primary_last4:
        label = card_label(statement.issuer, statement.product, statement.primary_last4)
    else:
        label = f"{statement.issuer} {statement.product}".strip()
    return f"{label}-{statement.statement_date.isoformat()}"


def statement_fingerprint(statement: "Statement") -> str:
    parts = [
        statement_identity(statement),
        "" if statement.amount_due is None else format_amount(statement.amount_due),
    ]
    parts.extend(line.key for line in statement.lines)
    for payment in statement.payments:
        parts.append("|".join([
            normalize_description(payment.description),
            format_amount(payment.amount),
            payment.post_date.isoformat(),
            payment.last4,
        ]))
    return sha256_hex("\n".join(parts).encode())


_CELL_REF = re.compile(r"(?:(?:'[^']+'|[A-Za-z]{3,})!)?[A-Z]{1,3}\d+")


def qualify_where(where: str, sheet: str) -> str:
    """Copied cells written name the sheet, for example Sep!AW6+Sep!AW22."""
    if not where or not sheet:
        return where or ""

    def repl(match: re.Match) -> str:
        token = match.group(0)
        if "!" in token:
            return token
        return f"{sheet}!{token}"

    return _CELL_REF.sub(repl, where)


def receipt_identity(merchant: str, number: str, when: Optional[date], total: Optional[float]) -> str:
    """Family-book receipt key: number at that store, or store, date, and total."""
    store = merchant or ""
    if number:
        return f"{store}|{number}"
    day = when.isoformat() if isinstance(when, date) else ""
    return f"{store}|{day}|{format_amount(total or 0)}"


def _name_beside_card(text: str, match: re.Match) -> str:
    """A holder is only a name printed on the same line, after that card's number."""
    line_end = text.find("\n", match.end())
    if line_end < 0:
        line_end = len(text)
    rest = text[match.end():line_end].strip()
    found = re.match(r"([A-Z][A-Za-z]+(?:[ \t]+[A-Z][A-Za-z]+){0,2})\s*$", rest)
    if not found:
        return ""
    return re.sub(r"\s+", " ", found.group(1)).strip()


def resolve_month_day(month: int, day: int, start: date, end: date) -> date:
    window_lo = start - timedelta(days=10)
    window_hi = end + timedelta(days=2)
    candidates = []
    for year in {start.year - 1, start.year, end.year, end.year + 1}:
        try:
            candidates.append(date(year, month, day))
        except ValueError:
            continue
    inside = [d for d in candidates if window_lo <= d <= window_hi]
    if not inside:
        raise ValueError(f"date {month}-{day} is outside {start}..{end}")
    in_period = [d for d in inside if start <= d <= end]
    if len(in_period) == 1:
        return in_period[0]
    return min(inside, key=lambda d: (0 if start <= d <= end else 1, abs((d - start).days)))


@dataclass
class StatementLine:
    trans_date: date
    post_date: date
    description: str
    amount: float
    last4: str
    issuer_category: str = ""
    fx_note: str = ""
    kind: str = "purchase"  # purchase | payment | return
    occurrence: int = 1
    key: str = ""


@dataclass
@dataclass
class StatementBill:
    statement_id: str
    issuer: str
    product: str
    last4s: str
    label: str
    statement_date: str
    due_date: str
    amount_due: Optional[float]
    remaining: Optional[float]
    paid_status: str
    file_name: str
    period_end: str = ""
    partial: bool = False


@dataclass
class CardOnStatement:
    last4: str
    holder: str = ""
    printed_total: Optional[float] = None


@dataclass
class Statement:
    issuer: str
    product: str
    statement_date: date
    period_start: date
    period_end: date
    due_date: Optional[date]
    minimum: Optional[float]
    amount_due: Optional[float]
    holder: str
    cards: list[CardOnStatement]
    lines: list[StatementLine]
    payments: list[StatementLine]
    partial: bool = False
    source_name: str = ""
    raw_kind: str = "text"

    @property
    def primary_last4(self) -> str:
        return self.cards[0].last4 if self.cards else ""

    def folder(self, ext: str) -> str:
        label = f"{self.issuer} {self.product}-{self.primary_last4}"
        year = self.statement_date.year
        return (
            f"Family Book - {year}/statements/{label}/"
            f"{self.statement_date.isoformat()} statement{ext}"
        )


def _is_wordstack(text: str) -> bool:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) < 20:
        return False
    short = sum(1 for ln in lines if " " not in ln)
    return short / len(lines) > 0.55


def _tokens(text: str) -> list[str]:
    if _is_wordstack(text):
        raw = [ln.strip() for ln in text.splitlines() if ln.strip()]
    else:
        raw = text.split()
    cleaned = []
    for token in raw:
        token = token.strip().strip(",").strip("Ý").strip("\u00dd")
        if token:
            cleaned.append(token)
    return cleaned


def _peel_category(words: list[str]) -> tuple[list[str], str]:
    if not words:
        return words, ""
    joined = " ".join(words)
    for category in ISSUER_CATEGORIES:
        if joined.lower().endswith(category.lower()):
            keep = len(category.split())
            return words[:-keep], category
    return words, ""


def _assign_occurrences(lines: list[StatementLine]) -> None:
    groups: dict[tuple, list[StatementLine]] = {}
    for line in lines:
        ident = (
            line.last4,
            line.post_date,
            format_amount(line.amount),
            normalize_description(line.description),
        )
        groups.setdefault(ident, []).append(line)
    for group in groups.values():
        for index, line in enumerate(group, 1):
            line.occurrence = index
            line.key = transaction_key(
                line.last4, line.post_date, line.amount, line.description, index
            )


def parse_csv_statement(text: str, source_name: str = "") -> Statement:
    meta = {}
    rows = []
    header = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            if ":" in line:
                key, value = line[1:].split(":", 1)
                meta[key.strip().lower()] = value.strip()
            continue
        parts = [p.strip() for p in line.split(",")]
        if header is None:
            header = [p.lower() for p in parts]
            continue
        rows.append(dict(zip(header, parts)))
    if "trans_date" not in (header or []):
        raise ValueError("CSV needs a trans_date header")
    issuer = meta.get("issuer", "CIBC")
    product = meta.get("product", "Visa")
    statement_date = date.fromisoformat(meta["statement_date"]) if meta.get("statement_date") else date.fromisoformat(rows[-1]["post_date"])
    period_start = date.fromisoformat(meta.get("period_start", rows[0]["post_date"]))
    period_end = date.fromisoformat(meta.get("period_end", rows[-1]["post_date"]))
    due = date.fromisoformat(meta["due_date"]) if meta.get("due_date") else None
    minimum = float(meta["minimum"]) if meta.get("minimum") else None
    amount_due = float(meta["amount_due"]) if meta.get("amount_due") else None
    holder = meta.get("holder", "")
    partial = meta.get("partial", "").lower() in {"1", "true", "yes"}
    cards: dict[str, CardOnStatement] = {}
    for piece in meta.get("cards", "").split(";"):
        piece = piece.strip()
        if not piece:
            continue
        # "1001:453.69" or "1001"
        if ":" in piece:
            last4, total = piece.split(":", 1)
            cards[last4] = CardOnStatement(last4, printed_total=float(total))
        else:
            cards[piece] = CardOnStatement(piece)
    lines: list[StatementLine] = []
    payments: list[StatementLine] = []
    for row in rows:
        last4 = row.get("last4") or meta.get("last4") or ""
        if last4 and last4 not in cards:
            cards[last4] = CardOnStatement(last4)
        amount = float(row["amount"])
        desc = row["description"]
        kind = "payment" if PAYMENT_RE.search(desc) or row.get("kind", "").lower() == "payment" else (
            "return" if amount < 0 else "purchase"
        )
        line = StatementLine(
            trans_date=date.fromisoformat(row["trans_date"]),
            post_date=date.fromisoformat(row["post_date"]),
            description=desc,
            amount=amount,
            last4=last4,
            issuer_category=row.get("spend_category", ""),
            fx_note=row.get("fx", ""),
            kind=kind,
        )
        (payments if kind == "payment" else lines).append(line)
    _assign_occurrences(lines)
    _assign_occurrences(payments)
    if not cards and lines:
        cards[lines[0].last4] = CardOnStatement(lines[0].last4)
    return Statement(
        issuer=issuer, product=product, statement_date=statement_date,
        period_start=period_start, period_end=period_end, due_date=due,
        minimum=minimum, amount_due=amount_due, holder=holder,
        cards=list(cards.values()), lines=lines, payments=payments,
        partial=partial, source_name=source_name, raw_kind="csv",
    )


def parse_statement(text: str, source_name: str = "") -> Statement:
    sample = text.lstrip()
    if sample.startswith("#") or ("," in sample.splitlines()[0] and "trans_date" in sample.splitlines()[0].lower()):
        return parse_csv_statement(text, source_name)
    if "<html" in sample.lower() or "<table" in sample.lower():
        text = re.sub(r"(?i)<br\s*/?>", "\n", text)
        text = re.sub(r"(?i)</tr>", "\n", text)
        text = re.sub(r"(?i)</t[dh]>", " ", text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = text.replace("&nbsp;", " ")
    return _parse_prose(text, source_name)


def _parse_prose(text: str, source_name: str) -> Statement:
    # Drop the Sport Chek (or any) detail block whose lines are already in Purchases.
    detail = re.search(
        r"Details of your .+?store purchases.*?(?=WAYS TO PAY|Page \d+ of \d+\s*$|\Z)",
        text, re.I | re.S,
    )
    scan_text = text
    if detail and re.search(r"included in the Purchases section", text, re.I):
        scan_text = text[:detail.start()] + "\n" + text[detail.end():]

    period_start, period_end, statement_date = _find_period(text)
    if not (period_start and period_end and statement_date):
        raise ValueError(f"missing statement metadata in {source_name}")
    issuer, product = detect_product(text)
    due = _find_due(text)
    minimum = _find_money(text, (r"Minimum\s+payment(?:\s+due)?",))
    amount_due = _find_money(text, (r"Amount\s+Due", r"Balance\s+Due", r"New\s+Balance"))
    holder = ""
    holder_match = re.search(
        r"(?:Prepared for|Account holder):[ \t]*([A-Z][A-Za-z]+(?:[ \t]+[A-Z][A-Za-z]+){0,2})",
        text,
    )
    if holder_match:
        holder = holder_match.group(1).strip()
    partial = bool(re.search(r"partial\s+export", text, re.I))

    # Card headers in order of appearance, with a printed per-card total when present.
    cards: list[CardOnStatement] = []
    seen = []
    for match in CARD_HEADER_RE.finditer(scan_text):
        last4 = match.group(1)
        if last4 not in seen:
            seen.append(last4)
            cards.append(CardOnStatement(last4=last4, holder=_name_beside_card(scan_text, match)))
    for match in re.finditer(
        r"Total\s+for\s+(?:card\s+)?(?:\d{4}\s+)?(?:XXXX\s+){0,3}(\d{4})\s+\$?\s*([\d,]+\.\d{2})",
        scan_text, re.I,
    ):
        last4, total = match.group(1), parse_amount(match.group(2))
        for card in cards:
            if card.last4 == last4:
                card.printed_total = total
        if last4 not in seen:
            seen.append(last4)
            cards.append(CardOnStatement(last4=last4, printed_total=total))
    if not cards:
        loose = LAST4_RE.search(text)
        if loose:
            cards.append(CardOnStatement(last4=loose.group(1)))

    tokens = _tokens(scan_text)
    # Positions of card headers in the token stream.
    card_at: list[tuple[int, str]] = []
    for index in range(len(tokens) - 3):
        window = " ".join(tokens[index:index + 8])
        found = CARD_HEADER_RE.search(window)
        if found and tokens[index].lower() in {"card", "purchases", "account"}:
            card_at.append((index, found.group(1)))

    def card_for(token_index: int) -> str:
        last4 = cards[0].last4 if cards else ""
        for pos, value in card_at:
            if pos <= token_index:
                last4 = value
            else:
                break
        return last4

    lines: list[StatementLine] = []
    payments: list[StatementLine] = []
    index = 0
    while index < len(tokens) - 1:
        month = MONTHS.get(tokens[index].lower().rstrip("."))
        if month and re.fullmatch(r"\d{1,2}", tokens[index + 1]):
            if index + 3 < len(tokens):
                month2 = MONTHS.get(tokens[index + 2].lower().rstrip("."))
                if month2 and re.fullmatch(r"\d{1,2}", tokens[index + 3]):
                    trans = resolve_month_day(month, int(tokens[index + 1]), period_start, period_end)
                    post = resolve_month_day(month2, int(tokens[index + 3]), period_start, period_end)
                    cursor = index + 4
                    words: list[str] = []
                    fx_note = ""
                    amount = None
                    while cursor < len(tokens):
                        tok = tokens[cursor]
                        if MONTHS.get(tok.lower().rstrip(".")) and cursor + 1 < len(tokens) and re.fullmatch(r"\d{1,2}", tokens[cursor + 1]):
                            break
                        if tok.lower() in {"total", "page", "purchases"} and cursor != index + 4:
                            # 'Total for' or a new section. Stop if we already have words.
                            if words or amount is not None:
                                break
                        if tok.upper() == "FOREIGN" and cursor + 1 < len(tokens) and tokens[cursor + 1].upper() == "CURRENCY":
                            fx_tokens = []
                            cursor += 2
                            while cursor < len(tokens) and len(fx_tokens) < 6:
                                fx_tokens.append(tokens[cursor])
                                cursor += 1
                                if "@" in fx_tokens and re.fullmatch(r"\d+\.\d+", fx_tokens[-1]):
                                    break
                            fx_note = "FOREIGN CURRENCY " + " ".join(fx_tokens)
                            fx_note = re.sub(r"\s*@\s*", " @ ", fx_note)
                            fx_note = re.sub(r"\s+", " ", fx_note).strip()
                            continue
                        parsed = parse_amount(tok)
                        if parsed is not None and not (tok.startswith("20") and len(tok) > 8):
                            amount = parsed
                            cursor += 1
                            break
                        words.append(tok.strip("Ý").strip("\u00dd"))
                        cursor += 1
                    words, issuer_category = _peel_category(words)
                    description = normalize_description(" ".join(words))
                    if description and amount is not None:
                        kind = "payment" if PAYMENT_RE.search(description) else ("return" if amount < 0 else "purchase")
                        line = StatementLine(
                            trans_date=trans,
                            post_date=post,
                            description=description,
                            amount=amount,
                            last4=card_for(index),
                            issuer_category=issuer_category,
                            fx_note=fx_note,
                            kind=kind,
                        )
                        (payments if kind == "payment" else lines).append(line)
                    index = cursor
                    continue
        index += 1

    _assign_occurrences(lines)
    _assign_occurrences(payments)
    # "Prepared for" is the account line. It does not fill a card holder.
    return Statement(
        issuer=issuer, product=product, statement_date=statement_date,
        period_start=period_start, period_end=period_end, due_date=due,
        minimum=minimum, amount_due=amount_due, holder=holder,
        cards=cards, lines=lines, payments=payments, partial=partial,
        source_name=source_name, raw_kind="text",
    )


def verify_card_totals(statement: Statement) -> list[str]:
    """Return a list of problems. Empty means the lines match the printed totals."""
    if statement.partial:
        return []
    problems = []
    by_card: dict[str, float] = {}
    for line in statement.lines:
        by_card[line.last4] = round(by_card.get(line.last4, 0.0) + line.amount, 2)
    printed = [card for card in statement.cards if card.printed_total is not None]
    if not printed:
        problems.append("statement has no per-card total to check")
        return problems
    for card in printed:
        got = round(by_card.get(card.last4, 0.0), 2)
        if abs(got - card.printed_total) > 0.001:
            problems.append(
                f"card {card.last4} lines sum to {got:.2f}, statement says {card.printed_total:.2f}"
            )
    return problems


# --- categories -----------------------------------------------------------

MERCHANT_PATTERNS: list[tuple[str, str]] = [
    (r"ANNUAL RENEWAL", "Other"),
    (r"ANNUAL FEE|INTEREST CHARGE|CASH ADVANCE FEE", "Bank fees"),
    (r"SHELL|PETRO[\s-]*CANADA|ESSO|GASBAR|GAS BAR", "Fuel"),
    (r"TIM HORTONS|TIMS\b|STARBUCKS", "Snacks"),
    (r"MCDONALDS|A AND W|SUBWAY|WENDY", "Dining Out"),
    (r"NETFLIX|SPOTIFY|DISNEY\+|CINEPLEX", "Entertainment"),
    (r"PROPERTY TAX|\b[A-Z .'-]*TAX\b", "Property Tax"),
    (r"SPORT CHEK|OLD NAVY|GAP\b|WINNERS", "Clothing"),
    (r"HOME DEPOT|CANADIAN TIRE(?! GAS)|RONA\b|IKEA", "Household Goods"),
    (r"SHOPPERS|PHARMACY|DENTAL|\bDR\b", "Medical"),
    (r"COSTCO|WALMART|T AND T|WHOLE FOODS|SUPERMARKET|FOODMART|LOBLAW|SUPERSTORE|NO FRILLS|GROCERY", "Snacks"),
    (r"PRESTO|UBER|LYFT|PARKING|TTC\b", "Transportation"),
    (r"MORTGAGE", "Rent / Mortgage"),
    (r"HYDRO|ENBRIDGE|ELECTRIC", "Electricity & Water"),
    (r"COGECO|BELL (?:INTERNET|CANADA)|ROGERS (?:INTERNET|COMMUNICATIONS)", "Internet"),
    (r"PAYROLL|PAY FROM", "Income"),
]


def _pattern_category(description: str) -> Optional[str]:
    text = match_fold(description)
    for pattern, category in MERCHANT_PATTERNS:
        if re.search(pattern, text, re.I):
            return category
    return None


ISSUER_TO_BOOK = {
    "Transportation": "Transportation",
    "Restaurants": "Dining Out",
    "Retail and Grocery": "Snacks",
    "Personal and Household Expenses": "Household Goods",
    "Hotel, Entertainment and Recreation": "Entertainment",
    "Health and Education": "Medical",
    "Professional and Financial Services": "Bank fees",
    "Home and Office Improvement": "Household Goods",
    "Other Transactions": "Other",
}


@dataclass
class CategoryDecision:
    category: str
    ask: bool
    reason: str


def categorize_transaction(description: str, amount: float, issuer_category: str,
                           learned: dict[str, str], threshold: float = BIG_CHARGE) -> CategoryDecision:
    learned_hit = _learned_lookup(description, learned)
    if learned_hit:
        return CategoryDecision(learned_hit, False, "learned map")
    patterned = _pattern_category(description)
    if patterned:
        return CategoryDecision(patterned, False, "merchant pattern")
    if issuer_category and issuer_category in ISSUER_TO_BOOK:
        return CategoryDecision(ISSUER_TO_BOOK[issuer_category], False, "issuer category")
    if abs(amount) >= threshold:
        return CategoryDecision("", True, "unknown big charge")
    return CategoryDecision("Other", False, "unknown small charge")


def _learned_lookup(description: str, learned: dict[str, str]) -> Optional[str]:
    text = match_fold(description).lower()
    best = None
    for pattern, category in learned.items():
        if pattern and pattern in text and (best is None or len(pattern) > len(best[0])):
            best = (pattern, category)
    return best[1] if best else None


def learn_pattern(description: str) -> str:
    """Leading merchant words. A known brand drops the city: Costco Burlington is costco."""
    folded = match_fold(description).lower()
    for needle, key in (
        ("costco", "costco"),
        ("t and t", "t&t"),
        ("home depot", "home depot"),
        ("sport chek", "sport chek"),
        ("tim hortons", "tim hortons"),
        ("canadian tire", "canadian tire"),
    ):
        if needle in folded:
            return key
    text = folded
    words = []
    stopped_at_province = False
    for word in text.split():
        if word in PROVINCES:
            stopped_at_province = True
            break
        if word.isdigit() or re.fullmatch(r"#?\d+", word) or re.fullmatch(r"[a-z]?\d{3,}", word):
            break
        words.append(word)
        if len(words) == 4:
            break
    if stopped_at_province and len(words) >= 2:
        words = words[:-1]
    return " ".join(words[:3])


ITEM_PATTERNS: list[tuple[str, str]] = [
    (r"tip|gratuity", "Dining Out"),
    (r"egg|milk|bread|chicken|beef|pork|fish|salmon|tuna|shrimp|seafood|vegetable|spinach|lettuce|tomato|onion|carrot|broccoli|potato|cucumber|cabbage|kale|produce|banana|apple|meat|grocery", "Meals"),
    (r"chip|candy|snack|cookie|coffee|pop\b|soda", "Snacks"),
    (r"drywall|drop cloth|screw|paper|towel|detergent|cleaner|soap|battery|bulb|tool|paint|brush|hardware", "Household Goods"),
    (r"jacket|shirt|shoe|adidas|clothing|sock", "Clothing"),
    (r"regular\s+\d|\d+(?:\.\d+)?\s*l\b|gas|fuel|unleaded", "Fuel"),
    (r"pharmacy|vitamin|prescription", "Medical"),
    (r"ticket|movie|netflix", "Entertainment"),
]


def categorize_item(name: str) -> str:
    text = name.lower()
    for pattern, category in ITEM_PATTERNS:
        if re.search(pattern, text, re.I):
            return category
    return "Other"


def spread_to_total(items: list[tuple[str, float]], total: float) -> list[tuple[str, float, str]]:
    """Items are (name, price). Scale so category amounts sum to the receipt total."""
    base = [(name, price, categorize_item(name)) for name, price in items]
    raw = round(sum(price for _, price, _ in base), 2)
    if raw == 0:
        return [(name, 0.0, cat) for name, _, cat in base]
    if abs(raw - total) < 0.001:
        return [(name, round(price, 2), cat) for name, price, cat in base]
    scaled = []
    running = 0.0
    for index, (name, price, cat) in enumerate(base):
        if index == len(base) - 1:
            share = round(total - running, 2)
        else:
            share = round(total * (price / raw), 2)
            running = round(running + share, 2)
        scaled.append((name, share, cat))
    return scaled


# --- receipts -------------------------------------------------------------

@dataclass
class ReceiptItem:
    name: str
    price: float
    category: str
    sku: str = ""


@dataclass
class Receipt:
    store: str
    when: datetime
    total: float
    payment: str  # last4, "cash", or ""
    items: list[ReceiptItem]
    number: str = ""
    source: str = "photo"
    file_name: str = ""
    content_hash: str = ""
    sku_hint: str = ""

    @property
    def date(self) -> date:
        return self.when.date()


def parse_receipt(text: str, source: str = "photo", content: bytes = b"") -> Receipt:
    store = _field(text, "STORE") or _first_store_line(text)
    number = _field(text, "RECEIPT") or _search(text, r"Receipt\s*#?\s*([A-Za-z0-9-]+)")
    card = _field(text, "CARD") or _search(text, r"(?:VISA|MC|MASTERCARD|AMEX)?\s*\*+\s*(\d{4})")
    if re.search(r"\bcash\b", text, re.I) and not card:
        payment = "cash"
    else:
        payment = card or ""
    when = _receipt_when(text)
    total_text = _field(text, "TOTAL") or _search(text, r"\bTOTAL\b\s*\$?\s*([\d,]+\.\d{2})")
    if not total_text:
        raise ValueError("receipt has no total")
    total = parse_amount(total_text) if not re.fullmatch(r"-?\d+\.\d{2}", total_text) else float(total_text)
    items = []
    for match in re.finditer(r"^(.+?)\s+\|\s+(-?\d+\.\d{2})\s*(?:\|\s*(\S+))?\s*$", text, re.M):
        name, price, sku = match.group(1).strip(), float(match.group(2)), match.group(3) or ""
        if name.lower() in {"total", "subtotal", "tax", "gst", "hst"}:
            continue
        items.append(ReceiptItem(name, price, categorize_item(name), sku))
    if not items:
        for match in re.finditer(r"^([A-Za-z][A-Za-z0-9 &'./-]{2,}?)\s{2,}(-?\d+\.\d{2})\s*$", text, re.M):
            name = match.group(1).strip()
            if name.lower() in {"total", "subtotal", "tax"}:
                continue
            items.append(ReceiptItem(name, float(match.group(2)), categorize_item(name)))
    sku_hint = _field(text, "SKU") or ""
    scaled = spread_to_total([(it.name, it.price) for it in items], total) if items else []
    final_items = []
    for (name, price, cat), original in zip(scaled, items):
        final_items.append(ReceiptItem(name, price, cat, original.sku))
    file_name = receipt_filename(when, store, total, "txt")
    return Receipt(
        store=short_merchant(store or "Store"),
        when=when, total=total, payment=payment, items=final_items,
        number=(number or "").lstrip("#"), source=source, file_name=file_name,
        content_hash=sha256_hex(content or text.encode()), sku_hint=sku_hint,
    )


def _field(text: str, name: str) -> str:
    match = re.search(rf"^{name}:\s*(.+)$", text, re.M | re.I)
    return match.group(1).strip() if match else ""


def _search(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.I)
    return match.group(1).strip() if match else ""


def _first_store_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return "Store"


def _receipt_when(text: str) -> datetime:
    match = re.search(r"DATE:\s*(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}))?", text, re.I)
    if match:
        clock = match.group(2) or "00:00"
        return datetime.strptime(match.group(1) + " " + clock, "%Y-%m-%d %H:%M")
    match = re.search(
        r"([A-Za-z]+\s+\d{1,2},?\s+\d{4})(?:\s+(\d{1,2}:\d{2}))?", text
    )
    if match:
        day = _parse_human_date(match.group(1))
        clock = match.group(2) or "00:00"
        hour, minute = clock.split(":")
        return datetime(day.year, day.month, day.day, int(hour), int(minute))
    raise ValueError("receipt has no date")


def receipt_filename(when: datetime, store: str, total: float, ext: str) -> str:
    store_part = short_merchant(store)
    stamp = when.strftime("%Y-%m-%d %H%M") if (when.hour or when.minute) else when.strftime("%Y-%m-%d")
    total_part = format_amount(total)
    name = f"{stamp} - {store_part} - {total_part}.{ext.lstrip('.')}"
    return re.sub(r"[/\\:*?\"<>|]", "", name)


# --- book -----------------------------------------------------------------

@dataclass
class LogRow:
    status: str
    source: str
    merchant: str
    total: Optional[float]
    when: Optional[date]
    where: str = ""
    key: str = ""
    receipt_number: str = ""
    payment: str = ""
    files: list[str] = field(default_factory=list)
    hashes: list[str] = field(default_factory=list)
    card: str = ""
    post_date: str = ""
    fx_note: str = ""
    linked: str = ""
    section_row: str = ""
    items: str = ""
    plan: str = ""  # recorded replacement plan, for an idempotent retry
    category: str = ""
    month_sheet_amount_written: bool = False


@dataclass
class TxnRow:
    card: str
    trans_date: str
    post_date: str
    description: str
    amount: Optional[float]
    category: str
    receipt_number: str
    key: str
    statement_file: str
    fx_note: str
    status: str
    where: str
    sheet: str


@dataclass
class ReceiptRow:
    number: str
    store: str
    when: str
    total: float
    payment: str
    items: list[ReceiptItem]
    file_name: str
    status: str  # pending | matched | cash | question | superseded
    where: str
    linked_key: str
    sheet: str
    hashes: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    identity: str = ""


@dataclass
class CardRow:
    issuer: str
    product: str
    last4: str
    holder: str
    statement_day: int
    due_day: int
    last_amount_due: Optional[float]
    paid_status: str
    statement_date: str = ""
    period_end: str = ""
    due_date: str = ""
    minimum: Optional[float] = None
    statement_file: str = ""
    label: str = ""
    account_cards: str = ""
    credit: float = 0.0


class Book:
    def __init__(self, year: int = 2026, version: str = "v2.0"):
        self.year = year
        self.version = version
        self.grid: dict[tuple[str, str], float] = {}
        self.grid_label: dict[tuple[str, str], str] = {}
        self.fixed: dict[tuple[str, str], float] = {}  # (sheet, "C27") 
        self.fixed_date: dict[tuple[str, str], str] = {}
        self.income: dict[tuple[str, int], tuple[float, str]] = {}  # (sheet, row) -> amount, label
        self.log: list[LogRow] = []
        self.txns: list[TxnRow] = []
        self.receipts: list[ReceiptRow] = []
        self.cards: list[CardRow] = []
        self.merchant_map: dict[str, str] = {}
        self.statements_seen: list[str] = []
        self.questions: list[str] = []
        self.skipped_payments: list[str] = []
        self.events: list[str] = []
        self.pending_formula: dict[str, str] = {}  # D46 style notes
        self.pending_income: list[StatementLine] = []
        self.bills: list[StatementBill] = []
        self.saved_files: list[str] = []
        self.linked: dict[int, "Book"] = {}
        self.asked_years: set[int] = set()
        self.statement_hashes: dict[str, str] = {}
        self.applied_payments: set[str] = set()
        self._receipt_seq = 1
        self._crash_after_grid = False

    def cell(self, sheet: str, addr: str) -> Optional[float]:
        if addr.startswith("C") and addr[1:].isdigit() and int(addr[1:]) >= 18:
            return self.fixed.get((sheet, addr))
        if addr.startswith("C") and addr[1:].isdigit():
            row = int(addr[1:])
            found = self.income.get((sheet, row))
            if found is not None:
                return found[0]
        return self.grid.get((sheet, addr))

    def _sheet_month(self, sheet: str) -> int:
        return MONTH_ABBR.index(sheet) + 1

    def _next_receipt_number(self) -> str:
        number = f"R-{self._receipt_seq:04d}"
        self._receipt_seq += 1
        return number

    def find_log_by_key(self, key: str) -> Optional[LogRow]:
        for row in self.log:
            if row.key == key and row.status != "superseded":
                return row
        return None

    def book_for_year(self, year: int) -> Optional["Book"]:
        if year == self.year:
            return self
        other = self.linked.get(year)
        if other is not None:
            return other
        if year not in self.asked_years:
            self.asked_years.add(year)
            self.questions.append(f"The {year} book is not here yet. Should I create it?")
        return None

    def _place_file(self, path: str, refused: bool = False, reuse: bool = False) -> str:
        stem, ext = os.path.splitext(path)
        if refused:
            stem = f"{stem} - not imported"
        if reuse and not refused and path in self.saved_files:
            return path
        candidate = stem + ext
        number = 2
        while candidate in self.saved_files:
            candidate = f"{stem} - {number}{ext}"
            number += 1
        self.saved_files.append(candidate)
        return candidate

    def import_statement(self, statement: Statement, file_name: str, crash_on_key: str = "") -> dict:
        problems = verify_card_totals(statement)
        statement_id = statement_identity(statement)
        home = self.book_for_year(statement.statement_date.year)
        if home is None:
            return {"wrote": 0, "skipped": 0, "refused": False, "problems": problems, "asked_year": statement.statement_date.year}
        digest = statement_fingerprint(statement)
        prior = home.statement_hashes.get(statement_id)
        resume = False
        if prior is not None and not problems:
            if prior == digest:
                resume = any(row.status == "pending" and row.key and not row.key.startswith("file|") for row in home.log)
                if not resume:
                    saved = next((path for path in home.saved_files if path == file_name or path.endswith(file_name.split("/")[-1])), file_name)
                    return {"wrote": 0, "skipped": 0, "refused": False, "problems": [], "saved": saved}
            else:
                home.questions.append(
                    f"Statement {statement_id} is already saved and this file is different. Which one should I keep?"
                )
                return {"wrote": 0, "skipped": 0, "refused": False, "problems": [], "asked": True}
        if resume:
            saved = file_name if file_name in home.saved_files else next(
                (path for path in reversed(home.saved_files) if "not imported" not in path),
                file_name,
            )
        else:
            saved = home._place_file(file_name, refused=bool(problems), reuse=statement_id in home.statements_seen)
        if problems:
            reason = "; ".join(problems)
            home.events.append("refused write: " + reason)
            home.log.append(LogRow(
                status="refused", source=reason, merchant=statement.issuer,
                total=statement.amount_due, when=statement.statement_date,
                files=[saved], hashes=[digest],
            ))
            return {"wrote": 0, "skipped": 0, "refused": True, "problems": problems, "saved": saved}
        if not resume:
            home.statement_hashes[statement_id] = digest
            home.log.append(LogRow(
                status="done", source="statement", merchant=statement.issuer,
                total=statement.amount_due, when=statement.statement_date,
                files=[saved], hashes=[digest], key=f"file|{digest}",
            ))
        wrote = 0
        skipped = 0
        home._record_bill(statement, saved, statement_id)
        home._upsert_cards(statement, saved, statement_id)
        for payment in statement.payments:
            if home._write_card_payment(payment, statement, saved):
                names = [payment.last4] if payment.last4 else [card.last4 for card in statement.cards]
                home._apply_payment(payment, names)
        touched = {home}
        for line in statement.lines:
            target = self.book_for_year(line.post_date.year)
            if target is None:
                skipped += 1
                continue
            touched.add(target)
            existing = target.find_log_by_key(line.key)
            if existing and existing.status not in {"pending", "writing"}:
                skipped += 1
                continue
            if existing and existing.status == "pending" and existing.month_sheet_amount_written:
                # Interrupted write: finish the row, do not add the amount again.
                target._finish_pending(existing, line, statement, saved)
                skipped += 1
                continue
            decision = categorize_transaction(
                line.description, line.amount, line.issuer_category, self.merchant_map
            )
            if decision.ask:
                target._open_question(line, statement, saved, decision.reason)
                wrote += 1
                continue
            linked = target._link_existing_receipt(line, decision.category)
            if linked is None and target is not self:
                linked = self._link_existing_receipt(line, decision.category)
            if linked:
                for existing_log in list(target.log) + list(self.log):
                    if existing_log.receipt_number == linked.number and existing_log.status != "superseded":
                        existing_log.key = line.key
                        existing_log.post_date = line.post_date.isoformat()
                        existing_log.card = card_label(statement.issuer, statement.product, line.last4)
                        existing_log.fx_note = line.fx_note
                        existing_log.category = decision.category
                        break
                target._write_txn(line, statement, saved, decision.category, "matched", linked, where=linked.where)
                wrote += 1
                continue
            target._write_new_transaction(line, statement, saved, decision, crash_on_key=crash_on_key)
            wrote += 1
            if crash_on_key and line.key == crash_on_key:
                target.events.append("crashed after grid write")
                break
        if statement_id not in home.statements_seen:
            home.statements_seen.append(statement_id)
        for book in touched:
            book._link_returns()
        return {"wrote": wrote, "skipped": skipped, "refused": False, "problems": [], "saved": saved}

    def _record_bill(self, statement: Statement, file_name: str, statement_id: str) -> None:
        # A partial or mid-month export is not a bill. Only a statement with an amount due is.
        if statement.partial or statement.amount_due is None:
            return
        existing = next((bill for bill in self.bills if bill.statement_id == statement_id), None)
        if existing is not None:
            return
        last4s = ",".join(card.last4 for card in statement.cards) or statement.primary_last4
        label = card_label(statement.issuer, statement.product, statement.primary_last4) if statement.primary_last4 else statement.issuer
        amount = statement.amount_due
        self.bills.append(StatementBill(
            statement_id=statement_id, issuer=statement.issuer, product=statement.product,
            last4s=last4s, label=label,
            statement_date=statement.statement_date.isoformat(),
            due_date=statement.due_date.isoformat() if statement.due_date else "",
            amount_due=amount, remaining=amount, paid_status="unpaid",
            file_name=file_name, period_end=statement.period_end.isoformat(),
            partial=statement.partial,
        ))

    def _apply_payment(self, payment: StatementLine, last4s: list[str]) -> None:
        """Pay the latest unpaid bill for that card dated on or before the payment.

        Paying that bill in full also marks every older unpaid bill for the card
        paid, because the balance carries forward. A partial payment reduces only
        the latest bill. Any overpayment is a credit on Cards. Remaining never
        goes negative. A payment with no eligible bill changes nothing.
        """
        if not payment.key:
            payment.key = transaction_key(
                payment.last4 or (last4s[0] if last4s else ""),
                payment.post_date, payment.amount, payment.description, payment.occurrence or 1,
            )
        if payment.key in self.applied_payments:
            return
        self.applied_payments.add(payment.key)
        self.skipped_payments.append(normalize_description(payment.description))
        names = [n for n in last4s if n]
        candidates = []
        for bill in self.bills:
            if bill.paid_status == "paid" or not bill.statement_date:
                continue
            if date.fromisoformat(bill.statement_date) > payment.post_date:
                continue
            bill_cards = [part for part in bill.last4s.split(",") if part]
            if names and bill_cards and not any(n in bill_cards for n in names):
                continue
            candidates.append(bill)
        if not candidates:
            return
        bill = max(candidates, key=lambda item: item.statement_date)
        if bill.remaining is None:
            return
        pay = abs(payment.amount)
        leftover = round(bill.remaining - pay, 2)
        if leftover > 0.001:
            bill.remaining = leftover
        else:
            over = round(pay - bill.remaining, 2)
            bill.remaining = 0.0
            bill.paid_status = "paid"
            for older in candidates:
                if older is bill or older.statement_date >= bill.statement_date:
                    continue
                older.remaining = 0.0
                older.paid_status = "paid"
            if over > 0.001:
                self._note_credit(names or bill.last4s.split(","), over)
        self._sync_cards_from_bills()

    def _note_credit(self, last4s: list[str], amount: float) -> None:
        names = {part.strip() for part in last4s if part and part.strip()}
        noted = False
        for card in self.cards:
            if card.last4 in names or any(part.strip() in names for part in card.account_cards.split(",")):
                card.credit = round(card.credit + amount, 2)
                noted = True
                break
        if not noted:
            return

    def _write_card_payment(self, payment: StatementLine, statement: Statement, file_name: str) -> bool:
        """A card payment is a Transactions row. It is not a grid expense."""
        if not payment.key:
            payment.key = transaction_key(
                payment.last4 or statement.primary_last4,
                payment.post_date, payment.amount, payment.description, payment.occurrence or 1,
            )
        if any(txn.key == payment.key for txn in self.txns):
            return False
        label = card_label(statement.issuer, statement.product, payment.last4 or statement.primary_last4)
        self.txns.append(TxnRow(
            card=label, trans_date=payment.trans_date.isoformat(), post_date=payment.post_date.isoformat(),
            description=normalize_description(payment.description), amount=payment.amount,
            category="Card payment", receipt_number="", key=payment.key, statement_file=file_name,
            fx_note="", status="no receipt", where="", sheet=month_name(payment.post_date.month),
        ))
        self.log.append(LogRow(
            status="no receipt", source="statement", merchant=short_merchant(payment.description),
            total=payment.amount, when=payment.trans_date, key=payment.key, payment=payment.last4,
            card=label, post_date=payment.post_date.isoformat(), category="Card payment",
        ))
        return True

    def _sync_cards_from_bills(self) -> None:
        for card in self.cards:
            mine = [bill for bill in self.bills if card.last4 in bill.last4s.split(",")]
            if not mine:
                continue
            latest = max(mine, key=lambda item: item.statement_date)
            card.paid_status = latest.paid_status
            card.last_amount_due = latest.amount_due
            card.due_date = latest.due_date
            card.statement_file = latest.file_name or card.statement_file

    def _upsert_cards(self, statement: Statement, file_name: str, statement_id: str = "") -> None:
        due_day = statement.due_date.day if statement.due_date else 0
        statement_day = statement.statement_date.day
        incoming = statement.statement_date.isoformat()
        account_cards = ", ".join(card.last4 for card in statement.cards)
        creates_bill = (not statement.partial) and statement.amount_due is not None
        for card in statement.cards:
            label = card_label(statement.issuer, statement.product, card.last4)
            current = next((row for row in self.cards if row.last4 == card.last4 and row.issuer == statement.issuer and row.product == statement.product), None)
            holder = card.holder
            if current is None:
                self.cards.append(CardRow(
                    issuer=statement.issuer, product=statement.product, last4=card.last4,
                    holder=holder, statement_day=statement_day, due_day=due_day,
                    last_amount_due=statement.amount_due if creates_bill else None,
                    paid_status="unpaid" if creates_bill else "",
                    statement_date=incoming if creates_bill else "",
                    period_end=statement.period_end.isoformat() if creates_bill else "",
                    due_date=statement.due_date.isoformat() if creates_bill and statement.due_date else "",
                    minimum=statement.minimum if creates_bill else None,
                    statement_file=file_name if creates_bill else "",
                    label=label, account_cards=account_cards,
                ))
            elif not creates_bill:
                if holder and not current.holder:
                    current.holder = holder
                if account_cards:
                    current.account_cards = account_cards
            elif current.statement_date and incoming < current.statement_date:
                if holder and not current.holder:
                    current.holder = holder
                if account_cards and not current.account_cards:
                    current.account_cards = account_cards
            else:
                current.statement_day = statement_day or current.statement_day
                current.due_day = due_day or current.due_day
                current.last_amount_due = statement.amount_due
                current.statement_date = incoming
                current.period_end = statement.period_end.isoformat()
                current.due_date = statement.due_date.isoformat() if statement.due_date else ""
                current.minimum = statement.minimum
                current.statement_file = file_name
                current.account_cards = account_cards or current.account_cards
                if holder:
                    current.holder = holder
        self._sync_cards_from_bills()

    def _mark_paid_from_payment(self, payment: StatementLine, statement: Statement) -> None:
        # A payment on the card statement itself is the previous bill being paid.
        for card in self.cards:
            if card.issuer == statement.issuer and card.product == statement.product:
                card.paid_status = "paid"

    def _open_question(self, line: StatementLine, statement: Statement, file_name: str, reason: str) -> None:
        self.questions.append(f"{line.key} {reason}")
        self.log.append(LogRow(
            status="question", source="open question: category; statement",
            merchant=short_merchant(line.description),
            total=line.amount, when=line.trans_date, key=line.key, payment=line.last4,
            card=card_label(statement.issuer, statement.product, line.last4),
            post_date=line.post_date.isoformat(), fx_note=line.fx_note,
        ))
        self.txns.append(TxnRow(
            card=card_label(statement.issuer, statement.product, line.last4),
            trans_date=line.trans_date.isoformat(), post_date=line.post_date.isoformat(),
            description=normalize_description(line.description), amount=line.amount,
            category="", receipt_number="", key=line.key, statement_file=file_name,
            fx_note=line.fx_note, status="question", where="",
            sheet=month_name(line.trans_date.month),
        ))

    def remember(self, description: str, category: str) -> str:
        """Store a learned merchant and write the open question once."""
        pattern = learn_pattern(description)
        self.merchant_map[pattern] = category
        for txn in self.txns:
            if txn.status != "question" or pattern not in txn.description.lower():
                continue
            log = self.find_log_by_key(txn.key)
            if log is None or log.status != "question":
                continue
            log.status = "pending"
            log.category = category
            line = StatementLine(
                date.fromisoformat(txn.trans_date), date.fromisoformat(txn.post_date),
                txn.description, txn.amount or 0, txn.card.rsplit("-", 1)[-1],
                fx_note=txn.fx_note, key=txn.key, occurrence=1,
            )
            where = self._fill_whole(line, category, log)
            log.where = where
            log.status = "no receipt"
            log.month_sheet_amount_written = True
            txn.category = category
            txn.status = "no receipt"
            txn.where = where
        self.questions = [
            question for question in self.questions
            if self.find_log_by_key(question.split()[0]) is not None
            and self.find_log_by_key(question.split()[0]).status == "question"
        ]
        return pattern

    def mark_paid(self, last4: str) -> None:
        touched = False
        for bill in self.bills:
            if last4 in bill.last4s.split(",") and bill.paid_status != "paid":
                bill.paid_status = "paid"
                bill.remaining = 0.0
                touched = True
        if not touched:
            for card in self.cards:
                if card.last4 == last4:
                    card.paid_status = "paid"
        self._sync_cards_from_bills()

    def _write_new_transaction(self, line: StatementLine, statement: Statement, file_name: str,
                               decision: CategoryDecision, crash_on_key: str = "") -> None:
        log = LogRow(
            status="pending", source="statement", merchant=short_merchant(line.description),
            total=line.amount, when=line.trans_date, key=line.key, payment=line.last4,
            card=card_label(statement.issuer, statement.product, line.last4),
            post_date=line.post_date.isoformat(), fx_note=line.fx_note,
            category=decision.category,
        )
        self.log.append(log)
        where = self._fill_whole(line, decision.category, log)
        log.where = where
        log.month_sheet_amount_written = True
        if crash_on_key and line.key == crash_on_key:
            return
        self._finish_pending(log, line, statement, file_name, decision.category, where)

    def _finish_pending(self, log: LogRow, line: StatementLine, statement: Statement,
                        file_name: str, category: str = "", where: str = "") -> None:
        category = category or log.category
        where = where or log.where
        status = "no receipt"
        # A fixed-expense line is still a transaction row.
        self._write_txn(line, statement, file_name, category, status, None, where)
        log.status = status
        log.where = where

    def _category_from_where(self, where: str) -> str:
        return ""

    def _write_txn(self, line, statement, file_name, category, status, receipt, where) -> None:
        if any(txn.key == line.key for txn in self.txns):
            for txn in self.txns:
                if txn.key == line.key and txn.status == "question":
                    return
            return
        number = ""
        if receipt is not None:
            number = receipt.number
            receipt.status = "matched"
            receipt.linked_key = line.key
        category_cell = "(split)" if receipt is not None and len({it.category for it in receipt.items}) > 1 else category
        if receipt is not None and category_cell != "(split)":
            category_cell = receipt.items[0].category if receipt.items else category
        self.txns.append(TxnRow(
            card=card_label(statement.issuer, statement.product, line.last4),
            trans_date=line.trans_date.isoformat(), post_date=line.post_date.isoformat(),
            description=normalize_description(line.description), amount=line.amount,
            category=category_cell, receipt_number=number, key=line.key,
            statement_file=file_name,             fx_note=line.fx_note, status=status, where=where,
            sheet=month_name(grid_day(line).month),
        ))
        log = self.find_log_by_key(line.key)
        if log:
            log.status = status
            log.where = where
            log.linked = number
            log.section_row = f"{month_name(grid_day(line).month)} transactions"

    def _fill_whole(self, line: StatementLine, category: str, log: LogRow) -> str:
        when = grid_day(line)
        if category in FIXED_ROWS:
            sheet = month_name(when.month)
            addr = f"C{FIXED_ROWS[category]}"
            key = (sheet, addr)
            amount = abs(line.amount)
            current = self.fixed.get(key)
            if current is None:
                self.fixed[key] = amount
                self.fixed_date[(sheet, f"D{FIXED_ROWS[category]}")] = when.isoformat()
            elif abs(current - amount) > 0.001:
                # Do not add a second copy. Leave the cell and record the plan.
                log.plan = f"{sheet}!{addr} already {current:.2f}"
            return f"{sheet}!{addr}"
        if category == "Income":
            return self._fill_income(line, log)
        return self._fill_daily(when, category, line.amount, short_merchant(line.description), log)

    def _fill_income(self, line: StatementLine, log: LogRow) -> str:
        sheet = month_name(line.trans_date.month)
        label = short_merchant(line.description)
        for row in range(8, 12):
            current = self.income.get((sheet, row))
            if current is None:
                self.income[(sheet, row)] = (line.amount, label)
                return f"{sheet}!C{row}"
            if abs(current[0] - line.amount) < 0.001 and current[1] == label:
                return f"{sheet}!C{row}"
        raise RuntimeError("no income row")

    def _fill_daily(self, when: date, category: str, amount: float, label: str, log: LogRow) -> str:
        sheet = month_name(when.month)
        column = day_amount_col(when.day)
        item_col = day_item_col(when.day)
        start, end = CATEGORY_ROWS[category if category != "Bank fees" else "Bank fees"]
        target = None
        for row in range(start, end + 1):
            addr = f"{column}{row}"
            if (sheet, addr) not in self.grid:
                target = addr
                break
        if target is None:
            # The block is full. Fold into the last cell as a formula, once.
            addr = f"{column}{end}"
            current = self.grid[(sheet, addr)]
            planned = round(current + amount, 2)
            plan = f"{sheet}!{addr} was {current:.2f}; write {planned:.2f}"
            if log.plan == plan or abs(current - planned) < 0.001:
                return f"{sheet}!{addr}"
            log.plan = plan
            self.grid[(sheet, addr)] = planned
            self.grid_label[(sheet, addr)] = self.grid_label.get((sheet, addr), label)
            return f"{sheet}!{addr}"
        current = self.grid.get((sheet, target))
        if current is None:
            self.grid[(sheet, target)] = round(amount, 2)
            self.grid_label[(sheet, f"{item_col}{target[len(column):]}")] = label
        return f"{sheet}!{target}"

    def _link_existing_receipt(self, line: StatementLine, category: str) -> Optional[ReceiptRow]:
        matches = []
        for receipt in self.receipts:
            if receipt.status in {"superseded", "question", "matched", "cash"}:
                continue
            if self._auto_link(receipt, line):
                matches.append(receipt)
        if len(matches) == 1:
            return matches[0]
        return None

    def _auto_link(self, receipt: ReceiptRow, line: StatementLine) -> bool:
        if abs(receipt.total - line.amount) > 0.001:
            return False
        delta = (line.post_date - date.fromisoformat(receipt.when[:10])).days
        if not 0 <= delta <= 3:
            return False
        if merchant_match(receipt.store, line.description) != "full":
            return False
        if receipt.payment and receipt.payment not in {"cash", ""} and receipt.payment != line.last4:
            return False
        return True

    def _link_returns(self) -> None:
        purchases = [txn for txn in self.txns if txn.amount is not None and txn.amount > 0 and txn.status != "superseded"]
        for txn in self.txns:
            if txn.amount is None or txn.amount >= 0 or txn.status == "question":
                continue
            if any(row.linked == txn.key for row in self.log):
                continue
            for purchase in purchases:
                if purchase.card != txn.card:
                    continue
                if abs((purchase.amount or 0) + (txn.amount or 0)) > 0.001:
                    continue
                if merchant_match(purchase.description, txn.description) != "full":
                    continue
                if purchase.post_date <= txn.post_date:
                    txn_log = self.find_log_by_key(txn.key)
                    if txn_log:
                        txn_log.linked = purchase.key
                    txn.receipt_number = txn.receipt_number or purchase.receipt_number
                    break

    def import_receipt(self, receipt: Receipt, file_label: str = "photo") -> dict:
        # Same file again.
        for row in self.receipts:
            if receipt.content_hash and receipt.content_hash in row.hashes:
                if file_label not in row.sources:
                    row.sources.append(file_label)
                self.events.append(f"attached file to {row.number}, no second amount")
                return {"action": "attach", "number": row.number}
        # Rule 1: same receipt number and store.
        if receipt.number:
            for row in self.receipts:
                if row.number == receipt.number and merchant_match(row.store, receipt.store) == "full" and row.status != "superseded":
                    self._attach(row, receipt, file_label)
                    return {"action": "attach", "number": row.number}
        # Rule 2: no number on one side, same store, same total, date within 1 day.
        rule2 = []
        rule3 = []
        for row in self.receipts:
            if row.status in {"superseded", "question"}:
                continue
            numbers_differ = bool(receipt.number and row.number and receipt.number != row.number)
            if numbers_differ:
                continue
            full = merchant_match(row.store, receipt.store) == "full"
            same_total = abs(row.total - receipt.total) < 0.001
            day_gap = abs((date.fromisoformat(row.when[:10]) - receipt.date).days)
            if full and same_total and day_gap <= 1 and (not receipt.number or not row.number):
                rule2.append(row)
            elif full and same_total and 1 < day_gap <= 7:
                rule3.append(row)
            elif full and day_gap <= 1 and not same_total:
                gap = abs(row.total - receipt.total)
                limit = max(5.0, 0.15 * max(abs(row.total), abs(receipt.total)))
                if 0 < gap <= limit:
                    rule3.append(row)
        if len(rule2) == 1:
            self._attach(rule2[0], receipt, file_label)
            return {"action": "attach", "number": rule2[0].number, "also": [r.number for r in rule3]}
        if len(rule2) > 1 or rule3:
            self._open_receipt_question(receipt, file_label, "near match")
            return {"action": "question", "reason": "near match"}

        # Statement already there?
        txn_hits = [txn for txn in self.txns if txn.status == "no receipt" and self._receipt_matches_txn(receipt, txn)]
        tip_hits = [txn for txn in self.txns if txn.status == "no receipt" and self._tip_or_near_txn(receipt, txn)]
        if len(txn_hits) == 1 and not tip_hits:
            return self._link_receipt_onto_txn(receipt, txn_hits[0], file_label)
        if tip_hits or len(txn_hits) > 1:
            self._open_receipt_question(receipt, file_label, "tip or near statement line")
            return {"action": "question", "reason": "tip or near statement line"}

        return self._write_receipt_first(receipt, file_label)

    def _receipt_matches_txn(self, receipt: Receipt, txn: TxnRow) -> bool:
        if txn.amount is None or abs(txn.amount - receipt.total) > 0.001:
            return False
        post = date.fromisoformat(txn.post_date)
        delta = (post - receipt.date).days
        if not 0 <= delta <= 3:
            return False
        if merchant_match(receipt.store, txn.description) != "full":
            return False
        last4 = txn.card.rsplit("-", 1)[-1]
        if receipt.payment and receipt.payment not in {"cash", ""} and receipt.payment != last4:
            return False
        return True

    def _tip_or_near_txn(self, receipt: Receipt, txn: TxnRow) -> bool:
        if txn.amount is None:
            return False
        if merchant_match(receipt.store, txn.description) != "full":
            return False
        post = date.fromisoformat(txn.post_date)
        delta = (post - receipt.date).days
        if not 0 <= delta <= 3:
            return False
        if abs(txn.amount - receipt.total) < 0.001:
            return False
        gap = abs(txn.amount - receipt.total)
        limit = max(5.0, 0.15 * max(abs(txn.amount), abs(receipt.total)))
        return gap <= limit

    def _attach(self, row: ReceiptRow, receipt: Receipt, file_label: str) -> None:
        if receipt.content_hash and receipt.content_hash not in row.hashes:
            row.hashes.append(receipt.content_hash)
        if file_label not in row.sources:
            row.sources.append(file_label)
        if receipt.number and row.number.startswith("R-"):
            row.number = receipt.number
        self.events.append(f"attached file to {row.number}, no second amount")

    def _open_receipt_question(self, receipt: Receipt, file_label: str, reason: str) -> None:
        number = receipt.number or self._next_receipt_number()
        self.questions.append(f"{number} {reason}")
        self.receipts.append(ReceiptRow(
            number=number, store=receipt.store, when=receipt.when.strftime("%Y-%m-%d %H:%M"),
            total=receipt.total, payment=receipt.payment or "", items=receipt.items,
            file_name=receipt.file_name, status="question", where="", linked_key="",
            sheet=month_name(receipt.date.month), hashes=[receipt.content_hash],
            sources=[file_label],
        ))
        self.log.append(LogRow(
            status="question", source=f"open question {file_label}", merchant=receipt.store,
            total=receipt.total, when=receipt.date, receipt_number=number, payment=receipt.payment,
        ))

    def _link_receipt_onto_txn(self, receipt: Receipt, txn: TxnRow, file_label: str) -> dict:
        """Statement was already in the grid. Replace a single-category amount with the item split."""
        number = receipt.number or self._next_receipt_number()
        old_where = txn.where
        log = self.find_log_by_key(txn.key)
        plan_cells = self._split_cells(receipt, log)
        # Clear the previous whole-amount cell when it is not one of the new cells
        # or when its amount must change. Do this from the recorded plan only.
        self._apply_split(receipt, old_where, plan_cells, log)
        where = "+".join(plan_cells)
        row = ReceiptRow(
            number=number, store=receipt.store,
            when=receipt.when.strftime("%Y-%m-%d %H:%M"), total=receipt.total,
            payment=receipt.payment or txn.card.rsplit("-", 1)[-1], items=receipt.items,
            file_name=receipt.file_name, status="matched", where=where, linked_key=txn.key,
            sheet=month_name(receipt.date.month), hashes=[receipt.content_hash], sources=[file_label],
        )
        self.receipts.append(row)
        txn.receipt_number = number
        txn.status = "matched"
        txn.where = where
        txn.category = "(split)" if len({it.category for it in receipt.items}) > 1 else (receipt.items[0].category if receipt.items else txn.category)
        if log:
            log.status = "matched"
            log.where = where
            log.linked = number
            log.receipt_number = number
            log.files.append(receipt.file_name)
            log.hashes.append(receipt.content_hash)
        return {"action": "linked", "number": number, "where": where}

    def _split_cells(self, receipt: Receipt, log: Optional[LogRow]) -> list[str]:
        """Choose cells and record them before any amount changes."""
        grouped: dict[str, float] = {}
        for item in receipt.items:
            grouped[item.category] = round(grouped.get(item.category, 0.0) + item.price, 2)
        cells = []
        sheet = month_name(receipt.date.month)
        column = day_amount_col(receipt.date.day)
        # Use a scratch log so choosing cells does not look like a second purchase.
        scratch = log or LogRow(status="pending", source="receipt", merchant=receipt.store, total=receipt.total, when=receipt.date)
        for category, amount in grouped.items():
            addr = self._reserve_daily(receipt.date, category, amount, receipt.store, scratch)
            cells.append(addr)
        if log is not None:
            log.where = "+".join(cells)
            log.plan = log.where
        return cells

    def _reserve_daily(self, when: date, category: str, amount: float, label: str, log: LogRow) -> str:
        return self._fill_daily(when, category, amount, label, log)

    def _apply_split(self, receipt: Receipt, old_where: str, new_cells: list[str], log: Optional[LogRow]) -> None:
        grouped: dict[str, float] = {}
        for item in receipt.items:
            grouped[item.category] = round(grouped.get(item.category, 0.0) + item.price, 2)
        # new_cells were just filled by _split_cells / _fill_daily, which ADDS.
        # If the old cell is a different cell, clear it so the amount is not counted twice.
        # If the old cell is one of the new cells, _fill_daily already put the split amount
        # only when the cell was empty. A cell that already held the whole amount must be
        # replaced, not added.
        if not old_where:
            return
        old_addrs = [part.split("!")[-1] if "!" in part else part for part in old_where.split("+")]
        sheet = old_where.split("!")[0] if "!" in old_where else month_name(receipt.date.month)
        new_addrs = [c.split("!")[-1] for c in new_cells]
        # The fill above may have added on top of the old amount if the cell was occupied
        # and the block's first empty row was used. Detect a double count: if the old cell
        # still holds the pre-split total AND a new cell also holds a part, clear the old
        # cell when it is not a intended split cell.
        for addr in old_addrs:
            full = f"{sheet}!{addr}"
            if addr not in new_addrs:
                # Remove the previous whole amount.
                self.grid.pop((sheet, addr), None)
                self.grid_label.pop((sheet, addr), None)
            else:
                # The split fill found this cell occupied and either folded or skipped.
                # Set it to the category amount that belongs here.
                pass
        # Re-assert the split amounts exactly, idempotently.
        categories = list(grouped.items())
        for (category, amount), cell in zip(categories, new_cells):
            sh, addr = cell.split("!")
            self.grid[(sh, addr)] = amount
        if log:
            log.plan = "split " + "+".join(new_cells)

    def _write_receipt_first(self, receipt: Receipt, file_label: str) -> dict:
        number = receipt.number or self._next_receipt_number()
        if not receipt.payment:
            receipt.payment = "cash"
        status = "cash" if receipt.payment == "cash" else "pending"
        log = LogRow(
            status="pending", source=file_label, merchant=receipt.store, total=receipt.total,
            when=receipt.date, receipt_number=number, payment=receipt.payment,
            files=[receipt.file_name], hashes=[receipt.content_hash], items=self._items_text(receipt),
        )
        self.log.append(log)
        cells = self._split_cells(receipt, log)
        where = "+".join(cells)
        log.where = where
        log.month_sheet_amount_written = True
        log.status = "cash" if status == "cash" else "awaiting statement"
        row = ReceiptRow(
            number=number, store=receipt.store, when=receipt.when.strftime("%Y-%m-%d %H:%M"),
            total=receipt.total, payment=receipt.payment or ("cash" if status == "cash" else ""),
            items=receipt.items, file_name=receipt.file_name, status=status, where=where,
            linked_key="", sheet=month_name(receipt.date.month), hashes=[receipt.content_hash],
            sources=[file_label],
        )
        self.receipts.append(row)
        log.section_row = f"{row.sheet} receipts"
        return {"action": status, "number": number, "where": where}

    def _items_text(self, receipt: Receipt) -> str:
        return "; ".join(f"{it.name}: {it.price:.2f}" for it in receipt.items)

    def answer_question_no(self, number: str) -> None:
        for row in self.receipts:
            if row.number == number and row.status == "question":
                row.status = "pending"
                log = next(r for r in self.log if r.receipt_number == number and r.status == "question")
                log.status = "pending"
                # Write the grid now that it is its own purchase.
                cells = []
                grouped: dict[str, float] = {}
                for item in row.items:
                    grouped[item.category] = round(grouped.get(item.category, 0) + item.price, 2)
                when = datetime.strptime(row.when, "%Y-%m-%d %H:%M")
                for category, amount in grouped.items():
                    cells.append(self._fill_daily(when.date(), category, amount, row.store, log))
                row.where = "+".join(cells)
                log.where = row.where
                log.status = "cash" if row.payment == "cash" else "awaiting statement"
                row.status = "cash" if row.payment == "cash" else "pending"
                return

    def grid_sum(self) -> float:
        return round(sum(self.grid.values()) + sum(self.fixed.values()), 2)

    def _bank_line_key(self, line: StatementLine, fallback_last4: str) -> str:
        if not line.key:
            line.key = transaction_key(
                line.last4 or fallback_last4, line.post_date, line.amount,
                line.description, line.occurrence or 1,
            )
        return line.key

    def _append_bank_txn(self, line: StatementLine, label: str, category: str, status: str, where: str) -> bool:
        if any(txn.key == line.key for txn in self.txns):
            return False
        self.txns.append(TxnRow(
            card=label, trans_date=line.trans_date.isoformat(), post_date=line.post_date.isoformat(),
            description=normalize_description(line.description), amount=line.amount, category=category,
            receipt_number="", key=line.key, statement_file="", fx_note="", status=status,
            where=where, sheet=month_name(line.trans_date.month),
        ))
        return True

    def import_bank(self, text: str, file_name: str = "bank.csv") -> dict:
        """Optional bank transactions. Cards-only books never call this.

        Every line becomes a Transactions row. The file is one Log row with its hash.
        Importing the same file again does not pay a bill a second time.
        """
        statement = parse_csv_statement(text) if "trans_date" in text.splitlines()[0] or text.lstrip().startswith("#") else None
        if statement is None:
            raise ValueError("bank import expects the CSV shape")
        digest = sha256_hex(text.encode())
        if any(digest in (row.hashes or []) for row in self.log):
            return {"results": [], "skipped": "already imported"}
        self.log.append(LogRow(
            status="done", source="bank", merchant=statement.issuer,
            total=None, when=statement.statement_date, files=[file_name],
            hashes=[digest], key=f"bank|{digest}",
        ))
        results = []
        account_last4 = statement.primary_last4
        for line in statement.lines + statement.payments:
            desc = normalize_description(line.description)
            label = card_label(statement.issuer, statement.product, line.last4 or account_last4)
            self._bank_line_key(line, account_last4)
            if re.search(r"TRANSFER", desc):
                self._append_bank_txn(line, label, "Transfer", "no receipt", "")
                results.append(("transfer", desc))
                continue
            if re.search(r"VISA|MASTERCARD|PAYMENT", desc) and line.amount < 0:
                paid_last4 = _search(line.description, r"(\d{4})")
                fresh = self._append_bank_txn(line, label, "Card payment", "no receipt", "")
                if fresh:
                    self._apply_payment(line, [paid_last4] if paid_last4 else [])
                results.append(("card payment", desc))
                continue
            if line.amount > 0:
                pattern = learn_pattern(line.description)
                if self.merchant_map.get(pattern) == "Income":
                    where = self._fill_income(line, LogRow(
                        status="pending", source="bank", merchant=pattern,
                        total=line.amount, when=line.trans_date,
                    ))
                    self._append_bank_txn(line, label, "Income", "no receipt", where)
                    results.append(("income", desc))
                else:
                    self.pending_income.append(line)
                    self.questions.append(f"income {pattern} {line.amount:.2f}")
                    self._append_bank_txn(line, label, "", "question", "")
                    results.append(("ask income", desc))
                continue
            decision = categorize_transaction(line.description, line.amount, "", self.merchant_map)
            if decision.category == "Rent / Mortgage":
                category = decision.category
                sheet = month_name(line.trans_date.month)
                addr = f"C{FIXED_ROWS[category]}"
                self.fixed[(sheet, addr)] = abs(line.amount)
                self.fixed_date[(sheet, f"D{FIXED_ROWS[category]}")] = line.trans_date.isoformat()
                self._append_bank_txn(line, label, "Mortgage", "no receipt", f"{sheet}!{addr}")
                results.append(("fixed", "Mortgage"))
            elif decision.category in FIXED_ROWS or decision.category == "Property Tax":
                category = decision.category
                sheet = month_name(line.trans_date.month)
                addr = f"C{FIXED_ROWS[category]}"
                self.fixed[(sheet, addr)] = abs(line.amount)
                self.fixed_date[(sheet, f"D{FIXED_ROWS[category]}")] = line.trans_date.isoformat()
                self._append_bank_txn(line, label, "Fixed expense", "no receipt", f"{sheet}!{addr}")
                results.append(("fixed", "Fixed expense"))
            else:
                self._append_bank_txn(line, label, "Fixed expense", "no receipt", "")
                results.append(("unclassified debit", desc))
        if account_last4 and not any(c.last4 == account_last4 for c in self.cards):
            self.cards.append(CardRow(
                issuer=statement.issuer, product=statement.product, last4=account_last4,
                holder="", statement_day=0, due_day=0, last_amount_due=None,
                paid_status="", label=card_label(statement.issuer, statement.product, account_last4),
                account_cards=account_last4,
            ))
        return {"results": results}

    def confirm_income(self, description: str) -> None:
        pattern = learn_pattern(description)
        self.merchant_map[pattern] = "Income"
        still = []
        for line in self.pending_income:
            if learn_pattern(line.description) == pattern:
                where = self._fill_income(line, LogRow(
                    status="done", source="bank", merchant=short_merchant(line.description),
                    total=line.amount, when=line.trans_date, category="Income",
                ))
                for txn in self.txns:
                    if txn.key == line.key and txn.status == "question":
                        txn.category = "Income"
                        txn.status = "no receipt"
                        txn.where = where
            else:
                still.append(line)
        self.pending_income = still
        self.questions = [q for q in self.questions if pattern not in q.lower()]


def due_reminders(book: Book, today: date) -> list[str]:
    """One line per unpaid statement whose due date has not passed.

    Fires on the due date and three days before it. The sentence ends with a period.
    """
    notes = []
    for bill in book.bills:
        if bill.paid_status == "paid" or not bill.due_date:
            continue
        if bill.product in {"Chequing", "Savings"}:
            continue
        due = date.fromisoformat(bill.due_date)
        if today > due:
            continue
        if today != due and today != due - timedelta(days=3):
            continue
        if bill.remaining is None and bill.amount_due is None:
            amount = "check your statement for the amount"
        else:
            value = bill.remaining if bill.remaining is not None else bill.amount_due
            amount = f"{value:.2f}"
        notes.append(f"Pay {bill.label} {amount} by {bill.due_date}.")
    return notes


def _safe_day(year: int, month: int, day: int) -> date:
    probe = day
    while probe >= 28:
        try:
            return date(year, month, probe)
        except ValueError:
            probe -= 1
    return date(year, month, probe)


def _prev_month(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    return year, month - 1


def _card_ids(card: CardRow) -> set[str]:
    ids = {card.last4} if card.last4 else set()
    ids.update(part.strip() for part in (card.account_cards or "").split(",") if part.strip())
    return ids


def statement_nudges(cards: list[CardRow], today: date, ready_emails: list[str],
                     imported_period_ends: set[str]) -> list[str]:
    """One nudge per account, from that account's statement cycle date.

    The second nudge is the cycle date plus three days, including when that
    day falls in the next month. Stop when that cycle's statement is imported.
    An email on the cycle date is the same first nudge, not a second one.
    """
    del ready_emails, imported_period_ends
    eligible = [card for card in cards if card.statement_day and card.product not in {"Chequing", "Savings"}]
    parent = list(range(len(eligible)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        parent[find(left)] = find(right)

    for i, left in enumerate(eligible):
        for j in range(i + 1, len(eligible)):
            right = eligible[j]
            if left.issuer != right.issuer or left.product != right.product:
                continue
            if _card_ids(left) & _card_ids(right):
                union(i, j)
            elif (
                not left.account_cards and not right.account_cards
                and left.statement_day == right.statement_day
            ):
                union(i, j)
    groups: dict[int, list[CardRow]] = {}
    for index, card in enumerate(eligible):
        groups.setdefault(find(index), []).append(card)
    notes = []
    for group in groups.values():
        primary = min(group, key=lambda item: item.last4)
        label = primary.label or card_label(primary.issuer, primary.product, primary.last4)
        prev_year, prev_month = _prev_month(today.year, today.month)
        windows = [
            _safe_day(prev_year, prev_month, primary.statement_day),
            _safe_day(today.year, today.month, primary.statement_day),
        ]
        for expected in windows:
            if any(member.statement_date == expected.isoformat() for member in group):
                continue
            if today == expected:
                notes.append(f"Statement ready for {label}: forward or download it.")
                break
            if today == expected + timedelta(days=3):
                notes.append(f"Statement should be out for {label}.")
                break
    return notes


def return_lookup(book: Book, query: str, today: date) -> Optional[dict]:
    text = query.lower()
    best = None
    for row in book.receipts:
        if row.status in {"superseded", "question"}:
            continue
        for item in row.items:
            hay = f"{item.name} {item.sku} {row.store}".lower()
            if all(part in hay for part in text.split() if len(part) > 2) or (item.sku and item.sku.lower() in text):
                best = (row, item)
                break
        if best:
            break
    if not best:
        # looser: any word of 4+ letters
        words = [w for w in re.findall(r"[a-z0-9-]+", text) if len(w) >= 4]
        for row in book.receipts:
            for item in row.items:
                hay = f"{item.name} {item.sku} {row.store}".lower()
                if words and all(w in hay for w in words):
                    best = (row, item)
                    break
            if best:
                break
    if not best:
        return _lookup_transaction(book, query, today)
    row, item = best
    for txn in book.txns:
        if txn.amount is None or txn.amount >= 0 or txn.status in {"superseded", "question"}:
            continue
        if merchant_match(row.store, txn.description) != "full":
            continue
        if abs(abs(txn.amount) - item.price) > 0.001 and abs(abs(txn.amount) - row.total) > 0.001:
            continue
        if txn.post_date and date.fromisoformat(txn.post_date[:10]) > today:
            continue
        return {
            "file": row.file_name,
            "store": row.store,
            "date": row.when[:10],
            "price": item.price,
            "card": row.payment,
            "receipt": row.number,
            "refunded": True,
            "refund_date": txn.post_date,
            "message": f"Already refunded on {txn.post_date}",
        }
    if row.total < 0:
        return {
            "file": row.file_name,
            "store": row.store,
            "date": row.when[:10],
            "price": item.price,
            "card": row.payment,
            "receipt": row.number,
            "days_left": None,
            "window": None,
            "estimate": False,
            "refunded": False,
            "message": "A return receipt has no return window.",
        }
    policy = 30
    for name, days in RETURN_WINDOWS.items():
        if name in row.store.lower():
            policy = days
            break
    purchased = date.fromisoformat(row.when[:10])
    days_left = (purchased + timedelta(days=policy) - today).days
    return {
        "file": row.file_name,
        "store": row.store,
        "date": row.when[:10],
        "price": item.price,
        "card": row.payment,
        "receipt": row.number,
        "days_left": days_left,
        "window": policy,
        "estimate": True,
        "refunded": False,
        "message": f"Return window is about {policy} days from the purchase date (an estimate). {days_left} days left.",
    }


def _lookup_transaction(book: Book, query: str, today: date) -> Optional[dict]:
    """No Receipts row. Show the matching Transactions line, if there is one."""
    words = {word for word in re.findall(r"[a-z0-9]+", query.lower()) if len(word) >= 4}
    hits = []
    for txn in book.txns:
        if txn.status in {"superseded", "question"} or txn.amount is None:
            continue
        desc_words = {word for word in re.findall(r"[a-z0-9]+", txn.description.lower()) if len(word) >= 4}
        if words and desc_words and (words & desc_words):
            hits.append(txn)
    if not hits:
        return None
    purchase = next((txn for txn in hits if txn.amount > 0), None)
    refund = next((txn for txn in hits if txn.amount < 0), None)
    shown = purchase or hits[0]
    message = "No receipt is saved."
    refunded = False
    refund_date = ""
    if purchase is not None and refund is not None and refund.post_date and date.fromisoformat(refund.post_date[:10]) <= today:
        refunded = True
        refund_date = refund.post_date
        message = f"Already refunded on {refund.post_date}. No receipt is saved."
    return {
        "file": "",
        "store": short_merchant(shown.description),
        "date": shown.trans_date,
        "price": abs(shown.amount or 0),
        "card": shown.card.rsplit("-", 1)[-1],
        "receipt": "",
        "refunded": refunded,
        "refund_date": refund_date,
        "message": message,
    }


def migrate_v124_to_v2(book: Book) -> dict:
    """Copy v1.2.4 receipt-list rows into the Receipts section.

    Amounts already in the grid stay where they are. A second call adds nothing.
    Duplicate rows are flagged and kept.
    """
    if book.version == "v2.0" and book.pending_formula.get("phase") != "v2-partial":
        return {"copied": 0, "already": True}
    copied = 0
    seen_keys = {row.identity for row in book.receipts if row.identity}
    flagged = []
    seen: list[ReceiptRow] = []
    # v1.2.4 rows are Log rows with status done and a month list, and no txn key.
    for log in book.log:
        if log.key:
            continue
        number = log.receipt_number or ""
        when = log.when if isinstance(log.when, date) else None
        receipt_key = receipt_identity(log.merchant, number, when, log.total)
        # A blank number is not a reason to skip. Skip only a key already copied.
        if receipt_key in seen_keys:
            continue
        duplicate = False
        for prior in seen:
            same_store = prior.store == log.merchant
            same_total = abs(prior.total - (log.total or 0)) < 0.001
            same_day = prior.when[:10] == (log.when.isoformat() if log.when else "")
            numbers_differ = bool(number and prior.number and number != prior.number)
            if same_store and same_total and same_day and not numbers_differ:
                duplicate = True
                flagged.append(receipt_key)
        items = []
        if log.items:
            for part in log.items.split(";"):
                if ":" not in part:
                    continue
                name, price = part.split(":", 1)
                items.append(ReceiptItem(name.strip(), float(price), categorize_item(name)))
        payment = log.payment or ""
        if log.status == "superseded":
            status = "superseded"
        elif payment.lower() == "cash" or not payment:
            status = "cash"
        else:
            status = "pending"
        sheet = month_name(log.when.month) if log.when else "Jan"
        where = qualify_where(log.where, sheet)
        original = log.files[0] if log.files else ""
        copy_name = ""
        if original:
            base = original.split("/")[-1]
            copy_name = f"Family Book - {book.year}/receipts/{base}"
        row = ReceiptRow(
            number=number,
            store=log.merchant,
            when=(log.when.isoformat() if log.when else "") + " 00:00",
            total=log.total or 0,
            payment=payment or ("cash" if status == "cash" else ""),
            items=items,
            file_name=copy_name,
            status=status,
            where=where,
            linked_key="",
            sheet=sheet,
            hashes=list(log.hashes),
            sources=[],
            identity=receipt_key,
        )
        if copy_name:
            log.files = [copy_name]
        seen_keys.add(receipt_key)
        book.receipts.append(row)
        seen.append(row)
        log.section_row = f"{row.sheet} receipts"
        copied += 1
        if duplicate:
            # Helper column CB holds only this mark. Never copy Source text into it.
            # Receipts column L is Item 2. Column M is the price of item 2.
            row.sources = ["pending duplicate"]
            for prior in seen:
                if prior is row:
                    continue
                same_store = prior.store == row.store
                same_total = abs(prior.total - row.total) < 0.001
                same_day = prior.when[:10] == row.when[:10]
                if same_store and same_total and same_day and "pending duplicate" not in prior.sources:
                    prior.sources.append("pending duplicate")
            token = row.identity
            book.pending_formula["duplicates"] = book.pending_formula.get("duplicates", "") + f" {token}"
    book.version = "v2.0"
    book.pending_formula.pop("phase", None)
    return {"copied": copied, "already": False, "flagged": flagged}
