# Family Book bot files

These files are what a Grok Bot needs to run Family Book. The published Grok Bot template is thin. It does not keep its own copy of the rules. On first use, its family-book skill downloads [bot/skills/family-book/SKILL.md](skills/family-book/SKILL.md) from this repo, and [getting-started.md](getting-started.md) pulls the routines and [memory.md](memory.md) from here. Changes pushed to this repo reach new users the next time a bot sets up.

| File | Role |
|---|---|
| [getting-started.md](getting-started.md) | First chat: download the latest files, check which services are already connected, and skip service questions when Google Drive or OneDrive is ready. Basic connect setup happens only when no store is connected. Currency and holiday region are inferred and confirmed in one line. The owner gets a `Family Book` root folder, with the year folder inside it. |
| [memory.md](memory.md) | Conventions saved to the bot's memory: owner or member, the root folder, the shared book, and what stays English. There is no language setting. |
| [skills/family-book/SKILL.md](skills/family-book/SKILL.md) | The family-book skill: detect-first setup, adding a service later, the root folder, the year's book, moving older year folders into the root, holidays, receipt logging through column BS, and the rule that the same purchase is never logged twice. |
| [skills/family-book-migrate/SKILL.md](skills/family-book-migrate/SKILL.md) | One-time update for books from v1.0 through v1.2.2. The owner's bot rebuilds the month receipt lists and renames files. It does not retype the numbers. |
| [routines/daily-receipt-scan.md](routines/daily-receipt-scan.md) | Daily email receipt scan of every ready Gmail and Outlook account, including one connected later. The owner's bot moves any top-level year folders into `Family Book`, and runs the v1.2.3 migration if the book is older, before it logs. The digest goes out in the user's chat language. |
| [routines/new-year-book.md](routines/new-year-book.md) | December 20 at 9:00 AM, on the owner's bot only: refresh the skill from this repo and create next year's book inside the same `Family Book` root. |

The workbook stays at [template/family-book-template.xlsx](../template/family-book-template.xlsx). Sheet names, category labels, receipt-list headers, and receipt file names stay English. Translated templates (for example `template/family-book-template-fr.xlsx`) may be added later on request. The bot replies in the language the user writes in, with no language question at setup. Older books are updated by [skills/family-book-migrate/SKILL.md](skills/family-book-migrate/SKILL.md). The plan is [docs/migration-v1.2.3.md](../docs/migration-v1.2.3.md).
