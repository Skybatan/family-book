# Bot memory: Family Book conventions

Generic facts for the bot's memory. User-specific values (storage type, folder and workbook ids, receipts folder id, inboxes to scan, currency, holiday region, language) are added at setup and never stored in this repo.

- Language: at setup, ask which language to use, guessing from the language they write in, and save it. Chat, item notes and descriptions in the book, holiday descriptions, and digests are in that language. These stay English on purpose: the workbook template's sheet names, category labels and notes, receipt file names (`YYYY-MM-DD Merchant Total.ext`), and this repo's skill, routine, and doc files. Translated templates (for example `template/family-book-template-fr.xlsx`) may be added later on request.
- Every receipt gets a saved file in that year's `receipts` folder, named `YYYY-MM-DD Merchant Total.ext`. A receipt does not count as logged until its file is saved.
- Email is read-only: never send, reply to, forward, label, or delete email.
- Keep a dedupe log (source message id or file name, date, merchant, total, where it was written, saved file name) and skip anything already in it.
- Use the `family-book` skill for setup and logging. The template lives at https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx.
- Use consistent merchant names (for example `Costco`, `Amazon`, `Home Depot`).
- If an amount or category is a guess, say so and ask.
