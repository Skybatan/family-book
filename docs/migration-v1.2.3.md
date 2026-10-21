# Migration to Family Book v1.2.3

You do not retype anything. The owner's bot rebuilds the new receipt list from what is already saved, on every year book in the `Family Book` folder. Income, bills, and daily amounts stay where they are. The bot changes an amount only after you confirm a duplicate.

This page is the plan. The bot follows [bot/skills/family-book-migrate/SKILL.md](../bot/skills/family-book-migrate/SKILL.md). Installed bots on v1.0 through v1.2.2 pick up the new skill on their next run, see that the book's version is older, and run this once.

## What changes

- Each month sheet (Jan through Dec) gets a **Receipts this month** list below the totals. One row per purchase.
- The same purchase is recognized by its receipt key (receipt or order number, or store plus total plus date), not by the file name. A photo and an email of one trip stay one row. The extra file is attached.
- Saved files are renamed to `YYYY-MM-DD HHMM - Store - TOTAL.ext`. The line items stay on the sheet.
- Annual Summary `C46` is set to `v1.2.3` so the update does not run again. `B46` is the label `Book version`.

The list columns are also what a later credit-card statement check will match on: date and time, store, receipt or order number, total, and the card's last 4 digits. That check is [issue #6](https://github.com/Skybatan/family-book/issues/6). This migration does not do the statement check, and it does not close that issue.

## Who

Only the bot that started the book (the owner) runs this. A family member's bot does not insert the list, does not rename files, and does not write the version cell. They keep logging. If the list is not there yet, their bot waits for the owner.

## What you see

Before it edits, the owner's bot says one line. In English: "I'm updating your Family Book to v1.2.3: a receipt list at the bottom of each month, filled in from the receipts you already saved. Your totals stay as they are."

When it finishes, it summarizes every year it touched: receipt rows written, files re-read, files renamed, anything it could not match, and any duplicate it wants you to confirm.

## Where the rows come from

For each `Family Book - YYYY` workbook inside `Family Book`:

1. **The hidden Log tab**, if the book has one (v1.2 and later). Each Log row becomes one receipt-list row on the month of its date.
2. **The files in that year's `receipts` folder.** The bot opens each file again and fills the receipt or order number, the time, the line items, and the card last 4 when they are printed.
3. **The original email**, when the Log has a message id and that inbox is connected. The bot reads the message for the same fields. It never sends or deletes mail.

A purchase that shows up in more than one of these is still one row. The extra file is linked. The amount is not added again.

### Books with no Log tab (v1.0 and v1.1)

The bot creates the hidden Log, reads the receipt files, and reads the amount cells already on the month sheets. It matches a file to those cells by date, store, and amount. It does not rewrite the cells.

- An amount with no file still gets a list row, flagged `no file`.
- A file with no matching amount still gets a list row, flagged `no matching amount`. The bot does not invent a number in the daily record.

## The list it writes

On a standard month sheet the numbers occupy rows 1 to 44. Rows 45 and 46 stay blank. The list starts at row 47. If someone has already typed below the totals, the bot places the list under that, and it does not overwrite those cells.

| Row | What |
|---|---|
| 47 | `Receipts this month`, plus a line that these rows are not included in the totals. Merged from column B through S. |
| 48 | Column headers |
| 49 on | One receipt per row |

| Column | Header |
|---|---|
| B | Date & time |
| C | Store |
| D | Receipt/order # |
| F | Items |
| G | Total |
| I | Category/cells written |
| J | Payment |
| K | File |
| L | Source |
| S | Logged by |

Columns E and H stay empty. They are the narrow gaps in the sheet above, and widening them would move the totals. No total formula includes this area.

The File cell reads `photo`, `email`, or `photo | email`. Each word links to the saved file.

## File names

Old names look like `2026-10-15 Costco.ca 57.29.png`. New names look like `2026-10-15 1432 - Costco - 57.29.png`. The time is left off when the receipt has none: `2026-10-15 - Costco - 57.29.png`. A receipt number or a short item hint is added only when two files would otherwise get the same name. Characters that Windows and OneDrive reject (`/ \ : * ? " < > |`) are removed. The bot renames the file in place and updates the link. A name that is already in the new pattern is left as it is.

## Duplicates it found

If the same purchase was logged twice (a photo and an email, or both Home Depot receipts), the totals are high by that amount. The bot reports each case and names the cells. It does not change them until you say yes.

A proposed fix keeps one receipt row, attaches both files, and clears only the extra amount. If the cell mixes this purchase with others and the extra cannot be separated, the bot asks instead of editing.

Until you answer, Annual Summary `D46` starts with `Pending duplicates:`. The book is still marked `v1.2.3`, so the list is not rebuilt on the next run. The question stays until you answer. Yes applies that one fix. No leaves the amounts and stops asking about that pair.

## Safe to run twice

The bot can stop and continue later.

- `C46` = `v1.2.3` means this book is done.
- `C46` = `migrating` means a run stopped. The next run continues. It does not add a second header, and it does not add a second row for a purchase that is already listed.
- A blank `C46` means the book has not been migrated.

The owner's bot checks every year folder, not only this year. A member's bot does not.

## What the bot will not do

- It will not retype or recalculate your income, fixed bills, or daily amounts during the update.
- It will not delete a receipt file. A rename keeps the same file.
- It will not log the same purchase a second time while it is rebuilding the list.
- It will not close issue #6. The new columns are there so that check can be added later.
