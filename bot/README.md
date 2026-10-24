# Family Book bot files

These files are what a Grok Bot needs to run Family Book. The published Grok Bot template is thin. It does not keep its own copy of the rules. On first use, its family-book skill downloads [bot/skills/family-book/SKILL.md](skills/family-book/SKILL.md) from this repo, and [getting-started.md](getting-started.md) pulls the routines, [memory.md](memory.md), and the local writer from here. Changes pushed to this repo reach new users the next time a bot sets up.

| File | Role |
|---|---|
| [getting-started.md](getting-started.md) | First chat: download the latest files, then ask only where to save receipts and the report. Statements are not part of setup. |
| [memory.md](memory.md) | Conventions saved to the bot's memory: owner or member, storage, statement features, the root folder or the local path, and what stays English. There is no language setting. |
| [skills/family-book/SKILL.md](skills/family-book/SKILL.md) | The family-book skill: receipts-first setup, the year's book, statements when the user adds them, local Excel, and the rule that the same purchase is never logged twice. |
| [skills/family-book-getting-started/SKILL.md](skills/family-book-getting-started/SKILL.md) | The setup skill. One storage question: Google Sheets, Excel Online, or a local Excel file. The first receipt can be logged in that same conversation. |
| [skills/family-book-migrate/SKILL.md](skills/family-book-migrate/SKILL.md) | Update for books from v1.0 through v2.0. The target is v2.1. A v2.0 book only gains statement-feature settings. Older books finish the v2.0 sections first. Amounts are not retyped. |
| [skills/statement-reader/SKILL.md](skills/statement-reader/SKILL.md) | Read a PDF, CSV, photo, or pasted statement into lines and metadata. Check the per-card total before writing. |
| [skills/transaction-category/SKILL.md](skills/transaction-category/SKILL.md) | Categorize a statement line from the learned map, merchant patterns, and the issuer spend category. |
| [skills/expense-category/SKILL.md](skills/expense-category/SKILL.md) | Categorize receipt items and spread tax so the parts add up to the total. |
| [skills/receipt-match/SKILL.md](skills/receipt-match/SKILL.md) | Link a receipt to a statement line, and dedupe a photo against an email. |
| [local/bookio.py](local/bookio.py) | Writes a local `.xlsx` on the bot's computer with openpyxl. Does not start Excel. Same receipt key and layout as the cloud books. |
| [local/queue.py](local/queue.py) | Bot-side queue for a computer that is off, asleep, or has the file locked. One row per receipt key. Never uploaded to GitHub. |
| [routines/daily-receipt-scan.md](routines/daily-receipt-scan.md) | Daily email receipt scan of every ready Gmail and Outlook account. While statement features are off, a statement email is not imported. The owner's bot runs the v2.1 migration when the book is older, before it logs. |
| [routines/spending-report.md](routines/spending-report.md) | Weekly, monthly, and yearly category totals plus one advice sentence, sent in chat. Created at setup. It does not wait for a statement and it does not open Excel. |
| [routines/card-due-reminder.md](routines/card-due-reminder.md) | Three days before a card's due date, and on the due date, unless that bill is paid. Created only after statement features are on. While they are off, the routine sends nothing. |
| [routines/statement-ready.md](routines/statement-ready.md) | Nudge when an issuer email says the statement is ready, or three days after the usual statement day. Created only after statement features are on. While they are off, the routine sends nothing. |
| [routines/new-year-book.md](routines/new-year-book.md) | December 20 at 9:00 AM, on the owner's bot only: refresh the skills from this repo, create next year's book, and carry Cards, the Merchant Map, and the statement-feature cells. Do not copy transactions. |

The workbook stays at [template/family-book-template.xlsx](../template/family-book-template.xlsx). Sheet names, category labels, section headers, and receipt file names stay English. Translated templates (for example `template/family-book-template-fr.xlsx`) may be added later on request. The bot replies in the language the user writes in, with no language question at setup. Older books are updated by [skills/family-book-migrate/SKILL.md](skills/family-book-migrate/SKILL.md). The plans are [docs/migration-v2.0.md](../docs/migration-v2.0.md) and [docs/migration-v2.1.md](../docs/migration-v2.1.md). Local Excel is [docs/local-excel.md](../docs/local-excel.md).
