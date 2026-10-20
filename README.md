# Family Book

Family Book: a yearly income & expense tracker run by your Grok Bot.

A yearly household income & expense workbook (Excel `.xlsx` template) that runs itself with your personal **Grok Bot**.

Snap a photo of a receipt, or let the bot read your order emails, and every purchase lands on the right day in the right category. The Annual Summary adds everything up. No typing in the year, no data entry by hand: the bot sets up each year's book and does the logging for you.

## Any language

Family Book Bot speaks whatever language you do, because it runs on Grok, so it works in English, French, Chinese, Japanese, Spanish, and many others. It chats, reads receipts, writes item notes, and sends digests in your language. The workbook's sheet and category labels are in English for now (translated templates may come later).

## What's in this repo

**`bot/`** holds the Grok Bot pieces: the skill, routines, getting-started, and memory. **`template/`** holds the workbook. During setup, bots download the blank template from this raw URL:

https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx

## Features

- **Any language:** Family Book Bot speaks whatever language you do, because it runs on Grok. English, French, Chinese, Japanese, Spanish, and many others. It chats, reads receipts, writes item notes, and sends digests in your language. Sheet and category labels are in English for now (translated templates may come later).
- **One book per year** in your own storage: a Google Sheet on **Google Drive**, or an Excel workbook on **Microsoft OneDrive** (Excel Online).
- **Receipt photos:** send a picture in chat; the bot reads the merchant, date, and total and logs it.
- **Email receipts:** daily scan of **Gmail** or **Outlook** for order confirmations, receipts, and invoices (read-only, never sends or deletes mail, never logs the same order twice).
- **Smart splits:** a multi-category receipt (say, groceries plus household goods) is split so each part lands in its own category and the parts add up to the total.
- **Every receipt saved:** a copy of each receipt (photo, PDF, or rendered email) goes into a `receipts` folder next to the book.
- **Public holidays** filled in for your country and province or state.
- **Any currency:** CAD by default; USD, EUR, GBP, and others are applied at setup.
- **Automatic yearly summary:** monthly balance, expenses by category, share of expenses, and net.
- **New year, new book:** each December 20 at 9:00 AM the bot creates next year's book.

## Get started with Grok Bot

1. Import the Family Book bot template into Grok Bot.
2. Say hi, in whatever language you write in. The bot asks you, one question at a time:
   - **Language:** English, French, Chinese, Japanese, Spanish, or another?
   - **Storage:** Google Drive or OneDrive?
   - **Email:** Gmail, Outlook, or none (and which accounts)?
   - **Currency:** CAD, USD, EUR, or another?
   - **Holiday region:** your country and province or state.
3. Sign in on the connect cards it shows. The bot downloads the template from this repo, creates this year's book with a `receipts` folder, fills in your holidays, and sets up the daily receipt scan.
4. Send your first receipt photo.

See [docs/setup-guide.md](docs/setup-guide.md) for details.

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
│   └── setup-guide.md            setting up Family Book with Grok Bot
└── bot/
    ├── README.md                 what each bot file is; the published template stays thin
    ├── getting-started.md        the bot's first conversation with a new owner
    ├── memory.md                 conventions the bot keeps in memory
    ├── skills/family-book/
    │   └── SKILL.md              the bot's family-book skill
    └── routines/
        ├── daily-receipt-scan.md daily email receipt scan
        └── new-year-book.md      creates next year's book each December
```

## Versioning

The template file is updated in place at the same path (`template/family-book-template.xlsx`), so the download link never changes and bots always get the latest version. The current version is shown in the note at the top of the Annual Summary sheet. See [CHANGELOG.md](CHANGELOG.md) for what changed.

## Credits

Made by SkybatanX. Follow [@SkyXFunNext](https://x.com/SkyXFunNext) on X for more templates and fun!
