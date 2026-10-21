---
name: family-book
description: Use when setting up a yearly Family Book household income and expense workbook (Google Sheets or Excel Online on OneDrive), or when logging a receipt photo, an order or receipt email, income, or a bill into it. Never log the same purchase twice.
---

# Family Book: household income and expense tracker

A yearly workbook built from the blank template `family-book-template.xlsx` from https://github.com/Skybatan/family-book (Annual Summary, Jan to Dec sheets, Holidays, and a hidden Log sheet). The assistant sets it up once per year, then logs receipts from photos and from email into the right month, day, and category.

Each month sheet has a receipt list at the bottom, below the totals, one row per purchase. The hidden Log tab is the authoritative dedupe list for the year. The month list is the same purchases, where people can check them. Several family members can each run their own bot against one shared book. One bot starts the book (the owner). The others join with the shared folder or workbook link. Every bot writes to that book and to its one `receipts` folder. Bots share that workbook, so the dedupe check works across bots. Do not keep a dedupe log in memory.

The owner's years live together under one root folder named `Family Book`, on Google Drive and on OneDrive. The owner remembers that folder's id, and on OneDrive its path. A member never uses the root. They keep working from the shared year-folder link.

```text
Family Book/                      root, created once
  Family Book - YYYY/             one folder per year
    Family Book - YYYY            the sheet or workbook
    receipts/
  Family Book - Templates/        the owner's blank template
```

This skill is the source of truth for where those folders go. If a routine prompt from an older install tells you to create `Family Book - YYYY` and does not name the root, the parent is still `Family Book`, and section 1c still runs first. On every run, the owner follows section 1c before creating, finding, or logging into a year folder, and section 1d before logging. A member skips section 1c and section 1d.

Keep user-specific values (root folder id and OneDrive path, year folder ids, file ids, currency, role, display name, merchant preferences) in the assistant's own memory, never in this skill. Which Gmail and Outlook accounts to scan is not a setup choice: each run checks which of those connectors are ready. Do not keep a dedupe log in memory. The root id is not the year folder id.

## Never log the same purchase twice

This section wins over every later step. Read it before any write. A match from any source must not add amounts again.

Check before every write, including a photo in chat, either email inbox, another family bot's copy, a re-scan, and a second Home Depot email. On OneDrive, re-download the workbook immediately before the check. Read the hidden Log (every data row) and the month receipt lists. The Log is authoritative. The month lists catch a row that was written to one place and not the other yet. A return is a separate receipt: a negative total does not match the original positive sale.

Normalize a receipt or order number by trimming spaces, ignoring a leading `#`, and comparing without case. `48291` and `#48291` are the same number. `48291` and `482910` are not.

Normalize a merchant by lowercasing, turning `&` into `and`, dropping punctuation, dropping a leading `the`, and dropping a store number (`#7016`, `no. 7016`, `store 7016`). Two names match when one normalized name contains the other, or every word of the shorter name appears in the longer one. `HOME DEPOT #7016` matches `The Home Depot Oakville`. `Costco` matches `Costco Wholesale`. `Costco` does not match `Walmart`. If a name is blank or unreadable, the merchant is unclear.

Matching order, stop at the first hit:

1. **Same receipt, transaction, or order number at the same merchant.** That is the same purchase, even when the dates are far apart and even when the message ids differ. An online order confirmation and its later shipping or receipt email are one purchase when they share the order number. A store slip and its eReceipt are one purchase when they share the receipt number.
2. **No number on at least one side.** Same merchant (fuzzy), same total to the cent, and the calendar dates within ±1 day. That is the same purchase. This is the photo with no readable number against the email of the same trip, and the Home Depot paper slip against the eReceipt when one of them has no number. If both sides have numbers and the numbers differ, they are different purchases. Do not use this rule.
3. **Near match. Ask one yes/no. Never guess, and do not write until they answer.** A near match is either of these:
   - Same merchant (fuzzy), dates within ±1 day, and the totals are not equal to the cent, but the absolute difference is at most the greater of 5.00 in the book currency and 15% of the larger absolute total.
   - The same total to the cent, and the merchant is unclear.
   If more than one existing row fits rule 2, that is also a near match: ask which row, or whether it is new. Do not pick one.

A message id already stored on a row means that same email was seen again. Treat it as a match. Do not add the amount.

On a match (rule 1 or rule 2, or the user answered yes to rule 3): do not write or change any category amount. Save the new file if it is not already in `receipts`, and attach it to the existing row. The File cell lists each copy as a short label joined with ` | `, for example `photo | email`. Each label links to that file. Add the new source (message id, order number) onto the Source cell the same way if it is not already there. Update the Log row and the month-list row together. Tell the user it was already logged and that the extra file was attached.

On a no to rule 3: log it as its own purchase.

If the user says a rule 2 pair was really two purchases (two coffees, same cafe, same day, same total, no receipt numbers), log the second amount. Set its Receipt/order # to `separate` and include `user confirmed separate` in Source. The next copy that fits more than one row is a near match: ask.

An unattended run (the daily scan) does not ask in a way that blocks. For rule 3 it does not log and does not guess. It puts the one yes/no question in the digest and leaves that receipt unlogged until the user answers.

### Worked examples

**Same order number.** Amazon order `111-2223333-4444555` on Oct 2 for $45.00, then a shipping email on Oct 8 with that same order number. Rule 1. The dates are a week apart and that does not matter. Attach the second file. Do not add $45.00 again.

**Store slip and eReceipt.** A photo: "The Home Depot Oakville", no receipt number, Oct 15, $84.12. An email: "HOME DEPOT #7016", receipt `48291`, Oct 15 or Oct 16, $84.12. Rule 2, because the photo has no number, the merchant matches, the total matches to the cent, and the dates are within ±1 day. One purchase. File becomes `photo | email`. Do not add $84.12 again.

**Second Home Depot email.** The row already has receipt `48291`. Another email arrives with receipt `48291` for Home Depot. Rule 1. Attach it. Do not add the amount.

**Read the receipts again.** The user sends the same photo, or the scan sees the same message id. If the number or the message id is already on a row, rule 1. Otherwise rule 2 on store, total, and date. Attach a file that is not already linked. Do not add the amount.

**Near match, small total gap.** Costco on Oct 3 for $120.00 is logged. A new Costco receipt on Oct 3 is $128.40. Same merchant, same day, totals differ by a small amount. Rule 3. Ask: "Is the Costco receipt for $128.40 the same purchase as the one for $120.00 on Oct 3?" Yes: attach, do not add. No: log it as its own purchase.

**Same total, merchant unclear.** A photo totals $57.29 on Oct 3 and the store name did not read. An email is Costco, $57.29, Oct 3. Rule 3. Ask one yes/no. Do not guess.

**A return.** Home Depot return, receipt `48299`, Oct 20, total -84.12. The sale was receipt `48291` for 84.12. Different numbers, and the totals are not the same to the cent because one is negative. Log the return as its own row, a negative amount in the original category. A photo and an email of receipt `48299` match each other by rule 1 and must not subtract twice.

**Two orders the same day.** Amazon order `111-AAA` for $20.00 and order `111-BBB` for $20.00, same day. Both have numbers and the numbers differ. Two purchases. Log both.

**The lookalike is a second purchase.** Two coffees, same cafe, same day, both $4.50, neither has a number. Rule 2 attaches the second file and does not add $4.50. If the user says it was a second coffee, log that second amount with Receipt/order # `separate` and Source `user confirmed separate`.

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

- They own this year's book: role `owner`. Save the ids, run section 1c, then section 1d if Annual Summary `C46` is not `v1.2.3`, and do not upload a new template over that workbook. Do not ask new or join, currency, or holidays. Read Annual Summary `C11` for the currency. Invite a receipt.
- The only book is shared with them and owned by someone else: role `member`. Save the year folder id, workbook id, and receipts folder id. Do not create a root, do not move folders, do not run section 1d, and do not ask for a link. Read `C11`. Do not refill holidays. Ask only for a display name, and let them skip.
- No book: role `owner` unless they paste a link. Infer the currency (ISO code and symbol) and the holiday country and province or state from the language they write in, the Grok Bot app or system language, and their timezone. Name the store, the currency, and the region in one line. Do not ask them as separate questions.

English shape: "I'll start a new book for this year in Google Sheets, in CAD, with public holidays for Canada / Ontario, and I'll scan Gmail. Say go, paste a shared Family Book link if you're joining, or tell me a different currency or region." Use the real store, code, and region. With no inbox `ready`, say email stays off until they connect Gmail or Outlook.

Inference to name in that line: a Canadian timezone or `en-CA` → CAD and that province (America/Toronto → Ontario). A US timezone or `en-US` → USD and that state when the timezone names one. `en-GB` → GBP, United Kingdom. French in Canada → CAD, Quebec, unless the timezone names another province. Other French, German, or Spain → EUR and that country. Japanese → JPY, Japan. Chinese → CNY, China. `en-AU` → AUD, Australia. English with no region → USD and United States.

If this turn already tells you to start (they said go, sent a receipt, or named a currency or region), apply what they named and create the book in this reply, with that one line included. If this turn is only a greeting, send the line and create the book on the next reply. A pasted folder or workbook link means join (below). If they say they are joining and send no link, ask only for the link. A new user whose Google store is already ready is done in that one or two replies.

Someone starting a book alone is not asked about sharing or a name. Ask for a short display name only when they joined, or when they said other people will log too (Mom or Alex). If they tell you a name later, save it and use it from then on. Entries include it only when one is saved, for example `Costco (Mom)`. The receipt list's Store column stays the merchant alone. The name goes in Logged by.

If they are starting a book that other people will also write to, and the store is OneDrive, say once that Google Sheets works better, because several people can edit at the same time. Do not refuse OneDrive, and do not say this to someone keeping the book alone.

**Join.** The owner shared the `Family Book - YYYY` folder as an editor. Resolve the link to the year folder id, the workbook id, and the `receipts` folder id. A workbook link uses its parent folder and the `receipts` folder inside it. A folder link uses the workbook named `Family Book - YYYY` inside it. If that store is not `ready`, connect it (Google Drive and Google Sheets, or OneDrive) and then continue. Do not create a folder, a workbook, or a `Family Book` root, and do not move anything. You may not be able to open the parent. Confirm you can read Annual Summary. If `receipts` is missing, create it inside the shared year folder. If the hidden Log sheet is missing, add it (section 3b). Do not insert the month receipt list and do not write `C46`. If `C46` is not `v1.2.3`, say once that the owner's bot will update the book. Save the code in `C11`. Do not change the shared book's currency, and do not refill holidays.

**Template** (owners only, and only when that year's workbook is not there yet). Follow section 1c so the root exists first. The blank template always comes from GitHub, on the box: `curl -fsSL -o family-book-template.xlsx https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx`. Verify it with openpyxl (Annual Summary, Jan to Dec, Holidays, and a hidden Log). Jan `B47` starts with `Receipts this month`. Annual Summary `C46` is `v1.2.3`. Upload that file into `Family Book - Templates` inside the root, replacing an older copy. A new year uses a fresh GitHub download. If GitHub can't be reached, say so and stop. Do not download the template, or any other file, from the owner's Google Drive. Listing folders and editing the Google Sheet through the Sheets connector is how the book is read and written.

**Save.** Year folder id, workbook id, receipts folder id, storage type, currency, holiday region, role (`owner` or `member`), and display name if they gave one. Do not save a fixed list of inboxes. For the owner, also save the root folder id, and on OneDrive the path `Family Book` from the top of their OneDrive. A member leaves the root empty. Do not save a language. Do not store the root id in the year-folder field.

**User's language vs English.** Chat, item notes and descriptions written into the book, holiday descriptions, product names in the Items column, and digests follow the language the user is writing in, or the Grok Bot app or system language when nobody has just written. These stay English on purpose: the workbook template's sheet names, category labels and notes, the receipt-list headers, receipt file names (`YYYY-MM-DD HHMM - Store - TOTAL.ext`), and this repo's skill, routine, and doc files. Translated templates per language (for example `template/family-book-template-fr.xlsx`) may be added later on request; until then, use the English template.

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

For year YYYY (default: the current year), the owner follows section 1c first, then section 1d for any older year books, then:

1. Inside the `Family Book` root, create folder `Family Book - YYYY` and inside it a subfolder `receipts`. This is the one receipts folder every family bot uses. The year folder's parent is the root, including when an older routine prompt forgets to name the parent. If that year folder is already inside the root and already holds the workbook, reuse the folder and `receipts` (create `receipts` only if it is missing). Do not upload a new template over that workbook, and do not create a second year folder. Steps 2 to 8 apply only when the workbook is not there yet.
2. Make a copy of the template with Annual Summary `F5` set to YYYY. Safest way on the box: open the .xlsx as a zip and replace `<c r="F5" s=".." t="n" />` in `xl/worksheets/sheet1.xml` with the same cell holding `<v>YYYY</v>` (this keeps all formatting). Verify with openpyxl. Leave the hidden Log sheet in place. Leave the receipt lists and Annual Summary `C46` (`v1.2.3`) in place.
3. Set the currency (skip if CAD): in `xl/styles.xml` replace `[$CAD]` with `[$XXX]` (the user's ISO code) in the number formats, and in `xl/worksheets/sheet1.xml` (Annual Summary) replace the `<t>CAD</t>` label in `C11` with the code. If the currency symbol is not `$` (for example EUR, GBP, CNY), also replace `&quot;$&quot;` with the symbol in the `numFmt` format codes. Rezip with Python (`shutil.make_archive`, no `zip` command needed) and verify the workbook opens with openpyxl and Annual Summary `C11` shows the code.
4. Google: UploadFile into the year folder with name `Family Book - YYYY` and convertToGoogleFormat true. OneDrive: upload `Family Book - YYYY.xlsx` into the year folder. On a shared OneDrive book, re-download immediately before this upload only when you are editing an existing file, not when the file is brand new.
5. Read the file back and confirm the Jan sheet shows dates (Jan 1 has the right weekday). Confirm the Log sheet exists and is hidden. If a Google Sheets conversion left it visible, hide it. If it is missing, add it (section 3b). Confirm Jan `B47` starts with `Receipts this month` and Annual Summary `C46` is `v1.2.3`. If a conversion dropped the list or the marker, follow section 1d for this book only. Day 31 is columns BR and BS.
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

A member's bot does not run the new-year routine and does not create a workbook. It does not create a `Family Book` root and it does not move folders, including when this year's folder now sits inside the owner's root. In December, or when a receipt is dated next year and that book is not in memory, look for a folder named `Family Book - YYYY` that the owner has shared with this user. You may see it only as a shared folder. Save the new folder id, workbook id, and receipts folder id. If the hidden Log is missing, add it (section 3b). Do not insert the receipt list. If it is not there yet, wait. The owner's bot creates it on December 20 inside the same root, and the owner shares that new year folder. Do not create the book yourself. The year folder id already in memory still works after the owner moves that folder. Do not replace it. Do not run the migration. If Annual Summary `C46` is not `v1.2.3`, the owner's bot will update that book.

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

## 1d. Book version, and migration from v1.0 through v1.2.2

Annual Summary `B46` says `Book version`. Annual Summary `C46` is the marker. `v1.2.3` means this workbook already has the receipt lists and the receipt-key dedupe. Anything else, including a blank cell, means the book was set up on v1.0 through v1.2.2.

On every run, the owner checks `C46` on every year workbook in the `Family Book` root. When a book is not `v1.2.3`, run the `family-book-migrate` skill once for that book before logging. Download it from `https://raw.githubusercontent.com/Skybatan/family-book/main/bot/skills/family-book-migrate/SKILL.md` when it is not installed. The plan for people is `docs/migration-v1.2.3.md`. The migration rebuilds the bottom receipt list from the hidden Log, the saved files, and the original emails. It renames files to the simple file name. It does not retype the number cells. It is owner-only, resumable, and safe to run twice. A member never runs it.

A new book made from the v1.2.3 template already has `C46` = `v1.2.3`. Do not migrate it.

The month-list columns (date and time, store, receipt or order number, total, payment last 4) are the fields a card-statement check will use. That check is issue #6. Do not build it here, and do not close the issue.

## 2. Sheet layout (every month sheet)

- **Income This Month:** rows 8 to 11. Column B is Item, C is Amount, D is Date Received.
- **Fixed Expenses This Month:** rows 18 to 38. Column B is the pre-set item, C is Amount, D is Date Paid. The items are Income (enter as negative), GAS, Electricity & Water, RESP, Mobile Phone, Daycare, Rent / Mortgage, Internet, Car Insurance, Property Tax, Fuel / Maintenance, Home Insurance, Car Loan Payment, Housing Management Fee, Term Deposit, Pocket Money, and Savings. Match by reading column B, not by fixed row.
- **Daily Record:** the day number is in row 2. Day d has its Item column at column index 10 + 2*(d-1), with A as 1, and the Amount column is the next one. Day 1 is J and K, day 2 is L and M, day 29 is BN and BO, day 30 is BP and BQ, and day 31 is BR and BS. Read and write the daily block through column BS. The month totals already do (`Jan!G8` is `=SUM(J21:BS21)`, and `J43:BS43` is temporary income). Always confirm the date in row 2 before writing. A blank row 2 means that day is not in this month. The receipt list below row 44 is not part of the daily block.
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
- **Receipts this month:** below the totals. Rows 45 and 46 stay empty. Row 47 is the title `Receipts this month` in column B, merged through column S. Row 48 is the header. The first receipt is row 49. No SUM or total formula includes row 45 or below. Do not extend one. Columns E and H are the sheet's narrow spacers. Leave them blank so the columns above do not change width.

| Column | Header | What to write |
|---|---|---|
| B | Date & time | `YYYY-MM-DD HH:MM`, or `YYYY-MM-DD` when the time is unknown |
| C | Store | Merchant, no person's name |
| D | Receipt/order # | Number, or blank. `separate` only when the user confirmed a second purchase |
| F | Items | `product: price; product: price` |
| G | Total | Number, negative for a return. This does not feed the totals above |
| I | Category/cells written | Amount cells joined with `+`, for example `AN6+AN17+AN22` |
| J | Payment | Card last 4 only, such as `1234`, or blank. Never the full card number |
| K | File | `photo`, `email`, or `photo \| email`. Each label links to the saved file |
| L | Source | `photo`, `email gmail/family@example.com 18c3fab`, or `statement`. The header is merged `L48:R48`. Write the value in L. Merge `L:R` on that data row only when the text needs the room. Do not merge over column S |
| S | Logged by | Display name, or blank |

If the title is not on row 47 because a migration placed it lower, find the cell in column B whose text starts with `Receipts this month`. The header row is the next row. Append under the last filled receipt row.

The File cell can hold more than one link. Join the labels with ` | `. On Google Sheets, link each label. On Excel, the cell shows `photo | email`, the cell hyperlink opens the first file, and the Log Saved file column keeps every url as `photo: <url> | email: <url>`.

The list is how people check a purchase, and it is the row a later card-statement match will use (issue #6). Do not build statement matching in this skill.

## 3. Log a receipt

Sources: a photo or PDF the user sends in chat, a receipt in the `receipts` folder, or an order or receipt email. Every bot logs into the same shared book. At the start of the run, the owner follows section 1c once and section 1d once. A member does not.

1. Read the receipt: merchant, date of purchase, time if shown, line items with prices, subtotal, tax, total, currency, receipt or order number, and card last 4 if shown. Store only the last 4.
2. Pick the month sheet and day from the purchase date. The day's columns are in section 2: day 31 is BR and BS, and any read of the daily block goes through BS. If the date is outside this book's year, use that year's book. An owner may create it (section 1). A member attaches to the one the owner shared (section 1b) and does not create a book. If the date is January 1 or December 31, also check the adjacent year's Log when that book exists, because rule 2's ±1 day can cross the year.
3. Categorise. One entry per category; if a receipt spans categories (for example Costco food plus household goods), split the total across categories by line items and spread tax and discounts proportionally so the parts add up to the receipt total. The receipt is still one list row and one Log row.
4. Run "Never log the same purchase twice" before writing any amount. On a match, save and attach the file (section 3c and 3a) and stop. On a near match during a conversation, ask the one yes/no and wait.
5. Write the amount: in the first empty row of that category block for that day, put the Item as the merchant (consistent naming, for example `Costco`, `Amazon`, `Home Depot`). If a display name is saved, add it in parentheses, for example `Costco (Mom)`. A short note in the language you are using with the user can follow, for example `Costco (Mom) milk and paper towels`. Put the Amount as a number. If every row in the block is used, add to an existing amount as a formula (`=12.50+8.20`). The file name does not include the person's name.
6. Refunds and returns: a negative amount in the original category, or row 43 if it is new money. A return is its own receipt row. Do not attach it to the original sale.
7. Recurring bills (hydro, phone, internet, insurance, mortgage) go in Fixed Expenses for that month, not the Daily Record. Salary and other income go in Income This Month. They get a list row and a Log row too.
8. **Always save a copy of a photo or email receipt in the shared `receipts` folder**, named as in section 3c (for example `2026-10-15 1432 - Costco - 57.29.png`). A photo or email receipt does not count as logged until its file is saved there. A bill the user dictates with no document can have a blank File and Source `note`. See section 3a for email receipts.
9. Only after that file is saved (or the entry is a dictated note with no document), append one row to the month list and one row to the hidden Log (section 3b). Write both in the same pass. If the file could not be saved, do not append either row. On the next attempt, save the file and append the rows, and do not write the amount a second time.
10. Tell the user, in the language they are writing in, what was logged in one or two lines (merchant, date, total, category split, and who logged it when a name is saved). If the amount or category was a guess, say so and ask. If the purchase was already there, say that the file was attached and the total was not added again.

## 3a. Save an email receipt as a file (required for every email receipt)

1. Use the original merchant email, not a forward, when both exist. If the email has a PDF receipt or invoice attachment, download that (DownloadFile) and save it as is.
2. Otherwise render the email's HTML body on the box:
   - Write the `htmlBody` from the mail connector's get_message to `receipt.html`.
   - Long one-page image (best for app-style receipts like Costco.ca or Amazon): `google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=800,4000 --virtual-time-budget=8000 --screenshot=out.png file:///path/receipt.html`, then crop the empty bottom with Pillow (find the content bounding box against the background colour). Raise the window height if the content reaches the bottom.
   - PDF (best for text-style till receipts like Home Depot): `google-chrome --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf=out.pdf file:///path/receipt.html`.
3. Look at the result (open the image, or `pdftotext` the PDF) and confirm the merchant, date, and total are visible before uploading.
4. Upload to the year's shared `receipts` folder (Google: UploadFile with the folder id; OneDrive: UploadFile with overwrite false). Name the file as in section 3c. The Log's Saved file column stores that name and the file url.
5. If rendering fails, save a plain-text summary of the receipt (merchant, date, time, order number, line items, tax, total, card last 4) as a `.txt` with the same file-name pattern, and mention it in the report.

## 3b. Log tab and month list

Dedupe is the hidden `Log` sheet, one row per purchase, shared by every bot. The month receipt list is the same row for people to read, and for a later statement match. Do not keep a second dedupe list in memory. If the Log and a month list disagree, the Log wins for "already counted". Repair the month list by adding or filling the row. Do not change number cells to force them to agree.

If the open book has no `Log` sheet, add one before logging, with the header below, and hide it. Google Sheets: add the sheet with the Sheets connector, write the header, then hide the tab. Excel: add the sheet with openpyxl, set its state to hidden, and re-upload. On OneDrive, re-download immediately before this write. A member may add that sheet so they can dedupe. A member does not insert the month receipt list and does not write `C46`. If the list header is missing, write the amount and the Log row, and say once that the owner's bot will add the month list.

The owner adds a missing Log before logging, but a missing receipt list on an older book is the migration (section 1d), not an ad-hoc insert during a single receipt. On a v1.2.3 book the list is already there.

Log header, row 1. Leave column H as the note. Do not write data there.

| Column | Header | Write |
|---|---|---|
| A | Source | `photo`, `email gmail/family@example.com 18c3fab`, `statement`, or several joined with ` \| `. |
| B | Date | Purchase date as text `YYYY-MM-DD`. |
| C | Merchant | Consistent merchant name, with no person's name. |
| D | Total | Receipt total as a number. Negative for a return. |
| E | Where written | Amount cells, for example `Oct!J6+Oct!J22`, or `Oct Fixed Expenses / GAS` when that is all an old row has. |
| F | Saved file | File name, and urls when there are several: `photo: <url> \| email: <url>`. Blank until the file is in `receipts`. |
| G | Logged by | The display name from memory, or blank. |
| I | Receipt/order # | The number, or blank. `separate` when the user confirmed a second purchase. |
| J | Date & time | `YYYY-MM-DD HH:MM`, or the date alone. |
| K | Items | `product: price; product: price`. |
| L | Payment | Last 4 digits, or blank. |
| M | Month list row | The Date & time cell of this purchase, for example `Oct!B49`. |

Month-list columns are in section 2. Category/cells written uses the same cells as Where written, without the sheet name when the row is already on that sheet, for example `J6+J22`.

Append the Log row and the month-list row only after the receipt file upload succeeds. Read both once more immediately before appending, so a row another bot just wrote is not duplicated. On OneDrive that read is a fresh download, and the upload follows immediately.

A row with no Saved file, for a photo or email receipt, is not finished. Save the missing file in `receipts`, then fill Saved file and the File cell. Do not write the amount a second time.

## 3c. File names

`YYYY-MM-DD HHMM - Store - TOTAL.ext`

Examples: `2026-10-15 1432 - Costco - 57.29.png`, `2026-10-15 - Costco - 57.29.pdf` when the time is unknown, `2026-10-20 0910 - Home Depot - -84.12.pdf` for a return.

- `HHMM` is 24-hour, four digits, no colon. Omit the time, including the space before the first ` - `, when it is unknown.
- Store is the merchant name, with no person's name.
- TOTAL is the receipt total with two decimals.
- Strip `/ \ : * ? " < > |` and control characters. Collapse spaces. Trim spaces and dots from the ends of each part.
- The details (line items, receipt number, card last 4, who logged it) live on the sheet, not in the file name.
- Add ` - #receiptno` or, if there is no number, ` - ` plus a short item hint, only when that folder already has the same name. If it still collides, add ` - 2`, ` - 3`.
- Do not rename a file that already matches this pattern.

## 4. Scan email for receipts

The owner follows section 1c and section 1d once before searching. A member skips both.

At the start of every scan, check Gmail and Outlook again (GetMcpServerStatus or GetDynamicTools). Scan every account that is `ready`, including an account connected after setup (section 0a). If a new one is `ready`, include it and say so in one line. If none is `ready`, stop and do not ask them to connect email.

1. Search since the last scan. The first scan of an inbox is the last 30 days. Say that older receipts from this year can be backfilled on request. A good starting Gmail query: `(subject:(receipt OR order OR invoice OR "your order" OR purchase) OR from:(amazon OR homedepot OR costco OR walmart OR bestbuy OR apple OR uber OR doordash)) -subject:(shipped OR delivered OR "out for delivery")`, and adapt it to the user's merchants. For Outlook use the matching search. Keep a shipping or receipt email when it carries an order number you may already have logged: that is one purchase under rule 1, and the file gets attached instead of skipped as a duplicate amount. Skip marketing. Skip a pure shipping notice that has no order number and no total.
2. Use the order confirmation or the final invoice as the source of truth for a new purchase. A later email with the same order number is the same purchase.
3. Log each receipt as in section 3. Run the dedupe check before any amount. Always save the receipt file in the shared `receipts` folder as in section 3a and name it as in section 3c. Never add a Log row or a month-list row until its file is saved.
4. Never reply to, forward, or send email while doing this; it is read-only.
5. Report a short digest in the language the user writes in, or the Grok Bot app or system language when nobody has just written: how many were found, what was logged, what was attached to an existing purchase, who logged it when a name is saved, any near-match question, and anything unclear.

## 5. Writing tools

- Google Sheets connector: write values to `'<Mon>'!<cell>` ranges. Read the target range first so you never overwrite. A daily read includes every day column through BS. Google Sheets is the right store when several bots write, because editors can update the same spreadsheet together. Hide the Log sheet and leave it hidden. Do not write receipt rows into rows 1 to 44.
- Do not download or export files from the owner's Google Drive, including the template and the Google Sheet. The template comes from GitHub (section 0). If Sheets is not `ready`, connect it (section 0 or 0a) and write with the Sheets connector.
- OneDrive or Excel Online: two bots editing the same .xlsx can overwrite each other. Re-download the workbook right before every write, edit that fresh copy, and upload it immediately with overwrite true. Do not write from a copy downloaded earlier in the turn. Check that the file is not open for editing elsewhere. Prefer Google when more than one person logs receipts.
