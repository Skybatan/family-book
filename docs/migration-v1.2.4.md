# Migration to Family Book v1.2.4

You do not retype anything. The owner's bot brings every year book in the `Family Book` folder up to v1.2.4. A book from v1.0 through v1.2.2 gets a receipt list built from what is already saved. A book that is already on v1.2.3 keeps that list and only picks up the v1.2.4 fixes: cents on the receipt total, the Education line no longer including fuel, a title Google Sheets can merge, and the updated note at the top. Income, bills, and daily amounts stay where they are. The bot changes an amount only after you confirm a duplicate, and it changes a formula that would move a displayed total only after you confirm that fix.

This page is the plan. The bot follows [bot/skills/family-book-migrate/SKILL.md](../bot/skills/family-book-migrate/SKILL.md). The v1.2.3 plan is still at [migration-v1.2.3.md](migration-v1.2.3.md); those steps are included here.

## What changes

- Each month sheet (Jan through Dec) gets a **Receipts this month** list below the totals, if it does not already have one. One row per purchase. A flagged duplicate is the exception: that pair stays as two rows until you answer, and a second run does not add a third.
- The same purchase is recognized by its receipt key (receipt or order number, or store plus total plus date), not by the file name. A photo and an email of one trip stay one row. The extra file is attached. The same clear store with the same total a few days apart is a question, not a second purchase.
- Saved files are renamed to `YYYY-MM-DD HHMM - Store - TOTAL.ext`. The store is the short name: `Costco.ca` becomes `Costco`. The line items stay on the sheet.
- Receipt totals show two decimals. A total of 87.45 no longer displays as 87.
- The Education line on each month sheet counts row 28 only. Fuel stays on its own line and inside the month's total, so the balance does not change. If that correction would change a number you see, the bot asks once for the whole book, listing every month and the before and after amount, and edits the formulas only after that one yes.
- A v1.2.3 book also picks up the file-label change (`photo +1` instead of `photo | email`), a content hash on old Log rows when the file can still be read, and the duplicate marker `pending duplicate` when the same purchase is already on the list twice.
- Annual Summary `C46` is set to `v1.2.4` so the update does not run again. `B46` is the label `Book version`. The note at the top of Annual Summary is replaced in full, including the line about the receipt list. The Log note is replaced in full too.

The list columns are also what a later credit-card statement check will match on: date and time, store, receipt or order number, total, and the card's last 4 digits. That check is [issue #6](https://github.com/Skybatan/family-book/issues/6). This migration does not do the statement check, and it does not close that issue.

## Who

Only the bot that started the book (the owner) runs this. A family member's bot does not insert the list, does not rename files, and does not write the version cell. They keep logging. If the list is not there yet, their bot waits for the owner.

## What you see

Before it edits, the owner's bot says one line. In English: "I'm updating your Family Book to v1.2.4. Older books get a receipt list filled in from the receipts you already saved. Your entered amounts stay as they are."

When it finishes, it summarizes every year it touched: receipt rows written, files re-read, files renamed, anything it could not match, any formula it aligned without changing a total, and any duplicate or formula fix it wants you to confirm.

## Where the rows come from

For each `Family Book - YYYY` workbook inside `Family Book`:

1. **The hidden Log tab**, if the book has one (v1.2 and later). Each Log row becomes one receipt-list row on the month of its date. A duplicate pair becomes two rows, so you can see both.
2. **The files in that year's `receipts` folder.** The bot opens each file again and fills the receipt or order number, the time, the line items, and the card last 4 when they are printed. The template itself still comes from this GitHub repo, not from your Drive. Your own receipt files are read on purpose.
3. **The original email**, when the Log has a message id and that inbox is connected. The bot reads the message for the same fields. It never sends or deletes mail.

A purchase that shows up in more than one of these is still one row, unless it is a duplicate already in the numbers. The extra file is linked. The amount is not added again. If the date on the receipt and the date already stored disagree, the date printed on the receipt wins.

### Books with no Log tab (v1.0 and v1.1)

The bot creates the Log, reads the receipt files, and reads the amount cells already on the month sheets. It matches a file to those cells by date, store, and amount. It does not rewrite the cells.

- An amount with no file still gets a list row, flagged `no file`.
- A file with no matching amount still gets a list row, flagged `no matching amount`. The bot does not invent a number in the daily record.

## The list it writes

On a standard month sheet the numbers occupy rows 1 to 44. Rows 45 and 46 stay blank. The list starts at row 47. If someone has already typed below the totals, the bot places the list under that, and it does not overwrite those cells.

Columns A through I are frozen. Google Sheets will not merge a title from column B through column S, because that crosses the frozen edge, and it will not set that freeze while the old merge is still there. On a v1.2.3 book the update removes the wide title merge, and any data-row merge such as L49:R49, before it freezes. Then it merges the title from B through I only. Data rows stay unmerged. On Google Sheets the title row is 53 px and the header row is 43 px. The narrow spacer columns E and H are 20 px. Those pixel sizes are for the Sheets connector. The Excel template stays at 40 pt, 32 pt, and a width of about 1.63.

| Row | What |
|---|---|
| 47 | `Receipts this month`, plus a line that these rows are not included in the totals. Merged from column B through I. Navy bar, white bold text. |
| 48 | Column headers, in a light blue bar |
| 49 on | One receipt per row. A flagged duplicate pair is two rows. |

| Column | Header |
|---|---|
| B | Date & time |
| C | Store |
| D | Receipt/order # |
| F | Items |
| G | Total, with two decimals |
| I | Category/cells written |
| J | Payment |
| K | File |
| L | Source |
| S | Logged by |

Columns E and H stay empty and narrow. They are the gaps in the sheet above. No total formula includes this area.

The File cell is one link, to the main file. If there is a second file it reads `photo +1`. Source cells that join copies with ` | ` are rewritten with `, `. An older File cell that says `photo | email` is rewritten to the `photo +N` form when a file is there. Four labels, such as `photo | email | photo | email`, become `photo +3`. A cell that is plain text gets its link from the saved file. A cell that is only `photo` or `email`, with no link, stays that text. If there is no file, the text is kept and ` | ` becomes `, `. Do not invent a url. Log column F is numbered (`1 photo:`, `2 email:`) only when a file is there. With no file, column F is not numbered, and its ` | ` also becomes `, `. When a file is there, column F joins the numbered files with `, ` as well. Old Log rows gain a SHA-256 when the saved file can still be read. That hash is how a renamed copy of the same file is recognized. If the file cannot be read, the hash stays blank.

## File names

Old names look like `2026-10-15 Costco.ca 57.29.png`. New names look like `2026-10-15 1432 - Costco - 57.29.png`. The time is left off when the receipt has none: `2026-10-15 - Costco - 57.29.png`. A receipt number or a short item hint is added only when two different files would otherwise get the same name. The same file sent again is not saved twice. Characters that Windows and OneDrive reject (`/ \ : * ? " < > |`) are removed. The bot renames the file in place and updates the link. A name that is already in the new pattern is left as it is.

## Formula fixes

On each month sheet, Education & Enrichment was adding the Fuel row. The fix counts Education on its own. Fuel stays in the month's living-expense total, so the balance does not change, and the Annual Summary Education line is pointed at the corrected cell so it does not subtract fuel twice.

February's category totals reached one column past the last day. Those stop at column BS.

If a book has fuel spending, the Education line on that month sheet goes down by the fuel amount and the balance stays the same. A month whose number would not change is updated right away. The bot asks one yes/no for the whole book, not one question per month, and that question lists only the months whose displayed total would change, with the before and after amount. One answer applies those months, or leaves them as they are. If the fuel total is zero and that extra February column is empty, nothing you see changes, and the bot applies the formulas and says so. It never types over an amount you entered.

## Duplicates it found

If the same purchase was logged twice (a photo and an email, or both Home Depot receipts), the totals are high by that amount. The bot reports each case and names the cells. It does not change them until you say yes. Both rows stay on the list so you can see the pair. Running the update again does not add another row.

A proposed fix keeps both rows, moves the extra receipt number and files onto the row that stays active, drops `pending duplicate` from that row, and clears only the extra amount. The extra Log row is marked superseded. It is not deleted. The same `pending duplicate` marker is written on a v1.2.3 book, not only when the list is rebuilt. If the cell mixes this purchase with others and the extra cannot be separated, the bot asks instead of editing.

Until you answer, Annual Summary `D46` contains `Pending duplicates:` or `Pending formula fixes:`. The book can still be marked `v1.2.4`, so the list is not rebuilt on the next run. The question stays until you answer. Yes applies that one fix. No leaves the amounts, or the formulas, and stops asking about that one.

## Safe to run twice

The bot can stop and continue later.

- `C46` = `v1.2.4` means this book is done.
- `C46` = `v1.2.3` means the list is there and the v1.2.4 patch has not finished.
- `C46` = `migrating` means a run stopped. The next run continues. It does not add a second header, and it does not add a row for a purchase that is already listed.
- A blank `C46` means the book has not been migrated.

The owner's bot checks every year folder, not only this year. A member's bot does not.

## What the bot will not do

- It will not retype or recalculate your income, fixed bills, or daily amounts during the update.
- It will not change a formula that moves a displayed total unless you say yes.
- It will not delete a receipt file. A rename keeps the same file.
- It will not delete a Log row. A confirmed duplicate is marked superseded and kept.
- It will not log the same purchase a second time while it is rebuilding the list.
- It will not close issue #6. The new columns are there so that check can be added later.
