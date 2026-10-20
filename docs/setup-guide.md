# Family Book with Grok Bot: Setup Guide

Your Grok Bot, with the Family Book template, keeps a yearly household income and expense workbook for your family. You send it a photo of a receipt, or let it read your order emails, and it puts each purchase on the right day and in the right category. The Annual Summary updates on its own.

## Any language

Family Book Bot speaks whatever language you do, because it runs on Grok, so it works in English, French, Chinese, Japanese, Spanish, and many others. It chats, reads receipts, writes item notes, and sends digests in your language. The workbook's sheet and category labels are in English for now (translated templates may come later).

## What you need

- A Grok Bot with the Family Book bot template imported. The bot downloads the blank workbook template from this repo by itself ([template guide](template-guide.md) explains every sheet).
- One place to keep the book:
  - **Google Drive + Google Sheets**, or
  - **Microsoft OneDrive + Excel Online**.
- Optional: an inbox where your order and receipt emails arrive (**Gmail** or **Outlook**).

## Step 1: Connect your accounts

When you first talk to the bot, it asks a few questions one at a time:

1. **Language:** whichever language you write in (English, French, Chinese, Japanese, Spanish, or another). It guesses, then chats in that language.
2. **Storage:** where to keep the book, Google Drive or OneDrive.
3. **Email:** which inbox (if any) gets your receipts, Gmail, Outlook, or none, and which accounts.
4. **Currency:** CAD, USD, EUR, or another.
5. **Holiday region:** your country and province or state.

Tell it which storage and email you use. It will show a connect card for each service that isn't connected yet. Sign in on the card and you're done; you never need to paste a password.

| You use | Connect |
|---|---|
| Google | Google Drive and Google Sheets |
| Microsoft | OneDrive (and Outlook for mail) |
| Gmail for receipts | Gmail |
| Outlook or Hotmail for receipts | Outlook |

You can connect more than one email account, and the bot will ask which ones to scan.

## Step 2: Create this year's book

Once your accounts are connected the bot sets up the book on its own (or say "set up my Family Book"). You don't need to send it any file: it downloads the latest template from this repo automatically. It will:

1. Download the blank template from this repo and save a copy in a `Family Book - Templates` folder in your storage.
2. Create a folder named `Family Book - YYYY` with a `receipts` subfolder inside it.
3. Create a workbook named `Family Book - YYYY` in that folder (a Google Sheet, or an .xlsx on OneDrive) with the year, your currency, and your public holidays already filled in.

Each December 20 at 9:00 AM your time it sets up next year's book for you, from the latest template.

## Step 3: Log receipts

- **Photo:** snap the receipt and send it in chat. The bot reads the merchant, date, and total, picks the category, writes it to that day, and files the photo in `receipts`.
- **Email:** ask the bot to scan your inbox (it also checks every evening on its own). It looks for order confirmations and receipts from places like Amazon, Costco, Home Depot, and Walmart, skips shipping notices, and never logs the same order twice.
- **By hand:** "Paid $142.50 hydro on Oct 3" or "Got $2,400 salary today" works too. Bills go under Fixed Expenses and salary goes under Income.

When one receipt covers several categories (for example groceries plus household goods at Costco), the bot splits it so each part lands in its own category and the parts add up to the total.

## Categories

Meals, Snacks & Groceries, Dining Out, Household Goods, Education & Enrichment, Fuel, Clothing, Medical, Hair & Cosmetics, Transportation, Entertainment, Gifts & Social, Other, and Temporary Income (refunds, cash back, items sold). Fixed monthly bills go in each month's Fixed Expenses list.

## Privacy

The bot only reads your email to find receipts. It never sends, replies to, or deletes mail, and it never shares your files with anyone.

## Tips

- The bot asks your currency at setup (CAD, USD, EUR, or any other) and sets the book to it.
- In Google Sheets, set **File > Settings > Locale** to your country so weekday names display correctly.
- Light grey cells are formulas, so don't type over them.
