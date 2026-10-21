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
- **One book per year**, kept together in one `Family Book` folder in your own storage: a Google Sheet on **Google Drive**, or an Excel workbook on **Microsoft OneDrive** (Excel Online).
- **Family sharing:** each person installs their own bot. One person starts the book and shares that year's folder; everyone else joins by pasting that link. The `Family Book` folder above it stays with the owner, so the blank template and other years are not part of the share. All of them write to the same book and the same `receipts` folder. A hidden Log tab stops the same receipt from being logged twice. Notes can show who logged an entry, such as `Costco (Mom)`. Google Drive works best when several people write.
- **Receipt photos:** send a picture in chat; the bot reads the merchant, date, and total and logs it.
- **Email receipts:** daily scan of every connected **Gmail** or **Outlook** account for order confirmations, receipts, and invoices (read-only, never sends or deletes mail, never logs the same order twice). Email is optional. Connecting an inbox later ("connect Outlook", "add my other Gmail") starts scanning that inbox too.
- **Smart splits:** a multi-category receipt (say, groceries plus household goods) is split so each part lands in its own category and the parts add up to the total.
- **Every receipt saved:** a copy of each receipt (photo, PDF, or rendered email) goes into a `receipts` folder next to the book.
- **Public holidays** filled in for your country and province or state.
- **Any currency:** inferred from your language or region (CAD, USD, EUR, GBP, and others) and confirmed in one line at setup. The blank template is CAD until then.
- **Automatic yearly summary:** monthly balance, expenses by category, share of expenses, and net.
- **New year, new book:** each December 20 at 9:00 AM the owner's bot creates next year's folder inside the same `Family Book` root. Bots that joined attach to that book.

## Get started with Grok Bot

1. Import the Family Book bot template into Grok Bot.
2. Say hi, in whatever language you write in. The bot replies in that language and does not ask you to pick one. Before it asks anything, it checks what is already connected.
   - **Google Drive or OneDrive already connected:** it skips service setup and starts. It uses the store that is ready. If both are connected, it uses the one that already holds a Family Book, or Google Sheets. It scans Gmail or Outlook when those are connected, and skips email when they are not. You are not asked which service to use.
   - **Nothing connected yet:** one connect step before anything else. Connect Google Drive, Google Sheets, and Gmail, or say you use Microsoft and connect OneDrive and Outlook. It continues as soon as one store is ready. Email can wait.
   - **The only confirmation:** a new book, with currency and holiday region inferred from your language or region, named in one line. Say go, paste a shared year-folder link if you are joining, or correct the currency or region. A name on entries (such as Mom, so a note can say `Costco (Mom)`) is asked only when you join or when other people will log too.
3. If you started the book, the bot downloads the template from this repo (it does not take files from your Drive), creates a `Family Book` folder (or reuses one you already have by that name), puts this year's folder and a `receipts` folder inside it, and fills in your holidays. If Gmail or Outlook is connected, it sets up the daily receipt scan. If you joined, it attaches to the shared book instead of creating one.
4. Send your first receipt photo. To add email later, say "connect Outlook" or "add my other Gmail". To add someone later, share the `Family Book - YYYY` folder with them as an editor and have them paste that link into their own Family Book bot. Share that year folder, not the `Family Book` folder above it.

See [docs/setup-guide.md](docs/setup-guide.md) for details.

## Where the files live

Google Drive and OneDrive use the same layout. The root folder is created once. Each year is a folder inside it.

```text
Family Book/
  Family Book - 2026/
    Family Book - 2026          the year's sheet or workbook
    receipts/
  Family Book - 2027/
    ...
  Family Book - Templates/      the owner's copy of the blank template
```

If you set up Family Book before this layout, your bot moves the existing `Family Book - YYYY` folders into `Family Book` the next time it runs. It tells you in one line first. The move keeps the file links. Someone who joined with a shared year-folder link does not move anything. Their link keeps working.

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
        └── new-year-book.md      creates next year's book inside Family Book each December
```

## Versioning

The template file is updated in place at the same path (`template/family-book-template.xlsx`), so the download link never changes and bots always get the latest version. Bot, skill, and docs are v1.2.2. The workbook template is unchanged: the note at the top of the Annual Summary sheet still shows v1.2. See [CHANGELOG.md](CHANGELOG.md) for what changed.

## Credits

Made by SkybatanX. Follow [@SkyXFunNext](https://x.com/SkyXFunNext) on X for more templates and fun!
