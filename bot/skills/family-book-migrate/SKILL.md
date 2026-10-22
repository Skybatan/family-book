---
name: family-book-migrate
description: "Never log the same purchase twice. Use when a Family Book workbook from v1.0 through v1.2.4 needs the v2.0 Transactions and Receipts sections, the Cards sheet, and the merchant map. Owner only. Does not retype numbers. Safe to rerun."
---

# Family Book migration to v2.0

The target is `v2.0`. Run this for each year workbook in the owner's `Family Book` root until Annual Summary `C46` is `v2.0`.

- `C46` is already `v2.0`: stop for that book, except to remind the user when `D46` still holds a pending question.
- `C46` is `v1.2.4`: skip the v1.2.4 half. Run only "Continue to v2.0".
- `C46` is `migrating`: resume. Do not clear rows that are already there. If the v1.2.4 patch is not finished, finish it, then continue to v2.0. If the Receipts section already holds the copied rows, the v2.0 half adds nothing and only sets `C46` to `v2.0`.
- Anything older, or the cell is missing: run the v1.2.4 half below as a checkpoint, then continue. Do not stop when that half says to set `C46` to `v1.2.4`.

A book from v1.0 through v1.2.2 gets a receipt list built from the Log, the saved files, and the original emails, then the v1.2.4 patch, then the v2.0 half. A book that is already `v1.2.3` does not get a new list. It gets the patch only, then the v2.0 half. The patch unmerges any receipt-list merge that crosses column I, and any data-row `L:R` merge, before the freeze; it applies two-decimal totals, the Education formula, `photo +N` file labels, a backfilled content hash, and the Log columns. Nobody retypes the income, bills, or daily amounts. Those number cells stay as they are unless the user confirms a duplicate fix.

The v2.0 half copies each old receipt-list row into the Receipts section. It does not change a total or a grid cell. The first statement imported afterwards links to those rows instead of adding them again. Duplicate groups are flagged in `D46` and kept. Rows are never deleted. The human-readable plan is `docs/migration-v2.0.md`. The v1.2.4 plan stays at `docs/migration-v1.2.4.md` and is the checkpoint this skill still follows for an older book.

The human-readable plan is `docs/migration-v1.2.4.md` in https://github.com/Skybatan/family-book. This skill is what the bot follows. The family-book skill's section "Never log the same purchase twice" is the matching rule for new receipts and for deciding that two old rows are the same purchase.

## Who runs it

Only the owner. The owner is the bot whose memory says `owner`, or a bot installed at v1.0 or v1.1 with no role saved that created the year folder in this user's own My Drive or OneDrive.

A member never runs this skill. A member does not insert the receipt list, does not rename the shared files, and does not write the version cell. If a member opens a book whose version is older than v2.0, they say once, in the language of the chat, that the owner's bot will update the book. In English that line is: "This Family Book still needs a one-time update. The owner's bot will update it. I won't change it from here." Then they log new receipts with the family-book skill. If the Receipts section is not there yet, they choose the amount cell, record it on the pending Log row, then write that cell only, and they do not create the section. A retry reads the recorded cell and does not pick a new row.

## When it runs

On the owner's next run, before logging a receipt and before creating a year folder, check every year workbook. Download this skill first if it is not installed:

`https://raw.githubusercontent.com/Skybatan/family-book/main/bot/skills/family-book-migrate/SKILL.md`

That address stays on `main`. It is the right address after this release is merged. Do not point it at a feature branch.

Save it as the `family-book-migrate` skill (keep the name and description, including "Never log the same purchase twice."). If a second skill cannot be installed, follow this text for the migration anyway.

Each workbook has its own marker. On **Annual Summary**, `B46` is the label `Book version` and `C46` is the marker.

| `C46` | Meaning |
|---|---|
| `v2.0` | This book is current. Do not rebuild it. If `D46` still has a pending question, remind the user and change nothing else. |
| `v1.2.4` | The v1.2.4 half is done. Run only "Continue to v2.0". |
| `migrating` | A previous run stopped. Resume this book. Do not start over, and do not add rows that are already there. Finish the checkpoint, then continue to v2.0. |
| `v1.2.3` | The receipt list already exists. Run the v1.2.4 patch, then "Continue to v2.0". Do not rebuild the list and do not rename a file that already uses the simple name. |
| anything else, or the cell is missing | This book is v1.0 through v1.2.2, or the marker was never written. Build the list, apply the v1.2.4 patch, then continue to v2.0. |

`D46` is a progress note. It is blank when there is nothing pending. A block that starts with `Pending duplicates:` is a duplicate question waiting for the user. A block that starts with `Pending formula fixes:` is a formula question waiting for the user. Do not apply either fix until they say yes. The two blocks can share the cell, each on its own line. Do not wipe one block while writing the other.

A book already created from the v2.0 template has `C46` = `v2.0` and empty Transactions and Receipts sections. Leave it alone. A book created from the v1.2.4 template has an empty receipt list and still needs "Continue to v2.0", which adds the new sections and does not invent rows.

Check every folder named `Family Book - YYYY` inside the `Family Book` root, not only the current year. Skip a folder that has no workbook. Do not migrate a workbook under Shared with me that this user does not own.

## Notice, then summary

If at least one owned book needs migration or a resume, say one line before changing anything, in the language of the chat. Say it once for the whole batch, not once per year. In English that line is: "I'm updating your Family Book to v2.0. Your entered amounts stay as they are. Existing receipt rows move into the Receipts section, and the first statement you import later links to them."

Then do the work. After the batch, send a short summary: which years were updated, how many receipt rows were written, how many files were re-read, how many files were renamed, any formula fix that was applied because it did not change a total, any formula fix still waiting for a yes, anything that could not be matched, and any duplicate groups waiting for a yes or no. If nothing needed migration, say nothing.

## Do not touch the numbers

The automatic pass must not change an amount, an item, a date, or a typed number. The number area is rows 1 to 44 on each month sheet (income, fixed expenses, daily record, totals) and every value the user typed. Do not rewrite those cells to "re-input" them. The new list is filled below that data.

Formula fixes are separate, and only the formulas named under "Formula fixes" may change. If applying one would change a displayed total, report it and wait. A number format change on the receipt-list Total column shows the cents that were already stored. That is not a formula fix and it does not change the stored amount. Apply it and mention it. Do not ask.

The only amount edits are the duplicate fixes in the last section, and only after the user confirms that specific fix.

On OneDrive, re-download the workbook immediately before each write and upload it immediately after. Read `C46` again on that fresh copy before inserting a list, so a retry cannot insert the list twice.

## Where the template and the receipt files come from

The blank template and this skill come only from GitHub, never from the owner's Google Drive. Reading this family's own receipt files is required for the re-read below, and so is reading the workbook. On Google, read and write the sheet with the Sheets connector. On OneDrive, re-download the workbook before a write. Do not export the Google Sheet in order to obtain a template.

## Resume and run it twice safely

The migration is safe to run twice. A rerun adds nothing that is already there.

1. Set `B46` to `Book version` if it is missing, set `C46` to `migrating`, and upload before the structural edits. If a fresh read already shows `v1.2.4`, stop for that book except for a pending question in `D46`. If it already shows `migrating`, continue without clearing rows. Remember whether the book was `v1.2.3` before you set `migrating` (the list is already there; do not rebuild it). `D46` can hold `phase: patch` or `phase: full` while you work.
2. A full migration (the book was not `v1.2.3` and has no receipt list yet) follows "Where the rows come from", then "List layout", then "File names", then "Duplicates already in the book". A patch (the book was `v1.2.3`, or the list is already there) does not rebuild the list and does not rename a file that already uses the simple name. It still adds a month-list row for a Log row that has none, so a duplicate pair that was collapsed to one list row shows as two. A rerun that already finds that row adds nothing.
3. Find the receipt list by scanning column B for a cell whose text starts with `Receipts this month`. If it is there, do not write the title or the headers again. Data rows start on the next row after the header row (the header row is the one that contains `Date & time` in column B).
4. If the list is not there and this is a full migration, place it below the number block. On a standard sheet, `I44` is `Balance` and row 47 is empty, so the title goes in `B47`. If row 47 already has a value, or `I44` is not `Balance`, put the title on the first row at or below 47 that is clear of values, with one blank row above it. Never overwrite a cell that already has a value.
5. Write the title and headers exactly as the v1.2.4 template does (see "List layout" below), including the styling. Leave columns E and H blank. In Excel set their width to 1.63 character units. On the Sheets connector set them to 20 px (the connector's minimum is 20 px, and it takes pixels, not character widths). Do not change any other column width. Do not change row heights in rows 1 to 44. Always apply the title and header styles. The connector cannot read formats, so do not try to skip styling.
6. On a full migration, add a list row only for a Log row that does not already have one. A purchase that is not an unresolved duplicate has one Log row and one month-list row. An unresolved duplicate pair has two Log rows and two month-list rows, so the pair shows clearly. A rerun sees those rows and adds nothing: no third row, and no second copy of a row that is already listed. Fill only blank cells (receipt number, time, items, payment, file link, source, hash, status). Do not change a Total that is already filled.
7. Rename a file only when its name is still the old pattern. A name that already matches `YYYY-MM-DD HHMM - Store - TOTAL.ext` or `YYYY-MM-DD - Store - TOTAL.ext` (optional ` - #receiptno` or ` - item` suffix included) stays as it is. The same name includes the extension.
8. Apply "v1.2.4 patch" (formats, merge, banner, Log note, formula questions). Do this for a v1.2.3 book and at the end of a full migration.
9. When the patch is done, the Log and the lists agree, and any full-migration renames are done, the v1.2.4 checkpoint is complete. Do not stop. Do not leave `C46` at `v1.2.4` as the finished marker. Continue with "Continue to v2.0" in this same run. A duplicate question or a formula question still lives in `D46` and is not a reason to rebuild tomorrow. The v2.0 half is what sets `C46` to `v2.0`.

`D46` can also hold a short progress line while `C46` is `migrating`, for example `2026: Jan-Apr lists done`. On resume, trust the sheet (the header and the existing rows), not only `D46`.

## Where the rows come from

Build one picture of each purchase, then write it. Use all three sources. A purchase that appears in more than one source is still one row, unless it is an unresolved duplicate pair, which stays two rows until the user answers.

The family's own receipt files are read here on purpose. That read is not a download of the template.

1. **Hidden Log tab**, when the book has one. Read every data row from row 2 down. Columns A to G are the v1.2 log: Source, Date, Merchant, Total, Where written, Saved file, Logged by. Columns I to O may already exist; if they do not, add those headers (see below) without clearing A to G.
2. **Files in that year's `receipts` folder.** Re-read each file (photo, PDF, or text) and take the receipt or order number, the time of purchase, the line items, and the card last 4 if they are printed. Hash the bytes with SHA-256 and store that in column O. Column O is the primary check that a file was already saved, including after a rename. The same hash is the same file: do not upload a second copy. Name plus size is only a fallback when the bytes cannot be hashed, and it misses a renamed copy. Never store more than the last 4 digits of a card. If a file cannot be read, keep the Log's date, merchant, and total, leave the missing fields blank, and flag `unreadable file: <name>` in the summary. When the date printed on the receipt and the date already in the Log differ, the receipt's transaction date wins. Update the Log date and the file name's date. Do not keep the email's sent date. When both dates are transaction dates on two receipts the user confirmed are the same purchase, the earlier transaction date wins. The receipt number does not pick the date.
3. **The original email**, when the Log Source (or the file) contains an email message id and that mailbox is connected. Re-read the message for the same fields. If this bot cannot open that mailbox, flag `email not re-read: <id>` and keep going. Do not send, reply, forward, label, or delete mail.

Books from v1.0 and v1.1 have no Log tab. For those:

1. Add a `Log` sheet with the v1.2.4 header row (below) and try to hide it (see "Log tab").
2. Re-read every file in `receipts`.
3. Read the number cells that are not formulas: income `C8:C11`, fixed expenses `C18:C38`, and the daily amount columns (K, M, O, and so on through BS) on rows 6 to 20, 22 to 40, and 43. Skip any cell whose value starts with `=`. Skip rows 21, 41, 42, and 44.
4. Match a file to those cells by the purchase date's day column, a full merchant match against the item text, and the amount. A split receipt is one purchase whose cells add up to the file's total. Put every cell in Category/cells written, for example `J6+J22`.
5. An amount cell with no file still gets a list row and a Log row. Leave File blank and set Source to `sheet`. Set Status to `done`. Flag `no file` in the summary.
6. A file with no matching amount still gets a list row and a Log row. Leave Category/cells written blank. Flag `no matching amount: <file>`. Do not invent an amount in the number area.
7. Then continue with the same rename, duplicate, and v1.2.4 patch steps as a book that had a Log.

## List layout

Month sheets freeze at `J6`: columns A:I and rows 1:5 are frozen. On a book that already has merges, unmerge first. Setting the freeze while a merge still crosses it is rejected ("you can't freeze columns which contain only part of a merged cell"). A merge that includes both a frozen column and an unfrozen column is also rejected ("You can't merge frozen and non-frozen columns"). A converted v1.2.3 book still has the title merged `B47:S47`, which crosses the boundary between I and J, and it still has data-row merges such as `L49:R49`.

Do this in order, on every month sheet, before you rely on the freeze:

1. In the receipt list (the title row and every row below it), unmerge every range that includes a column at or before I and a column at or after J. That removes `B47:S47`. Also unmerge every data-row merge, including `L49:R49` and any other `L:R` merge on a receipt row. Do this even when a data-row merge does not itself cross I/J. The header `L:R` does not cross I/J. Unmerge the header too if it does.
2. Then set the freeze at `J6`.
3. Then merge the title from B through I only. After the freeze, merge `L:R` on the header row only. That range is entirely unfrozen. If a freeze would split `L:R`, do not merge it; leave Source in L. Never merge over column S. Never merge a data row.

Write this on each month sheet that does not already have it. If the title is already there, still unmerge, freeze, merge, and style, in that order. English labels, exactly:

- Title, column B, merged **B through I only** after the unmerge and the freeze: the first line is `Receipts this month`. The second line is `One row per receipt. These rows are not included in the totals above.` Do not merge past column I. Do not merge into column J or through column S.
- Header row, the next row. Column B `Date & time`, C `Store`, D `Receipt/order #`, F `Items`, G `Total`, I `Category/cells written`, J `Payment`, K `File`, L `Source`, S `Logged by`.
- One data row per Log row that is being kept, starting the row after the header. An unresolved duplicate pair is two data rows. A row whose Status is `superseded` stays on the list. Write the Source value in column L. Do not merge the data row.

On the standard template the title is row 47, the headers are row 48, and the first receipt is row 49. Do not assume those row numbers if the title was placed lower.

### Styling a connector can apply

The Sheets connector cannot copy a style from the xlsx, and it cannot read cell formats, so it cannot tell whether styling is already in place. Always apply these values. Applying them again is safe. Do this on a new list and on a list that is already there. Do not skip this step.

Title, every cell `B` through `I` on the title row, then merge `B:I`:

- Font: Arial, 14 pt, bold, white `#FFFFFF`
- Fill: solid `#1F4E79`
- Align: left, vertical center, wrap text
- Row height: 40 pt in Excel. The Sheets connector takes pixels: set this row to 53 px. Do not write 53 as points.

Header cells B, C, D, F, G, I, J, K, L, and S (not E, not H):

- Font: Arial, 10 pt, bold, color `#1F4E79`
- Fill: solid `#D6E3F0`
- Align: center, vertical center, wrap text
- Border: thin `#8FA8C4` on all four sides
- Row height: 32 pt in Excel. The Sheets connector takes pixels: set this row to 43 px. Do not write 43 as points.

Columns E and H stay empty. Excel width is 1.63 character units. The Sheets connector takes pixels, and the minimum is 20 px, so a connector-only bot sets E and H to 20 px. Do this on every month sheet (Jan E and Jul H are the ones that drift). Do not change any other column width. Do not change a row height in rows 1 to 44. Do not set an Excel column width to 20, and do not set an Excel row height to 53 or 43: those numbers are pixels for the connector only.

Total column G, from the first receipt row down through at least row 200: number format `#,##0.00_);[Red](#,##0.00)`. The column default `#,##0_);[Red](#,##0)` shows 87.45 as 87. Do not leave that format on these cells. Applying it does not change the stored amount. Do not ask.

Cell values:

| Column | What to write |
|---|---|
| B Date & time | `YYYY-MM-DD HH:MM` when the time is known, otherwise `YYYY-MM-DD`. The receipt's transaction date wins. |
| C Store | Short merchant name, no person's name. `Costco.ca` is `Costco`. |
| D Receipt/order # | The number, or blank. A user-confirmed separate purchase uses `separate`. A fuel AUTH code is not a number; leave it blank. Fill a blank when a later copy of the same purchase has a number. |
| F Items | `product: price; product: price`. Product names follow the chat language. The header stays English. |
| G Total | A number with two decimals. Negative for a return. Do not copy this number up into the category cells. |
| I Category/cells written | Amount cells joined with `+`, for example `AN6+AN17+AN22`. Fixed expenses can stay `Fixed Expenses / GAS` when that is all the old Log row has; new rows prefer the cell, such as `C19`. |
| J Payment | Last 4 digits only, such as `1234`, or blank. |
| K File | One label and one link, to the primary file: `photo`, `email`, or `statement`. When there is another file, `photo +1`. Do not write `photo \| email`. |
| L Source | `photo`, `email gmail/family@example.com 18c3fab`, or `statement`. Join extra copies with ` \| `. |
| S Logged by | The display name from the old row, or blank. |

A cell holds one hyperlink. Column K links to the primary file. Every file, including a single one, is listed in Log column F as `1 photo: <url>` or `1 photo: <url> | 2 email: <url>`. The Log cell links to file 1. The other urls are plain text.

The list is not part of any total. Do not extend a SUM down into it.

These columns are also what a later card-statement check will match on (date and time, store, receipt or order number, total, payment last 4). That check is issue #6. This migration does not do it, and it does not close that issue.

## v1.2.4 patch

Run this on a v1.2.3 book and at the end of a full migration. It is safe to run twice. The Sheets connector cannot read formats, so styling is always applied. Do not skip a style, a row height, a column width, or the Total number format because you cannot tell whether it is already there. Applying them again is safe. Formula text can be read. Skip a formula write only when the cell already holds the target formula.

Do these in order. Freezing first fails on a converted v1.2.3 book, because `B47:S47` is still merged.

1. On every month sheet, in the receipt list, unmerge every range that crosses the I/J boundary, including the title `B:S`. Also unmerge every data-row merge, including `L49:R49` and any other receipt-row `L:R`. Do this before the freeze.
2. Then freeze every month sheet at `J6`.
3. Then merge the title `B:I` only. Merge header `L:R` only when that range sits entirely on one side of the freeze. Never merge a data row. Never merge across I and J.
4. Always apply the title and header styles, the row heights (53 px title and 43 px header on the connector; 40 pt and 32 pt in Excel), the E and H widths (20 px on the connector; 1.63 in Excel), and the Total number format from "Styling a connector can apply".
5. Convert old File labels in column K. A cell whose text is labels joined with ` | `, such as `photo | email` or `photo | email | photo | email`, becomes the new scheme. The first label is the primary file. One piece stays `photo`. Two pieces become `photo +1`. Four pieces become `photo +3`. Do not leave `photo | email` in column K. A cell that already reads `photo` or `photo +N` stays as it is. If the cell already has one link, keep that link on the primary file. If the cell is plain text with no link, and the saved file can be found (the url in Log column F, or the file of that name in `receipts`), create the one link from that file. If there is no file, leave the text as it is and do not invent a url.
6. Convert old Log column F. The v1.2.3 shape is `photo: <url> | email: <url>`, or a bare file name and url, with no leading number. Rewrite it to `1 photo: <url> | 2 email: <url>`. A single file becomes `1 photo: <url>`. A cell that already starts with `1 photo:` or `1 email:` is already new. If the cell already links to file 1, keep that link. If the cell is plain text with no link, and the file can be found in `receipts` or from a url already written in the cell, create the link to file 1. If there is no file, leave the text as it is and do not invent a url. Do this on the patch path and on a full migration.
7. Backfill Log column O where it is blank and the file can be read. Use the url in column F, or the file of that name in `receipts`. Hash the bytes with SHA-256 and write `1 <64 hex chars>`, or `1 <hex> | 2 <hex>` in the same order as column F. Column O is the primary re-sent-file check, including after a rename. If the file cannot be read, leave O blank and flag `hash not backfilled: <name>`. Do not invent a hash. Name plus size does not fill this cell.
8. Run "Formula fixes". One yes covers the whole book. The question lists every month and the before and after amount.
9. Replace the Annual Summary banner and the Log `H1` note. See "Banner and Log note". Always write the full text.
10. Add Log headers N `Status` and O `Content hash` if they are missing. Do not clear columns A to M. On a finished old row (it has a total, and it has a saved file or Source `sheet` or `note`), set Status to `done` if it is blank. Do not mark an old row `pending`. Do not mark an old row `question`.
11. Run "Duplicates already in the book" on this patch path too, not only after a full rebuild. Mark `pending duplicate` on both Source cells (Log column A and month-list column L). Do not delete a Log row.

## Formula fixes

These are the only formulas this migration may change. Never replace a formula with a typed number, and never change a cell that is not a formula. If the user has typed over one of these cells, leave it and flag `formula overwritten: <cell>` in the summary.

Check every month, Jan through Dec. The row labels are: Meals 6-16, Snacks 17-19, Dining Out 20, Total Food 21, Household Goods 22-27, Education & Enrichment 28, Fuel 29, Clothing 30-31, then Medical 32, Hair & Cosmetics 33, Transportation 34, Entertainment 35, Gifts & Social 36, Other 37-40.

| Cell | Target | Why |
|---|---|---|
| Each month `G10` | `=SUM(J28:BS28)` | Education is row 28. `=SUM(J28:BS29)` also adds the Fuel row. |
| Each month `G12` | `=SUM(G8:G11)+SUM(J29:BS29)` | Fuel stays inside Total Living Expenses, so the balance does not drop when it leaves `G10`. |
| Annual Summary Education, each month column | `=Jan!$G$10` (and `Feb`, `Mar`, ... through `Dec`) | `G10` no longer contains fuel, so do not subtract the fuel line. The old formula looks like `=Jan!$G$10-C17`. |
| Annual Summary February Clothing, Medical, Hair & Cosmetics, Transportation, Entertainment, and Gifts & Social (column D, rows 18 to 23) | the same formula with `BT` replaced by `BS` | Day 31 ends at BS. `BT` is past the grid. Leave the `K` start as it is. |

Leave these alone. They already match their labels:

- `G8` `=SUM(J21:BS21)` is the Food rollup through Total Food. Annual Summary Food subtracts snacks. Do not rewrite it.
- `G9` `=SUM(J22:BS27)` is Household Goods, rows 22-27.
- `G11` `=SUM(J30:BS41)` is the other daily categories from Clothing through Other. It does not include Fuel.
- Snacks, Fuel, and Other on Annual Summary already sum `$J$` through `$BS$` on the right rows.
- January's category sums already end at BS. March through December already end at BS. Do not change a `K` start to `J`. That does not fix a row label, and a number typed in the item column would change the total.

Apply a target only when the current formula is not already the target. Read the displayed value before and the value the target would show.

- A month whose displayed total would not change is applied right away. Fuel of 0.00 means that month's Education line does not change, so write that month's target now. An empty column BT means February's `BT` to `BS` change does not change a displayed total, so write it now. Say so in the summary.
- Only a month whose displayed total would change is held for a yes. The usual change is that month's Education line dropping by its fuel, while Total Living Expenses, the balance, and Annual Summary Education stay the same when that month's `G10`, `G12`, and Annual Summary Education cell are applied together. Those shown changes, and only those, are one group for the whole book. Do not put a month with no displayed change into the group. Do not ask once per month. Write the group into `D46` as one block starting `Pending formula fixes:`. Ask one yes/no question, answered once, that lists every month in the group and the before and after amount, and say the balance stays put. On later runs, if `C46` is already `v1.2.4` or `v2.0` and that line is still there, remind the user once. Do not apply the held months and do not rebuild the list.

When the user says yes, apply every month still in that group, then remove it from `D46`. Months that did not change a displayed total are already applied. When they say no, leave every formula still in the group and remove the line from `D46` so you do not ask again. Do not undo a month that was applied because its displayed total did not change. A no does not block the checkpoint, and it does not block continuing on to set `C46` = `v2.0`. Do not stop at `v1.2.4`.

## Banner and Log note

The v1.2.3 migration replaced only the version token inside `B2`. Books kept the older banner, without the third line, and the Log note stayed on the v1.2.2 wording. Replace both texts in full. Do not stop at the version token.

When `B2` contains `Family Book v`, set `B2` to exactly these four lines:

```text
Family Book v1.2.4 by SkybatanX: a yearly family income & expense book run by your personal Grok Bot.
The bot sets up each year's book and logs every receipt for you, from photos you send or from order and receipt emails.
Each month lists the receipts at the bottom, below the totals, and the same purchase is never added twice.
Follow @SkyXFunNext on X for more templates and fun!
```

If `B2` does not contain `Family Book v`, leave it and rely on `C46`.

Set Log `H1` to:

```text
Authoritative dedupe list for Family Book bots (v1.2.4). One row per purchase. Do not edit or delete rows. A duplicate the user confirms, and an answered question, is marked superseded in column N and kept. Columns I to M hold the receipt key and the link to that month's receipt list. Column N is Status: pending (the amount cell is chosen and recorded in column E before the amount is written), question (an open yes/no, nothing written), done, or superseded. Column O is the SHA-256 of each saved file. A retry reads the cell recorded in column E and does not pick a new row. The same purchase is also one row at the bottom of its month sheet.
```

Wrap the text. Do not put an amount in column H. A question row may list its dates there.

## Log tab

The hidden Log is the authoritative dedupe list for the year. The month list is the same purchases, written out where people can see them. After migration, a purchase that is not an unresolved duplicate is one active Log row and one month-list row. An unresolved duplicate pair is two Log rows and two month-list rows. A confirmed duplicate keeps both rows: the extra row's Status is `superseded`, and it is not deleted. A rerun adds neither a second row for the first case nor a third row for the second. Matching ignores a superseded row.

If the Log sheet is missing, create it and try to hide it. Excel: set the sheet state to hidden. Google Sheets: the Sheets connector has no hide-tab tool. Try to hide the tab if you can. If you cannot, ask the user once to right-click the Log tab and choose Hide sheet. Never fail the migration because the tab is visible. Do not ask again for that book.

Header row:

| Column | Header |
|---|---|
| A | Source |
| B | Date |
| C | Merchant |
| D | Total |
| E | Where written |
| F | Saved file |
| G | Logged by |
| H | The book note stays in `H1`. On a question row, column H is the notes column for the dates in that question. Do not write an amount there. |
| I | Receipt/order # |
| J | Date & time |
| K | Items |
| L | Payment |
| M | Month list row |
| N | Status |
| O | Content hash |

`Month list row` is the Date & time cell of that purchase, for example `Oct!B49`. Column F for one file is `1 photo: <url>`. Column O for one file is `1` plus the SHA-256 hex.

Column B stays `YYYY-MM-DD`. Column J repeats the date and time. An email sent date loses to the receipt's transaction date. When the user confirms two receipts are the same purchase, the earlier transaction date wins, and the receipt number does not pick the date. Column D is the number, shown to the cent. Do not delete old rows. Add the new columns onto them. A Log row with no month-list row gets one, unless a list row for that same Log row is already there. A month-list row with no Log row gets one Log row. That is how a pair becomes visible, and it is also how a single purchase gets its one row. A rerun that finds the row already in both places adds nothing. If the two disagree about the total, do not change the number cells. Flag it in the summary.

## File names

Rename each saved receipt to the simple name. Details stay on the sheet.

`YYYY-MM-DD HHMM - Store - TOTAL.ext`

- `HHMM` is 24-hour, four digits, no colon (`1432`). Omit it, leaving `YYYY-MM-DD - Store - TOTAL.ext`, when the time is unknown.
- Store is the short merchant name. `Costco.ca`, `Costco Wholesale`, and `COSTCO #7016` are `Costco`.
- `TOTAL` is two decimals, with a leading minus for a return (`-84.12`).
- The date is the receipt's transaction date.
- Strip characters Windows and OneDrive reject: `/ \ : * ? " < > |`, and control characters. Collapse spaces. Trim spaces and dots from the ends.
- The same name includes the extension. `57.29.png` and `57.29.pdf` are different names.
- The SHA-256 in Log column O is the primary check that a file was already saved, including after a rename. Name plus byte size is only a fallback when the bytes cannot be hashed, and that fallback misses a renamed copy. Do not upload a second copy and do not add ` - 2` when the hash matches.
- Add ` - #receiptno` or, if there is no number, ` - ` plus a short item hint, only when a different file would otherwise take a name the folder already has. If it still collides, add ` - 2`, ` - 3`.
- Rename in place. Do not upload a second copy. Then point the File link and the Log Saved file cell at the new name.
- If the rename fails, keep the old name, link that, and flag `rename failed: <old name>`.

## Duplicates already in the book

Run this after a full migration fills the lists, and run it on the v1.2.3 patch path as well (patch step 11). Look for the same purchase already recorded twice. Use the family-book matching rules. This pass does not auto-attach a new receipt. A new receipt auto-attaches only when it has exactly one candidate. Here, two Log rows that rules 1 or 2 call the same purchase are a duplicate group to report. Rule 3 is a question, not a silent merge. Skip rows whose Status is `superseded`. A fuel AUTH code is not a receipt number.

1. Same receipt, transaction, or order number at the same merchant (full match).
2. No number on one side: same merchant (full match), same total to the cent, dates within ±1 day.
3. A return (negative total) is its own purchase. It does not pair with the original sale.
4. If both sides have numbers and the numbers differ, they are different purchases. Do not pair them.

A group of two or more Log rows that rules 1 or 2 call the same purchase, or a receipt whose category cells add up to about twice the receipt total (or more), is an existing duplicate. The usual cause is a photo and an email, or the second Home Depot receipt, both added as amounts.

The pair stays on the list as two rows so it shows clearly. Do not collapse it to one row in this pass. Mark both Source cells with `pending duplicate` if that text is not already there: Log column A and month-list column L, on both rows. Do this on the patch path too, not only after a full rebuild. A rerun finds those two rows and adds nothing.

Report each group. Do not change the amounts in that report. For each group, name the year, the store, the date, the total, the cells that hold the extra amount, and the proposed fix. The proposed fix keeps one receipt row, attaches every file to it, and removes only the extra amount:

- A plain number that equals the extra amount: clear that cell.
- A formula such as `=84.12+84.12`: drop one addend, leaving `=84.12`.
- If the cell mixes this receipt with other purchases and the extra amount cannot be separated, do not propose an edit. Ask the user which cell to change.

Write the pending groups into `D46`, as a block that starts with `Pending duplicates:`, and list them in the summary. Ask for one yes or no per group, or one yes for all of them. On later runs, if `C46` is already `v1.2.4` or `v2.0` and `D46` still contains `Pending duplicates:`, remind the user. Do not rebuild the list. The daily scan mentions that reminder only inside a digest it is already sending, as one line. It never applies the fix.

When the user says yes to a group, apply only that proposed amount edit. Keep both Log rows and both month-list rows. Do not delete a Log row, and do not delete a list row. The Log note says not to edit or delete rows. The kept row drops `pending duplicate` from its Source, on Log column A and on month-list column L. Move the extra row's receipt number onto the kept row when the kept row's Receipt/order # is blank. Do not replace a number that is already there. Move the extra row's files onto the kept row (`photo +1` in column K, every url in Log column F). Set the extra Log row's Status to `superseded` and leave the row in place. Set that row's Source, and the extra list row's Source, to include `superseded` and to drop `pending duplicate`. Matching ignores a superseded row. Clear only the extra amount, as proposed. Remove that group from `D46`. When they say no, leave the amounts and leave both rows. On the extra row, set Receipt/order # to `separate` if it is blank, set Status to `done` if it was blank, and make sure Source includes `user confirmed separate` and no longer says `pending duplicate`. The kept row also drops `pending duplicate`. Drop that group from `D46`. A rerun must not propose it again and must not add another row.

## Flags

Put anything that does not match cleanly in the summary, and do not guess a number for it:

- unreadable file
- email not re-read
- no file for an amount cell
- no matching amount for a file
- list total and Log total disagree
- rename failed
- duplicate group waiting for a yes or no
- formula fix waiting for a yes or no
- formula overwritten
- hash not backfilled

A flagged row can still exist on the list with the fields that are known. A second run fills blanks. It does not create another row for a purchase that already has its one row, and it does not create a third row for a pair that already shows as two.

## Continue to v2.0

Run this after the v1.2.4 checkpoint, and run it alone when `C46` is already `v1.2.4`. It is safe to run twice. A second run copies nothing.

Set `C46` to `migrating` before the structural edits if it is not already `migrating`, and upload. On resume, trust the sheet. A Receipts row whose Receipt # is already there is not copied again.

Do not change an amount, an item, a date, a formula, or a typed number in rows 1 to 44. The grid cells that already hold a receipt stay exactly as they are. Copying a row into the Receipts section does not write the daily grid again.

A v1.2.4 month sheet has 71 columns. Column A is 1 and column BS is 71, which is day 31. Before you copy any receipt row, add the helper columns CA through CG. CA is column 79, CB 80, CC 81, CD 82, CE 83, CF 84, CG 85. They sit after BS. Columns BT through BZ (72 through 78) stay empty. Do not insert those helpers in the middle of the grid, and do not hide any column at or before BS. Write the headers from section 2 of the family-book skill: on Transactions, CA txn key through CG linked key; on Receipts, CA receipt key through CG linked txn key. Hide CA:CG only. If the connector cannot hide columns, still write them.

1. On every month sheet, find the old receipt list by scanning column B for a cell whose text starts with `Receipts this month` and whose header row has `Date & time` in column B. That is the v1.2.4 list. If that list is also the only section and it sits where the Transactions section now goes (usually row 47), do not leave it there. The v2.0 layout puts Transactions at row 47 and Receipts at row 150 on a blank template. On a book that already has receipt rows, place the Transactions title on the first clear row below the old list, or insert the Transactions block above the old title only when that insert does not shift a number cell in rows 1 to 44. The practical order on a standard v1.2.4 sheet: the old list occupies row 47 down. Insert 103 blank rows at row 47 (title, header, and 100 transaction rows, plus one blank), which moves the old `Receipts this month` title down to row 150. Then write the Transactions title and header into the inserted rows. Inserting rows below row 46 does not move rows 1 to 44. Do this once. If column B already has both `Transactions this month` and `Receipts this month`, do not insert again.
2. Write the Transactions title and header exactly as section 2 of the family-book skill, merged `B:I` only, with the connector sizes from that section. Leave columns E and H blank. Data rows start empty. Do not invent a transaction for an old receipt.
3. Copy each old receipt-list data row into the Receipts section. Map the old columns onto the new ones:
   - Old D Receipt/order # → Receipts B Receipt #. If it is blank, leave Receipt # blank. Do not invent `R-0001`. The receipt key in helper column CA is `Store|date time`, for example `Costco|2026-09-20 14:32`. That key is how a resume recognizes the row. A row whose Receipt # is already in the Receipts section is skipped. A blank-number row whose `Store|date time` key is already in column CA is skipped.
   - Old C Store → Receipts C Store.
   - Old B Date & time → Receipts D Date & time.
   - Old G Total → Receipts F Total. Copy the stored number. Do not retype it into the grid.
   - Old J Payment → Receipts G Card/pay. Last 4 only, or blank.
   - Old F Items → the Item / Price / Category triples starting at column I. Split `product: price` pairs. Categorize each item with the expense-category skill. Items that do not parse stay in the Note helper (column CC).
   - Old K File → Receipts column AA File. Copy the file into this year's `receipts` folder first, then point column AA and Log column F at that copy. Do not leave the link on the original path.
   - Old I Category/cells written → Receipts helper Where written (column CE). Do not write those cells again.
   - Old L Source and old S Logged by stay on the Log. The Receipts helper File list (column CB) can repeat the source labels.
   - Receipts helper Status is `pending` for a card receipt and `cash` when payment is cash. Do not mark it `matched`. There is no statement line yet.
4. Leave the old list's number cells alone if the insert moved them. After the copy, the Receipts section is the list people read. Do not delete the old rows if deleting them would be the only way to remove a value the user can still see: once the rows have moved with the insert, they are the Receipts rows, and step 3 fills the new columns in place when the old header is still on that row. If you inserted and the old rows moved, rewrite the header to the Receipts header and fill the new columns from the values you just read. Read the old values before you overwrite a header. Do not drop a total.
5. Add the Cards sheet if it is missing: row 1 note, row 2 headers (Issuer, Product, Last 4, Holder, Statement day, Due day, Last amount due, Paid status, Card label, Last statement date, Period start, Period end, Minimum payment, Statement file), data from row 3, freeze at `A3`, Paid status validation `unpaid,paid`. Leave it empty when the user has not named a card. Do not guess last-4 digits from old Payment cells into Cards. A later statement fills Cards.
6. Add the hidden Merchant Map sheet if it is missing. Headers: Pattern, Category, Source, Last 4, Confirmed, Example, Updated. Add the hidden Statements sheet if it is missing. Headers: Statement id, Issuer, Product, Last 4s, Period start, Period end, Statement date, Due date, Minimum, Amount due, Amount remaining, File, Paid status. Try to hide Merchant Map, Statements, and Log. If the connector cannot hide a tab, ask once and keep going.
7. Add Log headers P through V if they are missing: Txn key, Card, Post date, FX note, Linked to, Statement file, Section row. Do not clear columns A to O. On each copied receipt, set Section row (column V) and Month list row (column M) to the Receipts Receipt # cell. Leave Txn key blank. A finished old Status of `done` may stay `done`. The Receipts helper Status is what a later statement matches. Do not mark an old row `question`.
8. Replace the Annual Summary banner (`B2`) and the Log `H1` note with the v2.0 text from the template. The banner's four lines name Family Book v2.0, SkybatanX, and `@SkyXFunNext`. The Log note is the v2.0 note in the template builder. Do not stop at a version token.
9. Flag duplicates using the same rule as "Duplicates already in the book" and as family-book rule 4. Two rows are a duplicate group only when rule 1 or rule 2 says they are the same purchase. If both sides have receipt numbers and the numbers differ, they are different purchases. Do not flag them and do not write them into `D46`. A pair with no number on one side, the same store, the same total to the cent, and dates within ±1 day is a duplicate group. Write that group into `D46` as a block that starts with `Pending duplicates:`. Keep both rows. Do not delete either row and do not clear either grid cell. When the user later says yes, clear only the extra grid amount, mark the extra Log row `superseded`, and keep the row.
10. Create the year's `statements` folder if it is missing: `Family Book - {year}/statements/`. Do not create a card subfolder until a statement names that card.
11. When the copy is done, set `C46` to `v2.0`. Do this even if `D46` still has a pending question. A rerun that already sees `v2.0` returns without copying. A resume that sees `migrating` and Receipts rows already copied copies zero rows and sets `v2.0`.

The first statement imported after this links a line to an existing Receipts row when the receipt-match skill says they are the same purchase. That link does not write the grid again. A statement line with no matching receipt is a new Transactions row and does write the grid, once. A rerun of that statement adds nothing.

Made by SkybatanX (@SkyXFunNext).
