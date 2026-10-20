# Bot memory: Family Book conventions

Generic facts for the bot's memory. User-specific values (storage type, role as owner or member, display name, folder and workbook ids, receipts folder id, inboxes to scan, currency, holiday region) are added at setup and never stored in this repo.

- Language: do not ask which language to use, and do not save one. Chat, item notes and descriptions in the book, holiday descriptions, and digests follow the language the user is writing in. When a routine runs and nobody has just written, use the Grok Bot app or system language. These stay English on purpose: the workbook template's sheet names, category labels and notes, receipt file names (`YYYY-MM-DD Merchant Total.ext`), and this repo's skill, routine, and doc files. Translated templates (for example `template/family-book-template-fr.xlsx`) may be added later on request.
- Role: `owner` if this bot started the book, `member` if it joined a book someone else started. Only the owner's bot runs the new-year routine. A member's bot attaches to the new year's book in December and never creates one.
- Display name: saved when they give one. Setup asks for it when they join, or when they say other people will log too. Item notes then include it, for example `Costco (Mom)`. If there is no name, use the merchant alone. If they tell you a name later, save it and use it from then on.
- Every receipt gets a saved file in the shared `receipts` folder for that year, named `YYYY-MM-DD Merchant Total.ext`. A receipt does not count as logged until its file is saved there.
- Email is read-only: never send, reply to, forward, label, or delete email.
- Dedupe lives in the workbook's hidden `Log` tab, not in this bot's memory. Before logging, read that tab and skip a receipt whose source (message id, order number, or file name) is already there, or whose date, merchant, and total already match a row. Write the Log row only after the receipt file is saved. Several bots share this one tab so the same receipt is never logged twice.
- On OneDrive, re-download the workbook right before every write and upload it immediately afterward, so another member's edits are not overwritten. Google Sheets is the better shared book, because several editors can write at the same time.
- Use the `family-book` skill for setup and logging. The template lives at https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx.
- Use consistent merchant names (for example `Costco`, `Amazon`, `Home Depot`).
- If an amount or category is a guess, say so and ask.
