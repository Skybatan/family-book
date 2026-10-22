# Family Book v2.0 test plan

This plan is for **Family Book Bot -tester**. That bot is connector-only. It uses Google Sheets or OneDrive and Excel. It does not run Python. It works only inside a Drive folder named exactly `Family Book TEST`. It must not open, write, or migrate a real `Family Book` folder.

The fixtures under `tests/v2.0/fixtures/` are synthetic. The name on every statement is Jordan Lee. The last 4 digits are 1001, 1002, 2202, 3303, 4404, and 5505. Do not replace them with a real card, a real address, or a real statement. If a fixture is missing, regenerate it from the repo with `python3 tests/v2.0/generate_and_check.py`. That script is the author's offline check. The tester does not need it to pass a case.

## How to read a result

Rows 1 to 44 are the number grid. Nothing below row 44 is in a total.

- Transactions title is the cell in column B that starts with `Transactions this month` (row 47 on a blank v2.0 sheet). The header is the next row. Data starts on the row after that.
- Receipts title starts with `Receipts this month` (row 150 on a blank sheet). The header is the next row.
- Transactions columns: B Card, C Trans date, D Post date, F Description, G Amount, I Category, J Receipt #. Helpers CA–CG: txn key, statement file, FX note, status, where written, issuer category, linked key.
- Receipts columns: B Receipt #, C Store, D Date & time, F Total, G Card/pay, items from column I, File in column AA. Helpers CA–CG: receipt key, file list, note, status, where written, return-window days, linked txn key.
- Day *d* amount column, with A as 1: column index `11 + 2*(d-1)`. Day 1 is K, day 2 is M, day 7 is W, day 9 is AA, day 10 is AC, day 15 is AM, day 16 is AO, day 18 is AS, day 19 is AU, day 20 is AW, day 21 is AY, day 22 is BA, day 23 is BC, day 28 is BM, day 30 is BQ, day 31 is BS. The item column is the one to the left of the amount.
- The month sheet is the **transaction date**. The key uses the **post date**. A Dec 31 purchase posted Jan 2 is on the December sheet.

Status words, so the checks do not collide:

| Place | While the write is unfinished | After it is finished |
|---|---|---|
| Log column N | `pending` | `awaiting statement`, `cash`, `no receipt`, `matched`, or `question` |
| Transactions helper status | | `matched`, `no receipt`, `question`, `superseded` |
| Receipts helper status | | `pending` (waiting for a statement), `matched`, `cash`, `question`, `superseded` |

A `question` row may show the amount in the Transactions section, because that section is not in a total. Where written stays blank, and the grid cell stays empty, until the user answers.

A payment printed on the statement being imported paid the **previous** bill. It does not set Paid status to `paid`.

## Setup, once

1. Create `Family Book TEST` at the top of the test Drive. Do not use any other folder.
2. Copy `template/family-book-template.xlsx` into `Family Book TEST/Family Book - Templates/`.
3. Create `Family Book TEST/Family Book - 2026/` with a workbook named `Family Book - 2026`, a `receipts` folder, and a `statements` folder. Set Annual Summary `F5` to 2026. Confirm `C46` is `v2.0`, Jan `B47` starts with `Transactions this month` and is merged `B47:I47` only, Jan `G10` is `=SUM(J28:BS28)`, Jan `G12` is `=SUM(G8:G11)+SUM(J29:BS29)`, and Jan `I44` is `Balance`.
4. Create `Family Book TEST/Family Book - 2025/` the same way, with `F5` = 2025, for the year-cross case only.
5. Upload every file in `tests/v2.0/fixtures/` into `Family Book TEST/fixtures/`. Send the tester the file from that folder. Never send a real statement.

Use one 2026 workbook, called book T, for cases 1–22 in order. Use a second 2026 workbook, book M, for migration. Use a third, book C, for the interrupted write. Use a fourth, book N, for the statement nudge before any statement is imported.

## Cases

### 1. Bad total is refused

- **Input:** `fixtures/bad-total.txt` as a pasted statement.
- **Expect:** the bot writes nothing. No Transactions row, no grid amount, Aug `BM29` empty. It says the printed total for card 1001 ($99.99) does not match the lines ($71.04).
- **Verify:** Aug has no 71.04. Cards has no new row, or the row has no last amount due.

### 2. Layout A, CIBC Visa, two cards

- **Input:** `fixtures/layout-a-cibc-visa.pdf` (the `.txt` or `.html` is the same statement if the PDF tool is unavailable).
- **Expect:**
  - Statement date 2026-09-27, period 2026-08-28 to 2026-09-27, due 2026-10-19, minimum 10.00, amount due 453.69, holder Jordan Lee.
  - File: `Family Book TEST/Family Book - 2026/statements/CIBC Visa-1001/2026-09-27 statement.pdf`.
  - 8 Transactions rows and 1 skipped payment (`PAYMENT THANK YOU` 200.00 is not a row and not a grid amount).
  - Card 1001 lines sum to 453.69. Card 1002 lines sum to 42.10.
  - Cards: `CIBC Visa-1001` and `CIBC Visa-1002`, last 4 only, holder Jordan Lee, statement day 27, due day 19, last amount due 453.69 on 1001, Paid status `unpaid`.
  - Aug `BM29` Fuel = 71.04 (Shell, trans 2026-08-28, post 2026-08-31). Key `1001|2026-08-31|71.04|SHELL C11318 MISSISSAUGA ON|1`. The description has no `Ý`.
  - Sep `M35` Entertainment = 9.03 (Netflix, trans Sep 2).
  - Sep `AI17` Snacks = 1.92 (Tim Hortons, trans Sep 13).
  - Sep `AO17` = 1.92 and Sep `AO18` = 1.92 (the twin Tim Hortons lines, post 2026-09-17). Keys end in `|1` and `|2`.
  - Wrapped Shell, trans Sep 23, post Sep 25, description `SHELL C11318 MISSISSAUGA ON`, key `1001|2026-09-25|127.86|SHELL C11318 MISSISSAUGA ON|1`. Grid Sep `BC29` = 127.86. Do this line in case 8 if you run case 8 first; do not write 127.86 twice.
  - T&T, card 1002, trans Sep 7, Sep `W17` Snacks = 42.10. Key uses last 4 `1002`.
  - ACME 240.00 is a question. Transactions may show 240.00. Where written is blank. No grid cell holds 240.00.
- **Verify:** count Transactions rows with amount not equal to 200. Count of 71.04 in the whole grid is 1. Cards Paid status is `unpaid`.

If you will also run case 8 (receipt first), import `fixtures/mid-month.csv` and `fixtures/receipt-shell.txt` **before** this full statement. Case 3 and case 8 say the order. Do not import layout A twice before those cases.

### 3. Mid-month CSV, then the full statement

Run this **instead of** importing layout A first. On a fresh book T:

- **Input 1:** `fixtures/mid-month.csv`.
- **Expect:** one Transactions row. Aug `BM29` = 71.04. Category Fuel. Status `no receipt`. Key `1001|2026-08-31|71.04|SHELL C11318 MISSISSAUGA ON|1`.
- **Input 2:** `fixtures/layout-a-cibc-visa.txt`.
- **Expect:** the Shell row is not added again. Aug `BM29` is still 71.04, not 142.08. The other layout A lines from case 2 appear once. The skipped payment is still skipped.
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
- **Expect:** eggs and chicken are both Meals, so they are **one** cell. Sep `AW6` Meals = 38.00. Sep `AW22` Household Goods = 42.00. Receipts status `pending`. This is the live import. The migration case further down keeps three separate cells on purpose. Do not expect 18 and 20 in two Meals cells here.
- **Input 2:** `fixtures/layout-b-cibc-costco.pdf`.
- **Expect:**
  - 3 purchase lines and 1 skipped payment of 100.00. Lines 246.66 + 65.00 + 80.00 = 391.66.
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
  - 4 lines, net 160.00. The Sport Chek "Details of your store purchases" block is not extra lines. No Transactions row contains `MERCHANDISE`.
  - `BANK PAYMENT` −50.00 is skipped. It is not a Transactions row and not a grid amount.
  - Aug `BQ29` Fuel = 40.00 (Canadian Tire gas bar, Aug 30).
  - Sep `AA30` Clothing = 57.53 (Sport Chek, Sep 9).
  - Sep `C27` Property Tax = 120.00 and Sep `D27` = 2026-09-21. This is a fixed-expense row, not a daily cell.
  - Sep `BC30` Clothing = −57.53 (the return, Sep 23). Log column T (Linked to) is the purchase key of the +57.53 Sport Chek line.
  - Cards: `Triangle MC-3303`. Due 2026-10-19. Paid status `unpaid`.
- **Verify:** the return row's linked key equals the purchase row's txn key. Both amounts remain.

### 12. Layout D, Rogers, wrapped words and FX

- **Input:** `fixtures/layout-d-rogers-wordstack.pdf`. The text is one word per line.
- **Expect:**
  - 3 lines, net 9.12, plus a skipped payment of 30.00.
  - Aug `BA22` Household Goods = 48.20 (Home Depot, trans Aug 22).
  - Aug `BS37` Other = 9.12. FX note starts with `FOREIGN CURRENCY USD 6.40 @ 1.425`. The 6.40 is not the grid amount. Description contains `SOUTHWEST HARBOR PARKI` and `HARME`.
  - Sep `AC22` Household Goods = −48.20, linked to the +48.20 purchase.
  - Due date 2026-10-09, minimum 25.00, statement date 2026-09-18, period 2026-08-19 to 2026-09-18, amount due 9.12.
  - Cards: `Rogers MC-4404`, Paid status `unpaid`.
  - File: `statements/Rogers MC-4404/2026-09-18 statement.pdf`.
- **Verify:** one Transactions row has amount 9.12, and no row has amount 6.40.

### 13. Year crossing a month and a year

- **Input:** `fixtures/layout-year-cross.txt` (or `.pdf`). Statement date 2026-01-19. Period 2025-12-20 to 2026-01-19. Amount due 59.03. Due 2026-02-09.
- **Expect:**
  - File under `Family Book TEST/Family Book - 2026/statements/CIBC Visa-1001/2026-01-19 statement.pdf` (the statement date's year).
  - Grocery 20.00, trans 2025-12-28, post 2025-12-30: Snacks on the **2025** December sheet.
  - Gas 30.00, trans 2025-12-31, post 2026-01-02: Fuel on the **2025** December sheet. Key `1001|2026-01-02|30.00|GAS BAR OAKVILLE ON|1`.
  - Netflix 9.03, trans 2026-01-05: Entertainment on the **2026** January sheet.
  - The three lines sum to 59.03. No line is written on both years.
- **Verify:** open both workbooks. December 2025 holds 20.00 and 30.00. January 2026 holds 9.03.

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
- **Expect:** both items are Meals, so one cell. Oct `Q6` = 12.40. Receipts helper status `cash`. Log status `cash`. No statement is required.
- **Verify:** Card/pay is `cash`. The grid has 12.40 once.

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

Rogers MC-4404 has due date 2026-10-09, last amount due 9.12, Paid status `unpaid`, after layout D. Visa 1001 is still unpaid until case 21.

- **On 2026-10-06:** one reminder, `Pay Rogers MC-4404 9.12 by 2026-10-09`.
- **On 2026-10-07:** no reminder.
- **On 2026-10-09:** the Rogers reminder again.
- **Then:** the user says the Rogers bill is paid, or the tester sets Cards Paid status for 4404 to `paid` the way the skill does (`mark paid`).
- **On 2026-10-09 again:** no Rogers reminder.
- **On 2026-10-16:** no reminder for a card whose Paid status is `paid`. Visa 1001's due day is 19, so Oct 16 is its three-day reminder only while 1001 is unpaid. After case 21 marks 1001 paid, Oct 16 sends nothing for 1001.
- **Verify:** read Cards Paid status before and after. The routine does not write a grid amount.

### 20. Statement-ready nudge

On book N, add one Cards row by hand or by answering the setup question: issuer CIBC, product Visa, last 4 1001, statement day 27, no statement imported.

- **Input:** an email subject `Your CIBC Visa statement is ready` on 2026-09-27, with no attachment.
- **Expect:** one nudge, `Statement ready for CIBC Visa-1001: forward or download it`. The email is not a receipt. No Transactions row.
- **On 2026-09-29, no email:** no date nudge. Three days have not passed.
- **On 2026-09-30, no email:** `Statement should be out for CIBC Visa-1001`.
- **Then:** import `fixtures/layout-a-cibc-visa.txt`, whose statement date is 2026-09-27.
- **On 2026-09-30 again:** no nudge for 1001.
- **Verify:** the Statements sheet or the card's Statement file shows 2026-09-27.

### 21. Bank account is optional, then bank data

Book T already has expenses from the card statements. That is the card-only book. Do not require a bank file to finish cases 1–18.

- **Input:** `fixtures/bank-chequing.csv`.
  - Payroll 3200.00 on Sep 1.
  - Mortgage −1800.00 on Sep 2.
  - `CIBC VISA PAYMENT 1001` −495.79 on Sep 15.
  - `TRANSFER TO SAVINGS` −500.00 on Sep 16.
- **Expect:**
  - The bot asks before writing the payroll. Sep `C8` stays empty until you confirm.
  - After you confirm, Sep `C8` Income = 3200.00. Merchant Map remembers the payee as Income.
  - Sep `C24` Rent/Mortgage = 1800.00 (positive in the fixed-expense column).
  - The transfer is skipped. It is not an expense and not income.
  - The visa payment is skipped as an expense and sets Cards Paid status for last 4 1001 to `paid`.
  - Cards gains `North Bank Chequing-5505`.
  - No earlier expense cell changes. Aug `BM29` is still 71.04.
- **Verify:** read Sep `C8` before the confirmation (empty) and after (3200). Read Cards for 1001 (`paid`) and for 4404 (still `unpaid`, because this payment names 1001).

### 22. Return lookup from a product photo

- **Input 1:** `fixtures/receipt-sportchek.txt`, if that receipt is not already in the Receipts section from an earlier photo. Sport Chek, 2026-09-09, receipt 5138, card 3303, Adidas Milano jacket 57.53, SKU AM-23. If layout C already wrote the 57.53 purchase, this receipt should link to it rather than add a second 57.53. If it asks, answer that it is the same purchase. The grid must contain 57.53 once as a positive Clothing amount.
- **Input 2:** `fixtures/product-tag-adidas.png` (or `product-tag.txt`) on 2026-09-20. The text is Adidas, Milano jacket, SKU AM-23.
- **Expect:** the reply includes the receipt file, store Sport Chek, date 2026-09-09, price 57.53, card 3303, return window 30 days, and 19 days left. It does not invent a window for a store that is not in the list.
- **Verify:** the reply's date and price match the Receipts row. 2026-09-09 plus 30 days is 2026-10-09. From Sep 20 that is 19 days.

### 23. Migration from v1.2.4, including a rerun

Use book M, a v1.2.4 workbook (set `C46` to `v1.2.4` and use the old receipt-list header at row 47: Date & time, Store, Receipt/order #, Items, Total, Category/cells written, Payment, File, Source). Put these rows in before you migrate. Do not use book T.

| Receipt # | Store | Date | Total | Where written | Items |
|---|---|---|---|---|---|
| 482910 | Costco | 2026-09-20 | 80.00 | `Sep!AW6+Sep!AW22+Sep!AW7` | eggs 18.00; paper towel 42.00; chicken 20.00 |
| 111 | Costco | 2026-09-05 | 15.00 | `Sep!K17` | snack mix 15.00 |
| 222 | Costco | 2026-09-05 | 15.00 | `Sep!K18` | snack mix 15.00 |

Grid, written before migration and left alone: Sep `AW6` = 18.00, Sep `AW22` = 42.00, Sep `AW7` = 20.00, Sep `K17` = 15.00, Sep `K18` = 15.00. Card on the receipt rows is 2202.

- **Run migration once.**
- **Expect:** `C46` becomes `v2.0`. Three Receipts rows, including 482910 with helper status `pending`. The five grid cells are unchanged. `D46` contains `Pending duplicates:` and names 111 and 222. Neither duplicate row is deleted. Neither 15.00 cell is cleared.
- **Run migration again.**
- **Expect:** still three Receipts rows. No fourth row. `C46` stays `v2.0`.
- **Resume:** set `C46` back to `migrating` and run it again.
- **Expect:** zero rows copied. `C46` returns to `v2.0`. The grid is still the five cells above.
- **Then import** `fixtures/layout-b-cibc-costco.txt`.
- **Expect:** the 80.00 line links to 482910 and does not change `AW6`, `AW22`, or `AW7`. The unmatched 246.66 still posts to Aug `AY17` Snacks. The 15.00 cells stay. The annual renewal posts to Sep `K37` = 65.00 because `K17` and `K18` are already used; if the bot picks another empty Other cell, the amount is still 65.00 once and the Meals cells are untouched.
- **Verify:** sum of Sep `AW6`, `AW22`, and `AW7` is still 80.00. Receipt 482910 status is `matched`.

### 24. Interrupted write, retried, no double count

Use book C, empty v2.0.

- **Input:** `fixtures/mid-month.csv`, and stop the write after the amount is in the grid and the Log row exists, before the Transactions row is appended. The tester simulates this by writing Log status `pending`, Where written `Aug!BM29`, the txn key, and Aug `BM29` = 71.04, and by not adding a Transactions row. (A real crash leaves the same trail. The skill says a retry reads the recorded cell.)
- **Input 2:** import `fixtures/mid-month.csv` again.
- **Expect:** the bot resumes the pending row. It does not pick a new Fuel cell. Aug `BM29` is still 71.04. One Transactions row, status `no receipt`. One Log row, status `no receipt`.
- **Verify:** the grid contains 71.04 once. Transactions has one Shell row.

## Done

Every case above has an input file, a section, a column or a grid cell, and an amount. A case fails when a second import adds an amount, when a payment becomes an expense, when a question writes the grid, or when a migration changes a number the user already entered.

The fixtures are fake. Do not commit a real statement, a real name, a real address, or a real last 4 into this repo.

Made by SkybatanX (@SkyXFunNext).
