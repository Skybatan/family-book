# Family Book v2.0 test plan

This plan is for **Family Book Bot -tester**. That bot is connector-only. It uses Google Sheets or OneDrive and Excel. It does not run Python. It works only inside a Drive folder named exactly `Family Book TEST`. It must not open, write, or migrate a real `Family Book` folder.

The fixtures under `tests/v2.0/fixtures/` are synthetic. The name on every statement is Jordan Lee. The last 4 digits are 1001, 1002, 2202, 3303, 4404, and 5505. Do not replace them with a real card, a real address, or a real statement. If a fixture is missing, regenerate it from the repo with `python3 tests/v2.0/generate_and_check.py`. That script is the author's offline check. The tester does not need it to pass a case.

## How to read a result

Rows 1 to 44 are the number grid. Nothing below row 44 is in a total.

- Transactions title is the cell in column B that starts with `Transactions this month` (row 47 on a blank v2.0 sheet). The header is the next row. Data starts on the row after that.
- Receipts title starts with `Receipts this month` (row 150 on a blank sheet). The header is the next row.
- Transactions columns: B Card, C Trans date, D Post date, F Description, G Amount, I Category, J Receipt #. Helpers CA–CG: txn key, statement file, FX note, status, where written, issuer category, linked key.
- Receipts columns: B Receipt #, C Store, D Date & time, F Total, G Card/pay, then Item / Price / Category from column I. Column L is Item 2. Column M is the price of item 2. File is column AA. Helpers CA–CG: receipt key, pending duplicate (the CB header is `Pending duplicate`, and CB holds only that text), note, status, where written, return-window days, linked txn key.
- Day *d* amount column, with A as 1: column index `11 + 2*(d-1)`. Day 1 is K, day 2 is M, day 5 is S, day 7 is W, day 9 is AA, day 10 is AC, day 15 is AM, day 16 is AO, day 18 is AS, day 19 is AU, day 20 is AW, day 21 is AY, day 22 is BA, day 23 is BC, day 28 is BM, day 30 is BQ, day 31 is BS. The item column is the one to the left of the amount.
- When the transaction date and the post date are the same year, the month sheet and the day column are the **transaction date**. The key still uses the **post date**. When the years differ, the line goes in the post-date year's book, on the post date's month and day. The Trans date column still shows the purchase date. A Dec 31, 2025 purchase posted Jan 2, 2026 is on the 2026 January sheet, day 2 (`M29` for Fuel), not on a December sheet.

Status words, so the checks do not collide:

| Place | While the write is unfinished | After it is finished |
|---|---|---|
| Log column N | `pending` | `awaiting statement`, `cash`, `no receipt`, `matched`, `question`, or `refused` |
| Transactions helper status | | `matched`, `no receipt`, `question`, `superseded` |
| Receipts helper status | | `pending` (waiting for a statement), `matched`, `cash`, `question`, `superseded` |

A `question` row may show the amount in the Transactions section, because that section is not in a total. Where written stays blank, and the grid cell stays empty, until the user answers.

A card payment is a Transactions row, category `Card payment`, and not a grid amount. It applies to the latest statement for that card dated on or before the payment's post date. Paying that bill in full also marks every older unpaid bill for the card paid. A partial payment reduces only the latest bill, and the reminder continues. An overpayment is a credit on Cards. Nothing goes negative. A payment dated before every statement date does not count. Re-importing the same bank file does not pay a bill twice.

## Setup, once

1. Create `Family Book TEST` at the top of the test Drive. Do not use any other folder.
2. Copy `template/family-book-template.xlsx` into `Family Book TEST/Family Book - Templates/`.
3. Create `Family Book TEST/Family Book - 2026/` with a workbook named `Family Book - 2026`, a `receipts` folder, and a `statements` folder. Set Annual Summary `F5` to 2026. Confirm `C46` is `v2.0`, Jan `B47` starts with `Transactions this month` and is merged `B47:I47` only, Jan `G10` is `=SUM(J28:BS28)`, Jan `G12` is `=SUM(G8:G11)+SUM(J29:BS29)`, and Jan `I44` is `Balance`.
4. Create `Family Book TEST/Family Book - 2025/` the same way, with `F5` = 2025, for the year-cross case only.
5. Upload every file in `tests/v2.0/fixtures/` into `Family Book TEST/fixtures/`. Send the tester the file from that folder. Never send a real statement.

Use one 2026 workbook, called book T, for cases 1–18 and 21–22. Tip and acme-followup statements change Cards on book T. They are not the source for the reminder cases. Case 19 uses a fresh workbook, book R, that contains only layout D. Case 20 uses book N, with no statement imported yet. Case 23 uses book M. Case 24 uses book C. Cases 25–28 each use a fresh workbook. Do not mark a card paid on book T in order to finish case 19.

## Cases

### 1. Bad total is refused

- **Input:** `fixtures/bad-total.txt` as a pasted statement.
- **Expect:** no Transactions row and no grid amount. Aug `BM29` stays empty. It says the printed total for card 1001 ($99.99) does not match the lines ($71.04). The original file is still saved, with ` - not imported` before the extension: `Family Book TEST/Family Book - 2026/statements/CIBC Visa-1001/2026-09-27 statement - not imported.txt` (or `.pdf` if that was the file). The Log has one row, Status `refused`, and Source contains `card 1001 lines sum to 71.04, statement says 99.99`. No Statements bill is added.
- **Verify:** Aug has no 71.04. Cards has no last amount due from this file. The ` - not imported` file is in the statements folder.

### 2. Layout A, CIBC Visa, two cards

- **Input:** `fixtures/layout-a-cibc-visa.pdf` (the `.txt` or `.html` is the same statement if the PDF tool is unavailable).
- **Expect:**
  - Statement date 2026-09-27, period 2026-08-28 to 2026-09-27, due 2026-10-19, minimum 10.00, amount due 495.79. 495.79 is 453.69 for card 1001 plus 42.10 for card 1002. `Prepared for: Jordan Lee` is the account line. It is not printed beside either card number, so Holder stays blank.
  - File: `Family Book TEST/Family Book - 2026/statements/CIBC Visa-1001/2026-09-27 statement.pdf`.
  - 8 purchase rows plus 1 payment row. `PAYMENT THANK YOU` 200.00 is a Transactions row, category `Card payment`, with a generated key. It is not a grid amount.
  - Card 1001 lines sum to 453.69. Card 1002 lines sum to 42.10.
  - Cards shows the latest statement only: `CIBC Visa-1001` and `CIBC Visa-1002`, last 4 only, Holder blank, statement day 27, due day 19, last amount due 495.79, Paid status `unpaid`. Account cards is `1001, 1002` on both rows. The Statements sheet has one row, statement id `CIBC Visa-1001-2026-09-27`, due date 2026-10-19, amount due 495.79, Paid status `unpaid`. The T&T description stays `T&T`, not `T AND T`. Matching may still treat `&` as "and". The cell the person reads does not.
  - Aug `BM29` Fuel = 71.04 (Shell, trans 2026-08-28, post 2026-08-31). Key `1001|2026-08-31|71.04|SHELL C11318 MISSISSAUGA ON|1`. The description has no `Ý`.
  - Sep `M35` Entertainment = 9.03 (Netflix, trans Sep 2).
  - Sep `AI17` Snacks = 1.92 (Tim Hortons, trans Sep 13).
  - Sep `AO17` = 1.92 and Sep `AO18` = 1.92 (the twin Tim Hortons lines, post 2026-09-17). Keys end in `|1` and `|2`.
  - Wrapped Shell, trans Sep 23, post Sep 25, description `SHELL C11318 MISSISSAUGA ON`, key `1001|2026-09-25|127.86|SHELL C11318 MISSISSAUGA ON|1`. Grid Sep `BC29` = 127.86. Do this line in case 8 if you run case 8 first; do not write 127.86 twice.
  - T&T, card 1002, trans Sep 7, Sep `W17` Snacks = 42.10. Key uses last 4 `1002`.
  - ACME 240.00 is a question. Transactions may show 240.00. Where written is blank. No grid cell holds 240.00.
- **Verify:** the 200.00 row is category `Card payment` and the grid has no 200.00. Count of 71.04 in the whole grid is 1. Cards Paid status is `unpaid`. Holder is blank. Account cards reads `1001, 1002`.

If you will also run case 8 (receipt first), import `fixtures/mid-month.csv` and `fixtures/receipt-shell.txt` **before** this full statement. Case 3 and case 8 say the order. Do not import layout A twice before those cases.

### 3. Mid-month CSV, then the full statement

Run this **instead of** importing layout A first. On a fresh book T:

- **Input 1:** `fixtures/mid-month.csv`.
- **Expect:** one Transactions row. Aug `BM29` = 71.04. Category Fuel. Status `no receipt`. Key `1001|2026-08-31|71.04|SHELL C11318 MISSISSAUGA ON|1`. The file is a mid-month export (statement date 2026-09-15, period ending 2026-09-15, partial, no amount due). It does not create a Statements bill and it does not set Last amount due.
- **Input 2:** `fixtures/layout-a-cibc-visa.txt`.
- **Expect:** the Shell row is not added again. Aug `BM29` is still 71.04, not 142.08. The other layout A lines from case 2 appear once. The 200.00 payment is a `Card payment` row, not a grid amount. The Sep 27 statement is the bill.
- **Verify:** the txn key appears once on the Log (column P) and once in Transactions column CA.

### 4. Re-import the same statement

- **Input:** `fixtures/layout-a-cibc-visa.txt` again.
- **Expect:** zero new Transactions rows. Aug `BM29` still 71.04. Sep `M35` still 9.03. No second 1.92 pair.
- **Verify:** count the rows whose description contains `TIM HORTONS`. It is 3 (one on Sep 13, two on Sep 16).

### 5. Identical twins

Covered by layout A. The two Sep 16 Tim Hortons lines are the same last 4, post date, amount, and description.

- **Expect:** occurrence 1 and 2. Sep `AO17` = 1.92 and Sep `AO18` = 1.92. They are not collapsed.
- **Verify:** the two keys differ only in the final number.

### 6. Wrapped description

Covered by the Sep 23 Shell line in layout A. The city is on the next line.

- **Expect:** one line, description `SHELL C11318 MISSISSAUGA ON`, not two lines and not a description that stops at `C11318`.
- **Verify:** Transactions column F for amount 127.86.

### 7. Two cards on one account

Covered by layout A. Card 1001 and card 1002 are separate Transactions rows and separate Cards rows. One statement file, under `CIBC Visa-1001`, because 1001 is the first card. Both rows point at that file.

### 8. Receipt first, then the statement

On book T, before the full layout A import (after the mid-month CSV is fine):

- **Input:** `fixtures/receipt-shell.txt` (or `receipt-shell` text pasted as a receipt). Card 1001, total 127.86, date 2026-09-23, receipt 771100, one fuel item.
- **Expect:** Receipts row 771100, store Shell, helper status `pending`. Log status `awaiting statement`. Sep `BC29` Fuel = 127.86 once.
- **Then:** import layout A.
- **Expect:** the Sep 23 Shell Transactions row links to 771100. Status `matched` on both sides. Sep `BC29` is still 127.86. There is no second fuel cell for 127.86.
- **Verify:** grid search for 127.86 returns one cell.

### 9. Statement first, then the receipt, split by items

After layout A is in:

- **Input:** `fixtures/receipt-tandt.txt`. Store T&T, date 2026-09-07, total 42.10, card 1002, milk 20.00, chips 22.10, receipt 880021.
- **Expect:** the old Sep `W17` 42.10 is cleared. Sep `W6` Meals = 20.00. Sep `W18` Snacks = 22.10. The two cells sum to 42.10. Transactions category becomes `(split)`, Receipt # 880021, status `matched`. Receipts helper status `matched`.
- **Verify:** no cell holds 42.10, and `W6 + W18` = 42.10.

### 10. Layout B, CIBC Costco, and a receipt that arrives first

- **Input 1:** `fixtures/receipt-costco.txt` (also generated as `.png` and `.pdf`). Costco, 2026-09-20, receipt 482910, card 2202, total 80.00. Items: eggs 18.00, paper towel 42.00, chicken 20.00.
- **Expect:** eggs and chicken are both Meals, so they are **one** grid cell, the first empty Meals cell. Sep `AW6` Meals = 38.00. Sep `AW22` Household Goods = 42.00. Where written is `Sep!AW6+Sep!AW22`. The Receipts row still lists all three items and prices: Kirkland eggs 18.00, paper towel 42.00, and rotisserie chicken 20.00. Receipts status `pending`. This is the live import. The migration case further down keeps three separate cells on purpose. Do not expect 18 and 20 in two Meals cells here.
- **Input 2:** `fixtures/layout-b-cibc-costco.pdf`.
- **Expect:**
  - 3 purchase lines and 1 payment row of 100.00, category `Card payment`. It is not a grid amount. Lines 246.66 + 65.00 + 80.00 = 391.66.
  - Due date 2026-10-13. Statement date 2026-09-22. Period 2026-08-23 to 2026-09-22.
  - The 80.00 line links to 482910. Sep `AW6` stays 38.00 and Sep `AW22` stays 42.00.
  - Aug 21 Costco with no receipt: Aug `AY17` Snacks = 246.66.
  - Sep 1 annual renewal: Sep `K37` Other = 65.00 (not Snacks, even though the issuer says grocery).
  - Cards: `CIBC Costco MC-2202`, Paid status `unpaid`.
  - File: `statements/CIBC Costco MC-2202/2026-09-22 statement.pdf`.
- **Verify:** the 80.00 Transactions row is `matched` and does not add 80.00 to the grid.

### 11. Layout C, Triangle, payment skipped, return linked

- **Input:** `fixtures/layout-c-triangle.pdf`.
- **Expect:**
  - 4 lines, net 160.00. The Sport Chek purchase is one jacket line of 57.53, matching the receipt (Adidas Milano jacket 57.53). The detail block is that one jacket line, and the return detail is one line of −57.53. The detail block is not extra Transactions lines. No Transactions row contains `MERCHANDISE`.
  - `BANK PAYMENT` −50.00 is a Transactions row, category `Card payment`. It is not a grid amount.
  - Aug `BQ29` Fuel = 40.00 (Canadian Tire gas bar, Aug 30).
  - Sep `AA30` Clothing = 57.53 (Sport Chek, Sep 9).
  - Sep `C27` Property Tax = 120.00 and Sep `D27` = 2026-09-21. This is a fixed-expense row, not a daily cell.
  - Sep `BC30` Clothing = −57.53 (the return, Sep 23). Log column T (Linked to) is the purchase key of the +57.53 Sport Chek line.
  - Cards: `Triangle MC-3303`. Due 2026-10-19. Paid status `unpaid`.
- **Verify:** the return row's linked key equals the purchase row's txn key. Both amounts remain.

### 12. Layout D, Rogers, wrapped words and FX

- **Input:** `fixtures/layout-d-rogers-wordstack.pdf`. The text is one word per line.
- **Expect:**
  - 3 lines, net 9.12, plus a payment row of 30.00, category `Card payment`. It is not a grid amount.
  - Aug `BA22` Household Goods = 48.20 (Home Depot, trans Aug 22).
  - Aug `BS37` Other = 9.12. FX note starts with `FOREIGN CURRENCY USD 6.40 @ 1.425`. The 6.40 is not the grid amount. Description contains `SOUTHWEST HARBOR PARKI` and `HARME`.
  - Sep `AC22` Household Goods = −48.20, linked to the +48.20 purchase.
  - Due date 2026-10-09, minimum 25.00, statement date 2026-09-18, period 2026-08-19 to 2026-09-18, amount due 9.12.
  - Cards: `Rogers MC-4404`, Paid status `unpaid`.
  - File: `statements/Rogers MC-4404/2026-09-18 statement.pdf`.
- **Verify:** one Transactions row has amount 9.12, and no row has amount 6.40.

### 13. Year crossing a month and a year

Needs both `Family Book - 2026` and `Family Book - 2025`. Import into the 2026 book.

- **Input:** `fixtures/layout-year-cross.txt` (or `.pdf`). Statement date 2026-01-19. Period 2025-12-20 to 2026-01-19. Amount due 59.03. Due 2026-02-09.
- **Expect:**
  - The file and the Statements row live in the **2026** book, because the statement date is 2026-01-19. File: `Family Book TEST/Family Book - 2026/statements/CIBC Visa-1001/2026-01-19 statement.pdf`. Statements due date 2026-02-09, amount due 59.03.
  - Grocery 20.00, trans 2025-12-28, post 2025-12-30 (same year): Snacks on the **2025** December sheet, day 28, `BM17` = 20.00.
  - Gas 30.00, trans 2025-12-31, post 2026-01-02 (the years differ): Fuel on the **2026** January sheet, day 2, `M29` = 30.00. Trans date column still says 2025-12-31. Key `1001|2026-01-02|30.00|GAS BAR OAKVILLE ON|1`. It is not on the 2025 December sheet and not on a 2026 December sheet.
  - Netflix 9.03, trans 2026-01-05, post 2026-01-06 (same year): Entertainment on the **2026** January sheet, day 5, `S35` = 9.03.
  - The three lines sum to 59.03. No line is written in both years.
- **2025 book missing:** if `Family Book - 2025` is not there, the bot asks once, exactly `The 2025 book is not here yet. Should I create it?` It does not write the 20.00 grocery line. It does not ask a second time. The 2026 lines may still be written. After the 2025 book exists, a later import writes December `BM17` = 20.00 there.
- **Verify:** December 2025 holds 20.00 and does not hold 30.00. January 2026 holds 30.00 in `M29` and 9.03 in `S35`.

### 14. Unknown big charge, asked once, then remembered

After layout A, ACME 240.00 is the open question (case 2).

- **Input:** reply `Household Goods` for ACME WIDGETS.
- **Expect:** the question closes. Sep `AU22` Household Goods = 240.00. Merchant Map pattern `acme widgets`, category Household Goods. Transactions status `no receipt`.
- **Input 2:** `fixtures/acme-followup.csv`. ACME 80.00, trans 2026-10-02, post 2026-10-03, card 1001.
- **Expect:** no second question. Oct `M22` Household Goods = 80.00.
- **Verify:** the question list has no remaining ACME line. Merchant Map has one `acme widgets` row.

### 15. Receipt with a tip

- **Input 1:** `fixtures/tip-statement.csv`. Sun Palace, trans 2026-09-18, post 2026-09-19, 58.00, card 1001, restaurants.
- **Expect:** Sep `AS20` Dining Out = 58.00. Status `no receipt`.
- **Input 2:** `fixtures/receipt-tip.txt`. Same store and date, receipt total 50.00, receipt 55210.
- **Expect:** the bot asks. It does not write 50.00. Sep `AS20` stays 58.00. The receipt row is status `question`.
- **Verify:** the grid contains 58.00 once and does not contain 50.00.

### 16. Cash receipt

- **Input:** `fixtures/receipt-cash.txt`. Corner Market, 2026-10-04, cash, milk 6.40 and bread 6.00, total 12.40.
- **Expect:** both items are Meals, so one cell. Oct `Q6` = 12.40. Receipts helper status `cash`. Log status `cash`. No statement is required. A receipt with no card is `cash`.
- **Verify:** Card/pay is `cash`. The grid has 12.40 once.
- **Pasted text:** paste `STORE: Corner Market` / `DATE: 2026-10-04 09:00` / `TOTAL: 4.00` / `milk | 4.00` with no card line, on a fresh book if 12.40 is already in this one. Status is `cash`. The File label in Receipts column AA is `text`.

### 17. Photo plus email of the same receipt

- **Input 1:** `fixtures/receipt-homedepot.png` (or `.txt`). Home Depot, 2026-10-15, receipt 48291, card 1001, paint 60.00 and brush 24.12, total 84.12.
- **Expect:** one Receipts row. Both items are Household Goods, so one cell. Oct `AM22` = 84.12. Status `pending` / Log `awaiting statement`.
- **Input 2:** `fixtures/receipt-homedepot-email.txt`, sent as an email of the same receipt number.
- **Expect:** still one Receipts row for 48291. Sources are photo, then email. Oct `AM22` is still 84.12, not 168.24. The second file is attached. The amount is not written again.
- **Verify:** count Receipts rows with number 48291. It is 1. Log column F lists both files.

### 18. Near match asks

- **Input 1:** `fixtures/receipt-near-oct3.txt`. Costco, 2026-10-03, 57.29, no receipt number.
- **Expect:** Oct `O17` Snacks = 57.29.
- **Input 2:** `fixtures/receipt-near-oct8.txt`. Costco, 2026-10-08, 57.29, no receipt number. Five days apart, so this is rule 3, not rule 2.
- **Expect:** the bot asks one yes/no. It does not write a second 57.29. The second row is status `question` with Where written blank.
- **Verify:** the grid contains 57.29 exactly once.

### 19. Due reminders fire, then stop

Use book R, a fresh v2.0 workbook. Import only `fixtures/layout-d-rogers-wordstack.txt`. Do not use book T. Tip, acme-followup, and the bank file are not in this book. Ignore every card except Rogers MC-4404.

Rogers has statement due date 2026-10-09 and amount due 9.12. The reminder reads that full date from the Statements row, not the due day on Cards.

- **On 2026-10-06:** one reminder, `Pay Rogers MC-4404 9.12 by 2026-10-09.`
- **On 2026-10-07:** no reminder.
- **On 2026-10-09:** the same Rogers reminder, including the period.
- **Then:** the user says the Rogers bill is paid, or the tester marks that Statements row paid the way the skill does (`mark paid` for last 4 4404).
- **On 2026-10-09 again:** no Rogers reminder.
- **Verify:** the routine does not write a grid amount. Book T is unchanged, so case 21 still sees 4404 unpaid.

### 20. Statement-ready nudge

On book N, add Cards rows by hand or by answering the setup question: issuer CIBC, product Visa, last 4 1001 and authorized-user last 4 1002, both statement day 27, Account cards `1001, 1002`, no statement imported. The cycle date is the statement day, not "this month". Each account sends two nudges, then stops. Card 1002 does not get its own nudge.

- **On 2026-09-27, with or without an email:** one nudge, `Statement ready for CIBC Visa-1001: forward or download it.` An email subject `Your CIBC Visa statement is ready` on that day, with no attachment, is this same first nudge, not a second one. There is no second line for card 1002. The email is not a receipt. No Transactions row.
- **On 2026-09-28:** no nudge.
- **On 2026-09-29:** no nudge.
- **On 2026-09-30, still not imported:** the second nudge, `Statement should be out for CIBC Visa-1001.` There is no third nudge.
- **A statement day of 30** whose cycle is still missing nudges again on the 3rd of the next month (`Statement should be out for CIBC Visa-1001.`). Day plus 3 is allowed to cross the month.
- **Then:** import `fixtures/layout-a-cibc-visa.txt`, whose statement date is 2026-09-27.
- **On 2026-09-30 again:** no nudge for that cycle. Stop because that cycle's statement date is imported, not because the month matches today. Nothing more until the next cycle's statement day.
- **Verify:** the Statements sheet or the card's Statement file shows 2026-09-27. One nudge was sent for the account.

### 21. Bank account is optional, then bank data

Book T already has expenses from the card statements. That is the card-only book. Do not require a bank file to finish cases 1–18.

- **Input:** `fixtures/bank-chequing.csv`.
  - Payroll 3200.00 on Sep 1.
  - Mortgage −1800.00 on Sep 2.
  - `CIBC VISA PAYMENT 1001` −495.79 on Sep 15.
  - `TRANSFER TO SAVINGS` −500.00 on Sep 16.
- **Expect:**
  - Each line is a Transactions row with a generated key. The file is one Log row whose Content hash is the SHA-256 of the file. Importing the file again adds no row and does not pay a bill twice.
  - The bot asks before writing the payroll. Sep `C8` stays empty until you confirm. The payroll row's category becomes `Income` after you confirm.
  - After you confirm, Sep `C8` Income = 3200.00. Merchant Map remembers the payee as Income.
  - Sep `C24` Rent/Mortgage = 1800.00 (positive in the fixed-expense column). The Transactions category is `Mortgage`.
  - The transfer is a Transactions row, category `Transfer`. It is not an expense and not income, and it is not in the grid.
  - The visa payment is a Transactions row, category `Card payment`. It is not a grid amount. It is dated 2026-09-15, which is before the 2026-09-27 statement, so it does not pay that bill. If book T has no earlier 1001 bill, Cards and Statements for the Sep 27 bill stay `unpaid`, remaining 495.79, and Credit stays empty.
  - If the January 19, 2026 statement (amount due 59.03) is already on the book, it is the latest 1001 statement dated on or before Sep 15. The 495.79 payment pays that bill in full, marks every older unpaid 1001 bill paid, and notes Credit 436.76 on Cards (495.79 − 59.03). Remaining is 0, not negative. The Sep 27 bill stays `unpaid` at 495.79, and its reminder still fires when its due date has not passed.
  - Cards gains `North Bank Chequing-5505`. Holder stays blank unless a name is printed beside that account number.
  - Rogers 4404 is untouched. Case 19 does not run on this book, so 4404 stays `unpaid` if layout D was imported here, and it is simply absent if it was not.
  - No earlier expense cell changes. Aug `BM29` is still 71.04.
- **Verify:** read Sep `C8` before the confirmation (empty) and after (3200). Read the Statements row for the 2026-09-27 Visa bill (`unpaid`, remaining 495.79). On a book that also has the January 19 bill, that older row is `paid`, remaining 0, and Cards Credit for 1001 is 436.76. Import the bank file a second time and confirm Credit does not change.

### 22. Return lookup from a product photo

Do this twice, on two books, so the refund does not hide the open window.

**Open window.** A book that has only `fixtures/receipt-sportchek.txt` and does not have layout C. Sport Chek, 2026-09-09, receipt 5138, card 3303, Adidas Milano jacket 57.53, SKU AM-23.

- **Input:** `fixtures/product-tag-adidas.png` (or `product-tag.txt`) on 2026-09-20. The text is Adidas, Milano jacket, SKU AM-23.
- **Expect:** the reply includes the receipt file, store Sport Chek, date 2026-09-09, price 57.53, card 3303, return window 30 days, and 19 days left. The window is days from the purchase date. A known store policy is used when there is one, otherwise 30 days, and the reply says the window is an estimate. A return receipt has no window.
- **Verify:** 2026-09-09 plus 30 days is 2026-10-09. From Sep 20 that is 19 days.

**Already refunded.** On book T after layout C, the statement already has the Sport Chek return of −57.53 posted 2026-09-24. Look up the same tag on 2026-09-25, after that post.

- **Expect:** the reply is `Already refunded on 2026-09-24`. It does not say days left. The date is the refund line's post date.
- **Before the refund posts:** the same lookup on 2026-09-20 does not say `Already refunded`. The refund has not posted yet. The open window still applies.
- **No receipt saved:** on a book that has layout C and does not have the Sport Chek receipt, look up Sport Chek on 2026-09-25. The reply shows the Transactions line (store, date, price 57.53, card 3303) and says no receipt is saved. The refund line is `Already refunded on 2026-09-24`. The same lookup on 2026-09-20 says no receipt is saved and does not say already refunded.

### 23. Migration from v1.2.4, including a rerun

Use book M, a real v1.2.4 workbook. Set `C46` to `v1.2.4`. On a standard month sheet the title is row 47 (`Receipts this month`, merged B47:I47 only) and the header is row 48. Header columns: B Date & time, C Store, D Receipt/order #, F Items, G Total, I Category/cells written, J Payment, K File, L Source, S Logged by. The first receipt is row 49. Do not put the header on row 47, and do not look for Logged by in column L. Put these rows in before you migrate. Do not use book T.

Helper columns are always CA through CG (79 through 85). CB is the pending-duplicate column. Do not shift them. This book's data ends at or before BU (column 73), and the daily grid ends at BS (column 71, day 31). If the sheet is narrower than CG, add columns up to CG. Do not hide a column at or before BU.

| Receipt # | Store | Date | Total | Where written | Items | File |
|---|---|---|---|---|---|---|
| 482910 | Costco | 2026-09-20 | 80.00 | `Sep!AW6+Sep!AW22+Sep!AW7` | eggs 18.00; paper towel 42.00; chicken 20.00 | `2026-09-20 1432 - Costco - 80.00.png` |
| 111 | Costco | 2026-09-05 | 15.00 | `Sep!K17` | snack mix 15.00 | |
| *(blank)* | Costco | 2026-09-05 | 15.00 | `Sep!K18` | snack mix 15.00 | |

Grid, written before migration and left alone: Sep `AW6` = 18.00, Sep `AW22` = 42.00, Sep `AW7` = 20.00, Sep `K17` = 15.00, Sep `K18` = 15.00. Card on the receipt rows is 2202.

- **Run migration once.**
- **Expect:** `C46` becomes `v2.0`. Three Receipts rows, including 482910 with helper status `pending`. The five grid cells are unchanged. The blank receipt number stays blank and is not skipped. Resume skips a row by the receipt key in column CA, not by Receipt #. Where written keeps the sheet name, `Sep!AW6+Sep!AW22+Sep!AW7`. A cells-written value without a sheet name is saved with one. Its receipt key is `Costco|2026-09-05|15.00` (store, transaction date, and total to the cent). A numbered row's key is the number at that store, for example `Costco|482910`. Do not invent `R-0001`. `D46` contains `Pending duplicates:` and `Costco|2026-09-05|15.00`. Both rows of the pair are marked `pending duplicate` in helper column CB, not in column L. 111 and the blank row are the pair: same store, same total, dates within a day, and one side has no number. A row numbered 222 would be a different purchase and would not be flagged. Neither duplicate row is deleted. Neither 15.00 cell is cleared. The File link for 482910, including Log column F, points at the copy, `Family Book - 2026/receipts/2026-09-20 1432 - Costco - 80.00.png`, not at the original path. Log column F joins files with `, `.
- **Run migration again.**
- **Expect:** still three Receipts rows. No fourth row. `C46` stays `v2.0`.
- **Resume:** set `C46` back to `migrating` and run it again.
- **Expect:** zero rows copied. `C46` returns to `v2.0`. The grid is still the five cells above.
- **Then import** `fixtures/layout-b-cibc-costco.txt`.
- **Expect:** the 80.00 line links to 482910 and does not change `AW6`, `AW22`, or `AW7`. The unmatched 246.66 still posts to Aug `AY17` Snacks. The 15.00 cells stay. `K17` and `K18` are Snacks rows, so those 15.00 snack cells stay. The annual renewal is Other, Sep `K37` = 65.00, because the snack cells on day 1 are already used. The amount is 65.00 once. It is not written as a date.
- **Verify:** sum of Sep `AW6`, `AW22`, and `AW7` is still 80.00. Receipt 482910 status is `matched`.

### 24. Interrupted write, retried, no double count

Use book C, empty v2.0.

- **Input:** `fixtures/mid-month.csv`, and stop the write after the amount is in the grid and the Log row exists, before the Transactions row is appended. The tester simulates this by writing Log status `pending`, Where written `Aug!BM29`, the txn key, and Aug `BM29` = 71.04, and by not adding a Transactions row. (A real crash leaves the same trail. The skill says a retry reads the recorded cell.)
- **Input 2:** import `fixtures/mid-month.csv` again.
- **Expect:** the bot resumes the pending row. It does not pick a new Fuel cell. Aug `BM29` is still 71.04. One Transactions row, status `no receipt`. One Log row, status `no receipt`.
- **Verify:** the grid contains 71.04 once. Transactions has one Shell row.

### 25. Blank amount on a reminder

Use a fresh book. Paste a CIBC Visa statement for card 1002 only, statement date 2026-09-27, due 2026-10-19, with the T&T line of 42.10 and **no Amount Due line**.

- **Expect:** no Statements bill, because the paste has no amount due. On 2026-10-16 there is no reminder.
- **A bill row that does exist with both amount cells blank** still reminds with exactly `Pay CIBC Visa-1002 check your statement for the amount by 2026-10-19.` The amount words are not blank, and the text is not `Pay CIBC Visa-1002  by 2026-10-19.` This paste does not create that row.

### 26. Two unpaid bills, then a partial payment

Use a fresh book. Import two full statements for CIBC Visa-1001, both with an amount due, both due 2026-10-19. A partial flag would not create these bills.

1. Statement date 2026-08-27, amount due 40.00, one Shell line of 40.00.
2. Statement date 2026-09-27, amount due 71.04, one Tim Hortons line of 71.04.

- **Expect:** two Statements rows, both `unpaid`. Cards shows the latest only: last amount due 71.04. The August bill is still on Statements.
- **On 2026-10-16:** both reminders, `Pay CIBC Visa-1001 40.00 by 2026-10-19.` and `Pay CIBC Visa-1001 71.04 by 2026-10-19.`
- **A payment on 2026-07-01** of 40.00 (`CIBC VISA PAYMENT 1001`) does not change either bill. It is before both statement dates.
- **A payment on 2026-09-01** of 15.00 pays down the latest bill dated on or before that day, which is August. August remaining becomes 25.00 and stays `unpaid`. September is after Sep 1, so it stays 71.04. The next Oct 16 reminder for the August bill is `Pay CIBC Visa-1001 25.00 by 2026-10-19.`
- **Verify:** Cards still shows 71.04. Both Statements rows are still there.

### 27. A refused import is still saved

Use a fresh book if case 1 already used book T. Input is `fixtures/bad-total.txt`.

- **Expect:** the same refusal as case 1. The saved name ends with `statement - not imported.txt` (or `.pdf`). Log Status is `refused` and the reason includes `99.99`. No grid amount.
- **Verify:** the file is in `statements/CIBC Visa-1001/`. There is no Statements bill for it.

### 28. File name collision

Use a fresh book. Import `fixtures/layout-a-cibc-visa.pdf`. The file is `Family Book - 2026/statements/CIBC Visa-1001/2026-09-27 statement.pdf`.

- **Then** import a different statement for the same card and the same statement date (different bytes, not a re-send of layout A).
- **Expect:** the bot asks which file to keep. It does not save `2026-09-27 statement - 2.pdf` and it does not replace the first bill. The same key or the same hash, including importing layout A again, is a no-op and adds no suffix.
- **Verify:** the first file is unchanged. There is still one Statements row for 2026-09-27.

## Done

Every case above has an input file, a section, a column or a grid cell, and an amount. A case fails when a second import adds an amount, when a payment becomes an expense, when a question writes the grid, or when a migration changes a number the user already entered.

The fixtures are fake. Do not commit a real statement, a real name, a real address, or a real last 4 into this repo.

Made by SkybatanX (@SkyXFunNext).
