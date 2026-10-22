# Migration to Family Book v2.0

v2.0 adds a Transactions section and a Receipts section on each month sheet, a Cards sheet, a merchant map, and statement import. The number grid on top of each month does not change. The bot follows [bot/skills/family-book-migrate/SKILL.md](../bot/skills/family-book-migrate/SKILL.md). This page is the plan for people.

Annual Summary cell `C46` is the marker.

| `C46` | What happens |
|---|---|
| `v2.0` | The book is current. Nothing is rebuilt. |
| `v1.2.4` | Receipt rows are copied into the Receipts section. Totals stay as they are. Source cells, Log column F, and Log column O change ` | ` to `, `. An old `open question` Source becomes `open question: candidates <dates>; <source>`. Log column F is not renumbered. |
| `v1.2.3` | The owner's books are on this version. The same run applies the [v1.2.4 checkpoint](migration-v1.2.4.md), then the v2.0 copy. It does not ask for a separate update to v1.2.4, and it does not stop when that patch finishes. |
| older than `v1.2.3`, or blank | The list is rebuilt, then the same v1.2.4 patch runs, then the v2.0 copy. The bot does not stop at v1.2.4. |
| `migrating` | A previous run stopped. The next run continues. A row already copied is recognized by its receipt key in column CA, not by Receipt #. |

## What stays

Income, fixed bills, and daily amounts are not retyped. A receipt that was already in the grid stays in those cells. The migration does not add the amount again.

## What is added

- **Transactions this month**, then **Receipts this month**, under the totals. Old receipt-list rows become Receipts rows: receipt number, store, date, total, card, items, and the file link. The file is copied into this year's `receipts` folder, and the File link points at that copy.
- Helper columns, seven of them. Do not assume the sheet has 71 columns. The bot finds the last used column. Some books already use column 72 or 73. On a standard sheet the helpers are **CA through CG** (columns 79 through 85), after day 31 (column BS). If the sheet already uses column 72 or 73, those columns stay, and the helpers start in the next column after the last used one.
- A **Cards** sheet (issuer, product, last 4, holder, statement day, due day, last amount due, paid status). It starts empty until you name a card or import a statement. The bot freezes Cards at A3 and adds the Paid dropdown (`unpaid`, `paid`).
- A **Merchant Map** and a **Statements** sheet. The connector can freeze and can set a dropdown. It has no tool that hides a tab, so the bot asks once to hide the Log, Merchant Map, and Statements tabs, and it keeps going.
- A `statements` folder: `Family Book - {year}/statements/{Issuer Product}-{last4}/`.

## Duplicates

A duplicate pair stays as two rows. The bot writes it into `D46` and asks. It does not delete a row. A yes clears only the extra amount. A no leaves both amounts. Two rows with different receipt numbers are different purchases and are not flagged. A blank receipt number is not turned into `R-0001` and is not skipped. Its receipt key is the short store name, the transaction date, and the total to the cent, for example `Costco|2026-09-05|15.00`. A numbered receipt's key is that number at the store, for example `Costco|482910`. Skip and resume by that key in helper column CA, not by Receipt #. Mark `pending duplicate` in Receipts helper column CB only, not in column L and not in Log column A. Copied cells written include the sheet name, for example `Sep!AW6+Sep!AW22`. Log column F points at the copied file and joins files with `, `. Log column O joins hashes with `, ` too. Before inserting rows at row 47, unmerge the old title and header merges. The bot freezes the month sheets and Cards, and it adds the Paid dropdown. The only manual step is hiding the Log, Merchant Map, and Statements tabs.

## A book that is still on v1.2.3

That is the usual starting point. One run does both halves:

1. The v1.2.4 patch. The receipt list is kept, not rebuilt. The bot unmerges the old title and data-row merges, freezes each month sheet at J6, applies the two-decimal totals and the Education formula, rewrites file labels, converts ` | ` to `, ` in Source, Log column F, and Log column O, and backfills a hash when the file can still be read.
2. Continue to v2.0. Receipt rows are copied into the Receipts section, Transactions and Cards are added, and `C46` becomes `v2.0`.

The bot does not leave the book at `v1.2.4` and wait for a second update. A book that is already `v1.2.4` skips step 1 and runs only step 2.

## The first statement after the update

A statement line that matches a Receipts row is linked. The amount is not added again. A statement line with no receipt is new, and it fills the grid once. Importing that same statement again adds nothing.

## Run it twice

The owner's bot runs this once, for every year in the `Family Book` folder. A second run copies nothing. A family member's bot does not run it.

Made by SkybatanX (@SkyXFunNext).
