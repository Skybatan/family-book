# Family Book bot files

These files are what a Grok Bot needs to run Family Book. The published Grok Bot template is thin. It does not keep its own copy of the rules. On first use, its family-book skill downloads [bot/skills/family-book/SKILL.md](skills/family-book/SKILL.md) from this repo, and [getting-started.md](getting-started.md) pulls the routines and [memory.md](memory.md) from here. Changes pushed to this repo reach new users the next time a bot sets up.

| File | Role |
|---|---|
| [getting-started.md](getting-started.md) | First chat: download the latest files, check which services are already connected, and skip service questions when Google Drive or OneDrive is ready. Basic connect setup happens only when no store is connected. Currency and holiday region are inferred and confirmed in one line. The owner gets a `Family Book` root folder, with the year folder inside it. |
| [memory.md](memory.md) | Conventions saved to the bot's memory: owner or member, the root folder, the shared book, and what stays English. There is no language setting. |
| [skills/family-book/SKILL.md](skills/family-book/SKILL.md) | The family-book skill: detect-first setup, the cards question after the book exists, the root folder, the year's book, statements, receipts, and the rule that the same purchase is never logged twice. |
| [skills/family-book-migrate/SKILL.md](skills/family-book-migrate/SKILL.md) | Update for books from v1.0 through v1.2.4. The target is v2.0. A v1.2.4 book only gains the new sections. Older books finish the v1.2.4 checkpoint first. Amounts are not retyped. |
| [skills/statement-reader/SKILL.md](skills/statement-reader/SKILL.md) | Read a PDF, CSV, photo, or pasted statement into lines and metadata. Check the per-card total before writing. |
| [skills/transaction-category/SKILL.md](skills/transaction-category/SKILL.md) | Categorize a statement line from the learned map, merchant patterns, and the issuer spend category. |
| [skills/expense-category/SKILL.md](skills/expense-category/SKILL.md) | Categorize receipt items and spread tax so the parts add up to the total. |
| [skills/receipt-match/SKILL.md](skills/receipt-match/SKILL.md) | Link a receipt to a statement line, and dedupe a photo against an email. |
| [routines/daily-receipt-scan.md](routines/daily-receipt-scan.md) | Daily email receipt scan of every ready Gmail and Outlook account. A statement-ready email is handed to the statement nudge. The owner's bot runs the v2.0 migration when the book is older, before it logs. |
| [routines/card-due-reminder.md](routines/card-due-reminder.md) | Three days before a card's due date, and on the due date, unless that bill is paid. |
| [routines/statement-ready.md](routines/statement-ready.md) | Nudge when an issuer email says the statement is ready, or three days after the usual statement day. |
| [routines/new-year-book.md](routines/new-year-book.md) | December 20 at 9:00 AM, on the owner's bot only: refresh the skills from this repo, create next year's book, and carry the Cards rows and the Merchant Map. Do not copy transactions. |

The workbook stays at [template/family-book-template.xlsx](../template/family-book-template.xlsx). Sheet names, category labels, section headers, and receipt file names stay English. Translated templates (for example `template/family-book-template-fr.xlsx`) may be added later on request. The bot replies in the language the user writes in, with no language question at setup. Older books are updated by [skills/family-book-migrate/SKILL.md](skills/family-book-migrate/SKILL.md). The plan is [docs/migration-v2.0.md](../docs/migration-v2.0.md).
