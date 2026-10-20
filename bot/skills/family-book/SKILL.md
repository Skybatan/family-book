---
name: family-book
description: Use when setting up a yearly Family Book household income and expense workbook (Google Sheets or Excel Online on OneDrive), or when logging a receipt photo, an order or receipt email, income, or a bill into it.
---

# Family Book: household income and expense tracker

A yearly workbook built from the blank template `family-book-template.xlsx` from https://github.com/Skybatan/family-book (Annual Summary, Jan to Dec sheets, Holidays). The assistant sets it up once per year, then logs receipts from photos and from email into the right month, day, and category.

Keep user-specific values (folder ids, file ids, which inbox, currency, merchant preferences) in the assistant's own memory, never in this skill.

## 0. First-run setup (ask one thing at a time)

1. **Storage.** Ask whether they use Google Drive (Google Sheets) or Microsoft OneDrive (Excel Online). Check connector status first and never re-prompt for one already connected.
   - Google: needs the Google Drive and Google Sheets connectors. Install with InstallPlugin (search "google drive" and "google sheets" with SearchPlugins) so the connect cards appear.
   - Microsoft: needs the OneDrive connector (and the Outlook connector if their mail is there). The OneDrive connector browses and reads; files are written with UploadFile to OneDrive. Excel Online edits happen by downloading the .xlsx, editing on the box with Python (openpyxl, or direct XML edits to preserve formatting), and re-uploading with UploadFile and overwrite true.
2. **Template.** Use the blank template .xlsx if it is already in their storage (in `Family Book - Templates`). Otherwise download it on the box with `curl -fsSL -o family-book-template.xlsx https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx` and verify it opens with openpyxl (it should have the sheets Annual Summary, Jan to Dec, and Holidays). Keep a copy in a `Family Book - Templates` folder in their storage. When creating a new year's book, prefer a fresh download so the latest template version is used.
3. **Email (optional).** Ask which inbox gets order and receipt emails: Gmail (Gmail connector), Outlook (Outlook connector), or none. If several accounts are connected, ask which ones to scan.
4. **Currency.** Ask which currency they use, suggesting the one for their country (for example CAD, USD, EUR, GBP, AUD, CNY). Save its 3-letter ISO code and symbol. The book is set to it when it is created (section 1, step 3).
5. **Holiday region.** Ask for their country and, where holidays differ by region, their province or state (for example Canada / Ontario, United States / California, United Kingdom / Scotland). Guess from their timezone and confirm.
6. Save the folder id, workbook id, receipts folder id, storage type, inbox(es), currency, and holiday region to memory.

## 1. Create the year's book

For year YYYY (default: the current year):
1. Create folder `Family Book - YYYY` and inside it a subfolder `receipts`.
2. Make a copy of the template with Annual Summary `F5` set to YYYY. Safest way on the box: open the .xlsx as a zip and replace `<c r="F5" s=".." t="n" />` in `xl/worksheets/sheet1.xml` with the same cell holding `<v>YYYY</v>` (this keeps all formatting). Verify with openpyxl.
3. Set the currency (skip if CAD): in `xl/styles.xml` replace `[$CAD]` with `[$XXX]` (the user's ISO code) in the number formats, and in `xl/worksheets/sheet1.xml` (Annual Summary) replace the `<t>CAD</t>` label in `C11` with the code. If the currency symbol is not `$` (for example EUR, GBP, CNY), also replace `&quot;$&quot;` with the symbol in the `numFmt` format codes. Rezip with Python (`shutil.make_archive`, no `zip` command needed) and verify the workbook opens with openpyxl and Annual Summary `C11` shows the code.
4. Google: UploadFile into the year folder with name `Family Book - YYYY` and convertToGoogleFormat true. OneDrive: upload `Family Book - YYYY.xlsx` into the year folder.
5. Read the file back and confirm the Jan sheet shows dates (Jan 1 has the right weekday).
6. Fill the Holidays tab with the public holidays for the user's region (section 1a).
7. Offer a routine around Dec 20 to create next year's book.

## 1a. Fill public holidays

The month sheets look up row 3 (holiday) from `Holidays!B5:C33` and row 4 (anniversary) from `Holidays!F5:G33` by exact date, so dates must be real dates in the book's year.
1. Get the year's holidays for the region with the Python `holidays` package on the box (`pip install --user --break-system-packages holidays`), for example `holidays.country_holidays('CA', subdiv='ON', years=YYYY, categories=('public','optional'))`. Include observed days. Mark optional ones in the description (for example `Easter Monday (some employers)`). Cross-check a surprising date with a quick web search of the official government list.
2. Read `Holidays!B5:C33` first and keep anything the user already entered. Write date and English description pairs into empty rows, at most 29 rows. Google Sheets: write_range with parseInput true and dates as `YYYY/MM/DD`. Excel: write real date cells with openpyxl.
3. Leave the Anniversary columns (F and G) for the user's own dates (birthdays, anniversaries). Offer to add them.
4. Check one holiday shows in row 3 of its month sheet (for example Jan 1 in `Jan!J3`).

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

Sources: a photo or PDF the user sends in chat, a receipt in the `receipts` folder, or an order or receipt email.

1. Read the receipt: merchant, date of purchase, line items, subtotal, tax, total, currency, and order number if present.
2. Pick the month sheet and day from the purchase date. If the date is outside the book's year, use (or offer to create) that year's book.
3. Categorise. One entry per category; if a receipt spans categories (for example Costco food plus household goods), split the total across categories by line items and spread tax and discounts proportionally so the parts add up to the receipt total.
4. Write: in the first empty row of that category block for that day, put the Item as the merchant (consistent naming, for example `Costco`, `Amazon`, `Home Depot`) with a short note if useful, and the Amount as a number. If every row in the block is used, add to an existing amount as a formula (`=12.50+8.20`).
5. Refunds and returns: a negative amount in the original category, or row 43 if it is new money.
6. Recurring bills (hydro, phone, internet, insurance, mortgage) go in Fixed Expenses for that month, not the Daily Record. Salary and other income go in Income This Month.
7. **Always save a copy of the receipt in `receipts`**, named `YYYY-MM-DD Merchant Total.ext` (for example `2026-10-15 Costco.ca 57.29.png`). Every logged entry must have a file there, so the record survives even if the email or photo is deleted. See section 3a for email receipts.
8. Keep a dedupe log: a small hidden or extra tab (or a note in memory) with source (email message id or file name), date, merchant, total, where it was written, and the saved receipt file name. Skip anything already logged.
9. Tell the user what was logged in one or two lines (merchant, date, total, category split). If the amount or category was a guess, say so and ask.

## 3a. Save an email receipt as a file (required for every email receipt)

1. Use the original merchant email, not a forward, when both exist. If the email has a PDF receipt or invoice attachment, download that (DownloadFile) and save it as is.
2. Otherwise render the email's HTML body on the box:
   - Write the `htmlBody` from the mail connector's get_message to `receipt.html`.
   - Long one-page image (best for app-style receipts like Costco.ca or Amazon): `google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=800,4000 --virtual-time-budget=8000 --screenshot=out.png file:///path/receipt.html`, then crop the empty bottom with Pillow (find the content bounding box against the background colour). Raise the window height if the content reaches the bottom.
   - PDF (best for text-style till receipts like Home Depot): `google-chrome --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf=out.pdf file:///path/receipt.html`.
3. Look at the result (open the image, or `pdftotext` the PDF) and confirm the merchant, date, and total are visible before uploading.
4. Upload to the year's `receipts` folder (Google: UploadFile with the folder id; OneDrive: UploadFile with overwrite false) and record the file name in the dedupe log.
5. If rendering fails, save a plain-text summary of the receipt (merchant, date, order number, line items, tax, total) as `YYYY-MM-DD Merchant Total.txt` instead, and mention it in the report.

## 4. Scan email for receipts

1. Search since the last scan (first run: start of the year or the last 30 days, ask). A good starting Gmail query: `(subject:(receipt OR order OR invoice OR "your order" OR purchase) OR from:(amazon OR homedepot OR costco OR walmart OR bestbuy OR apple OR uber OR doordash)) -subject:(shipped OR delivered OR "out for delivery")`, and adapt it to the user's merchants. For Outlook use the matching search.
2. Use the order confirmation or final invoice as the source of truth. Skip shipping notices, marketing, and duplicates. Use the order date.
3. Log each new receipt as in section 3, and always save the receipt file in `receipts` as in section 3a. Never mark an email as done in the dedupe log until its file is saved.
4. Never reply to, forward, or send email while doing this; it is read-only.
5. Report a short digest: how many were found, what was logged, and anything unclear.

## 5. Writing tools

- Google Sheets connector: write values to `'<Mon>'!<cell>` ranges. Read the target range first so you never overwrite.
- If the Sheets connector is unavailable: export the sheet as .xlsx, edit on the box, and re-import. Warn first, because re-importing replaces the file and its edit history.
- OneDrive or Excel Online: download, edit the .xlsx with openpyxl (keep formulas), and re-upload with overwrite true. Check that the file is not open for editing elsewhere.
