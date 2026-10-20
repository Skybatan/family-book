# Changelog

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
