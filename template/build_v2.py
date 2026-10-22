#!/usr/bin/env python3
"""Bring template/family-book-template.xlsx to v2.0.

The number grid on each month sheet (rows 1-44, including its formulas)
stays as it was in v1.2.4. Below it, the receipt list becomes a Transactions
section and then a Receipts section. Cards is added, and Merchant Map and
Statements are added as hidden sheets. Run from the repo root:

    python3 template/build_v2.py
"""

from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "template" / "family-book-template.xlsx"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

NAVY = "1F4E79"
PALE = "D6E3F0"
LINE = "8FA8C4"
MONEY = '#,##0.00_);[Red](#,##0.00)'

TITLE_FONT = Font(name="Arial", size=14, bold=True, color="FFFFFF")
TITLE_FILL = PatternFill("solid", fgColor=NAVY)
HEADER_FONT = Font(name="Arial", size=10, bold=True, color=NAVY)
HEADER_FILL = PatternFill("solid", fgColor=PALE)
THIN = Border(
    left=Side(style="thin", color=LINE),
    right=Side(style="thin", color=LINE),
    top=Side(style="thin", color=LINE),
    bottom=Side(style="thin", color=LINE),
)
WRAP = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

TXN_HEADERS = {
    2: "Card",
    3: "Trans date",
    4: "Post date",
    6: "Description",
    7: "Amount",
    9: "Category",
    10: "Receipt #",
    79: "Txn key",
    80: "Statement file",
    81: "FX note",
    82: "Status",
    83: "Where written",
    84: "Issuer category",
    85: "Linked key",
}
RECEIPT_HEADERS = {
    2: "Receipt #",
    3: "Store",
    4: "Date & time",
    6: "Total",
    7: "Card/pay",
}
# Six item groups, then the file. Columns E and H stay empty on every row.
for index in range(6):
    start = 9 + index * 3  # I, L, O, R, U, X
    RECEIPT_HEADERS[start] = f"Item {index + 1}"
    RECEIPT_HEADERS[start + 1] = "Price"
    RECEIPT_HEADERS[start + 2] = "Category"
RECEIPT_HEADERS[27] = "File"  # column AA
RECEIPT_HEADERS[79] = "Receipt key"
RECEIPT_HEADERS[80] = "File list"
RECEIPT_HEADERS[81] = "Note"
RECEIPT_HEADERS[82] = "Status"
RECEIPT_HEADERS[83] = "Where written"
RECEIPT_HEADERS[84] = "Return window days"
RECEIPT_HEADERS[85] = "Linked txn key"

TXN_TITLE_ROW = 47
TXN_HEADER_ROW = 48
RECEIPT_TITLE_ROW = 150
RECEIPT_HEADER_ROW = 151

BANNER = (
    "Family Book v2.0 by SkybatanX: a yearly family income & expense book run by your personal Grok Bot.\n"
    "The bot sets up each year's book and logs spending from card statements, bank transactions when you share them, and receipts.\n"
    "Each month keeps the number grid, then a Transactions section and a Receipts section. The same purchase is never added twice.\n"
    "Follow @SkyXFunNext on X for more templates and fun!"
)
LOG_NOTE = (
    "Authoritative dedupe list for Family Book bots (v2.0). One row per purchase. Do not edit or delete rows. "
    "A duplicate the user confirms, and an answered question, is marked superseded in column N and kept. "
    "Column E is Where written: the amount cell is chosen and recorded here before the amount is written. "
    "A retry reads that cell and does not pick a new row. Column N is Status: pending (write in progress), "
    "question (an open yes/no, nothing written into the grid), awaiting statement, no receipt, matched, cash, done, or superseded. "
    "Column O is the SHA-256 of each saved file. Columns P to V hold the statement key (last4, post date, amount, "
    "normalized description, occurrence), the card label, the post date, the FX note, the linked receipt or purchase, "
    "the statement file, and the section row. The same purchase is one Transactions row, one Receipts row, or both, "
    "and it is never added to the grid twice."
)


def style_title(ws, row):
    for col in range(2, 10):
        cell = ws.cell(row, col)
        cell.font = TITLE_FONT
        cell.fill = TITLE_FILL
        cell.alignment = LEFT
    ws.row_dimensions[row].height = 40
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=9)


def style_header(ws, row, columns):
    for col in columns:
        cell = ws.cell(row, col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = WRAP
        cell.border = THIN
    ws.row_dimensions[row].height = 32


def clear_old_list(ws):
    for merged in list(ws.merged_cells.ranges):
        if merged.min_row >= 47:
            ws.unmerge_cells(str(merged))
    for row in ws.iter_rows(min_row=47, max_row=max(ws.max_row, 47), max_col=30):
        for cell in row:
            cell.value = None
    for col in range(79, 86):
        for row in range(47, 152):
            ws.cell(row, col).value = None


def build_month(ws):
    clear_old_list(ws)
    ws.cell(TXN_TITLE_ROW, 2).value = (
        "Transactions this month\n"
        "One row per posted line. These rows are not included in the totals above. Payments are not listed."
    )
    style_title(ws, TXN_TITLE_ROW)
    for col, header in TXN_HEADERS.items():
        ws.cell(TXN_HEADER_ROW, col).value = header
    style_header(ws, TXN_HEADER_ROW, TXN_HEADERS)
    for row in range(49, 149):
        ws.cell(row, 7).number_format = MONEY
    ws.cell(RECEIPT_TITLE_ROW, 2).value = (
        "Receipts this month\n"
        "One row per receipt. These rows are not included in the totals above. "
        "A linked receipt does not add a second amount."
    )
    style_title(ws, RECEIPT_TITLE_ROW)
    for col, header in RECEIPT_HEADERS.items():
        ws.cell(RECEIPT_HEADER_ROW, col).value = header
    style_header(ws, RECEIPT_HEADER_ROW, RECEIPT_HEADERS)
    price_cols = [10, 13, 16, 19, 22, 25]
    for row in range(152, 302):
        ws.cell(row, 6).number_format = MONEY
        for col in price_cols:
            ws.cell(row, col).number_format = MONEY
    # Helpers sit past the daily grid (day 31 is BS) so hiding them cannot hide a day.
    for col in range(79, 86):
        ws.column_dimensions[get_column_letter(col)].hidden = True


def add_cards(wb):
    if "Cards" in wb.sheetnames:
        del wb["Cards"]
    ws = wb.create_sheet("Cards", 0)
    # Keep Annual Summary first. create_sheet at 0 moves Cards before it, so move it back.
    wb.move_sheet(ws, offset=len(wb.sheetnames) - 1)
    ws["A1"] = (
        "Cards. One row per card or bank account. Store the last 4 only, never a full number. "
        "Paid status stops the due reminder. Statement day and due day are the usual day of the month."
    )
    ws.merge_cells("A1:H1")
    ws["A1"].font = TITLE_FONT
    ws["A1"].fill = TITLE_FILL
    ws["A1"].alignment = LEFT
    ws.row_dimensions[1].height = 40
    headers = [
        "Issuer", "Product", "Last 4", "Holder", "Statement day", "Due day",
        "Last amount due", "Paid status", "Card label", "Last statement date",
        "Period start", "Period end", "Minimum payment", "Statement file",
    ]
    for col, header in enumerate(headers, 1):
        ws.cell(2, col).value = header
    style_header(ws, 2, range(1, len(headers) + 1))
    for row in range(3, 30):
        ws.cell(row, 7).number_format = MONEY
        ws.cell(row, 13).number_format = MONEY
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = "A2:N2"
    widths = [16, 16, 12, 20, 16, 12, 18, 14, 24, 20, 16, 16, 18, 40]
    for index, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(index)].width = width
    paid = DataValidation(type="list", formula1='"unpaid,paid"', allow_blank=True)
    paid.add("H3:H30")
    ws.add_data_validation(paid)


def add_hidden_table(wb, name, note, headers):
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)
    ws["A1"] = note
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=min(8, len(headers)))
    ws["A1"].font = TITLE_FONT
    ws["A1"].fill = TITLE_FILL
    ws["A1"].alignment = LEFT
    ws.row_dimensions[1].height = 40
    for col, header in enumerate(headers, 1):
        ws.cell(2, col).value = header
    style_header(ws, 2, range(1, len(headers) + 1))
    ws.freeze_panes = "A3"
    ws.sheet_state = "hidden"
    return ws


def extend_log(wb):
    ws = wb["Log"]
    extra = [
        (16, "Txn key"),
        (17, "Card"),
        (18, "Post date"),
        (19, "FX note"),
        (20, "Linked to"),
        (21, "Statement file"),
        (22, "Section row"),
    ]
    for col, header in extra:
        cell = ws.cell(1, col)
        cell.value = header
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = WRAP
    ws["H1"] = LOG_NOTE
    ws["H1"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.sheet_state = "hidden"


def main():
    wb = load_workbook(PATH)
    jan = wb["Jan"]
    # The grid above the new sections is the v1.2.4 grid. Refuse to run twice blindly
    # if a formula we depend on has already been lost.
    assert jan["G10"].value == "=SUM(J28:BS28)"
    assert jan["G12"].value == "=SUM(G8:G11)+SUM(J29:BS29)"
    assert jan["I44"].value == "Balance"
    assert jan.freeze_panes == "J6"
    summary = wb["Annual Summary"]
    summary["B2"] = BANNER
    summary["B2"].alignment = Alignment(wrap_text=True, vertical="center")
    summary["C46"] = "v2.0"
    summary["B24"] = "Income offset"
    for name in MONTHS:
        wb[name]["B18"] = "Income offset"
        build_month(wb[name])
    add_cards(wb)
    add_hidden_table(
        wb, "Merchant Map",
        "Learned merchant to category map. Hidden helper. A correction is written once and then reused. Do not delete rows.",
        ["Pattern", "Category", "Source", "Last 4", "Confirmed", "Example", "Updated"],
    )
    add_hidden_table(
        wb, "Statements",
        "One row per imported statement. A second import of the same period adds nothing. Hidden helper.",
        ["Statement id", "Issuer", "Product", "Last 4s", "Period start", "Period end",
         "Statement date", "Due date", "Minimum", "Amount due", "Amount remaining",
         "File", "Paid status"],
    )
    extend_log(wb)
    # Cards was created at the end. Annual Summary stays the first sheet.
    order = ["Annual Summary", *MONTHS, "Holidays", "Cards", "Log", "Merchant Map", "Statements"]
    for index, name in enumerate(order):
        current = wb.sheetnames.index(name)
        wb.move_sheet(name, offset=index - current)
    wb.save(PATH)
    check = load_workbook(PATH)
    assert check["Annual Summary"]["C46"].value == "v2.0"
    assert check["Jan"]["G8"].value == "=SUM(J21:BS21)"
    assert check["Jan"]["G10"].value == "=SUM(J28:BS28)"
    assert str(check["Jan"]["B47"].value).startswith("Transactions this month")
    assert check["Merchant Map"].sheet_state == "hidden"
    assert check["Cards"].sheet_state == "visible"
    print("template updated to v2.0")


if __name__ == "__main__":
    main()
