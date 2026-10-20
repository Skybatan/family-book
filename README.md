# Family Book

Family Book: a yearly income & expense tracker run by your Grok Bot.

A yearly household income & expense workbook (Excel `.xlsx` template) that runs itself with your personal **Grok Bot**.

Snap a photo of a receipt, or let the bot read your order emails, and every purchase lands on the right day in the right category. The Annual Summary adds everything up. No typing in the year, no data entry by hand: the bot sets up each year's book and does the logging for you.

## Any language

Family Book Bot replies in the language you write in, or in the Grok Bot app language. There is no language setup step. It chats, reads receipts, writes item notes, and sends digests in that language, so English, French, Chinese, Japanese, Spanish, and many others all work. The workbook's sheet and category labels, and receipt file names, stay in English (translated templates may come later).

## What's in this repo

**`bot/`** holds the Grok Bot pieces: the skill, routines, getting-started, and memory. **`template/`** holds the workbook. During setup, bots download the blank template from this raw URL:

https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx

## Features

- **Any language:** Family Book Bot replies in the language you write in, or in the Grok Bot app language, with no language setup step. English, French, Chinese, Japanese, Spanish, and many others. It chats, reads receipts, writes item notes, and sends digests in that language. Sheet and category labels, and receipt file names, stay in English (translated templates may come later).
- **One book per year** in your own storage: a Google Sheet on **Google Drive**, or an Excel workbook on **Microsoft OneDrive** (Excel Online).
- **Family sharing:** each person installs their own bot. One person starts the book and shares the year's folder; everyone else joins by pasting that link. All of them write to the same book and the same `receipts` folder. A hidden Log tab stops the same receipt from being logged twice. Notes can show who logged an entry, such as `Costco (Mom)`. Google Drive works best when several people write.
- **Receipt photos:** send a picture in chat; the bot reads the merchant, date, and total and logs it.
- **Email receipts:** daily scan of **Gmail** or **Outlook** for order confirmations, receipts, and invoices (read-only, never sends or deletes mail, never logs the same order twice).
- **Smart splits:** a multi-category receipt (say, groceries plus household goods) is split so each part lands in its own category and the parts add up to the total.
- **Every receipt saved:** a copy of each receipt (photo, PDF, or rendered email) goes into a `receipts` folder next to the book.
- **Public holidays** filled in for your country and province or state.
- **Any currency:** CAD by default; USD, EUR, GBP, and others are applied at setup.
- **Automatic yearly summary:** monthly balance, expenses by category, share of expenses, and net.
- **New year, new book:** each December 20 at 9:00 AM the owner's bot creates next year's book. Bots that joined attach to that book.

## Get started with Grok Bot

1. Import the Family Book bot template into Grok Bot.
2. Say hi, in whatever language you write in. The bot replies in that language and does not ask you to pick one. It asks, one question at a time:
   - **New or join:** start a new family book, or join one your family already shares? If it's just you, say new.
   - **Storage:** Google Drive or OneDrive? (skipped when a join link already shows which one)
   - **The shared link,** only if you are joining.
   - **Email:** Gmail, Outlook, or none (and which accounts)?
   - **Currency** and **holiday region,** only when you are starting the book.
   - **Your name on entries,** when you are joining or when other people will log too (for example Mom), so a note can say `Costco (Mom)`. Someone starting a book alone is not asked.
3. Sign in on the connect cards it shows. If you started the book, the bot downloads the template from this repo, creates this year's book with a `receipts` folder, fills in your holidays, and sets up the daily receipt scan. If you joined, it attaches to the shared book instead of creating one.
4. Send your first receipt photo. To add someone later, share the `Family Book - YYYY` folder with them as an editor and have them paste that link into their own Family Book bot.

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
