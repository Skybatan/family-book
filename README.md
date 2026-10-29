# Family Book

Family Book: a yearly income & expense tracker run by your Grok Bot.

A yearly household income & expense workbook (Excel `.xlsx` template) that runs itself with your personal **Grok Bot**.

Snap a photo of a receipt, or let the bot read your order emails, and every purchase lands on the right day in the right category. The same purchase is never added twice. The Annual Summary adds everything up. Setup asks only where to save the receipts and the report. You can log the first receipt within minutes. Card and bank statements are optional and are not asked for during setup. The book works with none: empty Transactions and Cards sections are fine, and the month grid fills from receipts. The book can live in Google Sheets, in Excel Online, or as an Excel file on your computer. Excel does not have to be installed. The bot writes that file itself and sends weekly, monthly, and yearly reports in chat.

## Any language

Family Book Bot replies in the language you write in, or in the Grok Bot app language. There is no language setup step. It chats, reads receipts, writes item notes, and sends digests in that language, so English, French, Chinese, Japanese, Spanish, and many others all work. The workbook's sheet and category labels, and receipt file names, stay in English (translated templates may come later).

## What's in this repo

**`bot/`** holds the Grok Bot pieces: the skill, routines, getting-started, and memory. **`template/`** holds the workbook. During setup, bots download the blank template from this raw URL:

https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx

## Features

- **Any language:** Family Book Bot replies in the language you write in, or in the Grok Bot app language, with no language setup step. English, French, Chinese, Japanese, Spanish, and many others. It chats, reads receipts, writes item notes, and sends digests in that language. Sheet and category labels, and receipt file names, stay in English (translated templates may come later).
- **One book per year**, kept together in one `Family Book` folder in your own storage: a Google Sheet on **Google Drive**, an Excel workbook on **Microsoft OneDrive** (Excel Online), or an `.xlsx` file on your computer when the Grok Bot desktop app is connected. Local mode is Excel files only. Excel does not have to be installed. See [docs/local-excel.md](docs/local-excel.md).
- **Family sharing:** each person installs their own bot. One person starts the book and shares that year's folder; everyone else joins by pasting that link. The `Family Book` folder above it stays with the owner, so the blank template and other years are not part of the share. All of them write to the same book and the same `receipts` folder. The same purchase is logged once, whether it arrives as a photo, an email, or both. Notes can show who logged an entry, such as `Costco (Mom)`. Google Drive works best when several people write.
- **Card statements:** PDF, CSV, a photo, or pasted text. Each month sheet keeps the number grid, then a Transactions section and a Receipts section. A statement has no transaction id. The bot builds a key from the last 4, the post date, the amount, the description, and an occurrence number. It checks each card's total before it writes. Payments are skipped. A return links to the original purchase.
- **Cards:** issuer, product, last 4, holder, statement day, due day, last amount due, and whether the bill is paid. Setup does not ask which cards you have. The bot learns them from the first statement you choose to send. Until then, card-due reminders and statement-ready nudges stay off. After they are on, a reminder fires three days before the due date and on the due date, and it stops when the bill is paid.
- **Receipts:** send a picture in chat; the bot reads the merchant, date, and total and logs it. A receipt that arrives before the statement is pending. When the statement line arrives, they link, and the grid uses the receipt's item split. A cash receipt fills the grid by itself.
- **Email receipts:** daily scan of every connected **Gmail** or **Outlook** account for order confirmations, receipts, and invoices (read-only, never sends or deletes mail). Email is optional. Connecting an inbox later ("connect Outlook", "add my other Gmail") starts scanning that inbox too. A second copy of a purchase, including a Home Depot eReceipt after the paper slip, is attached to the existing row and is not added again.
- **Smart splits:** a multi-category receipt (say, groceries plus household goods) is split so each part lands in its own category and the parts add up to the total.
- **Every receipt saved:** a copy of each receipt (photo, PDF, or rendered email) goes into a `receipts` folder next to the book, named `YYYY-MM-DD HHMM - Store - TOTAL.ext`.
- **Public holidays** filled in for your country and province or state.
- **Any currency:** inferred from your language or region (CAD, USD, EUR, GBP, and others) and confirmed in one line at setup. The blank template is CAD until then.
- **Automatic yearly summary:** monthly balance, expenses by category, share of expenses, and net.
- **New year, new book:** each December 20 at 9:00 AM the owner's bot creates next year's folder inside the same `Family Book` root. Bots that joined attach to that book.

## Get started with Grok Bot

1. Import the Family Book bot template into Grok Bot.
2. Say hi, in whatever language you write in. The bot replies in that language and does not ask you to pick one. If you do not already have a book, it asks one question: where to save receipts and the yearly report. When a desktop computer is connected, the choices are Google Drive and Google Sheets, OneDrive and Excel Online, or an Excel file on this computer. When no computer is connected, the question shows two options: Google Drive and Google Sheets, or OneDrive and Excel Online. You are not asked for a bank, a card list, or a statement.
3. Currency and holiday region are inferred from your language or region and named in one line. The book is created in that same reply. A name on entries (such as Mom, so a note can say `Costco (Mom)`) is asked only when you join or when other people will log too. Paste a shared year-folder link if you are joining a cloud book.
4. If you started a cloud book, the bot downloads the template from this repo (it does not take files from your Drive), creates a `Family Book` folder (or reuses one you already have by that name), puts this year's folder and a `receipts` folder inside it, and fills in your holidays. A local book is an `.xlsx` in the folder you pick, with `receipts` and `backups` beside it. Each copy on that computer needs your approval. Excel is not opened. If Gmail or Outlook is connected, it sets up the daily receipt scan. It always sets up the spending report. Card reminders stay off until you add a statement. If you joined, it attaches to the shared book instead of creating one.
5. Send your first receipt photo. To add email later, say "connect Outlook" or "add my other Gmail". To add someone later, share the `Family Book - YYYY` folder with them as an editor and have them paste that link into their own Family Book bot. Share that year folder, not the `Family Book` folder above it. A local file is one computer. Several people writing at once should use Google Sheets.

See [docs/setup-guide.md](docs/setup-guide.md) for details.

## Where the files live

Google Drive and OneDrive use the same layout. The root folder is created once. Each year is a folder inside it.

```text
Family Book/
  Family Book - 2026/
    Family Book - 2026          the year's sheet or workbook
    receipts/
    statements/{Issuer Product}-{last4}/
      YYYY-MM-DD statement.ext
  Family Book - 2027/
    ...
  Family Book - Templates/      the owner's copy of the blank template
```

If you set up Family Book before this layout, your bot moves the existing `Family Book - YYYY` folders into `Family Book` the next time it runs. It tells you in one line first. The move keeps the file links. Someone who joined with a shared year-folder link does not move anything. Their link keeps working.

A local book uses the same names inside the folder you pick:

```text
Family Book/
  Family Book - 2026.xlsx
  receipts/
  backups/
```

`statements/` is created when you import a first statement. Until then the Transactions and Cards sections stay empty.

## Use the template without a bot

Download the template directly:

https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx

Open it in Excel (or import it into Google Sheets), enter the year in `F5` on the Annual Summary, and start filling in the month sheets. [docs/template-guide.md](docs/template-guide.md) explains every sheet.

## Repo layout

```text
family-book/
├── README.md                     this page
├── CHANGELOG.md                  version history
├── template/
│   └── family-book-template.xlsx the blank workbook template
├── docs/
│   ├── template-guide.md         how the workbook works, sheet by sheet
│   ├── setup-guide.md            setting up Family Book with Grok Bot
│   ├── migration-v1.2.3.md       pointer to the current migration
│   ├── migration-v1.2.4.md       the v1.2.4 checkpoint inside the v2.0 update
│   ├── migration-v2.0.md         how older books pick up the v2.0 sections
│   ├── migration-v2.1.md         settings-only step from v2.0 to v2.1
│   └── local-excel.md            the computer book, approvals, and the queue
├── tests/v2.0/                   synthetic v2.0 fixtures and the statement checker
├── tests/v2.1/                   the v2.1 tester plan and the offline checker
└── bot/
    ├── README.md                 what each bot file is; the published template stays thin
    ├── getting-started.md        the bot's first conversation with a new owner
    ├── memory.md                 conventions the bot keeps in memory
    ├── skills/family-book/
    │   └── SKILL.md              the bot's family-book skill
    ├── skills/family-book-getting-started/
    │   └── SKILL.md              receipts-first setup
    ├── skills/family-book-migrate/
    │   └── SKILL.md              update from v1.0–v2.0 to v2.1
    ├── local/
    │   ├── bookio.py             writes a local xlsx; does not start Excel
    │   └── queue.py              offline and locked-file queue
    ├── skills/statement-reader/
    │   └── SKILL.md              read a statement into lines and metadata
    ├── skills/transaction-category/
    │   └── SKILL.md              categorize a statement line
    ├── skills/expense-category/
    │   └── SKILL.md              categorize receipt items
    ├── skills/receipt-match/
    │   └── SKILL.md              link a receipt to a statement line
    └── routines/
        ├── daily-receipt-scan.md daily email receipt scan
        ├── spending-report.md    weekly, monthly, and yearly reports in chat
        ├── card-due-reminder.md  due-date reminders, after statement features are on
        ├── statement-ready.md    nudge when a statement should be out
        └── new-year-book.md      creates next year's book inside Family Book each December
```

## Updating an older book

Bots installed on v1.0 through v2.0 detect the book's version on the next run. The owner's bot runs the migration once, across every year in `Family Book`, and on a local workbook. An older book finishes the v1.2.4 checkpoint, then receipt rows are copied into the Receipts section. A book that is already v1.2.4 only gains the v2.0 sections. A book that is already v2.0 only gains a few settings cells. The bot does not ask you to retype the numbers. A duplicate is flagged and kept. The first statement imported afterwards links to the existing rows. Annual Summary cell `C46` is set to `v2.1` so the update does not run again. A family member's bot does not run it. Details: [docs/migration-v2.0.md](docs/migration-v2.0.md), [docs/migration-v2.1.md](docs/migration-v2.1.md), and [bot/skills/family-book-migrate/SKILL.md](bot/skills/family-book-migrate/SKILL.md).

## Versioning

The template file is updated in place at the same path (`template/family-book-template.xlsx`), so the download link never changes and bots always get the latest version. Bot, skills, docs, and the workbook template are v2.1. The note at the top of the Annual Summary sheet says v2.1, and cell `C46` (`Book version`) is `v2.1`. Cell `C47` (`Statement features`) starts at `off`. Cell `C48` (`Statement offer`) starts at `not yet`. Setup asks only where to save receipts and the report. See [CHANGELOG.md](CHANGELOG.md) for what changed. The offline checks are `python3 tests/v2.1/check_v21.py` and `python3 tests/v2.0/generate_and_check.py`. The step-by-step tester plans are [tests/v2.1/TEST-PLAN.md](tests/v2.1/TEST-PLAN.md) and [tests/v2.0/TEST-PLAN.md](tests/v2.0/TEST-PLAN.md).

## Credits

Made by SkybatanX. Follow [@SkyXFunNext](https://x.com/SkyXFunNext) on X for more templates and fun!
