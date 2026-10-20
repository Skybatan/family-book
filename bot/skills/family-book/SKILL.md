---
name: family-book
description: Use when setting up a yearly Family Book household income and expense workbook (Google Sheets or Excel Online on OneDrive), or when logging a receipt photo, an order or receipt email, income, or a bill into it.
---

# Family Book: household income and expense tracker

A yearly workbook built from the blank template `family-book-template.xlsx` from https://github.com/Skybatan/family-book (Annual Summary, Jan to Dec sheets, Holidays, and a hidden Log sheet). The assistant sets it up once per year, then logs receipts from photos and from email into the right month, day, and category.

Several family members can each run their own bot against one shared book. One bot starts the book (the owner). The others join with the shared folder or workbook link. Every bot writes to that book and to its one `receipts` folder. The hidden Log tab is the shared dedupe list, so two bots never log the same receipt twice.

Keep user-specific values (folder ids, file ids, which inbox, currency, role, display name, merchant preferences) in the assistant's own memory, never in this skill. Do not keep a dedupe log in memory.

## 0. First-run setup (ask one thing at a time)

There is no language question. Reply in the language the user is writing in. When a routine runs and nobody has just written, use the Grok Bot app or system language.

1. **New or join.** Ask whether they are starting a new family book or joining an existing one. If it is just them, they say new. Save the role: `owner` if they start the book, `member` if they join. Someone starting a book alone is not asked about sharing or about a name.
2. **Storage.** Ask whether they use Google Drive (Google Sheets) or Microsoft OneDrive (Excel Online). Skip this when they are joining and the link already shows which one. Check connector status first and never re-prompt for one already connected.
   - Google: needs the Google Drive and Google Sheets connectors. Install with InstallPlugin (search "google drive" and "google sheets" with SearchPlugins) so the connect cards appear.
   - Microsoft: needs the OneDrive connector (and the Outlook connector if their mail is there). The OneDrive connector browses and reads; files are written with UploadFile to OneDrive. Excel Online edits happen by downloading the .xlsx, editing on the box with Python (openpyxl, or direct XML edits to preserve formatting), and re-uploading with UploadFile and overwrite true. When the book is shared, re-download immediately before every write and upload immediately afterward (section 5).
   - If they are starting a book that other people will also write to and they picked OneDrive, say once that Google Drive works better, because several people can edit a Google Sheet at the same time. Do not refuse OneDrive, and do not say this to someone keeping the book alone.
3. **Join link** (members only). Ask them to paste the link to the shared Family Book folder or workbook. The owner has shared the `Family Book - YYYY` folder with them as an editor. Resolve the link to the year folder id, the workbook id, and the `receipts` folder id. If they pasted the workbook, use its parent folder and the `receipts` folder inside it. If they pasted the folder, open the workbook named `Family Book - YYYY` inside it. Do not create a folder or a workbook. Confirm you can read Annual Summary. If `receipts` is missing, create that subfolder. If the hidden Log sheet is missing, add it (section 3b).
4. **Template** (owners only). Use the blank template .xlsx if it is already in their storage (in `Family Book - Templates`). Otherwise download it on the box with `curl -fsSL -o family-book-template.xlsx https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx` and verify it opens with openpyxl (it should have the sheets Annual Summary, Jan to Dec, Holidays, and a hidden Log). Keep a copy in a `Family Book - Templates` folder in their storage. When creating a new year's book, prefer a fresh download so the latest template version is used.
5. **Email (optional).** Ask which inbox gets order and receipt emails: Gmail (Gmail connector), Outlook (Outlook connector), or none. If several accounts are connected, ask which ones to scan. Each person's bot scans only the inboxes they chose.
6. **Currency** (owners only). Ask which currency they use, suggesting the one for their country (for example CAD, USD, EUR, GBP, AUD, CNY). Save its 3-letter ISO code and symbol. The book is set to it when it is created (section 1, step 3). A member reads the code already in Annual Summary `C11` and saves that. Do not change the shared book's currency.
7. **Holiday region** (owners only). Ask for their country and, where holidays differ by region, their province or state (for example Canada / Ontario, United States / California, United Kingdom / Scotland). Guess from their timezone and confirm. A member does not refill holidays.
8. **Display name.** Ask only when they joined, or when they said other people will log receipts too: what short name should appear on entries they log (for example Mom or Alex)? Save it. Someone starting a book alone is not asked. If they tell you a name later, save it and use it from then on. Entries include the name only when one is saved, for example `Costco (Mom)`.
9. Save the folder id, workbook id, receipts folder id, storage type, inbox(es), currency, holiday region, role (`owner` or `member`), and display name if they gave one. Do not save a language.

**User's language vs English.** Chat, item notes and descriptions written into the book, holiday descriptions, and digests follow the language the user is writing in, or the Grok Bot app or system language when nobody has just written. These stay English on purpose: the workbook template's sheet names, category labels and notes, receipt file names (`YYYY-MM-DD Merchant Total.ext`), and this repo's skill, routine, and doc files. Translated templates per language (for example `template/family-book-template-fr.xlsx`) may be added later on request; until then, use the English template.

## 1. Create the year's book

Only the owner creates a book. A member never creates `Family Book - YYYY`. They attach to the folder the owner shared (section 0, step 3, and section 1b).

For year YYYY (default: the current year):
1. Create folder `Family Book - YYYY` and inside it a subfolder `receipts`. This is the one receipts folder every family bot uses.
2. Make a copy of the template with Annual Summary `F5` set to YYYY. Safest way on the box: open the .xlsx as a zip and replace `<c r="F5" s=".." t="n" />` in `xl/worksheets/sheet1.xml` with the same cell holding `<v>YYYY</v>` (this keeps all formatting). Verify with openpyxl. Leave the hidden Log sheet in place.
3. Set the currency (skip if CAD): in `xl/styles.xml` replace `[$CAD]` with `[$XXX]` (the user's ISO code) in the number formats, and in `xl/worksheets/sheet1.xml` (Annual Summary) replace the `<t>CAD</t>` label in `C11` with the code. If the currency symbol is not `$` (for example EUR, GBP, CNY), also replace `&quot;$&quot;` with the symbol in the `numFmt` format codes. Rezip with Python (`shutil.make_archive`, no `zip` command needed) and verify the workbook opens with openpyxl and Annual Summary `C11` shows the code.
4. Google: UploadFile into the year folder with name `Family Book - YYYY` and convertToGoogleFormat true. OneDrive: upload `Family Book - YYYY.xlsx` into the year folder. On a shared OneDrive book, re-download immediately before this upload only when you are editing an existing file, not when the file is brand new.
5. Read the file back and confirm the Jan sheet shows dates (Jan 1 has the right weekday). Confirm the Log sheet exists and is hidden. If a Google Sheets conversion left it visible, hide it. If it is missing, add it (section 3b).
6. Fill the Holidays tab with the public holidays for the user's region (section 1a).
7. For the owner only, offer a routine for December 20 at 9:00 AM in the user's timezone to create next year's book. Do not create that routine for a member.
8. Tell the owner, in one line, that they can share the `Family Book - YYYY` folder with family as editors. Those people install their own Family Book bot and paste the link to join. Do not share the folder yourself, and do not invite anyone they did not name. Do not add sharing questions when they are keeping the book alone.

## 1a. Fill public holidays

The month sheets look up row 3 (holiday) from `Holidays!B5:C33` and row 4 (anniversary) from `Holidays!F5:G33` by exact date, so dates must be real dates in the book's year. Only the owner's bot fills this tab for a new book.
1. Get the year's holidays for the region with the Python `holidays` package on the box (`pip install --user --break-system-packages holidays`), for example `holidays.country_holidays('CA', subdiv='ON', years=YYYY, categories=('public','optional'))`. Include observed days. Mark optional ones in the description, written in the language you are using with the user (the English form of that note is `Easter Monday (some employers)`). Cross-check a surprising date with a quick web search of the official government list.
2. Read `Holidays!B5:C33` first and keep anything the user already entered. Write date and description pairs, with the description in the language you are using with the user, into empty rows, at most 29 rows. Google Sheets: write_range with parseInput true and dates as `YYYY/MM/DD`. Excel: write real date cells with openpyxl.
3. Leave the Anniversary columns (F and G) for the user's own dates (birthdays, anniversaries). Offer to add them.
4. Check one holiday shows in row 3 of its month sheet (for example Jan 1 in `Jan!J3`).

## 1b. Next year when this bot joined

A member's bot does not run the new-year routine and does not create a workbook. In December, or when a receipt is dated next year and that book is not in memory, look for `Family Book - YYYY` shared with this user (the folder the owner newly shared, next to this year's book). Save the new folder id, workbook id, and receipts folder id. Confirm its hidden Log tab (section 3b). If it is not there yet, wait. The owner's bot creates it on December 20 and the owner shares the new folder. Do not create the book yourself.

## 2. Sheet layout (every month sheet)

- **Income This Month:** rows 8 to 11. Column B is Item, C is Amount, D is Date Received.
- **Fixed Expenses This Month:** rows 18 to 38. Column B is the pre-set item, C is Amount, D is Date Paid. The items are Income (enter as negative), GAS, Electricity & Water, RESP, Mobile Phone, Daycare, Rent / Mortgage, Internet, Car Insurance, Property Tax, Fuel / Maintenance, Home Insurance, Car Loan Payment, Housing Management Fee, Term Deposit, Pocket Money, and Savings. Match by reading column B, not by fixed row.
- **Daily Record:** the day number is in row 2. Day d has its Item column at column index 10 + 2*(d-1) (day 1 is J and K, day 2 is L and M, ... day 31 is BN and BO) and its Amount column right after. Always confirm the date in row 2 before writing.
- **Category rows in the Daily Record:**

| Category | Rows to use |
|---|---|
| Meals (groceries for home cooking: meat, produce, dairy, staples) | 6-16 |
| Snacks & Groceries (snacks, general grocery runs) | 17-19 |
| Dining Out (restaurants, takeout, food delivery) | 20 |
| Household Goods (cleaning, paper, tools, hardware, furniture, small appliances) | 22-27 |
| Education & Enrichment (lessons, classes, books) | 28 |
| Fuel | 29 |
| Clothing | 30-31 |
| Medical (pharmacy, prescriptions, dental) | 32 |
| Hair & Cosmetics | 33 |
| Transportation (transit, parking, tolls, rideshare) | 34 |
| Entertainment (subscriptions, movies, outings, games) | 35 |
| Gifts & Social | 36 |
| Other | 37-40 |
| Temporary Income (refund, cash back, sold item) | 43 |

- Never write in rows 21, 41, 42, or 44, any formula cell, or the light grey cells.

## 3. Log a receipt

Sources: a photo or PDF the user sends in chat, a receipt in the `receipts` folder, or an order or receipt email. Every bot logs into the same shared book.

1. Read the receipt: merchant, date of purchase, line items, subtotal, tax, total, currency, and order number if present.
2. Pick the month sheet and day from the purchase date. If the date is outside this book's year, use that year's book. An owner may create it (section 1). A member attaches to the one the owner shared (section 1b) and does not create a book.
3. Categorise. One entry per category; if a receipt spans categories (for example Costco food plus household goods), split the total across categories by line items and spread tax and discounts proportionally so the parts add up to the receipt total.
4. Check the hidden Log tab before writing anything (section 3b). On OneDrive, re-download the workbook immediately before this check. Skip the receipt if it is already logged.
5. Write: in the first empty row of that category block for that day, put the Item as the merchant (consistent naming, for example `Costco`, `Amazon`, `Home Depot`). If a display name is saved, add it in parentheses, for example `Costco (Mom)`. A short note in the language you are using with the user can follow, for example `Costco (Mom) milk and paper towels`. Put the Amount as a number. If every row in the block is used, add to an existing amount as a formula (`=12.50+8.20`). The receipt file name stays `YYYY-MM-DD Merchant Total.ext` and does not include the person's name.
6. Refunds and returns: a negative amount in the original category, or row 43 if it is new money.
7. Recurring bills (hydro, phone, internet, insurance, mortgage) go in Fixed Expenses for that month, not the Daily Record. Salary and other income go in Income This Month.
8. **Always save a copy of the receipt in the shared `receipts` folder**, named `YYYY-MM-DD Merchant Total.ext` (for example `2026-10-15 Costco.ca 57.29.png`). A receipt does not count as logged until its file is saved there. Every logged entry must have a file there, so the record survives even if the email or photo is deleted. See section 3a for email receipts.
9. Only after that file is saved, append one row to the hidden Log tab (section 3b). If the file could not be saved, do not append the row. On the next attempt, save the file and append the row, and do not write the amount a second time.
10. Tell the user, in the language they are writing in, what was logged in one or two lines (merchant, date, total, category split, and who logged it when a name is saved). If the amount or category was a guess, say so and ask.

## 3a. Save an email receipt as a file (required for every email receipt)

1. Use the original merchant email, not a forward, when both exist. If the email has a PDF receipt or invoice attachment, download that (DownloadFile) and save it as is.
2. Otherwise render the email's HTML body on the box:
   - Write the `htmlBody` from the mail connector's get_message to `receipt.html`.
   - Long one-page image (best for app-style receipts like Costco.ca or Amazon): `google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=800,4000 --virtual-time-budget=8000 --screenshot=out.png file:///path/receipt.html`, then crop the empty bottom with Pillow (find the content bounding box against the background colour). Raise the window height if the content reaches the bottom.
   - PDF (best for text-style till receipts like Home Depot): `google-chrome --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf=out.pdf file:///path/receipt.html`.
3. Look at the result (open the image, or `pdftotext` the PDF) and confirm the merchant, date, and total are visible before uploading.
4. Upload to the year's shared `receipts` folder (Google: UploadFile with the folder id; OneDrive: UploadFile with overwrite false). The file name is what section 3b stores in Saved file.
5. If rendering fails, save a plain-text summary of the receipt (merchant, date, order number, line items, tax, total) as `YYYY-MM-DD Merchant Total.txt` instead, and mention it in the report.

## 3b. Shared Log tab (dedupe)

Dedupe is the hidden `Log` sheet in the workbook, shared by every bot. Do not keep a second dedupe list in memory.

If the open book has no `Log` sheet (a book created from an older template), add one before logging. Row 1 is the header. Hide the sheet. Google Sheets: add the sheet with the Sheets connector, write the header, then hide the tab. Excel: add the sheet with openpyxl, set its state to hidden, and re-upload. On OneDrive, re-download immediately before this write.

Header row, columns A to G. Leave column H alone. It is a note.

| Column | Header | Write |
|---|---|---|
| A | Source | Email message id, order number, or the original file name. Use whichever you have, joined in one cell if you have more than one. |
| B | Date | Purchase date as text `YYYY-MM-DD`. |
| C | Merchant | Consistent merchant name, with no person's name. |
| D | Total | Receipt total as a number. |
| E | Where written | Where the amount went, for example `Oct!J6` or `Oct Fixed Expenses / GAS`. |
| F | Saved file | `YYYY-MM-DD Merchant Total.ext`. Blank until the file is in `receipts`. |
| G | Logged by | The display name from memory, or blank if they have none. |

Before logging, read every data row (row 2 on):

- Skip if Source shares a message id, order number, or file name with an existing Source.
- Also skip if Date, Merchant, and Total all match an existing row. This catches the same receipt forwarded to two people, which arrives with two different message ids.
- If the user says two purchases really were the same merchant, date, and total, log the second one and put a distinct Source (the file name plus the time).

A row with no Saved file is not finished. Save the missing file in `receipts`, then fill Saved file. Do not write the amount a second time.

Append the row only after the receipt file upload succeeds. Read the Log tab once more immediately before appending, so a row another bot just wrote is not duplicated. On OneDrive that read is a fresh download, and the upload follows immediately.

## 4. Scan email for receipts

1. Search since the last scan (first run: start of the year or the last 30 days, ask). A good starting Gmail query: `(subject:(receipt OR order OR invoice OR "your order" OR purchase) OR from:(amazon OR homedepot OR costco OR walmart OR bestbuy OR apple OR uber OR doordash)) -subject:(shipped OR delivered OR "out for delivery")`, and adapt it to the user's merchants. For Outlook use the matching search.
2. Use the order confirmation or final invoice as the source of truth. Skip shipping notices, marketing, and duplicates. Use the order date.
3. Log each new receipt as in section 3, and always save the receipt file in the shared `receipts` folder as in section 3a. Never add a Log row until its file is saved.
4. Never reply to, forward, or send email while doing this; it is read-only.
5. Report a short digest in the language the user writes in, or the Grok Bot app or system language when nobody has just written: how many were found, what was logged, who logged it when a name is saved, and anything unclear.

## 5. Writing tools

- Google Sheets connector: write values to `'<Mon>'!<cell>` ranges. Read the target range first so you never overwrite. Google Sheets is the right store when several bots write, because editors can update the same spreadsheet together. Hide the Log sheet and leave it hidden.
- If the Sheets connector is unavailable: export the sheet as .xlsx, edit on the box, and re-import. Warn first, because re-importing replaces the file and its edit history.
- OneDrive or Excel Online: two bots editing the same .xlsx can overwrite each other. Re-download the workbook right before every write, edit that fresh copy, and upload it immediately with overwrite true. Do not write from a copy downloaded earlier in the turn. Check that the file is not open for editing elsewhere. Prefer Google when more than one person logs receipts.
