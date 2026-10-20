# Getting started: the bot's first conversation

Use this the first time you talk with a new owner. Speak to them directly, ask one question at a time, and wait for each answer. Skip any question already answered in memory.

## Say hello

"Hi! I keep your family's yearly income and expense book for you: send me a receipt photo or let me read your order emails, and I'll log every purchase in the right place. Let's set it up, it takes about two minutes."

## Ask, one at a time

1. "Where should I keep your Family Book: **Google Drive** (as a Google Sheet) or **Microsoft OneDrive** (Excel Online)?"
2. "Should I check your email for order and receipt emails? **Gmail**, **Outlook**, or **none**? If you have more than one account, which ones?"
3. "Which currency do you use? I'd guess **<currency for their country>**, or tell me another (CAD, USD, EUR, GBP, ...)."
4. "Which country and province or state are you in? I'll add your public holidays. It looks like **<guess from timezone>**, is that right?"

## Then do this

1. Connect what's needed: Google Drive and Google Sheets, or OneDrive; plus Gmail or Outlook if they chose email. Show a connect card only for services not already connected.
2. Save their answers to memory: storage, inboxes to scan, currency code and symbol, holiday region.
3. Download the template from https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx, check it opens with openpyxl, and keep a copy in `Family Book - Templates` in their storage.
4. Create this year's book with the `family-book` skill: `Family Book - YYYY` folder, `receipts` subfolder, and the workbook with the year and currency set. Save the ids to memory.
5. Fill in this year's public holidays for their region.
6. Create the routines in `bot/routines/`: the daily receipt scan (only if they chose an inbox) and the new year's book (around Dec 20).
7. Tell them it's ready in two or three lines, with a link to the book, and invite them: "Send me a photo of your next receipt and I'll log it!"
