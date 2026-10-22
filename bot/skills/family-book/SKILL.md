---
name: family-book
description: "Never log the same purchase twice. Use when setting up a yearly Family Book workbook (Google Sheets or Excel Online), or when logging a card statement, a bank export, a receipt photo, an order or receipt email, income, or a bill."
---

# Family Book: household income and expense tracker

A yearly workbook built from the blank template `family-book-template.xlsx` from https://github.com/Skybatan/family-book (Annual Summary, Jan to Dec sheets, Holidays, and a hidden Log sheet). The assistant sets it up once per year, then logs receipts from photos and from email into the right month, day, and category.

Each month sheet keeps the number grid on top. Under it, a Transactions section lists statement lines and a Receipts section lists receipts. The hidden Log tab is the authoritative dedupe list for the year. The two sections are the same purchases, where people can check them. Card statements are the usual input. Bank accounts are optional. Receipts verify a line and add the item split. They never add a second amount. Several family members can each run their own bot against one shared book. One bot starts the book (the owner). The others join with the shared folder or workbook link. Every bot writes to that book and to its one `receipts` folder. Bots share that workbook, so the dedupe check works across bots. Do not keep a dedupe log in memory.

The owner's years live together under one root folder named `Family Book`, on Google Drive and on OneDrive. The owner remembers that folder's id, and on OneDrive its path. A member never uses the root. They keep working from the shared year-folder link.

```text
Family Book/                      root, created once
  Family Book - YYYY/             one folder per year
    Family Book - YYYY            the sheet or workbook
    receipts/
    statements/{Issuer Product}-{last4}/
  Family Book - Templates/        the owner's blank template
```

This skill is the source of truth for where those folders go. If a routine prompt from an older install tells you to create `Family Book - YYYY` and does not name the root, the parent is still `Family Book`, and section 1c still runs first. On every run, the owner follows section 1c before creating, finding, or logging into a year folder, and section 1d before logging. A member skips section 1c and section 1d.

Keep user-specific values (root folder id and OneDrive path, year folder ids, file ids, currency, role, display name, merchant preferences) in the assistant's own memory, never in this skill. Which Gmail and Outlook accounts to scan is not a setup choice: each run checks which of those connectors are ready. Do not keep a dedupe log in memory. The root id is not the year folder id.

## Never log the same purchase twice

This section wins over every later step. Read it before any write. A match from any source must not add amounts again.

Check before every write, including a photo in chat, either email inbox, another family bot's copy, a re-scan, and a second Home Depot email. On OneDrive, re-download the workbook immediately before the check. Read the hidden Log (every data row) and the month receipt lists. The Log is authoritative. The month lists catch a row that was written to one place and not the other yet. A return is a separate receipt: a negative total does not match the original positive sale.

Normalize a receipt or order number by trimming spaces, ignoring a leading `#`, and comparing without case. `48291` and `#48291` are the same number. `48291` and `482910` are not.

A fuel AUTH, approval, or authorization code is not a receipt, transaction, or order number. Do not put it in Receipt/order # and do not use it for rule 1. If that is the only code on the slip, the number is blank, so the pump slip can match the email by rule 2. A code labeled receipt, transaction, invoice, order, or sequence is a receipt number.

Normalize a merchant by lowercasing, turning `&` into `and`, dropping punctuation, dropping a leading `the`, and dropping a store number (`#7016`, `no. 7016`, `store 7016`). Two names are a full match when one normalized name contains the other, or every word of the shorter name appears in the longer one. `HOME DEPOT #7016` matches `The Home Depot Oakville`. `Costco` matches `Costco Wholesale` and `Costco.ca`. `Costco` does not match `Walmart`. If a name is blank or unreadable, the merchant is unclear. A partial match is weaker than a full match and is never automatic: after the same normalization the names are not a full match, but they share a word of 4 or more letters, or the normalized names are within 2 single-character edits (`Walmart` and `Walmrt`).

The name written in the Store column, the Log Merchant column, and the file name is the short merchant name. Drop a leading `the`, a store number, a domain suffix (`.com`, `.ca`, `.co.uk`, `.net`, `.org`), and a trailing `wholesale` or `online`. `Costco.ca`, `Costco Wholesale`, and `COSTCO #7016` are all `Costco`. `HOME DEPOT #7016` is `Home Depot`. Use that usual capitalization.

When a stored date is only an email sent date and the receipt prints a transaction date, the receipt's transaction date wins. The email's sent date is not a transaction date.

When a rule 2 auto-attach has two transaction dates, the earlier transaction date wins. The same rule applies after a yes on rule 3 when both sides are receipts. A receipt or order number does not pick the date. Copy a number onto a blank Receipt/order #, and do not replace a number that is already there.

Update the kept Log row's Date and Date & time to that earlier transaction date. Date & time uses that earlier receipt's HHMM. If the earlier receipt has no time, Date & time is the date alone. Do not copy a time from the other receipt. Update the Receipts date to match. If the month changes, move the Receipts row and clear the old one. Do not delete the Log row. Files keep their own names. On a match, do not rename a saved file. Do not rename a file to a time it does not show, and do not rename a file to a name that already exists.

If the amount sits on a different day column than the kept date, move that same amount to the kept date's day column, on the same category row, and clear it from the old day. Meals row 6 stays row 6 on the new day. Do not drop it onto the first empty row of the block. If the old cell is a formula that mixes this amount with other purchases, drop only this amount from the formula and write it on the kept day, still on that same category row. Update Where written and Category/cells written to the new cell. This moves the amount. It does not change the amount, so do not ask.

If both sides have a receipt, transaction, or order number and the normalized numbers differ, they are different purchases. Do not use rule 2 or rule 3, and do not ask. Two Amazon orders with different order numbers are two purchases even when the store, the total, and the date are the same.

Gather every candidate before you write or attach. Do not stop at the first hit. Read the whole Log and the month lists. Skip any row whose Status is `superseded`. A Status `question` row is an open question, not a candidate to attach to. The receipt key is how one purchase is recognized on the Log. When the receipt or order number is present, the key is that normalized number at that store. When the number is blank, the key is the short store name, the transaction date, and the total to the cent. A Status `pending` row with this same key is not a rule 2 match candidate. Resume that row through the write steps in section 3. Do not attach it as a second copy and do not add the amount. Collect every other row that fits rule 1, rule 2, or rule 3. Auto-attach only when that collection has exactly one candidate. With two or more candidates, ask one question that lists every one of them. Do not attach, and do not write an amount, until they answer.

1. **Same receipt, transaction, or order number at the same merchant (full match).** That is the same purchase, even when the dates are far apart and even when the message ids differ. An online order confirmation and its later shipping or receipt email are one purchase when they share the order number. A store slip and its eReceipt are one purchase when they share the receipt number.
2. **No number on at least one side.** Same merchant (full match), same total to the cent, and the calendar dates within ±1 day. That is the same purchase. This is the photo with no readable number against the email of the same trip, and the Home Depot paper slip against the eReceipt when one of them has no number.
3. **Near match. Never guess, and do not write until they answer.** One candidate is one yes/no. Two or more candidates are one question that lists every one of them. Anything close that is not the single automatic candidate is a near match. A near match is any of these:
   - Same merchant (full match), same total to the cent, and the calendar dates are more than 1 day apart and at most 7 calendar days apart. The same clear store with the same total two days apart is this case. Ask. Do not log it as a new purchase.
   - Same merchant (full match), dates within ±1 day, and the totals are not equal to the cent, but the absolute difference is at most the greater of 5.00 in the book currency and 15% of the larger absolute total.
   - The same total to the cent, and the merchant is unclear.
   - The same calendar date, the same total to the cent, and the merchant is only a partial match. Ask. Do not treat the partial name as a different store.
   Two or more candidates, of any mix of rules, are one question. Do not attach to the closest row.

A message id already stored on a row means that same email was seen again. Attach it to that row. This is the same message, not a second candidate. Do not add the amount.

Exactly one candidate, and it is rule 1 or rule 2: attach to that row. Do not add the amount. If the two transaction dates differ, the earlier date wins.

Exactly one candidate, and it is rule 3: ask one yes/no that names that one row. Do not write a category amount and do not choose an amount cell. Example: "Is the Costco receipt for $57.29 on Oct 5 the same purchase as the one on Oct 3?"

Two or more candidates: ask one question that lists every candidate, with its date and why it matched. The answer has to work for the whole list, not for the closest row alone. Example: "Is the Costco receipt for $57.29 on Oct 10 the same purchase as one of these: Oct 11 (one day apart), or Oct 3 (seven days apart)? Reply with the date it matches, or no if it is new." A reply that names one date attaches to that row only. A bare yes does not pick a row. Ask, with those same candidate dates: "Which date does it match: Oct 11 or Oct 3? Reply no if it's new." No means it is new. Do not auto-attach. Do not write an amount while the question is open. Do not add a third amount.

If a Status `question` row already covers this item, join that row instead of opening a second question. Covered means the same merchant (full match, or the same partial match that question already used), the same total to the cent, and a transaction date within 7 calendar days of a date already on that question row.

An open, unanswered question is one Log row with Status `question`. Its Source is `open question: candidates <dates>; <source>`. Example: `open question: candidates 2026-10-11, 2026-10-03; photo`. Where written stays blank. Nothing is written into a category cell. A receipt-only question, such as a near match, gets a Receipts row whose helper Status is `question`. A category question, such as an unknown statement merchant, gets a Transactions row whose helper Status is `question`. That row's Source is `open question: category; <source>`, for example `open question: category; statement`. Status `question` is on the Transactions row, or on the Receipts row when the question is receipt-only. A split receipt still writes every item and its price on the Receipts row. The grid uses one cell per category, the first empty cell of that category: Costco eggs and chicken share Meals `Sep!AW6`, and paper towel is Household `Sep!AW22`. Where written lists those cells with `+`, for example `Sep!AW6+Sep!AW22`. The file may be saved in `receipts` and listed on this row. That does not log the purchase. Record the same dates on Log column H, the notes column. H1 stays the book note. Example: `2026-10-10; candidates 2026-10-11, 2026-10-03`. A later receipt that joins the question adds its date to the candidates list in Source and in column H, and appends its source after the semicolon, still joined with `, `. Do not write an amount in column H. Do not append a second Log row. On a yes that names one candidate, attach the file to that purchase, fill a blank receipt number, apply the date rule above, and set this question row's Status to `superseded`. Do not delete the question row. On a no, this question row becomes the new purchase: set Status to `pending`, put the target cell in Where written, then write that cell. A superseded row stays on the Log and is ignored when matching.

On a match (the one automatic candidate, or the user named one candidate): do not write or change any category amount, except the date move above, which puts the same amount on the kept day. Do not create a second Log row. Save the new file only when it is not already in `receipts` (section 3c), and attach it to the existing row. The Receipts File cell (column AA) has one link, to the primary file. Its text is that file's label (`photo`, `email`, `statement`, or `text`). When there is another file, the text is the primary label plus the extra count, for example `photo +1`. Do not write `photo | email`, and do not repeat labels. Every file is listed in Log column F as `1 photo: <url>, 2 email: <url>`. A single file uses the same shape: `1 photo: <url>`. Append the new source on Log column A and on the Receipts helper File list (column CB), joined with `, `. Those two cells are where Source lives. The Receipts section has no Source column. Do not replace the source that is already there. A photo is `photo`. An email is never the bare word `email`. Gmail is `email gmail/<addr> <msgid>`, for example `email gmail/family@example.com 18c3fab`. Outlook is `email outlook/<addr> <msgid>`. A photo and that email read `photo, email gmail/family@example.com 18c3fab`. A second photo reads `photo, photo`. Column CB gets that same text whenever a match attaches a file. On a match, files keep their own names. If the new copy has a receipt or order number and the existing Receipt # is blank, fill that number in Receipts column B and Log column I. Do not replace a number that is already there. Update the Log row and the Receipts row together. Tell the user it was already logged and that the extra file was attached.

On a no to rule 3: log it as its own purchase, using the idempotent write in section 3, starting from the question row when one exists. Do not write a category amount while the question is still open.

If the user says a rule 2 pair was really two purchases (two coffees, same cafe, same day, same total, no receipt numbers), log the second amount. Set its Receipt/order # to `separate` and append `user confirmed separate` to Source, joined with `, `. The next copy that fits more than one row is a near match: ask.

An unattended run (the daily scan) does not ask in a way that blocks. For rule 3 it does not write a category amount and does not guess. It writes or joins the one Status `question` Log row, with Where written blank, and puts that one yes/no question in the digest. The receipt stays unlogged until the user answers. A later identical item joins that same question row.

### Worked examples

**Same order number.** Amazon order `111-2223333-4444555` on Oct 2 for $45.00, then a shipping email on Oct 8 with that same order number. Rule 1. The dates are a week apart and that does not matter. Attach the second file. Do not add $45.00 again.

**Store slip and eReceipt.** A photo: "The Home Depot Oakville", no receipt number, Oct 15, $84.12. An email: "HOME DEPOT #7016", receipt `48291`, Oct 15 or Oct 16, $84.12. One candidate, rule 2, because the photo has no number, the merchant matches, the total matches to the cent, and the dates are within ±1 day. Auto-attach. If the email is Oct 16, the earlier transaction date wins, so the kept Log row's date stays Oct 15 and its HHMM is the earlier receipt's time. The saved files keep their own names. Source becomes `photo, email gmail/family@example.com 18c3fab` when that is the email. A second photo would be `photo, photo`. The File cell reads `photo +1` and links to the photo. Log column F lists `1 photo: <url>, 2 email: <url>`. The blank Receipt/order # is filled with `48291`. Do not add $84.12 again.

**Second Home Depot email.** The row already has receipt `48291`. Another email arrives with receipt `48291` for Home Depot. Rule 1. Attach it. Do not add the amount.

**Same clear store, same total, two days apart.** Costco on Oct 3 for $57.29 is logged, and the receipt number did not read. A new Costco receipt for $57.29 is dated Oct 5, with no number (or only one side has a number). Exactly one candidate, and it is rule 3, because the dates are more than ±1 day apart. Ask: "Is the Costco receipt for $57.29 on Oct 5 the same purchase as the one on Oct 3?" Do not write it as new before that answer. Yes, and both sides are receipts: the earlier transaction date wins, so the kept Log row stays Oct 3 and keeps that receipt's HHMM. The files keep their own names. If the amount was written on Oct 5's day column, move the same amount to Oct 3 on the same category row and do not ask. The receipt number does not pick the date. Attach the file, fill a blank receipt number, and do not add. No: the question row becomes its own purchase.

**Two candidates, Oct 10.** Costco $57.29 on Oct 3 is logged, and Costco $57.29 on Oct 11 is logged. A new Costco receipt for $57.29 is dated Oct 10, with no number. Gather every candidate first. Oct 11 is a rule 2 candidate (within ±1 day). Oct 3 is a rule 3 candidate (same store, same total, within 7 days). That is two candidates, so do not auto-attach to Oct 11. Ask one question that lists both: "Is the Costco receipt for $57.29 on Oct 10 the same purchase as one of these: Oct 11 (one day apart), or Oct 3 (seven days apart)? Reply with the date it matches, or no if it is new." The question row's Source is `open question: candidates 2026-10-11, 2026-10-03; photo`. Write those dates in Log column H too: `2026-10-10; candidates 2026-10-11, 2026-10-03`. A reply of Oct 11 attaches to that row only, and the earlier of Oct 10 and Oct 11 wins on the Log row. The files keep their own names. A reply of Oct 3 attaches to that row only. A bare yes asks: "Which date does it match: Oct 11 or Oct 3? Reply no if it's new." No logs Oct 10 as its own purchase. Do not add a third $57.29 before that answer.

**An open question, then the same receipt again.** The Oct 5 Costco question above is still unanswered. Status is `question`, Where written is blank, and no category amount was written. Another Costco receipt for $57.29 dated Oct 4 arrives before the user answers. It is the same merchant, the same total, and within 7 days of a date already on that question. Join that question row. Add `2026-10-04` to the candidates in Source and in Log column H, and append the new source after the semicolon with `, `. Do not open a second question and do not write an amount.

**Read the receipts again.** The user sends the same photo, or the scan sees the same message id. A message id already on a row attaches to that row. Otherwise gather every candidate, and auto-attach only when there is exactly one. The primary check that a file was already saved is its SHA-256 in Log column O, and that check still hits after a rename. If column O is blank and the file is already in `receipts`, hash that saved file now and fill column O. If the file is missing, use the receipt key defined above (the short store name, the transaction date, and the total to the cent), and do not treat it as a new purchase when that key is already on a row. Name plus size is only a fallback when the bytes cannot be hashed, and that fallback misses a renamed copy. Attach a file that is not already listed. Do not upload a second copy. Do not add the amount.

**Near match, small total gap.** Costco on Oct 3 for $120.00 is logged. A new Costco receipt on Oct 3 is $128.40. Same merchant, same day, totals differ by a small amount. Rule 3. Ask: "Is the Costco receipt for $128.40 the same purchase as the one for $120.00 on Oct 3?" Yes: attach, do not add. No: log it as its own purchase.

**Same total, merchant unclear.** A photo totals $57.29 on Oct 3 and the store name did not read. An email is Costco, $57.29, Oct 3. Rule 3. Ask one yes/no. Do not guess.

**Same date, partial merchant.** A photo reads "Walmrt", Oct 3, $57.29, no receipt number. The book has Walmart, Oct 3, $57.29, no receipt number. The names are not a full match. They are one edit apart, so this is a partial match. Rule 3. Ask one yes/no. Do not log a second Walmart trip before the answer.

**A return.** Home Depot return, receipt `48299`, Oct 20, total -84.12. The sale was receipt `48291` for 84.12. Different numbers, and the totals are not the same to the cent because one is negative. Log the return as its own row, a negative amount in the original category. A photo and an email of receipt `48299` match each other by rule 1 and must not subtract twice.

**Two orders the same day.** Amazon order `111-AAA` for $20.00 and order `111-BBB` for $20.00, same day. Both have numbers and the numbers differ. Two purchases. Log both.

**The lookalike is a second purchase.** Two coffees, same cafe, same day, both $4.50, neither has a number. Rule 2 attaches the second file and does not add $4.50. If the user says it was a second coffee, log that second amount with Receipt/order # `separate` and append `user confirmed separate` to Source, joined with `, `.

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

- They own this year's book: role `owner`. Save the ids, run section 1c, then section 1d if Annual Summary `C46` is not `v2.0`, and do not upload a new template over that workbook. Do not ask new or join, currency, or holidays. Read Annual Summary `C11` for the currency. Invite a receipt.
- The only book is shared with them and owned by someone else: role `member`. Save the year folder id, workbook id, and receipts folder id. Do not create a root, do not move folders, do not run section 1d, and do not ask for a link. Read `C11`. Do not refill holidays. Ask only for a display name, and let them skip.
- No book: role `owner` unless they paste a link. Infer the currency (ISO code and symbol) and the holiday country and province or state from the language they write in, the Grok Bot app or system language, and their timezone. Name the store, the currency, and the region in one line. Do not ask them as separate questions.

English shape: "I'll start a new book for this year in Google Sheets, in CAD, with public holidays for Canada / Ontario, and I'll scan Gmail. Say go, paste a shared Family Book link if you're joining, or tell me a different currency or region." Use the real store, code, and region. With no inbox `ready`, say email stays off until they connect Gmail or Outlook.

Inference to name in that line: a Canadian timezone or `en-CA` → CAD and that province (America/Toronto → Ontario). A US timezone or `en-US` → USD and that state when the timezone names one. `en-GB` → GBP, United Kingdom. French in Canada → CAD, Quebec, unless the timezone names another province. Other French, German, or Spain → EUR and that country. Japanese → JPY, Japan. Chinese → CNY, China. `en-AU` → AUD, Australia. English with no region → USD and United States.

If this turn already tells you to start (they said go, sent a receipt, or named a currency or region), apply what they named and create the book in this reply, with that one line included. If this turn is only a greeting, send the line and create the book on the next reply. A pasted folder or workbook link means join (below). If they say they are joining and send no link, ask only for the link. A new user whose Google store is already ready is done in that one or two replies.

**Cards, after the book exists.** Do not ask about cards before the store is chosen, and do not block creating the book on the answer. Once the book is created, ask one question, in the language of the chat: which cards they have (issuer, product, and last 4). In English: "Which cards should I track? A short list is enough: issuer, product, and the last 4 digits. Or send the first statement and I will learn the cards from it." Write each card they name on the Cards sheet, Paid status `unpaid`, and leave statement day and due day blank until a statement shows them. If they skip the question or send a statement instead, learn the cards from that statement. Do not ask for a bank account. Bank data stays optional.

Someone starting a book alone is not asked about sharing or a name. Ask for a short display name only when they joined, or when they said other people will log too (Mom or Alex). If they tell you a name later, save it and use it from then on. Entries include it only when one is saved, for example `Costco (Mom)`. The Receipts Store column stays the merchant alone. The name goes in Logged by.

If they are starting a book that other people will also write to, and the store is OneDrive, say once that Google Sheets works better, because several people can edit at the same time. Do not refuse OneDrive, and do not say this to someone keeping the book alone.

**Join.** The owner shared the `Family Book - YYYY` folder as an editor. Resolve the link to the year folder id, the workbook id, and the `receipts` folder id. A workbook link uses its parent folder and the `receipts` folder inside it. A folder link uses the workbook named `Family Book - YYYY` inside it. If that store is not `ready`, connect it (Google Drive and Google Sheets, or OneDrive) and then continue. Do not create a folder, a workbook, or a `Family Book` root, and do not move anything. You may not be able to open the parent. Confirm you can read Annual Summary. If `receipts` is missing, create it inside the shared year folder. If the hidden Log sheet is missing, add it (section 3b). Do not insert the Transactions or Receipts sections and do not write `C46`. If `C46` is not `v2.0`, say once that the owner's bot will update the book. Save the code in `C11`. Do not change the shared book's currency, and do not refill holidays.

**Template** (owners only, and only when that year's workbook is not there yet). Follow section 1c so the root exists first. The blank template always comes from GitHub, on the box: `curl -fsSL -o family-book-template.xlsx https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx`. That address stays on `main`. It is the right address after this release is merged. Do not point it at a feature branch. Verify it with openpyxl (Annual Summary, Jan to Dec, Holidays, and a hidden Log). Jan `B47` starts with `Transactions this month` and is merged `B47:I47` (not through column S). A `Receipts this month` title sits lower on the sheet, also merged through column I only. The workbook has a Cards sheet and hidden Merchant Map and Statements sheets. Annual Summary `C46` is `v2.0`. Upload that file into `Family Book - Templates` inside the root, replacing an older copy. A new year uses a fresh GitHub download. If GitHub can't be reached, say so and stop. The blank template, and this repo's skill, routine, and doc files, come only from GitHub. Never take those files from the owner's Google Drive, and never treat a copy already in Drive as the source. Reading this family's own receipt files is required, and reading or writing this family's own workbook is required. On Google, list folders with Drive and read and write the sheet with the Sheets connector. On OneDrive, re-download the workbook before a write.

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
2. Make a copy of the template with Annual Summary `F5` set to YYYY. Safest way on the box: open the .xlsx as a zip and replace `<c r="F5" s=".." t="n" />` in `xl/worksheets/sheet1.xml` with the same cell holding `<v>YYYY</v>` (this keeps all formatting). Verify with openpyxl. Leave the hidden Log sheet in place. Leave the Transactions and Receipts sections and Annual Summary `C46` (`v2.0`) in place.
3. Set the currency (skip if CAD): in `xl/styles.xml` replace `[$CAD]` with `[$XXX]` (the user's ISO code) in the number formats, and in `xl/worksheets/sheet1.xml` (Annual Summary) replace the `<t>CAD</t>` label in `C11` with the code. If the currency symbol is not `$` (for example EUR, GBP, CNY), also replace `&quot;$&quot;` with the symbol in the `numFmt` format codes. Rezip with Python (`shutil.make_archive`, no `zip` command needed) and verify the workbook opens with openpyxl and Annual Summary `C11` shows the code.
4. Google: UploadFile into the year folder with name `Family Book - YYYY` and convertToGoogleFormat true. OneDrive: upload `Family Book - YYYY.xlsx` into the year folder. On a shared OneDrive book, re-download immediately before this upload only when you are editing an existing file, not when the file is brand new.
5. Read the file back and confirm the Jan sheet shows dates (Jan 1 has the right weekday). Confirm the Log sheet exists. Try to hide it (section 3b). If it is missing, add it (section 3b). Confirm Jan `B47` starts with `Transactions this month`, the title merge is `B47:I47`, a Receipts section follows it, and Annual Summary `C46` is `v2.0`. If a conversion dropped the list or the marker, or merged the title through column S, follow section 1d for this book only. Day 31 is columns BR and BS.
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

A member's bot does not run the new-year routine and does not create a workbook. It does not create a `Family Book` root and it does not move folders, including when this year's folder now sits inside the owner's root. In December, or when a receipt is dated next year and that book is not in memory, look for a folder named `Family Book - YYYY` that the owner has shared with this user. You may see it only as a shared folder. Save the new folder id, workbook id, and receipts folder id. If the hidden Log is missing, add it (section 3b). Do not insert the receipt list. If it is not there yet, wait. The owner's bot creates it on December 20 inside the same root, and the owner shares that new year folder. Do not create the book yourself. The year folder id already in memory still works after the owner moves that folder. Do not replace it. Do not run the migration. If Annual Summary `C46` is not `v2.0`, the owner's bot will update that book.

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

## 1d. Book version, and migration through v2.0

Annual Summary `B46` says `Book version`. Annual Summary `C46` is the marker.

| `C46` | Meaning |
|---|---|
| `v2.0` | Current. Transactions, Receipts, Cards, and the merchant map are in place. Do not migrate it. |
| `v1.2.4` | The v1.2.4 dedupe fixes are in place. Run the v2.0 half of `family-book-migrate`: copy receipt-list rows into the Receipts section, add the Transactions section, Cards, Merchant Map, and Statements. Do not change amounts. |
| `v1.2.3` or older, or a blank cell | Run the full migration. v1.0 through v1.2.2 are rebuilt, v1.2.3 is patched to the v1.2.4 rules, then the v2.0 half runs. |

On every run, the owner checks `C46` on every year workbook in the `Family Book` root. When a book is not `v2.0`, run the `family-book-migrate` skill once for that book before logging. Download it from `https://raw.githubusercontent.com/Skybatan/family-book/main/bot/skills/family-book-migrate/SKILL.md` when it is not installed. That address stays on `main`. It is the right address after this release is merged. Do not point it at a feature branch. The plan for people is `docs/migration-v2.0.md`. Neither path retypes the number cells. The migration is owner-only, resumable, and safe to run twice. A member never runs it.

A new book made from the v2.0 template already has `C46` = `v2.0`. Do not migrate it.

Also download these skills when they are not installed, from the same `main` raw path: `statement-reader`, `transaction-category`, `expense-category`, and `receipt-match`. They are the four skills that read a statement, categorize a line, categorize receipt items, and link a receipt to a line.

## 2. Sheet layout (every month sheet)

- **Income This Month:** rows 8 to 11. Column B is Item, C is Amount, D is Date Received.
- **Fixed Expenses This Month:** rows 18 to 38. Column B is the pre-set item, C is Amount, D is Date Paid. Row 18 is `Income offset` (enter as a negative number, for example rental income). It is not salary. Salary goes in Income This Month, rows 8 to 11. The other items are GAS, Electricity & Water, RESP, Mobile Phone, Daycare, Rent / Mortgage, Internet, Car Insurance, Property Tax, Fuel / Maintenance, Home Insurance, Car Loan Payment, Housing Management Fee, Term Deposit, Pocket Money, and Savings. Match by reading column B, not by fixed row.
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
- **Below the grid.** Rows 45 and 46 stay empty. Row 47 is `Transactions this month`, merged `B47:I47` only. Row 48 is the header. Rows 49 to 148 are the lines. Row 150 is `Receipts this month`, merged through column I only. Row 151 is that header. Rows 152 onward are receipts. No SUM includes row 45 or below. Columns E and H stay the narrow spacers (Excel width about 1.63; the Sheets connector uses pixels, minimum 20 px, so set E and H to 20 px). Title row height is 40 pt in Excel and 53 px on the connector. Header row height is 32 pt in Excel and 43 px on the connector. Do not write 53 or 43 as points. Amounts and inserted rows use `#,##0.00`. Cards and Statements amount cells use `#,##0.00` too. Only date columns get a date format. The connector cannot read formats, so apply that format when you write an amount. It cannot hide a tab. Do not merge across the freeze at column I, and do not merge a data row. Helper columns start at CA, past day 31 (column BS), so hiding them cannot hide a day. If you cannot hide them, still write them.

Transactions columns: B Card (`CIBC Visa-1001`), C Trans date, D Post date, F Description (as printed, so `T&T` stays `T&T`), G Amount, I Category (`(split)` when a receipt splits it), J Receipt #. Helpers CA–CG: txn key, statement file, FX note, status (`matched`, `no receipt`, `question`, `superseded`), where written, issuer category, linked key.

Receipts columns: B Receipt # (the store's number, or blank), C Store, D Date & time, F Total, G Card/pay (last 4, or `cash`), then Item, Price, Category up to six items starting at column I, and File in column AA. The File cell is one label and one link to the primary file: `photo`, `email`, `statement`, or `text` for a receipt the user pasted as text. Extras are a count, such as `photo +1`. There is no Source column in the Receipts section. Column L is the price of item 2, not a source. Source lives in two places only: Log column A, and the Receipts helper File list (column CB). Entries are joined with `, `. A photo is `photo`. An email is `email gmail/<addr> <msgid>` (Outlook: `email outlook/<addr> <msgid>`). A second photo is `photo, photo`. A near-match question is `open question: candidates <dates>; <source>`. A category question is `open question: category; <source>`. Helpers reuse CA–CG: receipt key, file list, note, status (`pending`, `matched`, `cash`, `question`, `superseded`), where written, return-window days, linked txn key. A receipt with no card is status `cash`.

If a title was placed on a different row, find the cell in column B whose text starts with `Transactions this month` or `Receipts this month`. The header is the next row. Append under the last filled row of that section. Never write a transaction into the Receipts rows.

A spreadsheet cell holds one hyperlink. Column K links to the primary file only. Extra files are not more links in that cell. They are listed in the Log, column F, as `1 photo: <url>, 2 email: <url>`. The Log cell's one hyperlink points at file 1. The other urls are plain text. A single file is `1 photo: <url>`, not a bare file name.

The two sections are how people check a purchase. Statement matching is the receipt-match skill. Do not add an amount that a link already covers.

## 3. Log a receipt or a statement line

Sources: a card statement (PDF, CSV, photo, or pasted HTML or text), a photo or PDF the user sends in chat, a receipt in the `receipts` folder, an order or receipt email, or a bank export when the user sends one. Every bot logs into the same shared book. At the start of the run, the owner follows section 1c once and section 1d once. A member does not.

A statement is read by the statement-reader skill, categorized by the transaction-category skill, and linked by the receipt-match skill. Receipt items are categorized by the expense-category skill. Section 6 is the grid rule. The steps below are the write order for both a receipt and a statement line. Do not write a statement line into the Receipts columns, and do not write a receipt into the Transactions columns. The columns are in section 2.

A statement has no transaction id. Its statement key, which is not the receipt key, is last 4, post date, amount, normalized description, and occurrence number, joined with `|`. The statement-reader skill builds it. A retry finds that statement key on the Log (column P) and does not add the amount again.

1. Read the receipt: merchant, date of purchase, time if shown, line items with prices, subtotal, tax, total, currency, receipt or order number, and card last 4 if shown. Store only the last 4.
2. Pick the month sheet and day from the purchase date. The day's columns are in section 2: day 31 is BR and BS, and any read of the daily block goes through BS. If the date is outside this book's year, use that year's book. An owner may create it (section 1). A member attaches to the one the owner shared (section 1b) and does not create a book. If the date is in the first or last 7 days of the year, also check the adjacent year's Log when that book exists, because rule 2's ±1 day and rule 3's 7 days can cross the year.
3. Categorise. One entry per category; if a receipt spans categories (for example Costco food plus household goods), split the total across categories by line items and spread tax and discounts proportionally so the parts add up to the receipt total. The receipt is still one list row and one Log row.
4. Run "Never log the same purchase twice" before writing any amount. Gather every candidate first. Auto-attach only when there is exactly one candidate. With two or more, ask the one question that lists them all and wait. On a near match, write or join the Status `question` row and wait. Do not choose an amount cell and do not write a category amount while that question is open. A statement whose totals fail is not written. The statement-reader skill has already saved that file with a ` - not imported` suffix and a Log row that records the reason.
5. **Append a pending Log row with the target cell already in Where written.** Do this only for a new purchase, including a question the user answered no. This is one write, before the amount. In that category block for that day, the target is the first empty amount cell. Meals is rows 6-16 and Household Goods is rows 22-27. The amount cell is the day's amount column, not the item column: day 1 is `Oct!K6`, not `Oct!J6`. A split receipt lists every cell, for example `Oct!K6+Oct!K22`. If every row in the block is used, the target is an existing amount that will become a formula, recorded as `Oct!K16 was =12.50; write =12.50+8.20`. Status is `pending`. Fill Date, Merchant, Total, Receipt/order #, Date & time, Items, Payment, Source, and Where written in that same row. Leave Saved file, Content hash, and Month list row blank. The receipt key is the one defined in the dedupe section. If a `pending` row for this receipt key is already there, resume it through these write steps. Do not append another row, and do not treat that pending row as a rule 2 match. If its Where written already names a cell, keep that cell. If its Where written is blank, search before using an empty cell. In that day's category block, an amount cell matches when it already holds this receipt's amount and the item text beside it contains the short store name. `Costco (Mom) milk` contains `Costco`. A split receipt checks every item cell and records every matching cell, for example `Oct!K6+Oct!K22`. The same search covers a Fixed Expenses row (amount in column C, label in column B) and an Income This Month row (rows 8 to 11). If a match is found, record it in Where written and write nothing. Only if none is found, use the first empty amount cell in that block, record it, and write the amount in step 6. Food Basics 19.31 already in `Nov!S6`, with item text that contains `Food Basics`, is recorded as `Nov!S6`. Do not write 19.31 into the empty `Nov!S7`.
6. **Write the amount into the cell named in Where written.** Do this only when Status is `pending` and Where written names the cell. Read that cell. If it is still empty, or it still holds the old formula recorded on the row, write once. Put the Item, in the item column beside that amount cell, as the short merchant name (for example `Costco`, `Amazon`, `Home Depot`). If a display name is saved, add it in parentheses, for example `Costco (Mom)`. A short note in the language you are using with the user can follow, for example `Costco (Mom) milk and paper towels`. Put the Amount as a number, or as the planned formula. If the cell already shows this merchant and this amount, or it already holds the planned formula, leave it. Do not look for the next empty row of that category block. The file name does not include the person's name.
7. Refunds and returns: a negative amount in the original category, or row 43 if it is new money. A receipt for a return is its own Receipts row. A negative statement line is its own Transactions row and links to the earlier purchase on the same card with the same merchant and the opposite amount (section 6). Do not delete the purchase, and do not add the return as a second copy of that purchase. Before a return lookup says a window is still open, check for that negative line. If it is already there, say the item was already refunded on that line's post date.
8. Recurring bills (hydro, phone, internet, insurance, mortgage) go in Fixed Expenses for that month, not the Daily Record. Salary and other income go in Income This Month (rows 8 to 11), and only after the user confirms a new payee (section 6). They do not go on Fixed Expenses row 18. They get a section row and a Log row too. The same order applies: the pending row already names the cell, then write it.
9. **Then save the file.** This is the same step the receipt-match skill calls step 9. Save a copy of a photo or email receipt in the shared `receipts` folder, named as in section 3c (for example `2026-10-15 1432 - Costco - 57.29.png`). A pasted text receipt uses the File label `text` and the same name with a `.txt` extension. A statement's original bytes were already copied before parsing, under `Family Book - {statement year}/statements/{Issuer Product}-{last4}/YYYY-MM-DD statement.ext`. This step records that path. Skip the upload when section 3c says this file is already there. If that exact name is already used by a different file, the new name is `YYYY-MM-DD HHMM - Store - TOTAL - 2.ext`, then ` - 3`. Example: `2026-10-15 1432 - Costco - 57.29 - 2.png`. A statement for the same card and the same statement date does not use `statement - 2`. The same hash is a no-op, and different content asks. Then fill Saved file and Content hash. A photo or email receipt is not finished until its file is saved there. A bill the user dictates with no document can have a blank File and Source `note`. See section 3a for email receipts.
10. **Then the section row.** Append it only when Month list row (Log column M) is blank, then write that cell address into Month list row. A receipt's address is the Receipt # cell in the Receipts section, for example `Oct!B152`. A statement line's address is the Card cell in the Transactions section, for example `Oct!B49`. Write the Receipts or Transactions columns from section 2. Do not write a Source into Receipts column L: that column is an item price. Sources stay on the Log (column A) and in the Receipts helper File list (column CB). If the file could not be saved, leave Status `pending` and do not finish the row. On the next attempt, start at step 4. If Where written names a cell, read that cell and do not write the amount again. If Where written is blank, step 5 searches that day's category block, including each item cell of a split and a Fixed Expenses or Income row, for this amount and item text that contains the short store name. Record that cell and write nothing when it is already there. Only if none is found, use the first empty cell. Finish the file and the section row.
11. **Then set the finished status.** Do this only after the amount is committed (Where written is a cell, or this is a note whose amount cell is filled), the file is saved or this is a dictated note with no document, and the section row is filled. The order is append the pending row with the target cell, write the amount, then the file (step 9), then the section row, then this status. Log column N:
    - `awaiting statement` for a card receipt that is in the grid and not yet linked. The Receipts helper Status (column CD) is `pending`.
    - `cash` for a receipt with no card, and for a receipt the user paid in cash. The Receipts helper Status is `cash`. Card/pay is `cash`.
    - `no receipt` for a statement line with no receipt. The Transactions helper Status is `no receipt`.
    - `matched` when a receipt and a statement line are linked. Both helper Status cells are `matched`.
    - `question` stays `question` until the user answers. Where written stays blank and the grid gets nothing.
    - `superseded` for a confirmed duplicate. The row stays.
    An older book may still say `done` on a finished receipt row. Treat `done` as finished. Do not rewrite it to `awaiting statement` during an ordinary log. The migration does that copy. A member who must not create a missing section sets the finished status without one and says once that the owner's bot will add the section row.
12. Tell the user, in the language they are writing in, what was logged in one or two lines (merchant, date, total, category split, and who logged it when a name is saved). If the amount or category was a guess, say so and ask. If the purchase was already there, say that the file was attached and the total was not added again.

## 3a. Save an email receipt as a file (required for every email receipt)

1. Use the original merchant email, not a forward, when both exist. If the email has a PDF receipt or invoice attachment, download that (DownloadFile) and save it as is.
2. Otherwise render the email's HTML body on the box:
   - Write the `htmlBody` from the mail connector's get_message to `receipt.html`.
   - Long one-page image (best for app-style receipts like Costco.ca or Amazon): `google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=800,4000 --virtual-time-budget=8000 --screenshot=out.png file:///path/receipt.html`, then crop the empty bottom with Pillow (find the content bounding box against the background colour). Raise the window height if the content reaches the bottom.
   - PDF (best for text-style till receipts like Home Depot): `google-chrome --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf=out.pdf file:///path/receipt.html`.
3. Look at the result (open the image, or `pdftotext` the PDF) and confirm the merchant, date, and total are visible before uploading.
4. Upload to the year's shared `receipts` folder (Google: UploadFile with the folder id; OneDrive: UploadFile with overwrite false) only when section 3c says the file is not already there. Name the file as in section 3c. The Log's Saved file column stores `1 photo: <url>` (or `email` or `statement`), and column O stores the SHA-256. Column O is the primary check that this file was already saved. Reading this file back from the family's own Drive or OneDrive is required. That is not a download of the template.
5. If rendering fails, save a plain-text summary of the receipt (merchant, date, time, order number, line items, tax, total, card last 4) as a `.txt` with the same file-name pattern, and mention it in the report.

## 3b. Log tab and month list

Dedupe is the hidden `Log` sheet, one active row per purchase, shared by every bot. A superseded row stays on the sheet and is ignored when matching. The Transactions section and the Receipts section are the same rows for people to read. Do not keep a second dedupe list in memory. If the Log and a section disagree, the Log wins for "already counted". Repair the section by adding or filling the row. Do not change number cells to force them to agree.

If the open book has no `Log` sheet, add one before logging, with the header below, and try to hide it. Excel: add the sheet with openpyxl, set its state to hidden, and re-upload. Google Sheets: add the sheet with the Sheets connector and write the header. The Sheets connector has no hide-tab tool. Try to hide the Log tab if the tool you have can hide a sheet. If you cannot, ask the user once, in the language of the chat, to right-click the Log tab and choose Hide sheet. In English: "Please hide the Log tab: right-click it and choose Hide sheet. I can't hide a tab from here, and I'll keep going either way." Never fail setup, logging, or migration because the tab is still visible. Do not ask again for that book. On OneDrive, re-download the workbook immediately before this write. A member may add that sheet so they can dedupe. A member does not insert the month receipt list and does not write `C46`. If the list header is missing, choose the amount cell, record it on the pending Log row, then write that cell, and say once that the owner's bot will add the month list. A retry reads the recorded cell.

The owner adds a missing Log before logging, but a missing Transactions or Receipts section on an older book is the migration (section 1d), not an ad-hoc insert during a single receipt. On a v2.0 book both sections are already there. A v1.2.3 or v1.2.4 book still needs the migration before logging.

Log header, row 1. `H1` is the book note. Do not replace it, and do not write an amount in column H. Column H on a question row is the notes column: the transaction dates in that question, as in the dedupe section.

| Column | Header | Write |
|---|---|---|
| A | Source | Entries joined with `, `. A photo is `photo`. An email is `email gmail/<addr> <msgid>`, or `email outlook/<addr> <msgid>`. A second photo is `photo, photo`. A photo plus that Gmail is `photo, email gmail/family@example.com 18c3fab`. A near-match question is `open question: candidates <dates>; <source>`. A category question is `open question: category; <source>`. The same text is copied to Receipts helper column CB. |
| B | Date | Purchase date as text `YYYY-MM-DD`. |
| C | Merchant | Consistent merchant name, with no person's name. |
| D | Total | Receipt total as a number. Negative for a return. |
| E | Where written | The target amount cells, written on the pending row before the amount. For example `Oct!K6`, `Oct!K6+Oct!K22`, or `Oct!K16 was =12.50; write =12.50+8.20`. An old row may still say `Oct Fixed Expenses / GAS`. Blank on a `question` row. If a `pending` row has this blank, search that day's category block, each item cell of a split, and Fixed Expenses or Income rows, for a cell that already holds this amount and whose text contains the short store name (`Costco (Mom) milk` contains `Costco`). Record that cell and write nothing. Only if none is found, use the first empty cell. |
| F | Saved file | Every file, one shape even when there is only one: `1 photo: <url>`, or `1 photo: <url>, 2 email: <url>`. The cell links to file 1. Blank until the file is in `receipts`. |
| G | Logged by | The display name from memory, or blank. |
| H | Notes | The book note stays in `H1`. On a question row, the same candidate dates as Source, for example `2026-10-10; candidates 2026-10-11, 2026-10-03`. A later receipt adds its date to that list, for example `2026-10-10; candidates 2026-10-11, 2026-10-03, 2026-10-04`. No amounts. |
| I | Receipt/order # | The number, or blank. `separate` when the user confirmed a second purchase. Fill this when a later copy has a number and this cell is blank. |
| J | Date & time | `YYYY-MM-DD HH:MM`, or the date alone. The receipt's transaction date wins over the email's sent date. |
| K | Items | `product: price; product: price`. |
| L | Payment | Last 4 digits, or blank. |
| M | Month list row | The Date & time cell of this purchase, for example `Oct!B49`. |
| N | Status | `pending` once the amount cell is recorded and before the row is finished. `question` for an open yes/no, with nothing written into a category cell. After the row is finished: `awaiting statement` (card receipt, not yet linked), `cash`, `no receipt` (statement line with no receipt), `matched` (receipt and statement linked), or `done` on a row migrated from an older book. `refused` when a statement's totals do not match and nothing was written. `superseded` for a confirmed duplicate or an answered question. A superseded row stays. Do not delete it. Matching ignores `superseded` rows. A retry that finds a finished status does not write the amount again. |
| O | Content hash | SHA-256 hex of each saved file, in the same order as column F: `1 <64 hex chars>`, or `1 <hex>, 2 <hex>`. |
| P | Txn key | `last4\|YYYY-MM-DD\|amount\|NORMALIZED DESCRIPTION\|occurrence`. Blank on a receipt that has no statement line yet. |
| Q | Card | Card label, such as `CIBC Visa-1001`. |
| R | Post date | Post date `YYYY-MM-DD`. The month sheet is chosen from the transaction date, not from this date. |
| S | FX note | Foreign-currency detail, or blank. |
| T | Linked to | The other side: a receipt number, or the purchase's txn key for a return. |
| U | Statement file | Path of the statement file. |
| V | Section row | The Transactions or Receipts cell, the same address as column M. |

Section columns are in section 2. Where written uses the amount cells, for example `Sep!AW6+Sep!AW22`. The visible Category column on a Transactions row is `(split)` when a receipt splits the amount.

The order is the one in section 3. First append one Status `pending` row with the target cell already in Where written. Read the Log once more immediately before that append, so a row another bot just wrote is not duplicated. On OneDrive that read is a fresh download of the workbook, and the upload follows immediately. Second, write the amount into that cell. Third, save the file (section 3 step 9). Fourth, write the section row. Fifth, set the finished status from step 11 (`awaiting statement`, `cash`, `no receipt`, or `matched`). A retry that finds a cell in Where written reads that cell. If it is still empty, or it still holds the old formula recorded on the row, write once. If it already shows this amount or the planned formula, leave it. A `pending` row whose Where written is blank uses one rule. Search that day's category block for an amount cell that already holds this receipt's amount and whose item text contains the short store name. A split receipt checks every item cell. Fixed Expenses and Income rows are included. If one is found, record it in Where written and write nothing. Only if none is found, use the first empty amount cell in that block and write the amount there once. Do not write the amount again into a later empty cell. A `pending` row with the same receipt key is this resume, not a rule 2 match. Do not create a second row. Do not delete a Log row.

A `pending` row with no Saved file, for a photo or email receipt, is not finished. Save the missing file in `receipts`, then fill Saved file, Content hash, and the File cell. Do not write the amount a second time. Set the finished status from step 11 only when those pieces are in place.

A question row looks like this. Nothing else is filled, and the grid has no amount from it:

| Column | Header | Value |
|---|---|---|
| A | Source | `open question: candidates 2026-10-11, 2026-10-03; photo` |
| B | Date | `2026-10-10` |
| C | Merchant | `Costco` |
| D | Total | `57.29` |
| E | Where written | blank |
| F | Saved file | `1 photo: <url>` once the file is in `receipts`, otherwise blank |
| H | Notes | `2026-10-10; candidates 2026-10-11, 2026-10-03` |
| I | Receipt/order # | blank |
| M | Month list row | blank |
| N | Status | `question` |
| V | Section row | blank |

The Transactions section may show that same 57.29 on its own row, with helper Status `question` and Where written blank, because that section is not in any total. The grid gets nothing until the user answers.

## 3c. File names

`YYYY-MM-DD HHMM - Store - TOTAL.ext`

Examples: `2026-10-15 1432 - Costco - 57.29.png`, `2026-10-15 - Costco - 57.29.pdf` when the time is unknown, `2026-10-20 0910 - Home Depot - -84.12.pdf` for a return. `Costco.ca` is `Costco` in the file name.

- `HHMM` is 24-hour, four digits, no colon. Omit the time, including the space before the first ` - `, when it is unknown.
- Store is the short merchant name from the dedupe section, with no person's name and no website. `Costco.ca` and `Costco Wholesale` are `Costco`.
- TOTAL is the receipt total with two decimals.
- The date in the name is the receipt's transaction date, not the email's sent date.
- Strip `/ \ : * ? " < > |` and control characters. Collapse spaces. Trim spaces and dots from the ends of each part.
- The details (line items, receipt number, card last 4, who logged it) live on the sheet, not in the file name.
- Before uploading, hash the bytes with SHA-256. Log column O is the primary check, including after the file was renamed. If column O already has that hash, this is the same file sent again: do not upload a second copy and do not add a suffix. If column O is blank and the file is already in `receipts`, hash that saved file now, write column O, and then do the same check. If the file is missing, the receipt key defined above (the short store name, the transaction date, and the total to the cent) is the purchase. A row with that key is the same purchase: save the file onto that row once the bytes are in hand, and do not add a second amount or a ` - 2` name. If both sides have receipt numbers and the numbers differ, they are still different purchases. Name plus size is only a fallback, and only when the bytes cannot be hashed. Then the same file is one already in `receipts` with the same normalized name and the same byte size. The same name includes the extension, compared without case. `57.29.png` and `57.29.pdf` are different names. That fallback misses a renamed copy, which is why the hash is checked first.
- Add ` - #receiptno` or, if there is no number, ` - ` plus a short item hint, only when a different file (a different hash) would otherwise take a name the folder already has. If it still collides, the suffix sits after the total and before the extension: `YYYY-MM-DD HHMM - Store - TOTAL - 2.ext`, then ` - 3`. Example: `2026-10-15 1432 - Costco - 57.29 - 2.png`. A re-sent file, including one whose name changed, is not a collision when the hash matches.
- Do not rename a file that already matches this pattern. On a match, files keep their own names. Do not rename a file to a time it does not show, and do not rename a file to a name that already exists. Only the kept Log row's Date and Date & time change.

## 4. Scan email for receipts

The owner follows section 1c and section 1d once before searching. A member skips both.

At the start of every scan, check Gmail and Outlook again (GetMcpServerStatus or GetDynamicTools). Scan every account that is `ready`, including an account connected after setup (section 0a). If a new one is `ready`, include it and say so in one line. If none is `ready`, stop and do not ask them to connect email.

1. Search since the last scan. The first scan of an inbox is the last 30 days. Say that older receipts from this year can be backfilled on request. A good starting Gmail query: `(subject:(receipt OR order OR invoice OR "your order" OR purchase OR statement) OR from:(amazon OR homedepot OR costco OR walmart OR bestbuy OR apple OR uber OR doordash)) -subject:(shipped OR delivered OR "out for delivery")`, and adapt it to the user's merchants. For Outlook use the matching search. Keep a shipping or receipt email when it carries an order number you may already have logged: that is one purchase under rule 1, and the file gets attached instead of skipped as a duplicate amount. Skip marketing. Skip a pure shipping notice that has no order number and no total. An issuer email whose subject says the statement is ready is not a receipt. Hand it to the statement-ready routine. Do not log it as a purchase.
2. Use the order confirmation or the final invoice as the source of truth for a new purchase. A later email with the same order number is the same purchase.
3. Log each receipt as in section 3. Gather every candidate before any amount. Auto-attach only when there is exactly one candidate. Two or more candidates are one digest question that lists every one of them, with no amount written. A single rule 3 candidate is one yes/no. For a new purchase, append the pending Log row with the target cell in Where written, then write the amount, then the file (section 3 step 9), then the Receipts or Transactions row, then the finished status. A retry reads that cell. A pending row with the same receipt key is resumed here and is not a rule 2 candidate. A pending row with a blank Where written searches that day's category block, including each item cell of a split and Fixed Expenses or Income rows, for this amount and item text that contains the short store name. If that cell is found, record it and write nothing. Only if none is found, use the first empty cell. Always save the receipt file in the shared `receipts` folder as in section 3a and name it as in section 3c, unless the SHA-256 in Log column O says that file is already there. If column O is blank, hash the saved file first. If that file is missing, use the store, date, and total key.
4. Never reply to, forward, or send email while doing this; it is read-only.
5. Report a short digest in the language the user writes in, or the Grok Bot app or system language when nobody has just written: how many were found, what was logged, what was attached to an existing purchase, who logged it when a name is saved, any near-match question, and anything unclear.

## 5. Writing tools

- Google Sheets connector: write values to `'<Mon>'!<cell>` ranges. Read the target range first so you never overwrite. A daily read includes every day column through BS. Google Sheets is the right store when several bots write, because editors can update the same spreadsheet together. Try to hide the Log, Merchant Map, and Statements sheets (section 7). If you cannot, ask once and keep going. Do not write Transactions or Receipts rows into rows 1 to 44. Append a Transactions row under the last filled row of that section, and a Receipts row under the last filled row of the Receipts section. When you write an amount, or insert a Transactions or Receipts row, set the amount cells to `#,##0.00`. Cards and Statements amount cells use `#,##0.00` too. The grid shows two decimals. Only a date column gets a date format (`YYYY-MM-DD`): Trans date, Post date, Date received, Date paid, and the statement dates. Do not put a date format on an amount. 65 in an amount cell is 65.00, not 1900-03-05. Day-of-month headers stay day numbers.
- The blank template and this repo's skill, routine, and doc files come only from GitHub (section 0). Never download or export those files from the owner's Google Drive. A family's own bot reading that family's own receipt files is required, and so is reading the workbook. If Sheets is not `ready`, connect it (section 0 or 0a) and write the sheet with the Sheets connector. Do not export the Google Sheet to get a copy of the template.
- OneDrive or Excel Online: two bots editing the same .xlsx can overwrite each other. Re-download the workbook right before every write, edit that fresh copy, and upload it immediately with overwrite true. Do not write from a copy downloaded earlier in the turn. Check that the file is not open for editing elsewhere. Prefer Google when more than one person logs receipts. That workbook download is the family's own file. It is not a download of the template.

## 6. Statements, the grid, cards, and banks

Read a statement with the statement-reader skill. Categorize a line with the transaction-category skill. Categorize receipt items with the expense-category skill. Link and dedupe with the receipt-match skill. Then write with the order in section 3.

The grid is filled from the two sections, once:

- A transaction with a receipt uses the receipt's item split.
- A transaction with no receipt uses its category for the whole amount.
- A cash receipt fills the grid by itself.
- A card receipt that arrives first is Receipts Status `pending` and already in the grid. When the statement line arrives, link it. Do not add the amount again.

Save the statement file before parsing. The file and the Statements row go in the book for the statement date's year: `Family Book - {year}/statements/{Issuer Product}-{last4}/YYYY-MM-DD statement.ext`. Each transaction is written in the book for its post date's year. When the purchase date and the post date are in the same year, the month sheet and the day column are the purchase date. When they are not, the line goes on the post date's month and day in the post-date year's book, and the Trans date column still shows the purchase date. A January 19, 2026 statement keeps its file and its Statements row in the 2026 book. A line that posts on December 30, 2025 is written in the 2025 book. A December 31 purchase that posts on January 2, 2026 is written in the 2026 book on the January sheet. If that year's book does not exist yet, ask once, in the language of the chat: "The 2027 book is not here yet. Should I create it?" Use the real year. Do not ask again. Do not write those lines until the book exists. Save a receipt as `YYYY-MM-DD HHMM - Store - TOTAL.ext` in `receipts`.

### Cards and statement bills

The Cards sheet shows the latest statement for each card. Row 1 note, row 2 headers, data from row 3: Issuer, Product, Last 4, Holder, Statement day, Due day, Last amount due, Paid status, then the label, the last statement date, the period, the minimum, the file, Account cards, and Credit. Account cards lists every card on that account, for example `1001, 1002`. Holder is filled only when the statement prints a name on the same line as that card's number. A `Prepared for` line does not fill it. Otherwise leave Holder blank. Learn a card from the first statement when the user did not name it. A newer statement updates that card row. It does not erase an older unpaid bill. Credit is an overpayment. It does not go negative.

The hidden Statements sheet is the bill ledger. A row is added only for a statement that has an amount due. A partial or mid-month CSV does not add one. Statement id is `{Issuer Product}-{last4 of the account's first card}-{statement date}`, for example `CIBC Visa-1001-2026-09-27`. The other columns are Issuer, Product, Last 4s, Period start, Period end, Statement date, Due date (the full date), Minimum, Amount due, Amount remaining, File, Paid status. The same statement key or the same file hash is a no-op. Different content for the same card and statement date asks which file to keep. Do not save that second file as `statement - 2`. Amount remaining starts as the amount due.

A card payment is a Transactions row with category `Card payment` and a generated key. It is not a grid expense. It applies to the latest statement for that card dated on or before the payment's post date. Paying that bill in full also marks every older unpaid bill for the card paid, because the balance carries forward. A partial payment reduces only that latest bill and leaves it `unpaid`. Any overpayment is a credit on Cards. Remaining and credit never go negative. A payment with no eligible bill changes nothing and does not invent a credit. The user saying a bill is paid sets that statement's Paid status to `paid`. Cards Paid status follows the latest statement only. Importing the same bank file again does not pay a bill twice. The bank file is one Log row with its SHA-256.

### Bank accounts are optional

Card statements are enough. With no bank file, the book tracks expenses only. Do not ask for a bank account during setup.

When the user does send bank transactions:

- Every bank line is a Transactions row with a generated key. The categories are `Income`, `Mortgage`, `Transfer`, `Card payment`, and `Fixed expense`.
- A mortgage debit is category `Mortgage`. The grid still uses the Rent/Mortgage row, and the amount in column C is positive.
- Another recurring debit (property tax, utilities, phone, internet, insurance) is category `Fixed expense`. It goes to Fixed Expenses This Month. The amount in column C is positive.
- A deposit (payroll or other) is category `Income` only after the user confirms that payee. It fills an Income row (rows 8 to 11). Remember a yes on the merchant map as Income so the next month does not ask. Do not write it on row 18.
- A transfer between the user's own accounts is category `Transfer`. It is not an expense and not income.
- A card payment is category `Card payment`. It uses the payment rule above. It is not a grid amount.

### Returns

A negative statement line links to the earlier purchase on the same card with the same merchant and the opposite amount. The grid gets the negative amount. Do not delete the purchase.

### Return lookup

When the user sends a photo of a product or a tag, search the Receipts section for the item name, brand, SKU, and store. Also search Transactions for a negative line or credit on that card, for that store, for the same amount. If a receipt exists and that refund is already there, say it was already refunded on that line's post date, and do not quote a window. If there is no Receipts row, show the matching Transactions line (store, date, price, and card) and say no receipt is saved. If that line has a matching refund, also say it was already refunded on the refund's post date. Otherwise reply with the receipt file, the store, the date, the price, the card, and the days left in the return window. The window is the number of days from the purchase date. Use the store's policy when it is known: Sport Chek 30 days, Costco 90, Home Depot 90, Walmart 90, Canadian Tire 90. Any other store uses 30 days. Say the window is an estimate either way. A return receipt, one with a negative total, has no window. Do not quote days left for it.

### Reminders

The card-due-reminder routine reads every unpaid row on the Statements sheet whose due date has not passed. It uses that row's full due date and the amount still owed. It does not use the due day on Cards. The sentence ends with a period, for example `Pay CIBC Visa-1001 495.79 by 2026-10-19.` The statement-ready routine sends one nudge per account, not per card, on that account's statement cycle date, and a second three days later even when that day is in the next month, then stops for that cycle once that cycle's statement is imported. An authorized-user card does not get its own nudge. A new year copies the Cards rows and the Merchant Map into the new book. It does not copy transactions.

## 7. Connector limits

The Sheets connector can freeze rows and columns, and it can set a dropdown. Freeze every month sheet at J6, and freeze Cards at A3 (the first two rows). Set the Paid status column to a dropdown of unpaid, paid. It has no tool that hides a tab, and it cannot read a cell's format. Ask the owner once: please hide the Log, Merchant Map, and Statements tabs. Then keep going. That is not a failure. Always apply the title, header, column width, and amount formats in section 2. Sizes the connector accepts are pixels: title row 53 px, header row 43 px, columns E and H 20 px. Excel uses 40 pt, 32 pt, and width 1.63. Do not merge a range that includes a column at or before I and a column at or after J. Columns A:I are frozen. Helper columns are CA onward on a standard sheet, or the seven columns after the last used column when the sheet already uses column 72 or 73. Never store more than the last 4 digits of a card or account.

Made by SkybatanX (@SkyXFunNext).
