# Local Excel book

Some people keep the yearly book on their own computer. Family Book v2.1 can do that when the Grok Bot desktop app is installed on macOS or Windows and that computer is connected. The book is an `.xlsx` file in a folder they choose. Receipt originals go in a `receipts` folder beside it.

Microsoft Excel does not have to be installed. The bot writes the `.xlsx` itself. It never starts Excel, Numbers, or LibreOffice. Weekly, monthly, and yearly category reports, plus one line of spending advice, are sent in the chat. The file stays in the folder so it can be opened later in Excel, Numbers, LibreOffice, or another viewer.

Local mode is Excel files only. Google Sheets and Excel Online remain the cloud choices. A local file is not the shared family book. Several people writing at once should use Google Sheets.

## Where the files sit

```text
Family Book/                         the folder they picked
  Family Book - 2026.xlsx
  receipts/
  backups/                           a copy taken before each replace
```

`statements/` is added when they import a first statement. Until then the Transactions and Cards sections stay empty, and the month grid is filled from receipts.

## Approvals

Every read or copy on the registered computer needs the user's local-tool approval. Editing does not. The bot copies the workbook to its own computer, edits that copy with Python (`bot/local/bookio.py`, openpyxl), and copies the result back.

A normal receipt is two approvals:

1. Copy the workbook to the bot.
2. Copy it back, after a backup, and copy the receipt file into `receipts/`.

Receipts that are waiting share those two approvals. The bot does not ask once per cell or once per sheet.

The copy back is one command. It refuses to replace the file when the workbook is open in another app, or when the file on disk is not the copy that was edited. It writes `backups/Family Book - YYYY - YYYYMMDD-HHMMSS.xlsx` first, and it does not overwrite an older backup.

## The computer is off

The bot keeps a queue on its own side, one row per receipt key (`bot/local/queue.py`). Nothing is written to GitHub. When the computer is off or asleep, the bot does not ask for an approval. It tells the user the receipt will be written when the computer is back, and that it will not be added twice.

When the computer returns, one copy-out and one copy-back apply every waiting receipt. A key that is already in the Log is marked done and is not given a second amount.

## The file is open

If Excel, Numbers, LibreOffice, or another app has the workbook locked, the copy back changes nothing. The same queue rows are marked retry. They are not added again. The next time the file is free, the receipt is written once. A backup from a failed attempt is not left half-written over the live file.

## The same book as the cloud

The receipt key, the dedupe rules, the categories, and the sheet layout match Google Sheets and Excel Online. A file can move from the computer to Drive or OneDrive, or the other way, without retyping amounts. A purchase that is already in the file is not logged again.

## Statement features

Annual Summary `C47` is `off` until the first statement is imported. Card-due reminders, statement-ready nudges, and income or fixed expenses taken from a bank file stay off. The routines read `C47` and send nothing while it is `off`. After about two weeks or 10 receipts, the bot may suggest statements once. A no is stored in `C48` as `declined` and is not asked again. Original statement files stay in the user's own folder or drive. Nothing is uploaded to GitHub.

Made by SkybatanX (@SkyXFunNext).
