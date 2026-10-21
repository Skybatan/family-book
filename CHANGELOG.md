# Changelog

## 1.2.4 - 2026-10-21

- Fixed: a near match now asks before anything is written. The same clear store with the same total up to 7 days apart is a yes/no question, and so is the same date and total with a partial merchant name. Rules 1 and 2 stay automatic. A fuel AUTH code is not a receipt number. The receipt's transaction date wins over the email's sent date.
- Fixed: logging is idempotent. The bot writes the Log row first as `pending`, with the receipt key, then the amount, then the file, then the month-list row, then `done`. A retry checks the Log key first and does not add the amount again. A blank Receipt/order # is filled when a later copy has the number.
- Fixed: one link per cell. The month list links the primary file (`photo`, or `photo +1` when there is another). Every url lives on the Log. A re-sent file is detected by SHA-256, or by the same name (extension included) and size, and is not saved twice.
- Fixed: the receipt-list title is merged from column B through I. Columns A:I are frozen, and Google Sheets rejects a merge through column S. The migration documents the title and header styling so a bot can apply it without copying the xlsx. Hiding the Log tab is tried, and if the connector cannot hide a sheet the bot asks once and continues.
- Fixed: the template. Receipt totals use two decimals, so 87.45 no longer shows as 87. Education on every month sheet sums row 28 only; Fuel stays in the living-expense total, so the balance does not change. February's category sums stop at column BS. Columns E and H are the narrow spacer on every month. The banner and the Log note are the full v1.2.4 text, not only a version token.
- Changed: the blank template and the bot files come from this GitHub repo. A family's bot may read that family's own receipt files. `Costco.ca` is `Costco` in the file name and the Store column.
- Changed: migration covers v1.0 through v1.2.3. A v1.2.3 book is patched and its list is not rebuilt. A rerun adds no row. A flagged duplicate stays two rows until you answer, and a second run adds nothing. Formula fixes that would change a displayed total are shown and applied only after a yes. Entered amounts are not retyped. See [docs/migration-v1.2.4.md](docs/migration-v1.2.4.md).
- Template: Annual Summary note and `Book version` cell are v1.2.4. The Log gains Status and Content hash columns.
- Fixed: migrating a v1.2.3 book unmerges the title (`B:S`) and any data-row merge (`L49:R49`) before it freezes at `J6`, then merges the title `B:I` only. Freezing first is rejected while that merge is still there. Styling is always applied, because the Sheets connector cannot read formats. Connector sizes are 53 px for the title row, 43 px for the header row, and 20 px for columns E and H. Excel stays at 40 pt, 32 pt, and width 1.63.
- Fixed: a retry writes only the amount cell recorded on the pending Log row before the amount is written. It does not take the next empty row in a category block.
- Fixed: a re-sent file is recognized by the SHA-256 in the Log, including after a rename. Name and size are only a fallback when the file cannot be hashed. Migration backfills that hash when the old file can be read.
- Fixed: the v1.2.3 patch rewrites `photo | email` file cells to `photo +N`, rewrites the old Log file list, and marks an existing duplicate `pending duplicate`. A confirmed duplicate is marked `superseded` and kept. Log rows are not deleted.
- Fixed: matching gathers every candidate first. A rule 1 or rule 2 hit still attaches automatically, and a rule 3 candidate besides that hit is mentioned. An unanswered question stays one Log row with nothing written, and a later identical receipt joins it. When both sides of a confirmed rule 3 match are receipts, the earlier transaction date wins. A match writes the new source on the month list (column L) as well as on the Log. Formula fixes that change a displayed total are one question for the whole book, listing every month and amount.

## 1.2.3 - 2026-10-21

- Added: a **Receipts this month** list at the bottom of each month sheet (Jan to Dec), below the totals. One row per receipt: date and time, store, receipt or order number, items, total, category cells, payment last 4, file link, source, and who logged it. No total formula includes those rows. The same columns are what a later card-statement check can match on ([issue #6](https://github.com/Skybatan/family-book/issues/6) stays open).
- Changed: dedupe is by receipt key, not by file name. The same receipt number at the same store is one purchase. With no number, the same store, the same total to the cent, and a date within a day is one purchase. A near match asks one yes/no and does not guess. A match attaches the extra file (`photo | email`) and does not add the amount again. A return is its own row. The hidden Log tab is the shared dedupe list. The month list shows the same rows.
- Changed: receipt file names are `YYYY-MM-DD HHMM - Store - TOTAL.ext`. The time is omitted when it is unknown. A receipt number or a short item hint is added only when the name would collide. Characters Windows and OneDrive reject are stripped.
- Added: migration for books set up on v1.0 through v1.2.2. The owner's bot runs it once on the next run, for every year in the `Family Book` folder. It rebuilds the lists from the Log, the saved files, and the original emails, and renames files. It does not retype the numbers. Existing duplicates are reported and corrected only after a yes. The run is resumable. Annual Summary `C46` records `v1.2.3` so it does not run again. See [docs/migration-v1.2.3.md](docs/migration-v1.2.3.md).
- Template: Annual Summary note and `Book version` cell are v1.2.3. The blank workbook includes the month lists and the extra Log columns. Day columns stay as fixed in v1.2.2: day 31 is BR/BS, and reads go through BS.

## 1.2.2 - 2026-10-21

- Changed: setup checks Google Drive, Google Sheets, Gmail, OneDrive, and Outlook before any question. If Google Drive or OneDrive is already connected, the bot skips service setup and starts. It uses the one store that is ready. If both are ready, it uses the one that already has a Family Book, or Google Sheets when neither or both do. It does not ask which service to use. Connected Gmail and Outlook accounts are scanned. If no inbox is connected, email is skipped.
- Changed: basic setup runs only when no store is connected. One step offers Google (Drive, Sheets, and Gmail), with Microsoft (OneDrive and Outlook) as the other choice. The bot continues as soon as one store is ready.
- Changed: the remaining setup is one confirmation. Currency and holiday region are inferred from language or region. A new book is assumed unless the user pastes a shared link or already has a book. A new user who already has Google connected is set up in one or two replies.
- Added: connecting a service later ("connect Outlook", "add my other Gmail") shows the connect card and starts scanning that inbox. The daily scan rechecks which accounts are ready.
- Fixed: day columns in the skill and docs. Day 29 is BN/BO, day 30 is BP/BQ, and day 31 is BR/BS. The formula 10+2*(d-1) was already right; the note that day 31 is BN/BO was wrong. Reads and writes go through column BS, which matches the sheet totals (`J21:BS21`). Verified with openpyxl against `template/family-book-template.xlsx`. At v1.2.2 the workbook file was unchanged and the Annual Summary note still said v1.2.
- Changed: the blank template is always downloaded from GitHub. The bot does not download files from the owner's Google Drive.

## 1.2.1 - 2026-10-20

- Changed: one `Family Book` root folder holds every year, on Google Drive and on OneDrive. Setup creates that folder once, or reuses a top-level folder that already has that exact name, and puts `Family Book - YYYY` and `receipts` inside it. The owner's bot remembers the root folder id, and on OneDrive the path. `Family Book - Templates` lives in the root too.
- Changed: the new-year routine creates next year's folder inside that same root.
- Added: migration for books set up with v1.0 through v1.2. On the next run, the owner's bot says so in one line, then moves top-level `Family Book - YYYY` folders, and a top-level templates folder, into `Family Book`. The move keeps folder ids and share links. A family member who joined with a shared year-folder link does not move anything.
- Sharing stays on the year folder. The root also holds the template and every year, so it is not the shared folder. Members still join by pasting the year-folder or workbook link.
- The workbook template is unchanged. The Annual Summary note still says v1.2.

## 1.2 - 2026-10-20

- Added: family sharing. Each person installs their own bot. Setup asks whether to start a new book or join an existing one. Joining uses the shared folder or workbook link the owner shared. A hidden Log tab in the workbook is the shared dedupe log, so two bots never log the same receipt twice. Item notes can show who logged them, for example `Costco (Mom)`. Everyone saves files to the same `receipts` folder. Only the owner's bot runs the new-year routine; members' bots attach to the new year's book. Google Drive works best when several people write. On OneDrive, the bot re-downloads the workbook right before each write. A receipt still counts as logged only once its file is saved in `receipts`.
- Changed: removed the language question. The bot replies in the language you write in, or the Grok Bot app or system language. Workbook labels, receipt file names, and these repo files stay English.
- Template: Annual Summary note bumped to v1.2. The blank workbook adds a hidden Log sheet.

## 1.1 - 2026-10-20

- Added: language choice at setup; the bot chats and writes notes in the user's language. Workbook labels stay English.
- The published Grok Bot template stays thin: on first use it downloads the skill, routines, and memory from this repo. The new-year routine runs December 20 at 9:00 AM and refreshes the skill first.

## 1.0 - 2026-10-20

Initial release.

- Blank yearly workbook template: Annual Summary, Jan to Dec month sheets, and Holidays.
- Month sheets with Income, Fixed Expenses, and a Daily Record by category; automatic monthly and cumulative balance.
- Annual Summary with monthly balance, expenses by category, share of expenses, and net.
- Grok Bot skill (`family-book`): yearly setup on Google Drive (Google Sheets) or OneDrive (Excel Online), year filled in automatically.
- Receipt logging from photos and from Gmail or Outlook order and receipt emails, with multi-category splits and a dedupe log.
- A saved copy of every receipt in the year's `receipts` folder.
- Public holidays filled in for the user's country and province or state.
- Any currency (CAD default; USD, EUR, and others applied at setup).
- Routines: daily email receipt scan, and next year's book created around Dec 20.
