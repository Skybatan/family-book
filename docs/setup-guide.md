# Family Book with Grok Bot: Setup Guide

Your Grok Bot, with the Family Book template, keeps a yearly household income and expense workbook for your family. You send it a photo of a receipt, or let it read your order emails, and it puts each purchase on the right day and in the right category. The Annual Summary updates on its own.

## Any language

Family Book Bot replies in the language you write in, or in the Grok Bot app language. There is no language setup step. It chats, reads receipts, writes item notes, and sends digests in that language, so English, French, Chinese, Japanese, Spanish, and many others all work. The workbook's sheet and category labels, and receipt file names, stay in English (translated templates may come later).

## What you need

- A Grok Bot with the Family Book bot template imported. The bot downloads the blank workbook template from this repo by itself ([template guide](template-guide.md) explains every sheet).
- One place to keep the book. The bot asks this once, and only when you do not already have a book:
  - **Google Drive + Google Sheets**, or
  - **Microsoft OneDrive + Excel Online**, or
  - an **Excel file on your computer**, when the Grok Bot desktop app is connected. Excel does not have to be installed. Details are in [local-excel.md](local-excel.md).
- Optional: an inbox where your order and receipt emails arrive (**Gmail** or **Outlook**). Card and bank statements are optional and are not part of setup.

## Step 1: Where the book goes

When you first talk to the bot, it replies in the language you write in. It does not ask you to pick a language. If you already have a book, it uses that book and does not ask again.

**No book yet.** One question: where should receipts and the yearly report be saved? Google Drive and Google Sheets, OneDrive and Excel Online, or an Excel file on this computer. The computer choice is offered only when the desktop app has a connected computer. You are not asked to install that app, and you are not asked for a bank, a card list, or a statement. Sign in on the connect card for the store you picked. You never paste a password. It continues as soon as that place can hold a file. Gmail and Outlook can wait.

Currency and the holiday region are inferred from your language or region, named in one line, and the book is created in that same reply. A short name for entries, such as Mom or Alex (`Costco (Mom)`), is asked only when you join or when other people will log too. Someone keeping the book alone is not asked for a name. Empty Transactions and Cards sections are correct. The month grid fills from receipts.

| You use | What ready looks like |
|---|---|
| Google storage | Google Drive and Google Sheets |
| Microsoft storage | OneDrive (Excel Online) |
| This computer | A connected Grok Bot desktop app. Excel does not have to be installed |
| Gmail receipts | Gmail, optional, scanned when it is connected |
| Outlook or Hotmail receipts | Outlook, optional, scanned when it is connected |

Say "connect Outlook" or "add my other Gmail" whenever you want another inbox. The bot shows the connect card, then scans that account too, including on the daily scan. You do not go through setup again.

## Step 2: Create this year's book

If you joined an existing book, the bot opens that shared workbook and does not create a second one. If you started a new book, it sets the book up on its own once your accounts are connected (or say "set up my Family Book"). You don't need to send it any file: it downloads the latest template from this repo automatically. The template and the bot's instructions come from this repo, not from your Google Drive. The bot does read the receipt files in your own `receipts` folder.

Google Drive and OneDrive use the same folders. `Family Book` is created once, at the top of your drive. If a folder with that exact name is already there, the bot reuses it and remembers its id (on OneDrive, its path too).

```text
Family Book/
  Family Book - YYYY/
    Family Book - YYYY          the year's sheet or workbook
    receipts/
    statements/{Issuer Product}-{last4}/
  Family Book - Templates/      blank template copy
```

The bot will:

1. Create or reuse the `Family Book` root, then download the blank template from this repo and save a copy in `Family Book - Templates` inside that root.
2. Create a folder named `Family Book - YYYY` inside the root, with a `receipts` subfolder inside the year folder.
3. Create a workbook named `Family Book - YYYY` in that year folder (a Google Sheet, or an .xlsx on OneDrive) with the year, your currency, and your public holidays already filled in. A `statements` folder is created when you import a first statement, not before. A local book is `Family Book - YYYY.xlsx` in the folder you picked, with `receipts` and `backups` beside it.

Each December 20 at 9:00 AM, the bot that started the book sets up next year's folder inside the same `Family Book` root, from the latest template. A bot that joined does not create a second book. It links the new one once that year folder is shared with you.

If your year folders were created at the top of the drive (Family Book v1.0 through v1.2), the owner's bot moves them into `Family Book` the next time it runs. It tells you in one line before the move. Moving keeps the file links. A family member who joined through a shared folder link does not move those folders.

## Sharing one book

Each person installs their own Family Book bot. One person starts the book. The others join it.

1. The owner shares the `Family Book - YYYY` folder (Google Drive or OneDrive) with each family member as an editor. The bot does not share the folder by itself. Share the year folder, not the `Family Book` root. The root is only there so every year sits in one place, and it also holds the blank template. Sharing the root would include that template and every year. A member does not need the parent folder. Joining is still pasting the year-folder or workbook link.
2. Each member pastes that year-folder or workbook link into their own bot. Their bot saves the same workbook and the same `receipts` folder. It does not create another book, and it does not move the owner's folders. After the owner moves a year folder into `Family Book`, the link the member already has still opens it.
3. Every bot logs into that one book. A hidden **Log** tab is the shared list that stops the same purchase from being entered twice, whether it arrived as a photo, an email, or both. The same row appears on that month's receipt list, at the bottom of the sheet. Notes can show who entered them, for example `Costco (Mom)`.
4. A photo or email receipt counts as logged only after its file is saved in the shared `receipts` folder. The file is named `YYYY-MM-DD HHMM - Store - TOTAL.ext`.

Google Drive and Google Sheets work best, because several people can edit at the same time. On OneDrive, two bots saving the same `.xlsx` can overwrite each other, so each bot re-downloads the workbook right before it writes and uploads it immediately after.

Someone keeping the book alone is not asked for a link or a name. Once they pick a place, the bot names the currency and holiday region in one line and starts the book.

## Step 3: Log receipts

- **Photo:** snap the receipt and send it in chat. The bot reads the merchant, date, and total, picks the category, writes it to that day, and files the photo in `receipts`.
- **Email:** ask the bot to scan your inbox (it also checks every evening on its own). It looks for order confirmations and receipts from places like Amazon, Costco, Home Depot, and Walmart. A second copy of a purchase (the paper slip and the eReceipt, or an order email and the later receipt email) is attached to the row already there. The amount is not added again.
- **By hand:** "Paid $142.50 hydro on Oct 3" or "Got $2,400 salary today" works too. Bills go under Fixed Expenses and salary goes under Income.
- **A statement:** forward the PDF, a CSV, a photo, or paste the text. The bot checks that each card's lines add up to the printed total before it writes anything. Payments on the statement are skipped. A return is a negative row linked to the original purchase.
- **The sections:** scroll below the totals. **Transactions this month** is one row per statement line. **Receipts this month** is one row per receipt, with a link to the file. A receipt and its statement line share one grid amount.
- **Reminders:** these stay off until you add a first statement. After that, three days before a card's due date, and on the due date, unless that bill is marked paid. A few days after the usual statement day, or when the issuer email says the statement is ready, the bot asks for the file. After about two weeks, or about 10 receipts, the bot may suggest statements once. A no is remembered.
- **Reports:** weekly, monthly, and yearly category totals, plus one line of spending advice, are sent in chat. You do not have to open the file. The file is still there to open in Excel, Numbers, or LibreOffice.

If this book was set up before v2.1, the owner's bot updates it on its next run. A book older than v2.0 moves receipt rows into the Receipts section. A v2.0 book only records whether statement reminders are on. You do not retype the year. The first statement imported afterwards links to the existing rows. See [migration-v2.0.md](migration-v2.0.md) and [migration-v2.1.md](migration-v2.1.md).

When one receipt covers several categories (for example groceries plus household goods at Costco), the bot splits it so each part lands in its own category and the parts add up to the total.

## Categories

Meals, Snacks & Groceries, Dining Out, Household Goods, Education & Enrichment, Fuel, Clothing, Medical, Hair & Cosmetics, Transportation, Entertainment, Gifts & Social, Other, and Temporary Income (refunds, cash back, items sold). Fixed monthly bills go in each month's Fixed Expenses list.

## Privacy

The bot only reads your email to find receipts. It never sends, replies to, or deletes mail. It does not share your files. If other family members' bots should write to the same book, you share that year's folder with them yourself, as editors. The `Family Book` root stays on your drive.

## Tips

- The bot infers your currency from your language or region (CAD, USD, EUR, or any other), names it in one line, and sets the book to it.
- In Google Sheets, set **File > Settings > Locale** to your country so weekday names display correctly.
- Light grey cells are formulas, so don't type over them.
