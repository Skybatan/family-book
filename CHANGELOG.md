# Changelog

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
