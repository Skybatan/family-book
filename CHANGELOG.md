# Changelog

## 2.0 - 2026-10-22

- Fixed: a card-due reminder reads each unpaid statement's amount and full due date. A missing amount says `check your statement for the amount`. An older unpaid bill is not replaced when a newer statement arrives. A payment counts only when it posts on or after that statement's date, and a partial payment reduces what is left.
- Fixed: a return lookup says the item was already refunded, with that refund's date, when a matching credit is already in the book. `T&T` stays `T&T` in the description. A refused import is still saved, with ` - not imported` in the name and the reason on the Log. A file-name collision is `YYYY-MM-DD HHMM - Store - TOTAL - 2.ext`, then ` - 3`. A receipt with no card is `cash`, and a pasted text receipt's File label is `text`.
- Fixed: a year-crossing statement files the statement under the statement-date year and each line under its post-date year. If that book does not exist, the bot asks once to create it. Fixed-expense row 18 is labeled `Income offset`, not `Income`.
- Fixed: migration copies receipt files and points the File links at the copies. A v1.2.4 sheet has 71 columns, so columns CA–CG (79–85) are added before the copy. A blank receipt number's key is `Store|date time`. Different receipt numbers are not flagged as one purchase.
- Changed: the final v1.2.4 rules from `main` (`e974065`). A retry with a blank Where written searches that day's category block, including each item cell of a split and Fixed Expenses or Income rows, for a cell that already holds this amount and whose text contains the short store name. It writes nothing when it finds one, and uses the first empty cell only when it does not. A pending row with the same receipt key is resumed, not treated as a rule 2 match. A match does not rename files. A bare yes asks which of the dates already listed. Source entries use one `, ` format. A book already on v1.2.4 still gets the ` | ` to `, ` conversion and the question-wording conversion.
- Added: each month sheet keeps the number grid and gains a Transactions section, then a Receipts section, both below the totals. The title merges from column B through I only. Columns A:I stay frozen.
- Added: a Cards sheet (issuer, product, last 4, holder, statement day, due day, last amount due, paid status). A hidden Merchant Map. A hidden Statements sheet. Statement files go in `Family Book - {year}/statements/{Issuer Product}-{last4}/YYYY-MM-DD statement.ext`.
- Added: four skills. `statement-reader` turns a PDF, CSV, photo, or pasted HTML or text into lines and statement metadata, and it checks each card's total before anything is written. `transaction-category` uses the issuer spend category, merchant patterns, and the learned map. `expense-category` categorizes receipt items. `receipt-match` links a receipt to a statement line and dedupes.
- Added: a generated transaction key, because a statement has no transaction id: last 4, post date, amount, normalized description, and occurrence number. Statement periods use the post date. The month sheet uses the transaction date when that date is in the same year as the post date. The CIBC `Ý` marker is stripped. Wrapped description lines, foreign-currency detail lines, two cards on one account, skipped payments, and returns linked to the original purchase are handled.
- Added: grid fill. A transaction with a receipt uses the receipt's item split. A transaction with no receipt uses its category for the whole amount. A cash receipt fills the grid alone. A receipt that arrives first is pending. When the statement line arrives, they link, and the amount is not added again.
- Added: bank accounts are optional. Card statements are enough, and without bank data the book tracks expenses only. With bank data, a recurring debit goes to Fixed Expenses, a deposit goes to Income after you confirm it, and a transfer or a card payment is skipped. A card payment pays down the oldest unpaid bill whose statement date is on or before the payment.
- Added: a card-due reminder, three days before the due date and on the due date, unless the bill is paid. A statement-ready nudge on the statement day, then once more three days later if it is still missing. An issuer "statement is ready" email on that day is the first nudge.
- Added: return lookup. A photo of a product or a tag searches the Receipts section and replies with the receipt file, store, date, price, card, and the return window when the store is known.
- Added: migration from v1.2.x to v2.0. Receipt-list rows become Receipts rows. Amounts are not retyped. The first statement imported afterwards links to those rows. The run is resumable and safe to run twice. Duplicates are flagged and never deleted. See [docs/migration-v2.0.md](docs/migration-v2.0.md).
- Changed: getting started still detects a connected store first. After the book exists, a new user is asked which cards they have, or the bot learns them from the first statement.
- Template: Annual Summary note and `Book version` cell are v2.0. The credit line stays "Made by SkybatanX (@SkyXFunNext)".
- Tests: [tests/v2.0/TEST-PLAN.md](tests/v2.0/TEST-PLAN.md) is the connector-only plan. `python3 tests/v2.0/generate_and_check.py` rebuilds the synthetic fixtures and checks keys and totals. The fixtures use invented names and last-4 digits.

## 1.2.4 - 2026-10-21

- Fixed: a near match now asks before anything is written. The same clear store with the same total up to 7 days apart is a yes/no question, and so is the same date and total with a partial merchant name. A single rule 1 or rule 2 candidate stays automatic. Two or more candidates ask first. A fuel AUTH code is not a receipt number. The receipt's transaction date wins over the email's sent date.
- Fixed: logging is idempotent. The bot writes the Log row first as `pending`, with the receipt key, then the amount, then the file, then the month-list row, then `done`. A retry checks the Log key first and does not add the amount again. A blank Receipt/order # is filled when a later copy has the number.
- Fixed: one link per cell. The month list links the primary file (`photo`, or `photo +1` when there is another). Every url lives on the Log. A re-sent file is detected by SHA-256, or by the same name (extension included) and size, and is not saved twice.
- Fixed: the receipt-list title is merged from column B through I. Columns A:I are frozen, and Google Sheets rejects a merge through column S. The migration documents the title and header styling so a bot can apply it without copying the xlsx. Hiding the Log tab is tried, and if the connector cannot hide a sheet the bot asks once and continues.
- Fixed: the template. Receipt totals use two decimals, so 87.45 no longer shows as 87. Education on every month sheet sums row 28 only; Fuel stays in the living-expense total, so the balance does not change. February's category sums stop at column BS. Columns E and H are the narrow spacer on every month. The banner and the Log note are the full v1.2.4 text, not only a version token.
- Changed: the blank template and the bot files come from this GitHub repo. A family's bot may read that family's own receipt files. `Costco.ca` is `Costco` in the file name and the Store column.
- Changed: migration covers v1.0 through v1.2.3. A v1.2.3 book is patched and its list is not rebuilt. A rerun adds no row. A flagged duplicate stays two rows until you answer, and a second run adds nothing. Formula fixes that would change a displayed total are shown and applied only after a yes. Entered amounts are not retyped. See [docs/migration-v1.2.4.md](docs/migration-v1.2.4.md).
- Template: Annual Summary note and `Book version` cell are v1.2.4. The Log gains Status and Content hash columns.
- Fixed: migrating a v1.2.3 book unmerges the title (`B:S`) and any data-row merge (`L49:R49`) before it freezes at `J6`, then merges the title `B:I` only. Freezing first is rejected while that merge is still there. Styling is always applied, because the Sheets connector cannot read formats. Connector sizes are 53 px for the title row, 43 px for the header row, and 20 px for columns E and H. Excel stays at 40 pt, 32 pt, and width 1.63.
- Fixed: a retry writes only the amount cell recorded on the pending Log row before the amount is written. If Where written is blank, it records a cell in that day's category block that already holds this amount and whose item text contains the store, and writes nothing. Only if none is found does it use the first empty cell.
- Fixed: a re-sent file is recognized by the SHA-256 in the Log, including after a rename. Name and size are only a fallback when the file cannot be hashed. Migration backfills that hash when the old file can be read.
- Fixed: the v1.2.3 patch rewrites `photo | email` file cells to `photo +N`, rewrites the old Log file list, and marks an existing duplicate `pending duplicate`. A confirmed duplicate is marked `superseded` and kept. Log rows are not deleted.
- Fixed: matching gathers every candidate first and auto-attaches only when there is exactly one. Two or more, including an Oct 10 receipt with an Oct 11 rule 2 match and an Oct 3 rule 3 candidate, are one question that lists every candidate. An unanswered question stays one Log row with nothing written. Dates that join it are recorded in Log column H. A later identical receipt joins that row. The earlier transaction date wins for a rule 2 auto-attach and for a yes on rule 3. Only the kept Log row's date and HHMM change. Files keep their own names. The same amount moves to that day's column on the same category row. Source entries are joined with `, `. An email is `email gmail/<addr> <msgid>`. A second photo is `photo, photo`. A question row's Source is `open question: candidates <dates>; <source>`. A bare yes asks which of those same dates, for example "Which date does it match: Oct 11 or Oct 3? Reply no if it's new." A retry with a blank Where written records a cell in that day's category block that already holds this amount and whose item text contains the store, and writes nothing. Only if none is found does it use the first empty cell. A match writes that source on the month list (column L) as well as on the Log. Formula fixes that do not change a displayed total are applied immediately. Only months that would show a change are one question for the whole book.

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
