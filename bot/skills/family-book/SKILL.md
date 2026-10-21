---
name: family-book
description: Use when setting up a yearly Family Book household income and expense workbook (Google Sheets or Excel Online on OneDrive), or when logging a receipt photo, an order or receipt email, income, or a bill into it.
---

# Family Book: household income and expense tracker

A yearly workbook built from the blank template `family-book-template.xlsx` from https://github.com/Skybatan/family-book (Annual Summary, Jan to Dec sheets, Holidays, and a hidden Log sheet). The assistant sets it up once per year, then logs receipts from photos and from email into the right month, day, and category.

Several family members can each run their own bot against one shared book. One bot starts the book (the owner). The others join with the shared folder or workbook link. Every bot writes to that book and to its one `receipts` folder. The hidden Log tab is the shared dedupe list, so two bots never log the same receipt twice.

The owner's years live together under one root folder named `Family Book`, on Google Drive and on OneDrive. The owner remembers that folder's id, and on OneDrive its path. A member never uses the root. They keep working from the shared year-folder link.

```text
Family Book/                      root, created once
  Family Book - YYYY/             one folder per year
    Family Book - YYYY            the sheet or workbook
    receipts/
  Family Book - Templates/        the owner's blank template
```

This skill is the source of truth for where those folders go. If a routine prompt from an older install tells you to create `Family Book - YYYY` and does not name the root, the parent is still `Family Book`, and section 1c still runs first. On every run, the owner follows section 1c before creating, finding, or logging into a year folder. A member skips section 1c.

Keep user-specific values (root folder id and OneDrive path, year folder ids, file ids, currency, role, display name, merchant preferences) in the assistant's own memory, never in this skill. Which Gmail and Outlook accounts to scan is not a setup choice: each run checks which of those connectors are ready. Do not keep a dedupe log in memory. The root id is not the year folder id.

## 0. First-run setup (detect first)

There is no language question. Reply in the language the user is writing in. When a routine runs and nobody has just written, use the Grok Bot app or system language.

On the first chat, check connectors before any setup question. Use GetMcpServerStatus, or GetDynamicTools namespace status. Each of Google Drive, Google Sheets, Gmail, OneDrive, and Outlook is `ready`, `needsAuth`, `needsGrant`, or `missing`.

A store is usable when Google Drive and Google Sheets are both `ready`, or when OneDrive is `ready`. Gmail and Outlook are optional email. The book starts without them.

**Already connected: skip service setup.** If Google Drive or OneDrive is already `ready`, do not ask about services. Do not ask which store, which inbox, or whether they want email. Do not show a connect card for a service that is already `ready`. Let them use the bot.

Pick the store with no question. Say which in one line. If they later say "use OneDrive" or "use Google", switch.

- OneDrive is `ready` and Google Drive is not: use OneDrive.
- Google Drive is `ready` and OneDrive is not: use Google. If Sheets is not `ready`, connect it with no question (`missing` → SearchPlugins for "google sheets", then InstallPlugin; `needsAuth` or `needsGrant` → AuthenticateMcpServer) and continue when it is `ready`.
- Both Google Drive and OneDrive are `ready`: look once for a `Family Book` root or a `Family Book - YYYY` folder on each. Use the store that already has a book. If both do, or neither does, use Google if Sheets is `ready`, otherwise use OneDrive so they can start now. Say which in one line. Connect Sheets only when they ask to use Google, or when Google Drive is the only store connected.

Microsoft writing, when OneDrive is the store: the OneDrive connector browses and reads. Files are written with UploadFile to OneDrive. Excel Online edits happen by downloading the .xlsx, editing on the box with Python (openpyxl, or direct XML edits to preserve formatting), and re-uploading with UploadFile and overwrite true. When the book is shared, re-download immediately before every write and upload immediately afterward (section 5). This download is the workbook on OneDrive. It is not a download from Google Drive.

Scan every Gmail account and every Outlook account that is `ready`. If none is `ready`, skip email. Do not ask.

**Basic setup only when nothing is connected.** Nothing connected means Google Drive is not `ready` and OneDrive is not `ready`. Only then do you ask them to connect, and you do it before any other question. One step. In English: "To start, connect Google Drive, Google Sheets, and Gmail. If you use Microsoft instead, say so and I will connect OneDrive and Outlook." Say it in their language. Show the Google cards: for Drive, Sheets, and Gmail, InstallPlugin when `missing` (SearchPlugins for "google drive", "google sheets", and "gmail"), and AuthenticateMcpServer when `needsAuth` or `needsGrant`. If they choose Microsoft, do that for OneDrive and Outlook.

Continue as soon as one store is usable. Do not wait for email. If Gmail or Outlook is `ready` by then, scan it. If not, skip email.

**One confirmation when there is no book yet.** Look once on the store you are using.

- They own this year's book: role `owner`. Save the ids, run section 1c, and do not upload a new template over that workbook. Do not ask new or join, currency, or holidays. Read Annual Summary `C11` for the currency. Invite a receipt.
- The only book is shared with them and owned by someone else: role `member`. Save the year folder id, workbook id, and receipts folder id. Do not create a root, do not move folders, and do not ask for a link. Read `C11`. Do not refill holidays. Ask only for a display name, and let them skip.
- No book: role `owner` unless they paste a link. Infer the currency (ISO code and symbol) and the holiday country and province or state from the language they write in, the Grok Bot app or system language, and their timezone. Name the store, the currency, and the region in one line. Do not ask them as separate questions.

English shape: "I'll start a new book for this year in Google Sheets, in CAD, with public holidays for Canada / Ontario, and I'll scan Gmail. Say go, paste a shared Family Book link if you're joining, or tell me a different currency or region." Use the real store, code, and region. With no inbox `ready`, say email stays off until they connect Gmail or Outlook.

Inference to name in that line: a Canadian timezone or `en-CA` → CAD and that province (America/Toronto → Ontario). A US timezone or `en-US` → USD and that state when the timezone names one. `en-GB` → GBP, United Kingdom. French in Canada → CAD, Quebec, unless the timezone names another province. Other French, German, or Spain → EUR and that country. Japanese → JPY, Japan. Chinese → CNY, China. `en-AU` → AUD, Australia. English with no region → USD and United States.

If this turn already tells you to start (they said go, sent a receipt, or named a currency or region), apply what they named and create the book in this reply, with that one line included. If this turn is only a greeting, send the line and create the book on the next reply. A pasted folder or workbook link means join (below). If they say they are joining and send no link, ask only for the link. A new user whose Google store is already ready is done in that one or two replies.

Someone starting a book alone is not asked about sharing or a name. Ask for a short display name only when they joined, or when they said other people will log too (Mom or Alex). If they tell you a name later, save it and use it from then on. Entries include it only when one is saved, for example `Costco (Mom)`.

If they are starting a book that other people will also write to, and the store is OneDrive, say once that Google Sheets works better, because several people can edit at the same time. Do not refuse OneDrive, and do not say this to someone keeping the book alone.

**Join.** The owner shared the `Family Book - YYYY` folder as an editor. Resolve the link to the year folder id, the workbook id, and the `receipts` folder id. A workbook link uses its parent folder and the `receipts` folder inside it. A folder link uses the workbook named `Family Book - YYYY` inside it. If that store is not `ready`, connect it (Google Drive and Google Sheets, or OneDrive) and then continue. Do not create a folder, a workbook, or a `Family Book` root, and do not move anything. You may not be able to open the parent. Confirm you can read Annual Summary. If `receipts` is missing, create it inside the shared year folder. If the hidden Log sheet is missing, add it (section 3b). Save the code in `C11`. Do not change the shared book's currency, and do not refill holidays.

**Template** (owners only, and only when that year's workbook is not there yet). Follow section 1c so the root exists first. The blank template always comes from GitHub, on the box: `curl -fsSL -o family-book-template.xlsx https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx`. Verify it with openpyxl (Annual Summary, Jan to Dec, Holidays, and a hidden Log). Upload that file into `Family Book - Templates` inside the root when the copy is missing. A new year uses a fresh GitHub download. If GitHub can't be reached, say so and stop. Do not download the template, or any other file, from the owner's Google Drive. Listing folders and editing the Google Sheet through the Sheets connector is how the book is read and written.

**Save.** Year folder id, workbook id, receipts folder id, storage type, currency, holiday region, role (`owner` or `member`), and display name if they gave one. Do not save a fixed list of inboxes. For the owner, also save the root folder id, and on OneDrive the path `Family Book` from the top of their OneDrive. A member leaves the root empty. Do not save a language. Do not store the root id in the year-folder field.

**User's language vs English.** Chat, item notes and descriptions written into the book, holiday descriptions, and digests follow the language the user is writing in, or the Grok Bot app or system language when nobody has just written. These stay English on purpose: the workbook template's sheet names, category labels and notes, receipt file names (`YYYY-MM-DD Merchant Total.ext`), and this repo's skill, routine, and doc files. Translated templates per language (for example `template/family-book-template-fr.xlsx`) may be added later on request; until then, use the English template.

## 0a. Connect a service later

Email can be added after setup. Another store can too. "Connect Outlook", "add Gmail", and "add my other Gmail" all use this section. Do not redo setup, and do not ask the first-run questions again.

1. Check that service with GetMcpServerStatus or GetDynamicTools.
2. `missing`: SearchPlugins for its name, InstallPlugin, then AuthenticateMcpServer if it still needs a sign-in.
3. `needsAuth` or `needsGrant`: AuthenticateMcpServer, so the connect card shows.
4. `ready`: use it. For Gmail or Outlook, scan every ready account on that service, including a second account that was not connected at setup. Create the daily receipt scan routine if it does not exist (around 8 PM their time, from the repo routine), then scan the new inbox on this turn. Say in one line that you are scanning it too.
5. "Use OneDrive" or "use Google" switches the store when the book is not created yet. Leave an existing book where it is unless they ask to move it.

The daily scan checks again on its own (section 4), so a new ready inbox is included even when they never asked.

## 1. Create the year's book

Only the owner creates a book. A member never creates `Family Book - YYYY` and never creates the `Family Book` root. They attach to the folder the owner shared (section 0, Join, and section 1b).

For year YYYY (default: the current year), the owner follows section 1c first, then:
1. Inside the `Family Book` root, create folder `Family Book - YYYY` and inside it a subfolder `receipts`. This is the one receipts folder every family bot uses. The year folder's parent is the root, including when an older routine prompt forgets to name the parent. If that year folder is already inside the root and already holds the workbook, reuse the folder and `receipts` (create `receipts` only if it is missing). Do not upload a new template over that workbook, and do not create a second year folder. Steps 2 to 8 apply only when the workbook is not there yet.
2. Make a copy of the template with Annual Summary `F5` set to YYYY. Safest way on the box: open the .xlsx as a zip and replace `<c r="F5" s=".." t="n" />` in `xl/worksheets/sheet1.xml` with the same cell holding `<v>YYYY</v>` (this keeps all formatting). Verify with openpyxl. Leave the hidden Log sheet in place.
3. Set the currency (skip if CAD): in `xl/styles.xml` replace `[$CAD]` with `[$XXX]` (the user's ISO code) in the number formats, and in `xl/worksheets/sheet1.xml` (Annual Summary) replace the `<t>CAD</t>` label in `C11` with the code. If the currency symbol is not `$` (for example EUR, GBP, CNY), also replace `&quot;$&quot;` with the symbol in the `numFmt` format codes. Rezip with Python (`shutil.make_archive`, no `zip` command needed) and verify the workbook opens with openpyxl and Annual Summary `C11` shows the code.
4. Google: UploadFile into the year folder with name `Family Book - YYYY` and convertToGoogleFormat true. OneDrive: upload `Family Book - YYYY.xlsx` into the year folder. On a shared OneDrive book, re-download immediately before this upload only when you are editing an existing file, not when the file is brand new.
5. Read the file back and confirm the Jan sheet shows dates (Jan 1 has the right weekday). Confirm the Log sheet exists and is hidden. If a Google Sheets conversion left it visible, hide it. If it is missing, add it (section 3b).
6. Fill the Holidays tab with the public holidays for the user's region (section 1a).
7. For the owner only, offer a routine for December 20 at 9:00 AM in the user's timezone to create next year's book. Do not create that routine for a member.
8. Tell the owner, in one line, that they can share the `Family Book - YYYY` folder with family as editors. Share that year folder. Leave the `Family Book` root unshared. The root also holds every year and `Family Book - Templates`, so a share of the root would include the blank template and years that person was not invited to. A member only needs the year folder: they paste its link, and their bot does not need the parent. The join flow is unchanged. Those people install their own Family Book bot and paste the link to join. Do not share the folder yourself, and do not invite anyone they did not name. Do not add sharing questions when they are keeping the book alone. Each new year is shared the same way. A later move of the year folder keeps the link they already have.

## 1a. Fill public holidays

The month sheets look up row 3 (holiday) from `Holidays!B5:C33` and row 4 (anniversary) from `Holidays!F5:G33` by exact date, so dates must be real dates in the book's year. Only the owner's bot fills this tab for a new book.
1. Get the year's holidays for the region with the Python `holidays` package on the box (`pip install --user --break-system-packages holidays`), for example `holidays.country_holidays('CA', subdiv='ON', years=YYYY, categories=('public','optional'))`. Include observed days. Mark optional ones in the description, written in the language you are using with the user (the English form of that note is `Easter Monday (some employers)`). Cross-check a surprising date with a quick web search of the official government list.
2. Read `Holidays!B5:C33` first and keep anything the user already entered. Write date and description pairs, with the description in the language you are using with the user, into empty rows, at most 29 rows. Google Sheets: write_range with parseInput true and dates as `YYYY/MM/DD`. Excel: write real date cells with openpyxl.
3. Leave the Anniversary columns (F and G) for the user's own dates (birthdays, anniversaries). Offer to add them.
4. Check one holiday shows in row 3 of its month sheet (for example Jan 1 in `Jan!J3`).

## 1b. Next year when this bot joined

A member's bot does not run the new-year routine and does not create a workbook. It does not create a `Family Book` root and it does not move folders, including when this year's folder now sits inside the owner's root. In December, or when a receipt is dated next year and that book is not in memory, look for a folder named `Family Book - YYYY` that the owner has shared with this user. You may see it only as a shared folder. Save the new folder id, workbook id, and receipts folder id. Confirm its hidden Log tab (section 3b). If it is not there yet, wait. The owner's bot creates it on December 20 inside the same root, and the owner shares that new year folder. Do not create the book yourself. The year folder id already in memory still works after the owner moves that folder. Do not replace it.

## 1c. Root folder, and moving books from v1.0 through v1.2

The owner has one root folder. Every year folder and the template folder live inside it. Google Drive and OneDrive use the same names.

```text
Family Book/                      root, created once, at the top of My Drive or OneDrive
  Family Book - YYYY/             one folder per year
    Family Book - YYYY            Google Sheet, or Family Book - YYYY.xlsx on OneDrive
    receipts/
  Family Book - Templates/        blank template copy
```

A folder named `Family Book - YYYY` is a year folder. The root's name is exactly `Family Book`.

**Who.** Only the owner runs this section. The owner is the bot whose memory says `owner`, or a bot installed at v1.0 or v1.1 with no role saved that created the year folder in this user's own My Drive or OneDrive. A member never runs it. A member is a bot whose memory says `member`, or a bot that joined through a shared folder link. A member must not create a root, must not search the owner's drive for a parent, and must not move the owner's folders. They keep the shared year-folder link and the year folder id, workbook id, and receipts folder id already in memory. After a move those ids and the share links still work, because the move does not create new files.

**Find or create the root.** If memory has a root folder id or path and that folder is still there, use it. Otherwise look at the top of My Drive or OneDrive for a folder named exactly `Family Book`. Ignore `Family Book - YYYY` and `Family Book - Templates` in that search. If more than one exact `Family Book` folder exists, use the one that already contains a year folder. If none exists, create `Family Book` at the top of My Drive or OneDrive. Save its id to memory. On OneDrive also save the path `Family Book` from the top of their OneDrive. Do not put this id in the year-folder field.

**Move older year folders on the next run.** Bots that set up under v1.0, v1.1, or v1.2 created `Family Book - YYYY` at the top of My Drive or OneDrive, with no `Family Book` parent. On the next run, before creating a year folder and before logging, check for that. When one or more `Family Book - YYYY` folders, or `Family Book - Templates`, sit at the top of this user's own My Drive or OneDrive (the parent is the drive root), move them into the `Family Book` root.

Before any move, tell the user in one line what is happening. In English that line is: "I'm moving your Family Book year folders into a Family Book folder so every year lives together. The links stay the same." Say it in the language you are using with them. Say it once, then move. If nothing is sitting at the top level, say nothing.

Move the folder. Do not copy it, rename it, download it, or upload a new workbook. On Google Drive, set the folder's parent to the `Family Book` root and remove My Drive as its parent. The folder id stays the same. On OneDrive, move the folder so its parent is `Family Book`. The item id stays the same. The path may become `Family Book/Family Book - YYYY`. Share links already sent keep working. Leave the year folder id, workbook id, and receipts folder id in memory as they are, and save the root id or path beside them.

Do this for every top-level year folder, not only the current year, and for a top-level `Family Book - Templates` folder in the same pass. If that same name is already inside the root, leave the top-level folder where it is and tell the user there are two.

If a routine prompt from an older install tells you to create `Family Book - YYYY` without naming a parent, run this section first and create the year folder inside the root.

Skip the move when the year folders are already inside `Family Book`. Do not move a folder under Shared with me, or any folder this user does not own.

## 2. Sheet layout (every month sheet)

- **Income This Month:** rows 8 to 11. Column B is Item, C is Amount, D is Date Received.
- **Fixed Expenses This Month:** rows 18 to 38. Column B is the pre-set item, C is Amount, D is Date Paid. The items are Income (enter as negative), GAS, Electricity & Water, RESP, Mobile Phone, Daycare, Rent / Mortgage, Internet, Car Insurance, Property Tax, Fuel / Maintenance, Home Insurance, Car Loan Payment, Housing Management Fee, Term Deposit, Pocket Money, and Savings. Match by reading column B, not by fixed row.
- **Daily Record:** the day number is in row 2. Day d has its Item column at column index 10 + 2*(d-1), with A as 1, and the Amount column is the next one. Day 1 is J and K, day 2 is L and M, day 29 is BN and BO, day 30 is BP and BQ, and day 31 is BR and BS. Read and write the daily block through column BS. The month totals already do (`Jan!G8` is `=SUM(J21:BS21)`, and `J43:BS43` is temporary income). Always confirm the date in row 2 before writing. A blank row 2 means that day is not in this month.
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

Sources: a photo or PDF the user sends in chat, a receipt in the `receipts` folder, or an order or receipt email. Every bot logs into the same shared book. At the start of the run, the owner follows section 1c once. A member does not.

1. Read the receipt: merchant, date of purchase, line items, subtotal, tax, total, currency, and order number if present.
2. Pick the month sheet and day from the purchase date. The day's columns are in section 2: day 31 is BR and BS, and any read of the daily block goes through BS. If the date is outside this book's year, use that year's book. An owner may create it (section 1). A member attaches to the one the owner shared (section 1b) and does not create a book.
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

The owner follows section 1c once before searching. A member skips it.

At the start of every scan, check Gmail and Outlook again (GetMcpServerStatus or GetDynamicTools). Scan every account that is `ready`, including an account connected after setup (section 0a). If a new one is `ready`, include it and say so in one line. If none is `ready`, stop and do not ask them to connect email.

1. Search since the last scan. The first scan of an inbox is the last 30 days. Say that older receipts from this year can be backfilled on request. A good starting Gmail query: `(subject:(receipt OR order OR invoice OR "your order" OR purchase) OR from:(amazon OR homedepot OR costco OR walmart OR bestbuy OR apple OR uber OR doordash)) -subject:(shipped OR delivered OR "out for delivery")`, and adapt it to the user's merchants. For Outlook use the matching search.
2. Use the order confirmation or final invoice as the source of truth. Skip shipping notices, marketing, and duplicates. Use the order date.
3. Log each new receipt as in section 3, and always save the receipt file in the shared `receipts` folder as in section 3a. Never add a Log row until its file is saved.
4. Never reply to, forward, or send email while doing this; it is read-only.
5. Report a short digest in the language the user writes in, or the Grok Bot app or system language when nobody has just written: how many were found, what was logged, who logged it when a name is saved, and anything unclear.

## 5. Writing tools

- Google Sheets connector: write values to `'<Mon>'!<cell>` ranges. Read the target range first so you never overwrite. A daily read includes every day column through BS. Google Sheets is the right store when several bots write, because editors can update the same spreadsheet together. Hide the Log sheet and leave it hidden.
- Do not download or export files from the owner's Google Drive, including the template and the Google Sheet. The template comes from GitHub (section 0). If Sheets is not `ready`, connect it (section 0 or 0a) and write with the Sheets connector.
- OneDrive or Excel Online: two bots editing the same .xlsx can overwrite each other. Re-download the workbook right before every write, edit that fresh copy, and upload it immediately with overwrite true. Do not write from a copy downloaded earlier in the turn. Check that the file is not open for editing elsewhere. Prefer Google when more than one person logs receipts.
