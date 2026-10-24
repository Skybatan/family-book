# Family Book v2.1 test plan

This plan is for **Family Book Bot -tester**. The tester works only inside a Google Drive folder named exactly `Family Book TEST`. Every test file name starts with `TEST - `. Do not open, write, or migrate a real `Family Book` folder. Do not use a real person's name, card, address, or statement.

Cloud cases (Google Sheets and Excel Online) are connector-only. The tester does not run Python for those. Local Excel cases are simulated by treating one folder on the tester's own computer as the user's computer. The author's offline check for that simulation is `python3 tests/v2.1/check_v21.py`. It uses synthetic receipts only. The v2.0 statement regression is still `python3 tests/v2.0/generate_and_check.py`, and those fixtures stay the synthetic Jordan Lee set.

Receipt file names in a real book are `YYYY-MM-DD HHMM - Store - TOTAL.ext`. In this plan the tester prefix is added in front: `TEST - 2026-10-03 1200 - Costco - 12.34.txt`. The sample file is `tests/v2.1/fixtures/TEST - 2026-10-03 1200 - Costco - 12.34.txt`. It is a cash Costco receipt for 12.34 with no person and no card.

## How to read the new cells

Annual Summary:

| Cell | Label | New book |
|---|---|---|
| `C46` | Book version | `v2.1` |
| `C47` | Statement features | `off` |
| `C48` | Statement offer | `not yet` |
| `C49` | Last weekly report | blank until a weekly report is sent |
| `C50` | Last monthly report | blank until a monthly report is sent |
| `C51` | Last yearly report | blank until a yearly report is sent |

`C47` = `on` is the only state that allows card-due reminders, statement-ready nudges, and income or fixed expenses filled from a bank file. `off`, blank, and missing are the same: those routines send nothing.

`C48` values: `not yet` (may suggest once), `asked` (already suggested, do not ask again), `declined` (the user said no), `accepted` (the user said yes, or a statement was imported).

Day 3 (2026-10-03) Meals amount is Oct `O6`. Day 4 (2026-10-04) Fuel amount is Oct `Q29`. A split of meals plus household goods uses Oct `O6` and Oct `O22`. Nothing below row 44 is in a total.

## Setup, once

1. Create `Family Book TEST` at the top of the test Drive. Do not use any other Drive folder.
2. Copy `template/family-book-template.xlsx` into `Family Book TEST/Family Book - Templates/`. Confirm Annual Summary `C46` is `v2.1`, `B47` is `Statement features`, `C47` is `off`, `C48` is `not yet`, and the banner says v2.1 and that Excel does not have to be installed.
3. Upload `tests/v2.1/fixtures/` into `Family Book TEST/fixtures/`. Also keep the v2.0 fixtures there for case 13. Every name already starts with `TEST - ` or, for the older fixtures, send them only from `Family Book TEST`.
4. On the tester's computer, pick one empty folder and treat it as the user's computer. Call it the computer folder. Do not point it at a real Family Book.

## Cases

### 1. Receipts-only setup on Google Sheets

- **Input:** a fresh tester chat. No `Family Book` folder exists yet. Google Drive can be connected. Do not connect a statement inbox for this case.
- **Expect:** the bot asks one question, where to save receipts and the report. It names Google Drive and Google Sheets, OneDrive and Excel Online, and the computer only if a desktop computer is connected. It does not ask for a bank, a card list, a statement, a language, or the word "go".
- **Input 2:** choose Google Drive and Google Sheets.
- **Expect:** the book is created in `Family Book TEST` (the tester's root, not a personal `Family Book` folder). The workbook is `TEST - Family Book - 2026` inside `Family Book TEST/TEST - Family Book - 2026/`, with a `receipts` folder beside it. `statements/` is not created. `C46` is `v2.1`, `C47` is `off`, `C48` is `not yet`. Transactions and Cards have no data rows. The bot invites a receipt and does not ask which cards you have.
- **Input 3:** send `Family Book TEST/fixtures/TEST - 2026-10-03 1200 - Costco - 12.34.txt`.
- **Expect:** one Receipts row, store Costco, total 12.34, status `cash`. Oct `O6` is 12.34 once. Transactions is still empty. Cards is still empty. The saved file name starts with `TEST - ` and matches `TEST - 2026-10-03 1200 - Costco - 12.34.txt`. Sending the same file again does not add a second 12.34.
- **Pass:** the first receipt is logged in that setup conversation, `C47` is still `off`, and the amount appears once.

### 2. Receipts-only setup on Excel Online

- **Input:** a second fresh chat. Choose OneDrive and Excel Online. Stay inside `Family Book TEST` on the test OneDrive if the connector can see it. If the tester has no OneDrive connector, record the case as blocked by tools and do not invent a workbook.
- **Expect:** the same cells as case 1: `C46` = `v2.1`, `C47` = `off`, `C48` = `not yet`, empty Transactions and Cards. The file is an `.xlsx`. The bot re-downloads it before the write and uploads it after. Excel the desktop app is not opened.
- **Input 2:** the same Costco fixture.
- **Expect:** Oct `O6` is 12.34 once. A second send does not change the total. `C47` stays `off`.
- **Pass:** one cash receipt, no statement asked, no second amount. If OneDrive is unavailable, the pass note says the connector was missing and case 1 still covers the receipts-only book.

### 3. Local Excel mode, simulated on the tester's computer

- **Input:** tell the tester the computer folder is the user's computer. Choose "an Excel file on this computer".
- **Expect:** one approval creates the folder, `receipts/`, `backups/`, and `TEST - Family Book - 2026.xlsx`. The bot does not start Excel, Numbers, or LibreOffice. The file is written with the local writer (`bot/local/bookio.py`), which runs on the bot, not on the user's computer.
- **Input 2:** the Costco fixture.
- **Expect:** two local-tool approvals for that receipt: copy the workbook out, then copy it back. Not one approval per cell. Oct `O6` is 12.34. The receipt file is in `receipts/` and its name starts with `TEST - `. A backup exists under `backups/` and its Oct `O6` is still empty, because the backup is the file from before the write.
- **Pass:** two approvals, one amount, one backup that does not yet contain the new receipt. The receipt key is `Costco|2026-10-03|12.34`, the same key the cloud book would use.

### 4. A computer with no Excel installed

- **Input:** run `python3 tests/v2.1/check_v21.py` from the repo. Do not install Excel. The check opens the `.xlsx` as a zip package.
- **Expect:** the script prints `v2.1 offline checks passed`. The writer source does not start another program. The saved workbook contains `[Content_Types].xml` and `xl/workbook.xml`.
- **Pass:** the book is a real `.xlsx` and the check passes with Excel absent. Opening it later in Excel, Numbers, or LibreOffice is optional and is not required to pass.

### 5. A book with zero statements

- **Input:** the book from case 1 or case 3, after the Costco receipt and before any statement.
- **Expect:** Transactions has no data row. Cards has no last-4. Oct `O6` is 12.34, so the month grid is filled from the receipt. A split receipt (10.00 meals and 4.34 household goods, total 14.34) writes Oct `O6` = 10.00 and Oct `O22` = 4.34 and still adds no Transactions row. The parts add up to the total.
- **Pass:** empty statement sections, and the grid shows the receipt amounts. No card-due reminder and no statement-ready nudge is created.

### 6. The one-time statement suggestion

- **Input:** a receipts-only book with `C47` = `off` and `C48` = `not yet`. Either log 10 finished receipts, or set the first receipt's date at least 14 days before today. One receipt from yesterday is not enough.
- **Expect:** the bot sets `C48` to `asked` before it speaks. The message includes the benefits (purchases you did not photograph, a reminder before a card is due, income and fixed bills) and says the original file stays in your own drive and nothing is uploaded to GitHub. It says a no will not be asked again. Amount cells do not change when `C48` is set.
- **Pass:** one suggestion, `C48` is `asked`, and a later receipt does not produce a second suggestion while `C48` stays `asked`.

### 7. A no is remembered

- **Input:** reply no to case 6.
- **Expect:** `C48` becomes `declined`. No amount changes. Log 11 or more receipts, or wait past 14 days, and run the daily scan again.
- **Expect 2:** the suggestion is not sent. `C48` stays `declined`. `C47` stays `off`.
- **Pass:** the no survives a later scan and a settings migration. See case 12 for the migration half: a book that already says `declined` is still `declined` after migrate, and a transaction amount such as 10.00 is unchanged.

### 8. Routines stay quiet with no statements

- **Input:** `C47` is `off`. Run the card-due reminder and the statement-ready nudge on a day that would otherwise be a due date or a statement day. Also leave an issuer "statement is ready" email in the test inbox, with no statement attached, or with a synthetic statement attached.
- **Expect:** both routines send nothing. The email is not imported. Income and Fixed Expenses are not filled from any bank file. The spending-report routine may still send a weekly, monthly, or yearly category report in chat. It does not suggest a statement. It does not open Excel. A weekly id is the Sunday that ends that Monday–Sunday week, written to `C49` only after the report is sent. Sunday 2026-10-04 is the week 2026-09-28 through 2026-10-04, id `2026-10-04`. The same id is not sent twice.
- **Pass:** no reminder, no nudge, no email-only import, and a report that does not repeat.

### 9. An offline queue writes the receipt once

- **Input:** enqueue the Costco receipt while the computer folder is offline (the tester's stand-in for the computer being off or asleep). Run the drain.
- **Expect:** zero local-tool approvals. Oct `O6` is still empty. The queue has one item, status `queued`. Enqueueing the same receipt again returns duplicate and does not add a second row.
- **Input 2:** mark the computer online and drain once.
- **Expect:** two approvals. Oct `O6` is 12.34. The queue item is `done`. Drain again.
- **Expect 2:** no second 12.34. Approvals for the empty drain do not write the file.
- **Pass:** the offline period produced no write and no duplicate, and the later write happened once. The queue file stays on the bot. It is not uploaded to GitHub and it is not committed.

### 10. A locked file is retried and not written twice

- **Input:** the book from case 9, with Oct `O6` already 12.34. Enqueue a Shell receipt dated 2026-10-04 for 40.00, category Fuel. Create `TEST - Family Book - 2026.xlsx.lock` beside the workbook, or open the file so it cannot be replaced. Drain.
- **Expect:** the copy back changes nothing. Oct `O6` is still 12.34. Oct `Q29` is empty. The Shell queue item is `retry`. There is still one queue row for that receipt key, not a second row. The live file is not replaced.
- **Input 2:** remove the lock and drain again.
- **Expect:** Oct `Q29` is 40.00. Oct `O6` is still 12.34. A third drain does not write 40.00 again.
- **Pass:** the locked attempt left the file as it was, and the retry wrote the new receipt once.

### 11. A backup before every write

- **Input:** any successful local write, including case 3 and the retry in case 10.
- **Expect:** `backups/` contains `TEST - Family Book - 2026 - YYYYMMDD-HHMMSS.xlsx` taken before the replace. The backup's new amount cell is empty. The live file has the amount. A second write does not overwrite the earlier backup. A failed locked write does not leave a half-written live file.
- **Pass:** every successful replace has its own backup, and the backup is the pre-write workbook.

### 12. The first statement turns statement features on

- **Input:** the receipts-only book, `C47` = `off`, Oct `O6` = 12.34. Send a synthetic statement in chat (use a v2.0 fixture from `Family Book TEST`, such as `mid-month.csv`, or a one-line statement whose totals match). Do not send it only by email while features are off.
- **Expect:** the statement imports under the v2.0 rules (one Transactions row, the amount once). `C47` becomes `on`. `C48` becomes `accepted`. The Costco 12.34 is unchanged. Card-due and statement-ready routines may now be created. A later bank deposit may be offered as Income, and a recurring debit may go to Fixed Expenses. A statement whose totals do not match is refused and does **not** set `C47` to `on`.
- **Settings migration, same case:** take a copy of a v2.0 workbook inside `Family Book TEST`, name it `TEST - v2.0 book.xlsx`, set `C46` to `v2.0`, leave `C47` blank, and put 12.34 in Oct `O6` and 80 in Oct `C19`. Run family-book-migrate.
- **Expect 2:** `C46` is `v2.1`, `C47` is `off` because Transactions, Statements, and Cards are empty, `C48` is `not yet`. Oct `O6` is still 12.34 and Oct `C19` is still 80. The banner prefix becomes `Family Book v2.1` and the rest of the banner stays. Run the migration again: nothing changes.
- **Expect 3:** put a Transactions or Cards row on a second copy, set `C48` to `declined`, and set a transaction amount to 10.00. Migrate. `C47` becomes `on` because statement data already exists. `C48` stays `declined`. The 10.00 is unchanged.
- **Pass:** importing a statement turns features on without moving the receipt amount, a refused file does not, and migration never changes an amount.

### 13. v2.0 statement flows still work

- **Input:** follow [tests/v2.0/TEST-PLAN.md](../v2.0/TEST-PLAN.md) inside `Family Book TEST`. Use the synthetic fixtures only. After the first successful statement import, `C47` is `on`. Where that plan says `C46` becomes `v2.0`, this migration ends at `v2.1`.
- **Author check:** `python3 tests/v2.0/generate_and_check.py` prints `v2.0 offline checks passed`. `python3 tests/v2.1/check_v21.py` also re-imports `mid-month.csv` twice and expects Aug `BM29` = 71.04 once.
- **Pass:** a bad total is refused, a good statement posts once, a second import adds nothing, a pending write resumes without a second amount, and migration keeps the grid cells it was given.

## What fails the plan

- A setup question about cards, banks, or statements.
- A second amount for the same receipt key.
- A reminder, a nudge, or an email-only statement import while `C47` is `off`.
- A second statement suggestion after `C48` is `asked`, `declined`, or `accepted`.
- A migration or an offer update that changes a number or a formula.
- A local write that starts Excel, that asks for an approval per cell, that writes while the computer is offline, or that replaces a locked file.
- A test file whose name does not start with `TEST - `, or any file written outside `Family Book TEST` on Drive.
- A real card number, a real person, or a real statement in the repo.
