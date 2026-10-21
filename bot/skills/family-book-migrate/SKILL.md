---
name: family-book-migrate
description: Use when a Family Book workbook from v1.0 through v1.2.2 needs the v1.2.3 receipt list, receipt-key dedupe, and simple file names. Owner only. Rebuilds each month's receipt list from the Log, the saved files, and the original emails without retyping the numbers.
---

# Family Book migration to v1.2.3

Run this once for each year workbook in the owner's `Family Book` root. It rebuilds the receipt list at the bottom of each month sheet, renames saved files to the simple file name, and records `v1.2.3` on the sheet so it does not run again. Nobody retypes the income, bills, or daily amounts. Those number cells stay as they are unless the user confirms a duplicate fix.

The human-readable plan is `docs/migration-v1.2.3.md` in https://github.com/Skybatan/family-book. This skill is what the bot follows. The family-book skill's section "Never log the same purchase twice" is the matching rule for new receipts and for deciding that two old rows are the same purchase.

## Who runs it

Only the owner. The owner is the bot whose memory says `owner`, or a bot installed at v1.0 or v1.1 with no role saved that created the year folder in this user's own My Drive or OneDrive.

A member never runs this skill. A member does not insert the receipt list, does not rename the shared files, and does not write the version cell. If a member opens a book whose version is older than v1.2.3, they say once, in the language of the chat, that the owner's bot will update the book. In English that line is: "This Family Book still needs a one-time update. The owner's bot will add the receipt list. I won't change it from here." Then they log new receipts with the family-book skill. If the month list is not there yet, they write the amount and the hidden Log row only, and they do not create the list.

## When it runs

On the owner's next run, before logging a receipt and before creating a year folder, check every year workbook. Download this skill first if it is not installed:

`https://raw.githubusercontent.com/Skybatan/family-book/main/bot/skills/family-book-migrate/SKILL.md`

Save it as the `family-book-migrate` skill (keep the name and description). If a second skill cannot be installed, follow this text for the migration anyway.

Each workbook has its own marker. On **Annual Summary**, `B46` is the label `Book version` and `C46` is the marker.

| `C46` | Meaning |
|---|---|
| `v1.2.3` | This book is migrated. Do not rebuild it. |
| `migrating` | A previous run stopped. Resume this book. Do not start over. |
| anything else, or the cell is missing | This book is v1.0 through v1.2.2, or the marker was never written. Migrate it. |

`D46` is a progress note. It is blank when there is nothing pending. A note that starts with `Pending duplicates:` is a question waiting for the user. Do not apply that fix until they say yes.

A book already created from the v1.2.3 template has `C46` = `v1.2.3` and an empty receipt list. Leave it alone.

Check every folder named `Family Book - YYYY` inside the `Family Book` root, not only the current year. Skip a folder that has no workbook. Do not migrate a workbook under Shared with me that this user does not own.

## Notice, then summary

If at least one owned book needs migration or a resume, say one line before changing anything, in the language of the chat. Say it once for the whole batch, not once per year. In English that line is: "I'm updating your Family Book to v1.2.3: a receipt list at the bottom of each month, filled in from the receipts you already saved. Your totals stay as they are."

Then do the work. After the batch, send a short summary: which years were updated, how many receipt rows were written, how many files were re-read, how many files were renamed, anything that could not be matched, and any duplicate groups waiting for a yes or no. If nothing needed migration, say nothing.

## Do not touch the numbers

The automatic pass must not change an amount, an item, a date, or a formula in the number area. That area is rows 1 to 44 on each month sheet (income, fixed expenses, daily record, totals) and every formula on Annual Summary. Do not rewrite those cells to "re-input" them. The new list is filled beside that data, below it.

The only amount edits are the duplicate fixes in the last section, and only after the user confirms that specific fix.

On OneDrive, re-download the workbook immediately before each write and upload it immediately after. Read `C46` again on that fresh copy before inserting a list, so a retry cannot insert the list twice.

## Resume and run it twice safely

The migration is safe to run twice.

1. Set `B46` to `Book version` if it is missing, set `C46` to `migrating`, and upload before the structural edits. If a fresh read already shows `v1.2.3`, stop for that book. If it already shows `migrating`, continue without clearing rows.
2. Find the receipt list by scanning column B for a cell whose text starts with `Receipts this month`. If it is there, do not write the title or the headers again. Data rows start on the next row after the header row (the header row is the one that contains `Date & time` in column B).
3. If the list is not there, place it below the number block. On a standard sheet, `I44` is `Balance` and row 47 is empty, so the title goes in `B47`. If row 47 already has a value, or `I44` is not `Balance`, put the title on the first row at or below 47 that is clear of values, with one blank row above it. Never overwrite a cell that already has a value.
4. Write the title and headers exactly as the v1.2.3 template does (see "List layout" below). Leave columns E and H blank. They are the sheet's narrow spacer columns. Do not change column widths, row heights in rows 1 to 44, or any formula.
5. Add a list row only when that purchase is not already on the list. Match with the family-book receipt key (receipt number plus merchant, or merchant plus total plus date within ±1 day). If the row is already there, fill only blank cells (receipt number, time, items, payment, file link, source). Do not add a second row. Do not change a Total that is already filled.
6. Rename a file only when its name is still the old pattern. A name that already matches `YYYY-MM-DD HHMM - Store - TOTAL.ext` or `YYYY-MM-DD - Store - TOTAL.ext` (optional ` - #receiptno` or ` - item` suffix included) stays as it is.
7. When every month of this book has been considered, the Log and the lists agree, and the renames are done, set `C46` to `v1.2.3`. Do this even if a duplicate question is still unanswered. The duplicate question lives in `D46` and in the chat, not as a reason to rebuild tomorrow.
8. Update the Annual Summary banner in `B2` only when that cell already contains `Family Book v`. Replace the version token with `v1.2.3`. If `B2` does not contain that banner, leave it and rely on `C46`.

`D46` can hold a short progress line while `C46` is `migrating`, for example `2026: Jan-Apr lists done`. On resume, trust the sheet (the header and the existing rows), not only `D46`.

## Where the rows come from

Build one picture of each purchase, then write it. Use all three sources. A purchase that appears in more than one source is still one row.

1. **Hidden Log tab**, when the book has one. Read every data row from row 2 down. Columns A to G are the v1.2 log: Source, Date, Merchant, Total, Where written, Saved file, Logged by. Columns I to M may already exist; if they do not, add those headers (see below) without clearing A to G.
2. **Files in that year's `receipts` folder.** Re-read each file (photo, PDF, or text) and take the receipt or order number, the time of purchase, the line items, and the card last 4 if they are printed. Never store more than the last 4 digits of a card. If a file cannot be read, keep the Log's date, merchant, and total, leave the missing fields blank, and flag `unreadable file: <name>` in the summary.
3. **The original email**, when the Log Source (or the file) contains an email message id and that mailbox is connected. Re-read the message for the same fields. If this bot cannot open that mailbox, flag `email not re-read: <id>` and keep going. Do not send, reply, forward, label, or delete mail.

Books from v1.0 and v1.1 have no Log tab. For those:

1. Add a hidden `Log` sheet with the v1.2.3 header row (below) and hide it.
2. Re-read every file in `receipts`.
3. Read the number cells that are not formulas: income `C8:C11`, fixed expenses `C18:C38`, and the daily amount columns (K, M, O, and so on through BS) on rows 6 to 20, 22 to 40, and 43. Skip any cell whose value starts with `=`. Skip rows 21, 41, 42, and 44.
4. Match a file to those cells by the purchase date's day column, a fuzzy merchant match against the item text, and the amount. A split receipt is one purchase whose cells add up to the file's total. Put every cell in Category/cells written, for example `J6+J22`.
5. An amount cell with no file still gets a list row and a Log row. Leave File blank and set Source to `sheet`. Flag `no file` in the summary.
6. A file with no matching amount still gets a list row and a Log row. Leave Category/cells written blank. Flag `no matching amount: <file>`. Do not invent an amount in the number area.
7. Then continue with the same rename and duplicate steps as a book that had a Log.

## List layout

Write this on each month sheet that does not already have it. English labels, exactly:

- Title, column B, merged across to column S: the first line is `Receipts this month`. The second line is `One row per receipt. These rows are not included in the totals above.`
- Header row, the next row. Column B `Date & time`, C `Store`, D `Receipt/order #`, F `Items`, G `Total`, I `Category/cells written`, J `Payment`, K `File`, L `Source`, S `Logged by`. Merge `L:R` on the header row only. Leave E and H empty.
- One data row per purchase, starting the row after the header. Write the Source value in column L. If that text needs more room, merge `L:R` on that data row only. Never merge over column S.

On the standard template the title is row 47, the headers are row 48, and the first receipt is row 49. Do not assume those row numbers if the title was placed lower.

Cell formats:

| Column | What to write |
|---|---|
| B Date & time | `YYYY-MM-DD HH:MM` when the time is known, otherwise `YYYY-MM-DD`. |
| C Store | Merchant name, no person's name. |
| D Receipt/order # | The number, or blank. A user-confirmed separate purchase uses `separate`. |
| F Items | `product: price; product: price`. Product names follow the chat language. The header stays English. |
| G Total | A number. Negative for a return. Do not copy this number up into the category cells. |
| I Category/cells written | Amount cells joined with `+`, for example `AN6+AN17+AN22`. Fixed expenses can stay `Fixed Expenses / GAS` when that is all the old Log row has; new rows prefer the cell, such as `C19`. |
| J Payment | Last 4 digits only, such as `1234`, or blank. |
| K File | `photo`, `email`, or `statement`, joined with ` \| ` when there are several, such as `photo \| email`. Each label is a link to the saved file. |
| L Source | `photo`, `email gmail/family@example.com 18c3fab`, or `statement`. Join extra copies with ` \| `. |
| S Logged by | The display name from the old row, or blank. |

Google Sheets can link each label in the File cell. Excel allows one hyperlink on the cell: show `photo | email`, point the cell hyperlink at the first file, and keep every url in the Log Saved file column as `photo: <url> | email: <url>`.

The list is not part of any total. Do not extend a SUM down into it.

These columns are also what a later card-statement check will match on (date and time, store, receipt or order number, total, payment last 4). That check is issue #6. This migration does not do it, and it does not close that issue.

## Log tab

The hidden Log is the authoritative dedupe list for the year. The month list is the same purchases, written out where people can see them. After migration, every purchase is one Log row and one month-list row, and they carry the same key.

If the Log sheet is missing, create it and hide it. Header row:

| Column | Header |
|---|---|
| A | Source |
| B | Date |
| C | Merchant |
| D | Total |
| E | Where written |
| F | Saved file |
| G | Logged by |
| H | Leave the note in `H1`. Do not use column H for data. |
| I | Receipt/order # |
| J | Date & time |
| K | Items |
| L | Payment |
| M | Month list row |

`Month list row` is the Date & time cell of that purchase, for example `Oct!B49`.

Column B stays `YYYY-MM-DD`. Column J repeats the date and time. Column D is the number. Do not delete old rows. Add the new columns onto them. A Log row with no month-list row gets one. A month-list row with no Log row gets one. If the two disagree about the total, do not change the number cells. Flag it in the summary.

## File names

Rename each saved receipt to the simple name. Details stay on the sheet.

`YYYY-MM-DD HHMM - Store - TOTAL.ext`

- `HHMM` is 24-hour, four digits, no colon (`1432`). Omit it, leaving `YYYY-MM-DD - Store - TOTAL.ext`, when the time is unknown.
- `TOTAL` is two decimals, with a leading minus for a return (`-84.12`).
- Strip characters Windows and OneDrive reject: `/ \ : * ? " < > |`, and control characters. Collapse spaces. Trim spaces and dots from the ends.
- Add ` - #receiptno` or, if there is no number, ` - ` plus a short item hint, only when the folder already has that name. If it still collides, add ` - 2`, ` - 3`.
- Rename in place. Do not upload a second copy. Then point the File link and the Log Saved file cell at the new name.
- If the rename fails, keep the old name, link that, and flag `rename failed: <old name>`.

## Duplicates already in the book

After the lists are filled, look for the same purchase recorded twice. Use the family-book matching order:

1. Same receipt, transaction, or order number at the same merchant (fuzzy).
2. No number on one side: same merchant (fuzzy), same total to the cent, dates within ±1 day.
3. A return (negative total) is its own purchase. It does not pair with the original sale.

A group of two or more Log rows, or a receipt whose category cells add up to about twice the receipt total (or more), is an existing duplicate. The usual cause is a photo and an email, or the second Home Depot receipt, both added as amounts.

Report each group. Do not change the amounts in that report. For each group, name the year, the store, the date, the total, the cells that hold the extra amount, and the proposed fix. The proposed fix keeps one receipt row, attaches every file to it, and removes only the extra amount:

- A plain number that equals the extra amount: clear that cell.
- A formula such as `=84.12+84.12`: drop one addend, leaving `=84.12`.
- If the cell mixes this receipt with other purchases and the extra amount cannot be separated, do not propose an edit. Ask the user which cell to change.

Write the pending groups into `D46`, prefixed `Pending duplicates:`, and list them in the summary. Ask for one yes or no per group, or one yes for all of them. On later runs, if `C46` is already `v1.2.3` and `D46` still starts with `Pending duplicates:`, remind the user. Do not rebuild the list. The daily scan mentions that reminder only inside a digest it is already sending, as one line. It never applies the fix.

When the user says yes to a group, apply only that proposed edit, merge the extra Log and list rows into the kept row, attach the extra files, and remove that group from `D46`. When they say no, leave the amounts, drop that group from `D46`, and leave both rows in place marked so they are not proposed again (Source includes `user confirmed separate` on the extra row).

## Flags

Put anything that does not match cleanly in the summary, and do not guess a number for it:

- unreadable file
- email not re-read
- no file for an amount cell
- no matching amount for a file
- list total and Log total disagree
- rename failed
- duplicate group waiting for a yes or no

A flagged row can still exist on the list with the fields that are known. A second run fills blanks and does not create another row for the same key.
