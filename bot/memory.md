# Bot memory: Family Book conventions

Generic facts for the bot's memory. User-specific values (storage type, folder and workbook ids, receipts folder id, inboxes to scan, currency, holiday region) are added at setup and never stored in this repo.

- Always write in English: chat replies, sheet entries, holiday descriptions, and receipt file names.
- Every receipt gets a saved file in that year's `receipts` folder, named `YYYY-MM-DD Merchant Total.ext`. A receipt does not count as logged until its file is saved.
- Email is read-only: never send, reply to, forward, label, or delete email.
- Keep a dedupe log (source message id or file name, date, merchant, total, where it was written, saved file name) and skip anything already in it.
- Use the `family-book` skill for setup and logging. The template lives at https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx.
- Use consistent merchant names (for example `Costco`, `Amazon`, `Home Depot`).
- If an amount or category is a guess, say so and ask.
