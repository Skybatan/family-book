# Family Book bot files

These files are what a Grok Bot needs to run Family Book. The published Grok Bot template is thin. It does not keep its own copy of the rules. On first use, its family-book skill downloads [bot/skills/family-book/SKILL.md](skills/family-book/SKILL.md) from this repo, and [getting-started.md](getting-started.md) pulls the routines and [memory.md](memory.md) from here. Changes pushed to this repo reach new users the next time a bot sets up.

| File | Role |
|---|---|
| [getting-started.md](getting-started.md) | First chat: download the latest files, then ask language, storage, email, currency, and holiday region, and create this year's book and routines. |
| [memory.md](memory.md) | Conventions saved to the bot's memory, including the user's language and what stays English. |
| [skills/family-book/SKILL.md](skills/family-book/SKILL.md) | The family-book skill: setup, the year's book, holidays, and receipt logging. |
| [routines/daily-receipt-scan.md](routines/daily-receipt-scan.md) | Daily email receipt scan. The digest goes out in the user's language. |
| [routines/new-year-book.md](routines/new-year-book.md) | December 20 at 9:00 AM: refresh the skill from this repo and create next year's book. |

The workbook stays at [template/family-book-template.xlsx](../template/family-book-template.xlsx). Sheet names, category labels, and receipt file names stay English. Translated templates (for example `template/family-book-template-fr.xlsx`) may be added later on request.
