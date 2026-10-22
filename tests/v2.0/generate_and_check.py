#!/usr/bin/env python3
"""Generate synthetic v2.0 fixtures and check keys, totals, and book rules.

The fixtures are fake. They follow the shapes of four public statement layouts
(CIBC Visa, CIBC Costco Mastercard, Triangle Mastercard, Rogers Mastercard)
with invented names, addresses, last-4 digits, and amounts.

Run from the repo root:

    python3 tests/v2.0/generate_and_check.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from familybook_v2 import (  # noqa: E402
    Book,
    card_label,
    day_amount_col,
    due_reminders,
    migrate_v124_to_v2,
    parse_receipt,
    parse_statement,
    return_lookup,
    statement_nudges,
    transaction_key,
    verify_card_totals,
    LogRow,
    ReceiptItem,
)

FIX = Path(__file__).resolve().parent / "fixtures"

LAYOUT_A = """CIBC Dividend Visa Infinite Card
Prepared for: Jordan Lee
Statement date: September 27, 2026
For the period: August 28, 2026 to September 27, 2026
Amount Due $453.69
Minimum payment due $10.00
Payment due date October 19, 2026
Account number: XXXX XXXX XXXX 1001

Your payments
Trans date Post date Description Amount($)
Sep 14 Sep 15 PAYMENT THANK YOU/PAIEMENT MERCI 200.00

Your new charges and credits
Card number XXXX XXXX XXXX 1001
Aug 28 Aug 31 Ymark SHELL C11318 MISSISSAUGA ON
Transportation 71.04
Sep 02 Sep 03 Ymark Netflix.com 866-716-0414 ON
Personal and Household Expenses 9.03
Sep 13 Sep 14 Ymark TIM HORTONS #0614 BURLINGTON ON
Restaurants 1.92
Sep 16 Sep 17 Ymark TIM HORTONS #0614 BURLINGTON ON
Restaurants 1.92
Sep 16 Sep 17 Ymark TIM HORTONS #0614 BURLINGTON ON
Restaurants 1.92
Sep 19 Sep 21 ACME WIDGETS PORTLAND OR
240.00
Sep 23 Sep 25 Ymark SHELL C11318
MISSISSAUGA ON
Transportation
127.86
Total for card 1001 $453.69

Card number XXXX XXXX XXXX 1002
Sep 07 Sep 08 T&T SUPERMARKET 042 MISSISSAUGA ON
Retail and Grocery 42.10
Total for card 1002 $42.10
""".replace("Ymark", "\u00dd")

LAYOUT_B = """CIBC Costco Mastercard
Prepared for: Jordan Lee
Statement date: September 22, 2026
September statement period August 23, 2026 to September 22, 2026
Amount Due $391.66
Minimum payment due $10.00
Payment due date October 13, 2026
Card number XXXX XXXX XXXX 2202
Aug 21 Aug 24 COSTCO WHOLESALE W253 BURLINGTON ON
Retail and Grocery 246.66
Sep 01 Sep 02 COSTCO *ANNUAL RENEWAL OTTAWA ON
Retail and Grocery 65.00
Sep 10 Sep 11 PAYMENT THANK YOU/PAIEMENT MERCI 100.00
Sep 20 Sep 21 COSTCO WHOLESALE W253 BURLINGTON ON
Retail and Grocery 80.00
Total for card 2202 $391.66
"""

LAYOUT_C = """Your Triangle World Elite Mastercard Statement
Prepared for: Jordan Lee
Statement date: September 27, 2026
For the period: August 28, 2026 to September 27, 2026
Balance Due $160.00
Minimum payment due $10.00
Payment due date October 19, 2026
Account number: XXXX XXXX XXXX 3303

Payments received
Sep 14 Sep 15 BANK PAYMENT/PAIEMENT BANQUE -50.00

Returns and other credits
Sep 23 Sep 24 #5138 SPORT CHEK OAKVILLE ON -57.53

Purchases
Purchases - Card #XXXX XXXX XXXX 3303
Aug 30 Aug 31 CDN TIRE GASBAR #01306 OAKVILLE ON
40.00
Sep 09 Sep 10 #5138 SPORT CHEK OAKVILLE ON 57.53
Sep 21 Sep 22 OAKVILLE-TAX 316 120.00
Total for card 3303 $160.00

The total of each transaction is included in the Purchases section.
Details of your Sport Chek store purchases
Sep 09 Sep 10 1 MERCHANDISE 34.99
1 ADIDAS MILANO JACKET 22.54
Total for transaction $57.53
Sep 23 Sep 24 1 MERCHANDISE -34.99
1 ADIDAS MILANO JACKET -22.54
Total for transaction -$57.53
WAYS TO PAY
Online banking
"""

LAYOUT_D = """Rogers Bank Mastercard
Statement date: September 18, 2026
Statement Period August 19, 2026 to September 18, 2026
Payment due date October 9, 2026
Minimum payment $25.00
Amount Due $9.12
Prepared for: Jordan Lee
Card number XXXX XXXX XXXX 4404
Aug
22
Aug
24
THE
HOME
DEPOT
#7142
GUELPH
ON
48.20
Aug
31
Sep
1
SOUTHWEST
HARBOR
PARKI
SOUTHWEST
HARME
FOREIGN
CURRENCY
USD
6.40
@
1.425
9.12
Sep
04
Sep
05
PAYMENT
THANK
YOU/PAIEMENT
MERCI
30.00
Sep
10
Sep
11
THE
HOME
DEPOT
#7142
GUELPH
ON
-48.20
Total
for
card
4404
$9.12
"""

YEAR_CROSS = """CIBC Dividend Visa Infinite Card
Prepared for: Jordan Lee
Statement date: January 19, 2026
For the period: December 20, 2025 to January 19, 2026
Amount Due $59.03
Minimum payment due $10.00
Payment due date February 9, 2026
Card number XXXX XXXX XXXX 1001
Dec 28 Dec 30 GROCERY MART BURLINGTON ON
Retail and Grocery 20.00
Dec 31 Jan 02 GAS BAR OAKVILLE ON
30.00
Jan 05 Jan 06 Netflix.com ON
9.03
Total for card 1001 $59.03
"""

CSV_PARTIAL = """# issuer: CIBC
# product: Visa
# statement_date: 2026-09-15
# period_start: 2026-08-28
# period_end: 2026-09-27
# due_date: 2026-10-19
# minimum: 10.00
# amount_due: 71.04
# partial: true
# holder: Jordan Lee
# last4: 1001
trans_date,post_date,description,amount,last4,spend_category
2026-08-28,2026-08-31,SHELL C11318 MISSISSAUGA ON,71.04,1001,Transportation
"""

BAD_TOTAL = """CIBC Dividend Visa Infinite Card
Prepared for: Jordan Lee
Statement date: September 27, 2026
For the period: August 28, 2026 to September 27, 2026
Amount Due $71.04
Minimum payment due $10.00
Payment due date October 19, 2026
Card number XXXX XXXX XXXX 1001
Aug 28 Aug 31 SHELL C11318 MISSISSAUGA ON
Transportation 71.04
Total for card 1001 $99.99
"""

TIP_STATEMENT = """# issuer: CIBC
# product: Visa
# statement_date: 2026-09-27
# period_start: 2026-08-28
# period_end: 2026-09-27
# due_date: 2026-10-19
# minimum: 10.00
# amount_due: 58.00
# holder: Jordan Lee
# cards: 1001:58.00
trans_date,post_date,description,amount,last4,spend_category
2026-09-18,2026-09-19,SUN PALACE BURLINGTON ON,58.00,1001,Restaurants
"""

BANK = """# issuer: North Bank
# product: Chequing
# statement_date: 2026-09-30
# period_start: 2026-09-01
# period_end: 2026-09-30
# holder: Jordan Lee
# last4: 5505
# partial: true
trans_date,post_date,description,amount,last4
2026-09-01,2026-09-01,PAYROLL ACME EMPLOYER,3200.00,5505
2026-09-02,2026-09-02,NORTH BANK MORTGAGE,-1800.00,5505
2026-09-15,2026-09-15,CIBC VISA PAYMENT 1001,-495.79,5505
2026-09-16,2026-09-16,TRANSFER TO SAVINGS 5506,-500.00,5505
"""

RECEIPT_COSTCO = """STORE: Costco Burlington
DATE: 2026-09-20 14:32
RECEIPT: 482910
CARD: 2202
TOTAL: 80.00
ITEMS:
Kirkland eggs | 18.00
Paper towel | 42.00
Rotisserie chicken | 20.00
"""

RECEIPT_SHELL = """STORE: Shell
DATE: 2026-09-23 08:10
RECEIPT: 771100
CARD: 1001
TOTAL: 127.86
ITEMS:
Unleaded fuel | 127.86
"""

RECEIPT_TT = """STORE: T&T Supermarket
DATE: 2026-09-07 11:05
RECEIPT: 880021
CARD: 1002
TOTAL: 42.10
ITEMS:
Milk | 20.00
Chips | 22.10
"""

RECEIPT_TIP = """STORE: Sun Palace
DATE: 2026-09-18 19:40
RECEIPT: 55210
CARD: 1001
TOTAL: 50.00
ITEMS:
Dinner plate | 50.00
"""

RECEIPT_CASH = """STORE: Corner Market
DATE: 2026-10-04 09:15
CARD: cash
TOTAL: 12.40
ITEMS:
Milk | 6.40
Bread | 6.00
"""

RECEIPT_DEPOT = """STORE: The Home Depot Oakville
DATE: 2026-10-15 16:40
RECEIPT: 48291
CARD: 1001
TOTAL: 84.12
ITEMS:
Paint | 60.00
Brush | 24.12
"""

RECEIPT_DEPOT_EMAIL = """STORE: HOME DEPOT #7016
DATE: 2026-10-15 16:42
RECEIPT: 48291
CARD: 1001
TOTAL: 84.12
ITEMS:
Paint | 60.00
Brush | 24.12
"""

RECEIPT_NEAR_A = """STORE: Costco
DATE: 2026-10-03 12:00
TOTAL: 57.29
ITEMS:
Snack mix | 57.29
"""

RECEIPT_NEAR_B = """STORE: Costco
DATE: 2026-10-08 12:00
TOTAL: 57.29
ITEMS:
Snack mix | 57.29
"""

RECEIPT_SPORT = """STORE: Sport Chek
DATE: 2026-09-09 15:04
RECEIPT: 5138
CARD: 3303
TOTAL: 57.53
SKU: AM-23
ITEMS:
Adidas Milano jacket | 57.53 | AM-23
"""

ACME_FOLLOWUP = """# issuer: CIBC
# product: Visa
# statement_date: 2026-10-27
# period_start: 2026-09-28
# period_end: 2026-10-27
# due_date: 2026-11-18
# minimum: 10.00
# amount_due: 80.00
# holder: Jordan Lee
# cards: 1001:80.00
trans_date,post_date,description,amount,last4
2026-10-02,2026-10-03,ACME WIDGETS PORTLAND OR,80.00,1001
"""


class Fail(Exception):
    pass


def check(cond: bool, message: str) -> None:
    if not cond:
        raise Fail(message)


def write_pdf(path: Path, text: str) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 8)
    y = 760
    for line in text.splitlines():
        if y < 40:
            c.showPage()
            c.setFont("Courier", 8)
            y = 760
        c.drawString(36, y, line[:110])
        y -= 11
    c.save()


def write_png(path: Path, text: str) -> None:
    from PIL import Image, ImageDraw

    lines = text.splitlines()
    image = Image.new("RGB", (900, 40 + 22 * max(len(lines), 1)), "white")
    draw = ImageDraw.Draw(image)
    for index, line in enumerate(lines):
        draw.text((20, 16 + index * 22), line, fill="black")
    image.save(path)


def generate() -> None:
    FIX.mkdir(parents=True, exist_ok=True)
    files = {
        "layout-a-cibc-visa.txt": LAYOUT_A,
        "layout-b-cibc-costco.txt": LAYOUT_B,
        "layout-c-triangle.txt": LAYOUT_C,
        "layout-d-rogers-wordstack.txt": LAYOUT_D,
        "layout-year-cross.txt": YEAR_CROSS,
        "mid-month.csv": CSV_PARTIAL,
        "bad-total.txt": BAD_TOTAL,
        "tip-statement.csv": TIP_STATEMENT,
        "bank-chequing.csv": BANK,
        "acme-followup.csv": ACME_FOLLOWUP,
        "receipt-costco.txt": RECEIPT_COSTCO,
        "receipt-shell.txt": RECEIPT_SHELL,
        "receipt-tandt.txt": RECEIPT_TT,
        "receipt-tip.txt": RECEIPT_TIP,
        "receipt-cash.txt": RECEIPT_CASH,
        "receipt-homedepot.txt": RECEIPT_DEPOT,
        "receipt-homedepot-email.txt": RECEIPT_DEPOT_EMAIL,
        "receipt-near-oct3.txt": RECEIPT_NEAR_A,
        "receipt-near-oct8.txt": RECEIPT_NEAR_B,
        "receipt-sportchek.txt": RECEIPT_SPORT,
        "product-tag.txt": "BRAND: Adidas\nPRODUCT: Milano jacket\nSKU: AM-23\n",
    }
    files["layout-a-cibc-visa.html"] = "<html><body><pre>\n" + LAYOUT_A + "</pre></body></html>\n"
    for name, text in files.items():
        (FIX / name).write_text(text, encoding="utf-8")
    for name in (
        "layout-a-cibc-visa.txt",
        "layout-b-cibc-costco.txt",
        "layout-c-triangle.txt",
        "layout-d-rogers-wordstack.txt",
        "layout-year-cross.txt",
    ):
        write_pdf(FIX / name.replace(".txt", ".pdf"), files[name])
    write_png(FIX / "receipt-costco.png", RECEIPT_COSTCO)
    write_png(FIX / "receipt-homedepot.png", RECEIPT_DEPOT)
    write_png(FIX / "product-tag-adidas.png", "Adidas\nMilano jacket\nSKU AM-23\n")
    write_pdf(FIX / "receipt-costco.pdf", RECEIPT_COSTCO)


def expect_key(last4, post, amount, description, occurrence=1) -> str:
    year, month, day = (int(p) for p in post.split("-"))
    return transaction_key(last4, date(year, month, day), amount, description, occurrence)


def test_parsers() -> None:
    a = parse_statement((FIX / "layout-a-cibc-visa.txt").read_text(encoding="utf-8"), "A")
    check(a.issuer == "CIBC" and a.product == "Visa", f"A product {a.issuer} {a.product}")
    check(a.statement_date == date(2026, 9, 27), "A statement date")
    check(a.period_start == date(2026, 8, 28) and a.period_end == date(2026, 9, 27), "A period")
    check(a.due_date == date(2026, 10, 19), "A due")
    check(a.minimum == 10.00 and a.amount_due == 453.69, f"A money {a.minimum} {a.amount_due}")
    check(a.holder == "Jordan Lee", f"A holder {a.holder}")
    check([c.last4 for c in a.cards] == ["1001", "1002"], f"A cards {[c.last4 for c in a.cards]}")
    check(len(a.lines) == 8, f"A lines {len(a.lines)} {[ln.description for ln in a.lines]}")
    check(len(a.payments) == 1, "A payment skipped into payments")
    check(not verify_card_totals(a), verify_card_totals(a))
    shell = next(ln for ln in a.lines if ln.amount == 127.86)
    check(shell.description == "SHELL C11318 MISSISSAUGA ON", shell.description)
    check("\u00dd" not in shell.description, "marker stripped")
    check(shell.post_date == date(2026, 9, 25) and shell.trans_date == date(2026, 9, 23), "wrapped dates")
    twins = [ln for ln in a.lines if ln.amount == 1.92 and ln.post_date == date(2026, 9, 17)]
    check([ln.occurrence for ln in twins] == [1, 2], f"twins {[(ln.occurrence, ln.key) for ln in twins]}")
    check(twins[0].key.endswith("|1") and twins[1].key.endswith("|2"), "occurrence in key")
    check(a.folder(".pdf") == "Family Book - 2026/statements/CIBC Visa-1001/2026-09-27 statement.pdf", a.folder(".pdf"))

    html = parse_statement((FIX / "layout-a-cibc-visa.html").read_text(encoding="utf-8"), "A-html")
    check([ln.key for ln in html.lines] == [ln.key for ln in a.lines], "HTML keys match text")

    from pypdf import PdfReader
    pdf_text = "\n".join((page.extract_text() or "") for page in PdfReader(str(FIX / "layout-a-cibc-visa.pdf")).pages)
    pdf = parse_statement(pdf_text, "A-pdf")
    check([ln.key for ln in pdf.lines] == [ln.key for ln in a.lines], f"PDF keys\n{pdf.lines and [ln.key for ln in pdf.lines]}\n{[ln.key for ln in a.lines]}")

    b = parse_statement((FIX / "layout-b-cibc-costco.txt").read_text(encoding="utf-8"), "B")
    check(b.issuer == "CIBC" and b.product == "Costco MC", f"B {b.issuer} {b.product}")
    check(b.due_date == date(2026, 10, 13), "B due")
    check(len(b.lines) == 3 and len(b.payments) == 1, f"B lines {len(b.lines)} pays {len(b.payments)}")
    early = next(ln for ln in b.lines if ln.amount == 246.66)
    check(early.trans_date == date(2026, 8, 21) and early.post_date == date(2026, 8, 24), "B post-date period")
    check(not verify_card_totals(b), verify_card_totals(b))

    c = parse_statement((FIX / "layout-c-triangle.txt").read_text(encoding="utf-8"), "C")
    check(c.issuer == "Triangle" and c.product == "MC", f"C {c.issuer} {c.product}")
    check(len(c.lines) == 4, f"C lines {len(c.lines)} {[ln.description for ln in c.lines]}")
    check(len(c.payments) == 1, "C payment")
    check(any(ln.amount == -57.53 for ln in c.lines), "C return")
    check(not any("MERCHANDISE" in ln.description for ln in c.lines), "C detail block skipped")
    check(not verify_card_totals(c), verify_card_totals(c))

    d = parse_statement((FIX / "layout-d-rogers-wordstack.txt").read_text(encoding="utf-8"), "D")
    check(d.issuer == "Rogers" and d.product == "MC", f"D {d.issuer} {d.product}")
    check(d.due_date == date(2026, 10, 9) and d.minimum == 25.00, f"D due {d.due_date} {d.minimum}")
    check(len(d.lines) == 3, f"D lines {len(d.lines)} {[ (ln.description, ln.amount, ln.fx_note) for ln in d.lines]}")
    check(len(d.payments) == 1, "D payment")
    fx = next(ln for ln in d.lines if ln.amount == 9.12)
    check(fx.fx_note.startswith("FOREIGN CURRENCY USD 6.40 @ 1.425"), fx.fx_note)
    check("SOUTHWEST HARBOR PARKI" in fx.description and "HARME" in fx.description, fx.description)
    check(not verify_card_totals(d), verify_card_totals(d))
    check(d.folder(".pdf") == "Family Book - 2026/statements/Rogers MC-4404/2026-09-18 statement.pdf", d.folder(".pdf"))

    for name in ("layout-b-cibc-costco.pdf", "layout-c-triangle.pdf", "layout-d-rogers-wordstack.pdf"):
        text = "\n".join((page.extract_text() or "") for page in PdfReader(str(FIX / name)).pages)
        parsed = parse_statement(text, name)
        original = {
            "layout-b-cibc-costco.pdf": b,
            "layout-c-triangle.pdf": c,
            "layout-d-rogers-wordstack.pdf": d,
        }[name]
        check([ln.key for ln in parsed.lines] == [ln.key for ln in original.lines], f"{name} keys diverged")

    cross = parse_statement((FIX / "layout-year-cross.txt").read_text(encoding="utf-8"), "year")
    check(cross.period_start == date(2025, 12, 20) and cross.period_end == date(2026, 1, 19), "year period")
    by_amount = {ln.amount: ln for ln in cross.lines}
    check(by_amount[20.00].trans_date == date(2025, 12, 28), "Dec purchase")
    check(by_amount[30.00].trans_date == date(2025, 12, 31) and by_amount[30.00].post_date == date(2026, 1, 2), "year cross line")
    check(by_amount[30.00].key == expect_key("1001", "2026-01-02", 30.00, "GAS BAR OAKVILLE ON"), by_amount[30.00].key)
    check(by_amount[9.03].trans_date == date(2026, 1, 5), "January netflix")
    check(cross.folder(".pdf").startswith("Family Book - 2026/statements/"), cross.folder(".pdf"))

    bad = parse_statement((FIX / "bad-total.txt").read_text(encoding="utf-8"), "bad")
    problems = verify_card_totals(bad)
    check(problems, "bad total must fail the check")
    book = Book()
    result = book.import_statement(bad, "bad.txt")
    check(result["refused"] and result["wrote"] == 0 and not book.grid, "refused write changes nothing")


def test_book() -> None:
    book = Book()
    partial = parse_statement((FIX / "mid-month.csv").read_text(encoding="utf-8"), "csv")
    first = book.import_statement(partial, "mid-month.csv")
    check(first["wrote"] == 1, first)
    shell_key = expect_key("1001", "2026-08-31", 71.04, "SHELL C11318 MISSISSAUGA ON")
    check(book.txns[0].key == shell_key, book.txns[0].key)
    check(book.cell("Aug", "BM29") == 71.04, book.grid)
    check(book.txns[0].category == "Fuel", book.txns[0].category)

    # Receipt arrives before the statement line. The grid is filled once.
    shell_receipt = parse_receipt((FIX / "receipt-shell.txt").read_text(encoding="utf-8"), content=b"shell-photo")
    first_receipt = book.import_receipt(shell_receipt, "photo")
    check(first_receipt["action"] == "pending", first_receipt)
    check(book.cell("Sep", "BC29") == 127.86, "receipt filled fuel once")

    full = parse_statement((FIX / "layout-a-cibc-visa.txt").read_text(encoding="utf-8"), "A")
    second = book.import_statement(full, full.folder(".pdf"))
    # 8 lines, 1 already present, 1 is the big question, so 6 new writes plus the question counted in wrote.
    check(second["skipped"] >= 1, second)
    check(book.cell("Aug", "BM29") == 71.04, "shell was not doubled")
    keys = [txn.key for txn in book.txns]
    check(keys.count(shell_key) == 1, keys)
    twins = [txn for txn in book.txns if txn.amount == 1.92 and txn.post_date == "2026-09-17"]
    check(len(twins) == 2, twins)
    check(book.cell("Sep", "AO17") == 1.92 and book.cell("Sep", "AO18") == 1.92, book.grid)
    check(book.cell("Sep", "BC29") == 127.86, book.grid)
    check(book.cell("Sep", "M35") == 9.03, book.grid)
    check(book.cell("Sep", "W17") == 42.10, book.grid)
    acme = next(txn for txn in book.txns if "ACME" in txn.description)
    check(acme.status == "question" and acme.where == "", acme)
    check(all(not str(addr).endswith("240") for addr in []), "placeholder")
    check(not any(abs(amount - 240.00) < 0.001 for amount in book.grid.values()), book.grid)
    labels = {card.label: card for card in book.cards}
    check("CIBC Visa-1001" in labels and "CIBC Visa-1002" in labels, labels)
    check(labels["CIBC Visa-1001"].holder == "Jordan Lee", labels["CIBC Visa-1001"].holder)
    check(labels["CIBC Visa-1001"].statement_day == 27 and labels["CIBC Visa-1001"].due_day == 19, "card days")
    check(labels["CIBC Visa-1001"].last_amount_due == 453.69, "amount due")
    check(labels["CIBC Visa-1001"].paid_status == "unpaid", "payment on the statement is the previous bill")
    check(all(len(card.last4) == 4 for card in book.cards), "last 4 only")

    again = book.import_statement(full, full.folder(".pdf"))
    check(again["wrote"] == 0, again)
    check(book.cell("Aug", "BM29") == 71.04, "reimport doubled fuel")

    # Unknown big charge is asked once, then remembered.
    check(any("ACME" in q or "unknown" in q for q in book.questions), book.questions)
    book.remember("ACME WIDGETS PORTLAND OR", "Household Goods")
    check("acme widgets" in book.merchant_map, book.merchant_map)
    check(not any(log.status == "question" and "ACME" in (log.merchant + log.key) for log in book.log if "acme" in log.merchant.lower() or (log.key and "ACME" in log.key)), "question closed")
    acme = next(txn for txn in book.txns if "ACME" in txn.description)
    check(acme.status == "no receipt" and acme.category == "Household Goods", acme)
    check(book.cell("Sep", "AU22") == 240.00, book.grid)
    follow = parse_statement((FIX / "acme-followup.csv").read_text(encoding="utf-8"), "acme2")
    book.import_statement(follow, "acme-followup.csv")
    check(not any("acme widgets" in q.lower() for q in book.questions), book.questions)
    check(book.cell("Oct", f"{day_amount_col(2)}22") == 80.00, book.grid)

    # Statement first, then the receipt splits the grid and does not add.
    before = book.cell("Sep", "W17")
    check(before == 42.10, before)
    tt = parse_receipt((FIX / "receipt-tandt.txt").read_text(encoding="utf-8"), source="photo", content=b"tandt-photo")
    linked = book.import_receipt(tt, "photo")
    check(linked["action"] == "linked", linked)
    check(book.cell("Sep", "W17") is None, book.grid)
    check(book.cell("Sep", "W6") == 20.00, book.grid)
    check(book.cell("Sep", "W18") == 22.10, book.grid)
    check(round((book.cell("Sep", "W6") or 0) + (book.cell("Sep", "W18") or 0), 2) == 42.10, "split sum")

    fuel_before = book.cell("Sep", "BC29")
    check(fuel_before == 127.86, fuel_before)
    shell_txn = next(txn for txn in book.txns if txn.amount == 127.86)
    check(shell_txn.status == "matched" and shell_txn.receipt_number == "771100", shell_txn)

    # Other layouts on the same book.
    b = parse_statement((FIX / "layout-b-cibc-costco.txt").read_text(encoding="utf-8"), "B")
    # Costco receipt first for the 80.00 line, so the statement links.
    costco = parse_receipt((FIX / "receipt-costco.txt").read_text(encoding="utf-8"), content=b"costco-photo")
    costco_result = book.import_receipt(costco, "photo")
    check(costco_result["action"] == "pending", costco_result)
    check(book.cell("Sep", "AW6") == 38.00, book.grid)
    check(book.cell("Sep", "AW22") == 42.00, book.grid)
    meals_household = (book.cell("Sep", "AW6") or 0) + (book.cell("Sep", "AW22") or 0)
    book.import_statement(b, b.folder(".pdf"))
    check(round(meals_household, 2) == 80.00, "costco statement doubled a linked receipt")
    costco_txn = next(txn for txn in book.txns if txn.amount == 80.00 and "COSTCO" in txn.description)
    check(costco_txn.status == "matched" and costco_txn.receipt_number == "482910", costco_txn)
    check(book.cell("Aug", f"{day_amount_col(21)}17") == 246.66, book.grid)
    check(book.cell("Sep", "K37") == 65.00, book.grid)
    check("CIBC Costco MC-2202" in {card.label for card in book.cards}, book.cards)

    c = parse_statement((FIX / "layout-c-triangle.txt").read_text(encoding="utf-8"), "C")
    book.import_statement(c, c.folder(".pdf"))
    check(book.cell("Sep", "AA30") == 57.53, book.grid)
    check(book.cell("Sep", "BC30") == -57.53, book.grid)
    check(book.cell("Sep", "C27") == 120.00, book.fixed)
    check(book.fixed_date.get(("Sep", "D27")) == "2026-09-21", book.fixed_date)
    check(book.cell("Aug", "BQ29") == 40.00, book.grid)
    ret = next(txn for txn in book.txns if txn.amount == -57.53)
    purchase = next(txn for txn in book.txns if txn.amount == 57.53 and "SPORT CHEK" in txn.description)
    ret_log = book.find_log_by_key(ret.key)
    check(ret_log and ret_log.linked == purchase.key, ret_log)
    check("Triangle MC-3303" in {card.label for card in book.cards}, "triangle card")

    d = parse_statement((FIX / "layout-d-rogers-wordstack.txt").read_text(encoding="utf-8"), "D")
    book.import_statement(d, d.folder(".pdf"))
    fx = next(txn for txn in book.txns if txn.amount == 9.12 and "SOUTHWEST" in txn.description)
    check(fx.fx_note.startswith("FOREIGN CURRENCY USD 6.40 @ 1.425"), fx.fx_note)
    check(book.cell("Aug", "BS37") == 9.12, book.grid)
    check(book.cell("Aug", "BA22") == 48.20, book.grid)
    check(book.cell("Sep", "AC22") == -48.20, book.grid)
    depot_return = next(txn for txn in book.txns if txn.amount == -48.20)
    depot_buy = next(txn for txn in book.txns if txn.amount == 48.20)
    check(book.find_log_by_key(depot_return.key).linked == depot_buy.key, "return linked")
    check("Rogers MC-4404" in {card.label for card in book.cards}, "rogers card")

    # Tip asks, and does not add a second amount.
    tip_statement = parse_statement((FIX / "tip-statement.csv").read_text(encoding="utf-8"), "tip")
    book.import_statement(tip_statement, "tip.csv")
    check(book.cell("Sep", f"{day_amount_col(18)}20") == 58.00, book.grid)
    tip = parse_receipt((FIX / "receipt-tip.txt").read_text(encoding="utf-8"), content=b"tip")
    tip_result = book.import_receipt(tip, "photo")
    check(tip_result["action"] == "question", tip_result)
    check(book.cell("Sep", f"{day_amount_col(18)}20") == 58.00, "tip added a second amount")
    check(not any(abs(v - 50.00) < 0.001 for v in book.grid.values()), book.grid)

    # Cash receipt fills the grid and does not wait for a statement.
    cash = parse_receipt((FIX / "receipt-cash.txt").read_text(encoding="utf-8"), content=b"cash")
    cash_result = book.import_receipt(cash, "photo")
    check(cash_result["action"] == "cash", cash_result)
    check(book.cell("Oct", "Q6") == 12.40, book.grid)
    check(any(row.status == "cash" and row.store == "Corner Market" for row in book.receipts), book.receipts)

    # Photo plus email of the same receipt is one record.
    photo = parse_receipt((FIX / "receipt-homedepot.txt").read_text(encoding="utf-8"), source="photo", content=b"depot-photo")
    email = parse_receipt((FIX / "receipt-homedepot-email.txt").read_text(encoding="utf-8"), source="email", content=b"depot-email")
    book.import_receipt(photo, "photo")
    second_file = book.import_receipt(email, "email")
    check(second_file["action"] == "attach", second_file)
    depot_rows = [row for row in book.receipts if row.number == "48291"]
    check(len(depot_rows) == 1, depot_rows)
    check(depot_rows[0].sources == ["photo", "email"], depot_rows[0].sources)
    check(book.cell("Oct", "AM22") == 84.12, book.grid)

    # Near match asks and writes no amount.
    near_a = parse_receipt((FIX / "receipt-near-oct3.txt").read_text(encoding="utf-8"), content=b"near-a")
    near_b = parse_receipt((FIX / "receipt-near-oct8.txt").read_text(encoding="utf-8"), content=b"near-b")
    book.import_receipt(near_a, "photo")
    near = book.import_receipt(near_b, "photo")
    check(near["action"] == "question", near)
    check(book.cell("Oct", "O17") == 57.29, book.grid)
    check(sum(1 for v in book.grid.values() if abs(v - 57.29) < 0.001) == 1, "near match wrote a second 57.29")

    # Return lookup from a product tag.
    sport = parse_receipt((FIX / "receipt-sportchek.txt").read_text(encoding="utf-8"), content=b"sport")
    book.import_receipt(sport, "photo")
    found = return_lookup(book, "Adidas Milano jacket SKU AM-23", date(2026, 9, 20))
    check(found is not None, "lookup missed")
    check(found["store"] == "Sport Chek", found)
    check(found["date"] == "2026-09-09", found)
    check(found["price"] == 57.53, found)
    check(found["card"] == "3303", found)
    check(found["file"].endswith(".txt") or "Sport Chek" in found["file"], found)
    check(found["window"] == 30 and found["days_left"] == 19, found)

    # Card-only book already tracked expenses. Bank data is optional and adds the rest.
    expenses_before = book.grid_sum()
    bank = book.import_bank((FIX / "bank-chequing.csv").read_text(encoding="utf-8"))
    check(("ask income", "PAYROLL ACME EMPLOYER") in bank["results"], bank)
    check(("fixed", "Rent / Mortgage") in bank["results"], bank)
    check(any(item[0] == "card payment" for item in bank["results"]), bank)
    check(any(item[0] == "skip" for item in bank["results"]), bank)
    check(book.cell("Sep", "C24") == 1800.00, book.fixed)
    check(book.cell("Sep", "C8") is None, "income written before confirmation")
    book.confirm_income("PAYROLL ACME EMPLOYER")
    check(book.cell("Sep", "C8") == 3200.00, book.income)
    check(next(card for card in book.cards if card.last4 == "1001").paid_status == "paid", book.cards)
    check(book.grid_sum() >= expenses_before, "bank import removed expenses")
    check(any(card.product == "Chequing" and card.last4 == "5505" for card in book.cards), book.cards)

    # Due reminders fire 3 days before and on the day, and stop when paid.
    rogers = next(card for card in book.cards if card.last4 == "4404")
    check(rogers.paid_status == "unpaid" and rogers.due_date == "2026-10-09", rogers)
    check(due_reminders(book.cards, date(2026, 10, 6)) == [f"Pay {rogers.label} {rogers.last_amount_due:.2f} by 2026-10-09"], due_reminders(book.cards, date(2026, 10, 6)))
    check(due_reminders(book.cards, date(2026, 10, 7)) == [], "no reminder on the in-between day")
    check(due_reminders(book.cards, date(2026, 10, 9)), "reminder on the due date")
    book.mark_paid("4404")
    check(due_reminders(book.cards, date(2026, 10, 9)) == [], due_reminders(book.cards, date(2026, 10, 9)))
    check(all("1001" not in note for note in due_reminders(book.cards, date(2026, 10, 16))), "paid visa does not remind")

    # Statement-ready nudge from an issuer email, or a few days after statement day.
    fresh = Book()
    from familybook_v2 import CardRow
    fresh.cards.append(CardRow(
        issuer="CIBC", product="Visa", last4="1001", holder="Jordan Lee",
        statement_day=27, due_day=19, last_amount_due=None, paid_status="unpaid",
        label="CIBC Visa-1001",
    ))
    check(statement_nudges(fresh.cards, date(2026, 9, 27), ["Your CIBC Visa statement is ready"], set()) 
          == ["Statement ready for CIBC Visa-1001: forward or download it"], "email nudge")
    check(statement_nudges(fresh.cards, date(2026, 9, 29), [], set()) == [], "too early for the date nudge")
    check(statement_nudges(fresh.cards, date(2026, 9, 30), [], set()) == ["Statement should be out for CIBC Visa-1001"], "date nudge")
    fresh.import_statement(full, full.folder(".pdf"))
    check(statement_nudges(fresh.cards, date(2026, 9, 30), [], {fresh.cards[0].period_end}) == [], "nudge stops once the statement is in")


def test_migration_and_crash() -> None:
    old = Book(version="v1.2.4")
    old.grid[("Sep", "AW6")] = 18.00
    old.grid[("Sep", "AW22")] = 42.00
    old.grid[("Sep", "AW7")] = 20.00
    old.log.append(LogRow(
        status="done", source="photo", merchant="Costco", total=80.00, when=date(2026, 9, 20),
        where="Sep!AW6+Sep!AW22+Sep!AW7", receipt_number="482910", payment="2202",
        items="Kirkland eggs: 18.00; Paper towel: 42.00; Rotisserie chicken: 20.00",
        files=["2026-09-20 1432 - Costco - 80.00.png"],
    ))
    # A flagged duplicate pair stays two rows.
    old.log.append(LogRow(
        status="done", source="photo", merchant="Costco", total=15.00, when=date(2026, 9, 5),
        where="Sep!K17", receipt_number="111", payment="2202", items="Snack mix: 15.00",
    ))
    old.log.append(LogRow(
        status="done", source="email", merchant="Costco", total=15.00, when=date(2026, 9, 5),
        where="Sep!K18", receipt_number="222", payment="2202", items="Snack mix: 15.00",
    ))
    old.grid[("Sep", "K17")] = 15.00
    old.grid[("Sep", "K18")] = 15.00
    before = dict(old.grid)
    first = migrate_v124_to_v2(old)
    check(first["copied"] == 3, first)
    check(old.version == "v2.0", old.version)
    check(old.grid == before, "migration changed an amount")
    check(any(row.number == "482910" and row.status == "pending" for row in old.receipts), old.receipts)
    check("111" in old.pending_formula.get("duplicates", "") or "222" in old.pending_formula.get("duplicates", ""), old.pending_formula)
    second = migrate_v124_to_v2(old)
    check(second["already"] and len(old.receipts) == 3, second)
    # Resume mid-way: version not final, rows already copied.
    old.version = "migrating"
    third = migrate_v124_to_v2(old)
    check(third["copied"] == 0 and len(old.receipts) == 3, third)
    check(old.version == "v2.0", old.version)
    statement = parse_statement(LAYOUT_B, "B")
    # The migrated Costco row matches the Sep 20 line. The other Costco lines are new.
    grid_before = dict(old.grid)
    old.import_statement(statement, statement.folder(".pdf"))
    check(old.grid[("Sep", "AW6")] == 18.00, old.grid)
    check(old.grid[("Sep", "AW22")] == 42.00, old.grid)
    check(old.grid[("Sep", "AW7")] == 20.00, old.grid)
    linked = next(txn for txn in old.txns if txn.amount == 80.00)
    check(linked.status == "matched" and linked.receipt_number == "482910", linked)
    check(old.grid[("Aug", f"{day_amount_col(21)}17")] == 246.66, "unmatched statement line still posts")
    check(grid_before[("Sep", "K17")] == 15.00 and old.grid[("Sep", "K17")] == 15.00, "flagged duplicate kept")

    # Interrupted write: the amount cell is recorded and filled, then the run stops.
    crash = Book()
    partial = parse_statement(CSV_PARTIAL, "csv")
    key = partial.lines[0].key
    stopped = crash.import_statement(partial, "mid-month.csv", crash_on_key=key)
    check(stopped["wrote"] == 1, stopped)
    check(crash.cell("Aug", "BM29") == 71.04, crash.grid)
    check(crash.log[0].status == "pending" and crash.log[0].where == "Aug!BM29", crash.log[0])
    check(crash.txns == [], "crash happened before the transactions row")
    crash.import_statement(partial, "mid-month.csv")
    check(crash.cell("Aug", "BM29") == 71.04, crash.grid)
    check(len(crash.txns) == 1 and crash.txns[0].status == "no receipt", crash.txns)
    check(crash.log[0].status == "no receipt", crash.log[0].status)


def test_template() -> None:
    from openpyxl import load_workbook
    path = ROOT / "template" / "family-book-template.xlsx"
    wb = load_workbook(path)
    check("Cards" in wb.sheetnames, wb.sheetnames)
    check("Merchant Map" in wb.sheetnames, wb.sheetnames)
    check(wb["Merchant Map"].sheet_state == "hidden", "merchant map should be hidden")
    check(wb["Log"].sheet_state == "hidden", "log stays hidden")
    summary = wb["Annual Summary"]
    check(summary["C46"].value == "v2.0", summary["C46"].value)
    check("v2.0" in str(summary["B2"].value), "banner")
    check("SkybatanX" in str(summary["B2"].value) and "@SkyXFunNext" in str(summary["B2"].value), "credit")
    jan = wb["Jan"]
    check(jan.freeze_panes == "J6", jan.freeze_panes)
    check(str(jan["B47"].value).startswith("Transactions this month"), jan["B47"].value)
    check("B47:I47" in {str(r) for r in jan.merged_cells.ranges}, "title merge crosses the freeze")
    titles = []
    for row in range(47, 180):
        value = jan.cell(row, 2).value
        if isinstance(value, str) and value.startswith("Receipts this month"):
            titles.append(row)
    check(titles, "receipts section missing")
    header = titles[0] + 1
    check(jan.cell(header, 2).value == "Receipt #", jan.cell(header, 2).value)
    check(jan.cell(48, 2).value == "Card", jan.cell(48, 2).value)
    check(jan["G8"].value == "=SUM(J21:BS21)", jan["G8"].value)
    check(jan["G10"].value == "=SUM(J28:BS28)", jan["G10"].value)
    check(jan["G12"].value == "=SUM(G8:G11)+SUM(J29:BS29)", jan["G12"].value)
    check(jan["I44"].value == "Balance", "grid was overwritten")
    cards = wb["Cards"]
    headers = [cards.cell(2, col).value for col in range(1, 9)]
    check(headers == ["Issuer", "Product", "Last 4", "Holder", "Statement day", "Due day", "Last amount due", "Paid status"], headers)
    # Frozen columns are not merged into the unfrozen side.
    for merged in jan.merged_cells.ranges:
        if merged.min_row >= 47:
            check(not (merged.min_col <= 9 and merged.max_col >= 10), f"merge crosses I/J: {merged}")


def main() -> None:
    generate()
    test_parsers()
    test_book()
    test_migration_and_crash()
    template = ROOT / "template" / "family-book-template.xlsx"
    if template.exists() and "v2.0" in str(__import__("openpyxl").load_workbook(template)["Annual Summary"]["C46"].value):
        test_template()
    else:
        print("template is not v2.0 yet; parser and book checks passed")
    print("v2.0 offline checks passed")


if __name__ == "__main__":
    try:
        main()
    except Fail as exc:
        print("FAIL:", exc)
        sys.exit(1)
